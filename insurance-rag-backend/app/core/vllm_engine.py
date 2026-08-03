# app/core/vllm_engine.py
"""
vLLM Inference Engine for faster LLM responses
Replaces the default Hugging Face pipeline
"""

from vllm import LLM, SamplingParams
from typing import List, Dict, Any
import torch

class VLLMEngine:
    def __init__(self, model_path: str = "Qwen/Qwen2.5-7B-Instruct"):
        """Initialize vLLM engine with your model"""
        print(f"🚀 Loading model with vLLM: {model_path}")
        
        self.llm = LLM(
            model=model_path,
            tensor_parallel_size=1,  # 1 GPU
            gpu_memory_utilization=0.85,  # Use 85% of VRAM
            max_model_len=8192,  # Max context length
            trust_remote_code=True,
            dtype="float16",  # Use FP16 for speed
            enforce_eager=True,  # Disable CUDA graphs for compatibility
        )
        
        self.sampling_params = SamplingParams(
            temperature=0.7,
            max_tokens=512,
            top_p=0.9,
        )
        print("✅ vLLM engine loaded")
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        """Generate response using vLLM"""
        sampling_params = SamplingParams(
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=0.9,
        )
        
        outputs = self.llm.generate([prompt], sampling_params)
        return outputs[0].outputs[0].text
    
    def generate_batch(self, prompts: List[str], max_tokens: int = 512) -> List[str]:
        """Generate responses for multiple prompts in batch (faster!)"""
        sampling_params = SamplingParams(
            temperature=0.7,
            max_tokens=max_tokens,
            top_p=0.9,
        )
        
        outputs = self.llm.generate(prompts, sampling_params)
        return [o.outputs[0].text for o in outputs]

# Singleton instance
_vllm_instance = None

def get_vllm_engine():
    global _vllm_instance
    if _vllm_instance is None:
        _vllm_instance = VLLMEngine()
    return _vllm_instance