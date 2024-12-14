from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import random
import csv

model_name = "EleutherAI/gpt-neo-1.3B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

def parse_csv_to_categories(file_path):
    categories = []
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            if row:
                categories.append(row[0].strip())
    return categories

def generate_next_category(input_categories):
    prompt = (
        f"Пользователь купил категории: {', '.join(input_categories)}. "
        "Укажи одну категорию, логически связанную с предыдущими покупками. "
        "Пример: \"Электроника\" -> \"Смартфоны\". Следующая подходящая категория: "
    )
    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)

    outputs = model.generate(
        inputs.input_ids,
        attention_mask=inputs.attention_mask,
        max_new_tokens=20,
        num_return_sequences=1,
        temperature=0.7,
        top_k=50,
        do_sample=True,
        pad_token_id=tokenizer.pad_token_id,
    )

    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    if "Следующая подходящая категория:" in generated_text:
        generated_text = generated_text.split("Следующая подходящая категория:")[-1].strip()

    generated_text = generated_text.split(".")[0].split(",")[0].strip()

    if len(generated_text.split()) > 3:
        generated_text = " ".join(generated_text.split()[:3])

    return generated_text

def create_dataset(categories, num_users, num_sessions):
    dataset = []
    for user_id in range(1, num_users + 1):
        user = f"User_{user_id}"
        for _ in range(num_sessions):

            input_categories = random.sample(categories, 2)
            next_category = generate_next_category(input_categories)
            if next_category:
                dataset.append({
                    "input": input_categories,
                    "target": next_category
                })
    return dataset

def save_synthetic_data_to_csv(synthetic_data, file_path):
    with open(file_path, mode="w", encoding="utf-8-sig", newline="") as csvfile:
        fieldnames = ["input_1", "input_2", "target"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for data in synthetic_data:
            writer.writerow({
                "input_1": data["input"][0],
                "input_2": data["input"][1],
                "target": data["target"]
            })

categories_file = 'categories.csv'
categories = parse_csv_to_categories(categories_file)

num_users = 10
num_sessions = 3

synthetic_data = create_dataset(categories, num_users, num_sessions)

output_file = "synthetic_data_transformers.csv"
save_synthetic_data_to_csv(synthetic_data, output_file)

print(f"Синтетический датасет сохранён в файл: {output_file}")
