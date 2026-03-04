import pandas as pd
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
import pickle

# Set device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# Load the dataset
try:
    df = pd.read_csv('anxiety_text_dataset.csv')
except FileNotFoundError:
    print("Error: anxiety_text_dataset.csv not found. Run data_preprocessing.py first.")
    exit(1)

# Map labels to integers
label_mapping = {"Low": 0, "Moderate": 1, "High": 2}
df['label'] = df['Exam_Anxiety_Level'].map(label_mapping)

texts = df['student_text'].tolist()
labels = df['label'].tolist()

# Split the dataset
train_texts, val_texts, train_labels, val_labels = train_test_split(texts, labels, test_size=0.2, random_state=42)

# Load tokenizer
model_name = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Tokenize data
train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=128)
val_encodings = tokenizer(val_texts, truncation=True, padding=True, max_length=128)

# Create torch datasets
class AnxietyDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

train_dataset = AnxietyDataset(train_encodings, train_labels)
val_dataset = AnxietyDataset(val_encodings, val_labels)

# Load model
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=3)
model.to(device)

# We will use native PyTorch training loop to avoid Trainer segfaults on this environment.
from torch.utils.data import DataLoader
from torch.optim import AdamW

train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=16)

optimizer = AdamW(model.parameters(), lr=5e-5)

epochs = 1
print("Starting to train the BERT model using native PyTorch loop...")

for epoch in range(epochs):
    model.train()
    total_train_loss = 0
    
    for batch in train_loader:
        optimizer.zero_grad()
        
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)
        
        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss
        total_train_loss += loss.item()
        
        loss.backward()
        optimizer.step()
        
    avg_train_loss = total_train_loss / len(train_loader)
    print(f"Epoch {epoch+1} - Average Training Loss: {avg_train_loss:.4f}")

# Evaluation
model.eval()
total_eval_loss = 0
correct_predictions = 0

print("Evaluating...")
with torch.no_grad():
    for batch in val_loader:
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)
        
        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss
        total_eval_loss += loss.item()
        
        logits = outputs.logits
        preds = torch.argmax(logits, dim=-1)
        correct_predictions += torch.sum(preds == labels).item()

avg_eval_loss = total_eval_loss / len(val_loader)
accuracy = correct_predictions / len(val_dataset)

print(f"Validation Loss: {avg_eval_loss:.4f}")
print(f"Validation Accuracy: {accuracy:.4f}")

# Save the trained model and tokenizer
model_dir = "bert_anxiety_model"
model.save_pretrained(model_dir)
tokenizer.save_pretrained(model_dir)
print(f"Model and tokenizer saved to {model_dir}/")

# Also save the label encoder logic so the API knows the classes
with open("bert_label_encoder.sav", "wb") as f:
    # reverse mapping
    reverse_mapping = {v: k for k, v in label_mapping.items()}
    pickle.dump(reverse_mapping, f)

print("Finished successfully!")
