"""
Incremental Trainer - Fine-tune existing model with new data

This trainer uses the previously trained model as base and continues
training with new admin-labeled data, preserving learned knowledge
while adapting to new examples.
"""

import os
import pandas as pd
import torch
from datetime import datetime
from typing import Dict, Optional
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
    EarlyStoppingCallback,
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from datasets import Dataset
import numpy as np


class IncrementalTrainer:
    def __init__(
        self,
        base_model_path: str,
        dataset_path: str,
        output_path: str,
        epochs: int = 2,  # Fewer epochs for incremental training
        batch_size: int = 8,
        learning_rate: float = 1e-5,  # Lower LR for fine-tuning
    ):
        self.base_model_path = base_model_path
        self.dataset_path = dataset_path
        self.output_path = output_path
        self.epochs = epochs
        self.batch_size = batch_size
        self.learning_rate = learning_rate

        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def load_base_model(self) -> bool:
        """Load the existing trained model as base"""
        try:
            print(f"Loading base model from: {self.base_model_path}")

            # Check if model exists
            if not os.path.exists(self.base_model_path):
                print(f"Base model not found at {self.base_model_path}")
                print("Will use default IndoBERT model")
                self.base_model_path = "indobenchmark/indobert-base-p1"

            self.tokenizer = AutoTokenizer.from_pretrained(self.base_model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.base_model_path,
                num_labels=2,
                id2label={0: "non-hoax", 1: "hoax"},
                label2id={"non-hoax": 0, "hoax": 1}
            )

            self.model.to(self.device)
            print(f"Model loaded successfully on {self.device}")
            return True

        except Exception as e:
            print(f"Error loading base model: {e}")
            return False

    def load_dataset(self) -> Optional[pd.DataFrame]:
        """Load training dataset from CSV"""
        try:
            if not os.path.exists(self.dataset_path):
                print(f"Dataset not found: {self.dataset_path}")
                return None

            df = pd.read_csv(self.dataset_path)

            # Validate required columns
            if "text" not in df.columns or "label" not in df.columns:
                print("Dataset must have 'text' and 'label' columns")
                return None

            # Remove empty rows
            df = df.dropna(subset=["text", "label"])
            df = df[df["text"].str.strip() != ""]

            print(f"Loaded {len(df)} samples")
            print(f"  Non-hoax: {sum(df['label'] == 0)}")
            print(f"  Hoax: {sum(df['label'] == 1)}")

            return df

        except Exception as e:
            print(f"Error loading dataset: {e}")
            return None

    def prepare_datasets(self, df: pd.DataFrame):
        """Prepare train/val datasets"""
        # Split data (90% train, 10% validation)
        train_df, val_df = train_test_split(
            df,
            test_size=0.1,
            random_state=42,
            stratify=df["label"] if len(df) > 10 else None
        )

        print(f"Train samples: {len(train_df)}")
        print(f"Validation samples: {len(val_df)}")

        # Convert to HuggingFace Dataset
        train_dataset = Dataset.from_pandas(train_df[["text", "label"]])
        val_dataset = Dataset.from_pandas(val_df[["text", "label"]])

        # Tokenize
        def tokenize_function(examples):
            return self.tokenizer(
                examples["text"],
                padding="max_length",
                truncation=True,
                max_length=512
            )

        train_dataset = train_dataset.map(tokenize_function, batched=True)
        val_dataset = val_dataset.map(tokenize_function, batched=True)

        # Set format
        train_dataset.set_format("torch", columns=["input_ids", "attention_mask", "label"])
        val_dataset.set_format("torch", columns=["input_ids", "attention_mask", "label"])

        return train_dataset, val_dataset

    def compute_metrics(self, eval_pred):
        """Compute metrics for evaluation"""
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)

        precision, recall, f1, _ = precision_recall_fscore_support(
            labels, predictions, average="binary"
        )
        acc = accuracy_score(labels, predictions)

        return {
            "accuracy": acc,
            "precision": precision,
            "recall": recall,
            "f1": f1
        }

    def train(self) -> Dict:
        """
        Run incremental training

        Returns:
            Dict with keys: success, samples, accuracy, f1_score, error
        """
        print("\n" + "=" * 60)
        print("INCREMENTAL TRAINING")
        print("=" * 60)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Device: {self.device.upper()}")

        # Step 1: Load base model
        if not self.load_base_model():
            return {"success": False, "error": "Failed to load base model", "samples": 0}

        # Step 2: Load dataset
        df = self.load_dataset()
        if df is None or len(df) == 0:
            return {"success": False, "error": "No training data available", "samples": 0}

        # Check minimum samples
        if len(df) < 10:
            return {
                "success": False,
                "error": f"Need at least 10 samples, got {len(df)}",
                "samples": len(df)
            }

        # Step 3: Prepare datasets
        try:
            train_dataset, val_dataset = self.prepare_datasets(df)
        except Exception as e:
            return {"success": False, "error": f"Data preparation failed: {e}", "samples": len(df)}

        # Step 4: Configure training
        training_args = TrainingArguments(
            output_dir=f"{self.output_path}/checkpoints",
            evaluation_strategy="epoch",
            save_strategy="epoch",
            learning_rate=self.learning_rate,
            per_device_train_batch_size=self.batch_size,
            per_device_eval_batch_size=self.batch_size,
            num_train_epochs=self.epochs,
            weight_decay=0.01,
            load_best_model_at_end=True,
            metric_for_best_model="f1",
            logging_dir=f"{self.output_path}/logs",
            logging_steps=10,
            save_total_limit=2,
            fp16=torch.cuda.is_available(),
            warmup_ratio=0.1,  # Warm up for fine-tuning
        )

        # Step 5: Create trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            compute_metrics=self.compute_metrics,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]
        )

        # Step 6: Train
        try:
            print("\nStarting incremental training...")
            trainer.train()

            # Step 7: Evaluate
            eval_results = trainer.evaluate()
            print("\nEvaluation Results:")
            for key, value in eval_results.items():
                if "loss" not in key:
                    print(f"  {key}: {value:.4f}")

            # Step 8: Save model
            print(f"\nSaving model to {self.output_path}")
            trainer.save_model(self.output_path)
            self.tokenizer.save_pretrained(self.output_path)

            # Save training metadata
            self._save_training_metadata(len(df), eval_results)

            print("\n" + "=" * 60)
            print("INCREMENTAL TRAINING COMPLETED!")
            print("=" * 60)

            return {
                "success": True,
                "samples": len(df),
                "accuracy": eval_results.get("eval_accuracy"),
                "f1_score": eval_results.get("eval_f1"),
            }

        except Exception as e:
            print(f"Training error: {e}")
            return {"success": False, "error": str(e), "samples": len(df)}

    def _save_training_metadata(self, samples: int, eval_results: Dict):
        """Save metadata about this training run"""
        metadata = {
            "trained_at": datetime.now().isoformat(),
            "samples_used": samples,
            "base_model": self.base_model_path,
            "epochs": self.epochs,
            "learning_rate": self.learning_rate,
            "eval_accuracy": eval_results.get("eval_accuracy"),
            "eval_f1": eval_results.get("eval_f1"),
            "eval_precision": eval_results.get("eval_precision"),
            "eval_recall": eval_results.get("eval_recall"),
        }

        metadata_path = f"{self.output_path}/training_metadata.json"
        import json
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"Training metadata saved to {metadata_path}")


# Standalone execution for testing
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Incremental Training")
    parser.add_argument("--base-model", default="./hoax_model", help="Base model path")
    parser.add_argument("--dataset", required=True, help="Training dataset CSV")
    parser.add_argument("--output", default="./hoax_model", help="Output path")
    parser.add_argument("--epochs", type=int, default=2, help="Number of epochs")

    args = parser.parse_args()

    trainer = IncrementalTrainer(
        base_model_path=args.base_model,
        dataset_path=args.dataset,
        output_path=args.output,
        epochs=args.epochs
    )

    result = trainer.train()
    print(f"\nResult: {result}")
