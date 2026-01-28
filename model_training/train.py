import os
import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification, 
    Trainer, 
    TrainingArguments
)
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels.tolist()

    def __getitem__(self, idx):
        item = {k: torch.tensor(v[idx]) for k, v in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = logits.argmax(axis=1)
    return {
        "accuracy": accuracy_score(labels, preds),
        "f1": f1_score(labels, preds)
    }

def train_model(data_path, output_dir="saved_model/fake-news-bert"):
    # Load dataset
    logger.info(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    
    # Split data
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        df["text"], df["label"], test_size=0.1, random_state=42
    )

    # Initialize tokenizer
    model_name = "bert-base-uncased"
    logger.info(f"Initializing tokenizer: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Tokenize
    logger.info("Tokenizing datasets...")
    train_enc = tokenizer(list(train_texts), truncation=True, padding=True, max_length=256)
    val_enc = tokenizer(list(val_texts), truncation=True, padding=True, max_length=256)

    # Create datasets
    train_ds = NewsDataset(train_enc, train_labels)
    val_ds = NewsDataset(val_enc, val_labels)

    # Initialize model
    logger.info(f"Initializing model: {model_name}")
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)

    # Training arguments
    training_args = TrainingArguments(
        output_dir="./results",
        evaluation_strategy="epoch",
        save_strategy="epoch",
        num_train_epochs=3,
        per_device_train_batch_size=16,
        learning_rate=2e-5,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        report_to="none"
    )

    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        compute_metrics=compute_metrics
    )

    # Train
    logger.info("Starting training...")
    trainer.train()

    # Save model and tokenizer
    logger.info(f"Saving model to {output_dir}...")
    os.makedirs(output_dir, exist_ok=True)
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    logger.info("Training complete!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Train BERT Fake News Detector")
    parser.add_argument("--data", type=str, required=True, help="Path to CSV data")
    parser.add_argument("--output", type=str, default="saved_model/fake-news-bert", help="Output directory")
    args = parser.parse_args()
    
    train_model(args.data, args.output)
