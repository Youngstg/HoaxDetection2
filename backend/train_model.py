"""
Training Script untuk Fine-tune IndoBERT untuk Hoax Detection

Requirements:
- dataset.csv (dari dataset_collector.py)
- GPU (optional tapi recommended)
"""

import pandas as pd
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
    EarlyStoppingCallback,
    TrainerCallback
)
from sklearn.model_selection import train_test_split
from datasets import Dataset
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report
)
import os
import matplotlib.pyplot as plt
import seaborn as sns


class PrinterCallback(TrainerCallback):
    """Custom callback untuk print progress setiap epoch"""
    def on_epoch_end(self, args, state, control, **kwargs):
        print(f"\n{'='*70}")
        print(f"📊 EPOCH {int(state.epoch)} COMPLETED")
        print(f"{'='*70}")

    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs and 'loss' in logs:
            epoch = int(state.epoch) if state.epoch else 0
            if 'eval_accuracy' in logs:
                print(f"\n✅ Epoch {epoch} | "
                      f"Loss: {logs['loss']:.4f} | "
                      f"Val Accuracy: {logs['eval_accuracy']:.4f} | "
                      f"Val F1: {logs.get('eval_f1', 0):.4f}")


class HoaxModelTrainer:
    def __init__(self, dataset_path="dataset.csv", model_name="indobenchmark/indobert-base-p1"):
        self.dataset_path = dataset_path
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.train_dataset = None
        self.val_dataset = None
        self.test_dataset = None
        self.trainer = None

    def load_dataset(self):
        """Load dataset dari CSV"""
        print(f"Loading dataset from {self.dataset_path}...")

        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(
                f"Dataset file {self.dataset_path} not found!\n"
                "Run dataset_collector.py first to collect data."
            )

        df = pd.read_csv(self.dataset_path)

        print(f"Total samples: {len(df)}")
        print(f"Non-hoax: {sum(df['label'] == 0)} ({sum(df['label'] == 0)/len(df)*100:.1f}%)")
        print(f"Hoax: {sum(df['label'] == 1)} ({sum(df['label'] == 1)/len(df)*100:.1f}%)")

        # Check balance
        if len(df[df['label'] == 0]) < 50 or len(df[df['label'] == 1]) < 50:
            print("\n⚠️  WARNING: Dataset tidak seimbang!")
            print("Minimal 50 samples per class diperlukan untuk training yang baik.")
            print(f"Current: Non-hoax={len(df[df['label'] == 0])}, Hoax={len(df[df['label'] == 1])}")

        return df

    def prepare_data(self, df, test_size=0.2, val_size=0.1):
        """Split data menjadi train, val, test"""
        print("\nSplitting dataset...")

        # First split: train+val vs test
        train_val, test = train_test_split(
            df, test_size=test_size, random_state=42, stratify=df['label']
        )

        # Second split: train vs val
        train, val = train_test_split(
            train_val, test_size=val_size/(1-test_size), random_state=42, stratify=train_val['label']
        )

        print(f"Train: {len(train)} samples")
        print(f"Validation: {len(val)} samples")
        print(f"Test: {len(test)} samples")

        # Convert to HuggingFace Dataset
        self.train_dataset = Dataset.from_pandas(train[['text', 'label']])
        self.val_dataset = Dataset.from_pandas(val[['text', 'label']])
        self.test_dataset = Dataset.from_pandas(test[['text', 'label']])

    def tokenize_data(self):
        """Tokenize text data"""
        print("\nTokenizing data...")

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

        def tokenize_function(examples):
            return self.tokenizer(
                examples['text'],
                padding="max_length",
                truncation=True,
                max_length=512
            )

        self.train_dataset = self.train_dataset.map(tokenize_function, batched=True)
        self.val_dataset = self.val_dataset.map(tokenize_function, batched=True)
        self.test_dataset = self.test_dataset.map(tokenize_function, batched=True)

        # Set format for PyTorch
        self.train_dataset.set_format('torch', columns=['input_ids', 'attention_mask', 'label'])
        self.val_dataset.set_format('torch', columns=['input_ids', 'attention_mask', 'label'])
        self.test_dataset.set_format('torch', columns=['input_ids', 'attention_mask', 'label'])

        print("Tokenization completed!")

    def compute_metrics(self, eval_pred):
        """Compute metrics untuk evaluation"""
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)

        precision, recall, f1, _ = precision_recall_fscore_support(
            labels, predictions, average='binary'
        )
        acc = accuracy_score(labels, predictions)

        return {
            'accuracy': acc,
            'precision': precision,
            'recall': recall,
            'f1': f1
        }

    def plot_confusion_matrix(self, output_dir):
        """Plot dan save confusion matrix"""
        # Get predictions
        predictions = self.trainer.predict(self.test_dataset)
        y_pred = np.argmax(predictions.predictions, axis=1)
        y_true = predictions.label_ids

        # Compute confusion matrix
        cm = confusion_matrix(y_true, y_pred)

        # Plot
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            cm,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=['Non-Hoax', 'Hoax'],
            yticklabels=['Non-Hoax', 'Hoax'],
            cbar_kws={'label': 'Count'}
        )
        plt.title('Confusion Matrix - Hoax Detection Model', fontsize=16, fontweight='bold')
        plt.ylabel('True Label', fontsize=12)
        plt.xlabel('Predicted Label', fontsize=12)

        # Add text annotations
        total = cm.sum()
        accuracy = (cm[0,0] + cm[1,1]) / total
        plt.text(
            0.5, 1.15,
            f'Overall Accuracy: {accuracy:.2%}',
            ha='center',
            transform=plt.gca().transAxes,
            fontsize=14,
            fontweight='bold'
        )

        # Save figure
        plt.tight_layout()
        save_path = f"{output_dir}/confusion_matrix.png"
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()

        # Print confusion matrix
        print(f"\n{'='*70}")
        print("CONFUSION MATRIX")
        print(f"{'='*70}")
        print(f"\n                 Predicted")
        print(f"                 Non-Hoax    Hoax")
        print(f"True Non-Hoax      {cm[0,0]:4d}      {cm[0,1]:4d}")
        print(f"True Hoax          {cm[1,0]:4d}      {cm[1,1]:4d}")
        print(f"\n{'='*70}")

        # Calculate metrics from confusion matrix
        tn, fp, fn, tp = cm.ravel()
        print(f"\n📊 Detailed Metrics:")
        print(f"   True Negatives (TN):  {tn:4d} - Correctly identified as Non-Hoax")
        print(f"   False Positives (FP): {fp:4d} - Non-Hoax predicted as Hoax")
        print(f"   False Negatives (FN): {fn:4d} - Hoax predicted as Non-Hoax")
        print(f"   True Positives (TP):  {tp:4d} - Correctly identified as Hoax")
        print(f"\n   Total Samples: {total}")
        print(f"   Accuracy: {accuracy:.2%}")

    def print_classification_report(self):
        """Print detailed classification report"""
        # Get predictions
        predictions = self.trainer.predict(self.test_dataset)
        y_pred = np.argmax(predictions.predictions, axis=1)
        y_true = predictions.label_ids

        # Generate classification report
        report = classification_report(
            y_true,
            y_pred,
            target_names=['Non-Hoax', 'Hoax'],
            digits=4
        )

        print(f"\n{report}")

    def train(self, output_dir="./hoax_model", epochs=3, batch_size=8):
        """Train model"""
        print("\n" + "="*60)
        print("Starting Training")
        print("="*60)

        # Check CUDA
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"\n🎮 Device: {device.upper()}")
        if device == "cuda":
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
            print(f"   Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        else:
            print(f"   ⚠️  WARNING: CUDA not available, using CPU (will be slow!)")

        # Load model
        print(f"\nLoading model: {self.model_name}")
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=2,
            id2label={0: "non-hoax", 1: "hoax"},
            label2id={"non-hoax": 0, "hoax": 1}
        )

        # Move model to GPU if available
        if device == "cuda":
            self.model = self.model.to(device)

        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            evaluation_strategy="epoch",
            save_strategy="epoch",
            learning_rate=2e-5,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            num_train_epochs=epochs,
            weight_decay=0.01,
            load_best_model_at_end=True,
            metric_for_best_model="f1",
            logging_dir=f"{output_dir}/logs",
            logging_steps=10,
            save_total_limit=2,
            fp16=torch.cuda.is_available(),
            no_cuda=False,  # Force use CUDA if available
            use_cpu=False,  # Don't force CPU
        )

        # Create trainer
        self.trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=self.train_dataset,
            eval_dataset=self.val_dataset,
            compute_metrics=self.compute_metrics,
            callbacks=[
                EarlyStoppingCallback(early_stopping_patience=2),
                PrinterCallback()
            ]
        )

        # Train
        print("\n🚀 Starting Training...")
        print(f"📊 Training on {len(self.train_dataset)} samples")
        print(f"📊 Validating on {len(self.val_dataset)} samples")
        print(f"📊 Testing on {len(self.test_dataset)} samples\n")

        self.trainer.train()

        # Evaluate on test set
        print("\n" + "="*70)
        print("📊 FINAL EVALUATION ON TEST SET")
        print("="*70)

        test_results = self.trainer.evaluate(self.test_dataset)
        print("\n✅ Test Results:")
        for key, value in test_results.items():
            if 'loss' not in key:
                print(f"   {key.replace('eval_', '').title()}: {value:.4f}")

        # Generate predictions for confusion matrix
        print("\n📈 Generating Confusion Matrix...")
        self.plot_confusion_matrix(output_dir)

        # Classification report
        print("\n📋 Detailed Classification Report:")
        self.print_classification_report()

        # Save final model
        print(f"\n💾 Saving model to {output_dir}")
        self.trainer.save_model(output_dir)
        self.tokenizer.save_pretrained(output_dir)

        print("\n" + "="*70)
        print("✅ TRAINING COMPLETED SUCCESSFULLY!")
        print("="*70)
        print(f"\n📁 Model saved to: {output_dir}")
        print(f"📊 Confusion matrix saved to: {output_dir}/confusion_matrix.png")
        print("\n📝 To use this model:")
        print(f"   1. Update .env: MODEL_NAME={output_dir}")
        print(f"   2. Update .env: USE_ML_MODEL=true")
        print(f"   3. Restart backend server")
        print("="*70)

    def run(self, epochs=3, batch_size=8):
        """Run full training pipeline"""
        # Load dataset
        df = self.load_dataset()

        # Prepare data
        self.prepare_data(df)

        # Tokenize
        self.tokenize_data()

        # Train
        self.train(epochs=epochs, batch_size=batch_size)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Train Hoax Detection Model")
    parser.add_argument("--dataset", default="dataset.csv", help="Path to dataset CSV")
    parser.add_argument("--model", default="indobenchmark/indobert-base-p1", help="Base model name")
    parser.add_argument("--epochs", type=int, default=3, help="Number of epochs")
    parser.add_argument("--batch-size", type=int, default=8, help="Batch size")
    parser.add_argument("--output", default="./hoax_model", help="Output directory")

    args = parser.parse_args()

    trainer = HoaxModelTrainer(
        dataset_path=args.dataset,
        model_name=args.model
    )

    trainer.run(epochs=args.epochs, batch_size=args.batch_size)
