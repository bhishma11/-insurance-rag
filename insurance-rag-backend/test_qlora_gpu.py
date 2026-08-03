import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import gc

# Paths
BASE_MODEL = "Qwen/Qwen2.5-7B-Instruct"
ADAPTER_PATH = "./qlora_adapters_gpu"

print("📥 Loading model...")

# Clear CUDA cache
torch.cuda.empty_cache()
gc.collect()

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token

# Load base model with explicit GPU mapping
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float16,
    device_map="cuda:0",  # Force GPU
    trust_remote_code=True,
)

# Load adapter
model = PeftModel.from_pretrained(
    base_model, 
    ADAPTER_PATH,
    device_map="cuda:0",  # Force GPU
)
model.eval()

print("✅ Model loaded on GPU!")

# Test prompts
test_prompts = [
    "Calculate my premium for 30 year old with $35,000 car",
    "Does auto policy cover windshield damage?",
    "What is the deductible for renters insurance?",
]

print("\n" + "=" * 60)
print("🧪 Testing QLoRA Fine-tuned Model (GPU)")
print("=" * 60)

for prompt in test_prompts:
    print(f"\n📝 User: {prompt}")
    
    formatted = f"User: {prompt}\nAssistant:"
    inputs = tokenizer(formatted, return_tensors="pt").to("cuda")
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=200,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    if "Assistant:" in response:
        response = response.split("Assistant:")[-1].strip()
    
    print(f"🤖 Assistant: {response}")
    print("-" * 40)

print("\n✅ Testing complete!")