import os
import json
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import Dataset
from trl import SFTTrainer

# Configuration
MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"
OUTPUT_DIR = "./qlora_adapters_gpu"
TRAINING_DATA = "training_data/insurance_qa_large.jsonl"

# Check GPU
if torch.cuda.is_available():
    print(f"✅ Using GPU: {torch.cuda.get_device_name(0)}")
else:
    print("⚠️ CUDA not available, using CPU")

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

# QLoRA Config - Use float16
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

# LoRA Config
lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

print("📥 Loading model...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
)

model = prepare_model_for_kbit_training(model)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

print("📊 Loading dataset...")
with open(TRAINING_DATA, "r") as f:
    data = [json.loads(line) for line in f]

def format_chat_template(example):
    return {"text": f"User: {example['instruction']}\nAssistant: {example['response']}"}

dataset = Dataset.from_list(data)
dataset = dataset.map(format_chat_template)

print(f"✅ Loaded {len(dataset)} training examples")

# Training args - DISABLE mixed precision
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    num_train_epochs=3,
    learning_rate=2e-4,
    logging_steps=5,
    save_steps=50,
    save_total_limit=3,
    report_to="none",
    fp16=False,  # Disable fp16
    bf16=False,  # Disable bf16
    optim="paged_adamw_8bit",
    save_strategy="steps",
    dataloader_pin_memory=False,
    remove_unused_columns=False,
    max_grad_norm=0.3,
)

print("🚀 Starting training on GPU (no mixed precision)...")

trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
)

trainer.train()

print("💾 Saving adapter...")
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print(f"✅ QLoRA adapter saved to {OUTPUT_DIR}")
print("📁 Files saved:")
for file in os.listdir(OUTPUT_DIR):
    print(f"   - {file}")