"""
ML-based Hoax Detector
Menggunakan fine-tuned IndoBERT model untuk deteksi hoax
"""

import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from app.models import HoaxPrediction
from typing import Dict


class MLHoaxDetector:
    def __init__(self, model_path: str = None):
        """
        Initialize ML-based hoax detector

        Args:
            model_path: Path ke trained model (default: ./hoax_model)
        """
        if model_path is None:
            model_path = os.getenv("MODEL_PATH", "./hoax_model")

        self.model_path = model_path
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        print(f"Loading model from {model_path}...")
        print(f"Using device: {self.device}")

        # Load tokenizer dan model
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.model = self.model.to(self.device)
        self.model.eval()

        # Label mapping
        self.id2label = {0: "non-hoax", 1: "hoax"}

        print("Model loaded successfully!")

    def predict(self, text: str, source: str = "") -> HoaxPrediction:
        """
        Predict apakah text adalah hoax atau non-hoax menggunakan ML model

        Args:
            text: Konten berita
            source: Sumber berita (tidak digunakan oleh ML model, tapi kept for API consistency)

        Returns:
            HoaxPrediction object
        """
        # Tokenize input
        inputs = self.tokenizer(
            text,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )

        # Move to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Predict
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)
            predicted_class = torch.argmax(probs, dim=-1).item()
            confidence = probs[0][predicted_class].item()

        # Get label
        label = self.id2label[predicted_class]

        return HoaxPrediction(
            label=label,
            confidence=round(confidence, 4)
        )

    def predict_batch(self, texts: list) -> list:
        """
        Predict multiple texts at once (more efficient)

        Args:
            texts: List of text strings

        Returns:
            List of HoaxPrediction objects
        """
        # Tokenize all inputs
        inputs = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )

        # Move to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Predict
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)
            predicted_classes = torch.argmax(probs, dim=-1)
            confidences = torch.max(probs, dim=-1).values

        # Convert to predictions
        predictions = []
        for pred_class, conf in zip(predicted_classes, confidences):
            label = self.id2label[pred_class.item()]
            predictions.append(
                HoaxPrediction(
                    label=label,
                    confidence=round(conf.item(), 4)
                )
            )

        return predictions

    def get_explanation(self, text: str, source: str = "") -> Dict:
        """
        Memberikan penjelasan prediksi (simplified version for ML)
        """
        prediction = self.predict(text, source)

        return {
            "prediction": prediction.label,
            "confidence": prediction.confidence,
            "model": "IndoBERT Fine-tuned",
            "model_path": self.model_path,
            "device": self.device
        }


# Global instance (will be initialized lazily)
ml_detector = None


def get_ml_detector() -> MLHoaxDetector:
    """
    Get or create ML detector instance (singleton pattern)
    """
    global ml_detector
    if ml_detector is None:
        ml_detector = MLHoaxDetector()
    return ml_detector
