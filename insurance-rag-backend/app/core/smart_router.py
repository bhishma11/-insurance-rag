# app/core/smart_router.py
import os
import json
import re
import torch
import gc
from openai import OpenAI
from typing import Tuple, Dict, Any, Optional
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig
from peft import PeftModel

# ==== CUDA OPTIMIZATIONS ====
if torch.cuda.is_available():
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.benchmark = True
    torch.backends.cudnn.deterministic = False

# Try to import vLLM for faster inference
try:
    from app.core.vllm_engine import get_vllm_engine
    VLLM_AVAILABLE = True
except ImportError:
    VLLM_AVAILABLE = False
    print("⚠️ vLLM not available - using standard PyTorch inference")


class SmartRouter:
    """Smart router that decides which LLM to use based on query type"""

    def __init__(self):
        # ✅ AUTOMATIC CLOUD RUN DETECTION
        self.is_cloud_run = (
            os.getenv('CLOUD_RUN', 'false').lower() == 'true' or 
            'K_SERVICE' in os.environ
        )
        
        # ✅ DeepSeek (Cloud) - for everything except premium & claim status
        self.deepseek = OpenAI(
            api_key=os.getenv('DEEPSEEK_API_KEY'),
            base_url="https://api.deepseek.com"
        )

        # ✅ QLoRA Qwen (Local/Kaggle)
        self.qlora_model = None
        self.qlora_tokenizer = None
        self.vllm_engine = None
        self.model_device = "cpu"  # Track model device
        
        # ✅ Only load QLoRA if NOT on Cloud Run
        if self.is_cloud_run:
            print("☁️ Cloud Run detected (K_SERVICE present) - using DeepSeek only (QLoRA disabled)")
            print(f"   Service: {os.environ.get('K_SERVICE', 'unknown')}")
            print(f"   Revision: {os.environ.get('K_REVISION', 'unknown')}")
        else:
            print("💻 Local/Kaggle development - loading QLoRA...")
            if VLLM_AVAILABLE:
                try:
                    self.vllm_engine = get_vllm_engine()
                    print("✅ vLLM engine initialized for faster inference")
                except Exception as e:
                    print(f"⚠️ vLLM initialization failed: {e}")
                    self.vllm_engine = None
            
            self._load_qlora()

    def _load_qlora(self):
        """Load QLoRA fine-tuned model with optimizations"""
        if self.is_cloud_run:
            print("☁️ Skipping QLoRA loading on Cloud Run")
            self.qlora_model = None
            return
        
        try:
            print("📥 Loading QLoRA model...")
            
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                self.model_device = "cuda"
                print(f"   GPU detected: {torch.cuda.get_device_name(0)}")
            else:
                print("⚠️ No GPU detected - skipping QLoRA loading")
                self.qlora_model = None
                self.model_device = "cpu"
                return

            adapter_path = "./qlora_adapters_gpu"
            if not os.path.exists(adapter_path):
                print(f"⚠️ Adapters not found at {adapter_path} - skipping QLoRA")
                self.qlora_model = None
                return

            config = AutoConfig.from_pretrained("Qwen/Qwen2.5-7B-Instruct")
            config.use_cache = True
            
            base_model = AutoModelForCausalLM.from_pretrained(
                "Qwen/Qwen2.5-7B-Instruct",
                config=config,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True,
            )

            self.qlora_model = PeftModel.from_pretrained(
                base_model,
                adapter_path,
                device_map="auto",
            )
            
            self.qlora_tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct")
            self.qlora_tokenizer.pad_token = self.qlora_tokenizer.eos_token
            self.qlora_tokenizer.padding_side = "left"
            
            self.qlora_model.eval()
            
            # ✅ Get actual device from model safely
            self.model_device = getattr(
                self.qlora_model, 
                "device", 
                next(self.qlora_model.parameters()).device if hasattr(self.qlora_model, "parameters") else "cuda"
            )
            print(f"✅ QLoRA model loaded on {self.model_device}!")
            
        except Exception as e:
            print(f"⚠️ QLoRA load failed: {e}")
            self.qlora_model = None
            self.model_device = "cpu"

    def is_premium_calculation(self, query: str) -> bool:
        """Check if query is a premium calculation"""
        query_lower = query.lower()
        premium_keywords = ['premium', 'calculate', 'cost', 'quote', 'rate', 'monthly', 'yearly', 'how much', 'pay']
        car_keywords = ['car', 'auto', 'vehicle', 'tesla', 'toyota', 'honda', 'bmw']
        
        has_premium = any(kw in query_lower for kw in premium_keywords)
        has_car = any(kw in query_lower for kw in car_keywords)
        has_number = any(char.isdigit() for char in query)
        
        return has_premium and (has_car or has_number)

    def is_claim_status(self, query: str) -> bool:
        """Check if query is a claim status check"""
        query_upper = query.upper()
        if re.search(r'CL-\d+', query_upper):
            return True
        claim_keywords = ['claim status', 'status of claim', 'is my claim', 'claim approved', 'claim denied']
        if any(kw in query.lower() for kw in claim_keywords):
            return True
        return False

    def _extract_premium_data(self, query: str) -> Dict[str, Any]:
        """Extract age and vehicle value reliably from query strings without pattern collision"""
        # 1. Parse age explicitly
        age_match = re.search(r'\b(\d{1,2})\s*(?:years?\s*old|yo|yr)\b', query, re.IGNORECASE)
        age = int(age_match.group(1)) if age_match else 30
        
        # 2. Strip age match to avoid age-number collisions during currency parsing
        query_sans_age = re.sub(r'\b\d{1,2}\s*(?:years?\s*old|yo|yr)\b', '', query, flags=re.IGNORECASE)

        car_value = 35000.0  # Default baseline
        
        # 3. Match currency patterns ($45k, $45,000, worth 45k, valued at 45000)
        val_match = re.search(
            r'(?:\$|\bworth\b|\bvalued?\s*at\b|\bvehicle\s*value\b|\bcar\b)\s*:?\s*\$?(\d+(?:,\d+)*(?:\.\d+)?)\s*(k|thousand)?',
            query_sans_age,
            re.IGNORECASE
        )

        if val_match:
            raw_val = val_match.group(1).replace(',', '')
            try:
                parsed_val = float(raw_val)
                # Apply 1000 multiplier if explicit 'k'/'thousand' or if value is shorthand (<500)
                multiplier = 1000 if (val_match.group(2) or parsed_val < 500) else 1
                car_value = parsed_val * multiplier
            except ValueError:
                pass

        return self._build_premium_response(age, car_value)

    def _build_premium_response(self, age: int, car_value: float) -> Dict[str, Any]:
        """Helper to build premium calculation response"""
        base_rate = 500
        age_factor = 1.2 if age < 25 else 0.8 if age < 60 else 1.3
        vehicle_factor = car_value / 20000
        coverage_factor = 1.5
        monthly = base_rate * age_factor * vehicle_factor * coverage_factor
        yearly = monthly * 12

        return {
            "monthly": round(monthly, 2),
            "yearly": round(yearly, 2),
            "breakdown": [
                {"step": 1, "label": "Base Rate", "value": f"${base_rate:.2f}", "description": "Standard rate for your vehicle class"},
                {"step": 2, "label": "Age Factor", "value": f"× {age_factor:.1f}", "description": f"You're {age} years old - {'low risk' if age_factor < 1 else 'standard risk'}"},
                {"step": 3, "label": "Vehicle Value", "value": f"× {vehicle_factor:.2f}", "description": f"Vehicle valued at ${car_value:,.2f}"},
                {"step": 4, "label": "Coverage Type", "value": f"× {coverage_factor:.1f}", "description": "Comprehensive coverage selected"}
            ],
            "summary": f"Your age ({age}) puts you in a {'low' if age_factor < 1 else 'standard'} risk category, resulting in a premium of ${monthly:.2f}/month.",
            "tip": "💡 Tip: Increasing your deductible could lower your monthly premium by up to 15%."
        }

    def _apply_chat_template(self, query: str, system_prompt: str = None) -> str:
        """Apply Qwen ChatML template for proper formatting"""
        if not self.qlora_tokenizer:
            return query
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": query})
        
        try:
            formatted = self.qlora_tokenizer.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            return formatted
        except Exception as e:
            print(f"⚠️ Chat template failed: {e}, using fallback")
            return f"User: {query}\nAssistant:"

    def _ask_qlora_with_vllm(self, query: str) -> Optional[str]:
        """Use vLLM with proper chat template"""
        if self.is_cloud_run or not self.vllm_engine:
            return None
        
        try:
            system_prompt = """You are an expert insurance premium calculator. Provide DETAILED, STRUCTURED responses with clear formatting."""
            
            if self.qlora_tokenizer:
                formatted = self._apply_chat_template(query, system_prompt)
            else:
                formatted = f"""You are an expert insurance premium calculator. Provide a DETAILED, STRUCTURED response.

User Question: {query}

Please provide:
1. **Monthly Premium**: Clear amount with $ sign
2. **Yearly Premium**: Annual total
3. **Calculation Breakdown**: Step-by-step table
4. **Risk Category**: Explain why this applies
5. **Money-Saving Tips**: 2-3 actionable tips

Assistant:"""
            
            response = self.vllm_engine.generate(
                prompt=formatted,
                max_tokens=1024,
                temperature=0.7
            )
            
            for tag in ["Assistant:", "<|im_start|>assistant"]:
                if tag in response:
                    response = response.split(tag)[-1].strip()
            
            return response
        except Exception as e:
            print(f"⚠️ vLLM generation failed: {e}")
            return None

    def _ask_qlora_pytorch(self, query: str) -> str:
        """Optimized PyTorch QLoRA execution with safe memory management and device routing"""
        if self.is_cloud_run:
            return self._ask_deepseek(query)
            
        if not self.qlora_model or not self.qlora_tokenizer:
            return "⚠️ QLoRA model not available."

        system_prompt = """You are an expert insurance premium calculator. Provide DETAILED, STRUCTURED responses with:
1. Monthly Premium
2. Yearly Premium
3. Calculation Breakdown table
4. Risk Category
5. Money-Saving Tips

Format with ## headings, tables, and **bold** numbers."""
        
        formatted = self._apply_chat_template(query, system_prompt)
        inputs = self.qlora_tokenizer(formatted, return_tensors="pt")
        
        # ✅ Get target device safely without breaking multi-GPU / device_map="auto"
        model_device = getattr(
            self.qlora_model, 
            "device", 
            next(self.qlora_model.parameters()).device if hasattr(self.qlora_model, "parameters") else "cuda"
        )
        inputs = {k: v.to(model_device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.qlora_model.generate(
                **inputs,
                max_new_tokens=1024,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.qlora_tokenizer.eos_token_id,
                use_cache=True,
                num_beams=1,
                repetition_penalty=1.1,
                min_new_tokens=10,
                top_p=0.9,
                top_k=50,
            )

        # Slice input tokens to prevent prompt spillover
        input_length = inputs['input_ids'].shape[1]
        generated_tokens = outputs[0][input_length:]
        response = self.qlora_tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()
        
        # Clean output artifacts
        for tag in ["Assistant:", "<|im_start|>assistant", "<|im_end|>"]:
            if tag in response:
                response = response.split(tag)[-1].strip()

        # ✅ Check reserved memory (fragmented blocks) to clear VRAM effectively
        if torch.cuda.is_available() and torch.cuda.memory_reserved() > 4_000_000_000: # >4GB
            gc.collect()
            torch.cuda.empty_cache()
            
        return response

    def _ask_qlora(self, query: str) -> str:
        """Ask QLoRA model - uses DeepSeek on Cloud Run, QLoRA on Local/Kaggle"""
        if self.is_cloud_run:
            print("☁️ Cloud Run: Using DeepSeek instead of QLoRA")
            return self._ask_deepseek(query)
        
        if VLLM_AVAILABLE and self.vllm_engine:
            try:
                print("⚡ Using vLLM for inference...")
                response = self._ask_qlora_with_vllm(query)
                if response:
                    return response
            except Exception as e:
                print(f"⚠️ vLLM failed, falling back to PyTorch: {e}")
        
        return self._ask_qlora_pytorch(query)

    def _ask_deepseek(self, query: str) -> str:
        """Ask DeepSeek API with timeout guard"""
        try:
            is_insurance = any(kw in query.lower() for kw in [
                'insurance', 'claim', 'policy', 'coverage', 'deductible',
                'premium', 'auto', 'renters', 'health', 'life',
                'compare', 'difference', 'cover', 'exclude', 'file'
            ])
            
            if is_insurance:
                system_prompt = """You are an expert insurance claims adjuster with a warm, professional personality. 
                
Provide DETAILED, STRUCTURED responses with:

1. **Clear headings** using #, ##, ###
2. **Policy Analysis** section with specific policy details
3. **Coverage Summary** table
4. **Recommended Next Steps** with numbered list
5. **Important Notes** with warnings

Use markdown formatting:
- Tables with |---|
- **Bold** for policy numbers and key terms
- Bullet points for lists
- Emojis naturally where they enhance understanding

Be thorough, professional, and helpful. Provide complete, comprehensive answers. Always finish your response with a clear conclusion."""
            else:
                system_prompt = """You are a helpful assistant. Answer questions concisely and accurately with clear formatting. Always finish your response."""
            
            response = self.deepseek.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.7,
                max_tokens=2048,
                timeout=45.0
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"⚠️ DeepSeek API request failed: {e}"

    def ask(self, query: str, use_deepseek_only: bool = False) -> Tuple[str, str, Dict[str, Any]]:
        """
        Route query to appropriate LLM
        
        ROUTING RULES:
        - Cloud Run → Always DeepSeek (QLoRA disabled)
        - use_deepseek_only=True → DeepSeek (sidebar modals)
        - Premium calculations → QLoRA 🟢 (Local/Kaggle only)
        - Claim status checks → QLoRA 🟢 (Local/Kaggle only)
        - Everything else → DeepSeek 🔵
        """
        if self.is_cloud_run:
            print(f"☁️ Cloud Run: Using DeepSeek for: {query[:50]}...")
            response = self._ask_deepseek(query)
            premium_data = self._extract_premium_data(query) if self.is_premium_calculation(query) else {}
            return response, "deepseek", premium_data
        
        if use_deepseek_only:
            print(f"🔵 Using DeepSeek (sidebar) for: {query[:50]}...")
            response = self._ask_deepseek(query)
            premium_data = self._extract_premium_data(query) if self.is_premium_calculation(query) else {}
            return response, "deepseek", premium_data
        
        if self.is_premium_calculation(query):
            if self.qlora_model:
                print(f"🟢 Using QLoRA (premium) for: {query[:50]}...")
                response = self._ask_qlora(query)
                premium_data = self._extract_premium_data(query)
                return response, "qlora", premium_data
            else:
                print(f"⚠️ QLoRA unavailable, using DeepSeek: {query[:50]}...")
                response = self._ask_deepseek(query)
                premium_data = self._extract_premium_data(query)
                return response, "deepseek", premium_data
        
        if self.is_claim_status(query):
            if self.qlora_model:
                print(f"🟢 Using QLoRA (claim status) for: {query[:50]}...")
                response = self._ask_qlora(query)
                return response, "qlora", {}
            else:
                print(f"⚠️ QLoRA unavailable, using DeepSeek: {query[:50]}...")
                response = self._ask_deepseek(query)
                return response, "deepseek", {}
        
        print(f"🔵 Using DeepSeek for: {query[:50]}...")
        response = self._ask_deepseek(query)
        return response, "deepseek", {}