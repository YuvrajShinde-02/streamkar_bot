import json
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments, DataCollatorForLanguageModeling

# 1. Load the dataset from the JSONL file.
# The file is assumed to be in JSON Lines format.
dataset = load_dataset("json", data_files="streamkar_data.jsonl", split="train")

# 2. Create a new column "text" by concatenating "prompt" and "response".
def concat_example(example):
    return {"text": example["prompt"] + example["response"]}

# Map the function to create the "text" column.
dataset = dataset.map(concat_example)

# Optionally, remove the original columns if you don't need them anymore.
dataset = dataset.remove_columns(["prompt", "response"])

# 3. Load the tokenizer and model.
model_name = "microsoft/DialoGPT-small"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer.add_special_tokens({'pad_token': '[PAD]'})
model.resize_token_embeddings(len(tokenizer))


# 4. Tokenize the dataset.
def tokenize_function(examples):
    return tokenizer(examples["text"], truncation=True, max_length=256)

tokenized_dataset = dataset.map(tokenize_function, batched=True)

# 5. Set up a data collator for causal language modeling.
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

# 6. Set up training arguments.
training_args = TrainingArguments(
    output_dir="./dialoGPT-finetuned-streamkar",
    overwrite_output_dir=True,
    num_train_epochs=3,               # Adjust the number of epochs as needed.
    per_device_train_batch_size=2,    # Adjust batch size based on your hardware.
    save_steps=500,
    save_total_limit=2,
    prediction_loss_only=True,
    logging_steps=100,
)

# 7. Initialize the Trainer.
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=data_collator,
)

# 8. Fine-tune the model.
trainer.train()

# 9. Save the fine-tuned model and tokenizer.
model.save_pretrained("./dialoGPT-finetuned-streamkar")
tokenizer.save_pretrained("./dialoGPT-finetuned-streamkar")
