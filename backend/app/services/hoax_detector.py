from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import os
from app.models import HoaxPrediction

class HoaxDetector:
    def __init__(self):
        self.model_name = os.getenv("MODEL_NAME", "indobenchmark/indobert-base-p1")
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def load_model(self):
        if self.model is None:
            print(f"Loading model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

            # Note: For a real implementation, you would need a fine-tuned model
            # This is a placeholder that loads the base model
            # You'll need to replace this with your actual fine-tuned hoax detection model
            try:
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    self.model_name,
                    num_labels=2  # binary classification: hoax or non-hoax
                )
            except:
                # If the model doesn't have a classification head, use base model
                # This is just for demo purposes
                print("Warning: Using base model. You need a fine-tuned model for actual hoax detection.")
                from transformers import AutoModel
                self.model = AutoModel.from_pretrained(self.model_name)

            self.model.to(self.device)
            self.model.eval()
            print(f"Model loaded successfully on {self.device}")

    def predict(self, text: str) -> HoaxPrediction:
        if self.model is None:
            self.load_model()

        # Tokenize input
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        )

        # Move to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Make prediction
        with torch.no_grad():
            try:
                outputs = self.model(**inputs)

                # Check if model has classification head
                if hasattr(outputs, 'logits'):
                    logits = outputs.logits
                    probabilities = torch.softmax(logits, dim=-1)
                    prediction = torch.argmax(probabilities, dim=-1).item()
                    confidence = probabilities[0][prediction].item()

                    label = "hoax" if prediction == 1 else "non-hoax"
                else:
                    # Fallback for base model without classification head
                    # This is a dummy prediction - replace with actual logic
                    print("Warning: Model doesn't have classification head. Using dummy prediction.")
                    label = "non-hoax"
                    confidence = 0.5

            except Exception as e:
                print(f"Error during prediction: {e}")
                # Return default prediction
                label = "non-hoax"
                confidence = 0.5

        return HoaxPrediction(label=label, confidence=round(confidence, 4))

# Global instance
hoax_detector = HoaxDetector()
