import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

# Paths
BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
ADAPTER_PATH = "./qlora_adapters"

print("📥 Loading model...")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token

base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    trust_remote_code=True,
    torch_dtype=torch.float32,
)

model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)
model.eval()

print("✅ Model loaded!")

# Test prompts
test_prompts = [
    "Calculate my premium for 30 year old with $35,000 car",
    "Does auto policy cover windshield damage?",
    "What is the deductible for renters insurance?",
]

print("\n" + "=" * 60)
print("🧪 Testing QLoRA Fine-tuned Model")
print("=" * 60)

for prompt in test_prompts:
    print(f"\n📝 User: {prompt}")
    
    formatted = f"User: {prompt}\nAssistant:"
    inputs = tokenizer(formatted, return_tensors="pt")
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=150,
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