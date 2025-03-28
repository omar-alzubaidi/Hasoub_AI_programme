import pandas as pd
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer, DataCollatorForLanguageModeling
from peft import get_peft_model, PromptTuningConfig, TaskType, PromptTuningInit
from datasets import load_dataset


# Model and Tokenizer Initialization
model_name = "bigscience/bloomz-560m"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True)


def generate_text(model, tokenizer, prompt_text, max_tokens):
    prompt_text = tokenizer(prompt_text, return_tensors="pt")
    outputs = model.generate(
        input_ids=prompt_text["input_ids"],
        attention_mask=prompt_text["attention_mask"],
        max_length=max_tokens,
        repetition_penalty=1.5,
        eos_token_id=tokenizer.eos_token_id
    )
    return tokenizer.batch_decode(outputs, skip_special_tokens=True)


# Initial Model Output
initial_output = generate_text(model, tokenizer, 'I want you to act as a logistician', 100)
print("Initial model output:", initial_output)


# Loading Dataset

dataset_prompt = "fka/awesome-chatgpt-prompts"
data_prompt = load_dataset(dataset_prompt)
data_prompt = data_prompt.map(lambda x: tokenizer(x["prompt"]), batched=True)
train_prompts = data_prompt["train"].select(range(30))


# Setting Up Prompt Tuning Configuration

tuning_config = PromptTuningConfig(
    task_type=TaskType.CAUSAL_LM,
    prompt_tuning_init=PromptTuningInit.RANDOM,
    num_virtual_tokens=4,
    tokenizer_name_or_path=model_name
)

peft_model = get_peft_model(model, tuning_config)


# Training Configuration

training_args = TrainingArguments(
    use_cpu=True,
    output_dir="./",
    auto_find_batch_size=True,
    learning_rate=0.005,
    num_train_epochs=5
)

trainer = Trainer(
    model=peft_model,
    args=training_args,
    train_dataset=train_prompts,
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False)
)

# Training the Model
trainer.train()


# Generating Tuned Model Output

tuned_output = generate_text(trainer.model, tokenizer, "I want you to act as a logistician. ", 100)
print("Tuned model output:", tuned_output)
