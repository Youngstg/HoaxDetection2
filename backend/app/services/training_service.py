"""
Training Service - Manages training data queue and auto-retraining

Features:
- Track admin-labeled data for training
- Auto-retrain when threshold (50 samples) is reached
- Incremental training using previous model as base
- Exclude user-checked data from training
"""

import os
import pandas as pd
from datetime import datetime
from typing import List, Optional, Dict
from app.utils.firebase_config import get_db
from app.models import TrainingDataItem, TrainingQueueStatus, RetrainResponse


class TrainingService:
    def __init__(self):
        self.db = get_db()
        self.training_threshold = int(os.getenv("TRAINING_THRESHOLD", "50"))
        self.model_path = os.getenv("MODEL_PATH", "./hoax_model")
        self.dataset_path = os.getenv("TRAINING_DATASET_PATH", "./training_data")

    def get_training_queue_status(self) -> TrainingQueueStatus:
        """Get current status of training queue"""
        try:
            # Count pending (admin-labeled but not trained)
            pending_query = (
                self.db.collection("news")
                .where("can_use_for_training", "==", True)
                .where("trained", "==", False)
            )
            pending_docs = list(pending_query.stream())
            total_pending = len(pending_docs)

            # Count already trained
            trained_query = (
                self.db.collection("news")
                .where("can_use_for_training", "==", True)
                .where("trained", "==", True)
            )
            trained_docs = list(trained_query.stream())
            total_trained = len(trained_docs)

            return TrainingQueueStatus(
                total_pending=total_pending,
                total_trained=total_trained,
                ready_for_training=total_pending >= self.training_threshold,
                threshold=self.training_threshold
            )
        except Exception as e:
            print(f"Error getting training queue status: {e}")
            return TrainingQueueStatus(
                total_pending=0,
                total_trained=0,
                ready_for_training=False,
                threshold=self.training_threshold
            )

    def get_pending_training_data(self) -> List[Dict]:
        """Get all pending training data (admin-labeled, not yet trained)"""
        try:
            query = (
                self.db.collection("news")
                .where("can_use_for_training", "==", True)
                .where("trained", "==", False)
            )
            docs = query.stream()

            training_data = []
            for doc in docs:
                data = doc.to_dict()
                # Use manual_label if available, otherwise hoax_label
                label = data.get("manual_label") or data.get("hoax_label")
                if label:
                    training_data.append({
                        "id": doc.id,
                        "text": f"{data.get('title', '')} {data.get('content', '')}".strip(),
                        "label": 1 if label == "hoax" else 0,
                        "source": data.get("source", "admin"),
                        "url": data.get("link", ""),
                        "labeled_by": data.get("labeled_by", "admin"),
                        "labeled_at": data.get("labeled_at"),
                    })

            return training_data
        except Exception as e:
            print(f"Error getting pending training data: {e}")
            return []

    def export_training_dataset(self, include_old: bool = True) -> str:
        """
        Export training data to CSV for model training

        Args:
            include_old: If True, include previously trained data for full retraining
                        If False, only export new pending data (for incremental)
        """
        try:
            # Ensure directory exists
            os.makedirs(self.dataset_path, exist_ok=True)

            training_data = []

            if include_old:
                # Get all admin-labeled data (both trained and pending)
                query = self.db.collection("news").where("can_use_for_training", "==", True)
            else:
                # Get only pending data
                query = (
                    self.db.collection("news")
                    .where("can_use_for_training", "==", True)
                    .where("trained", "==", False)
                )

            docs = query.stream()

            for doc in docs:
                data = doc.to_dict()
                label = data.get("manual_label") or data.get("hoax_label")
                if label:
                    training_data.append({
                        "text": f"{data.get('title', '')} {data.get('content', '')}".strip(),
                        "label": 1 if label == "hoax" else 0,
                        "source": data.get("source", "admin"),
                        "url": data.get("link", ""),
                    })

            if not training_data:
                print("No training data available")
                return ""

            # Create DataFrame and save
            df = pd.DataFrame(training_data)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.dataset_path}/training_data_{timestamp}.csv"
            df.to_csv(filename, index=False)

            print(f"Exported {len(training_data)} samples to {filename}")
            return filename

        except Exception as e:
            print(f"Error exporting training dataset: {e}")
            return ""

    def mark_as_trained(self, news_ids: List[str]) -> int:
        """Mark news items as trained"""
        try:
            count = 0
            for news_id in news_ids:
                self.db.collection("news").document(news_id).update({
                    "trained": True,
                    "trained_at": datetime.now().isoformat()
                })
                count += 1
            return count
        except Exception as e:
            print(f"Error marking as trained: {e}")
            return 0

    def check_and_trigger_retrain(self) -> Optional[RetrainResponse]:
        """
        Check if threshold is met and trigger retraining
        Called by scheduler or manually
        """
        status = self.get_training_queue_status()

        if not status.ready_for_training:
            return RetrainResponse(
                success=False,
                message=f"Not enough data. Need {status.threshold}, have {status.total_pending}",
                samples_used=0
            )

        # Export dataset
        dataset_path = self.export_training_dataset(include_old=True)
        if not dataset_path:
            return RetrainResponse(
                success=False,
                message="Failed to export training dataset",
                samples_used=0
            )

        # Trigger incremental training
        return self.run_incremental_training(dataset_path)

    def run_incremental_training(self, dataset_path: str) -> RetrainResponse:
        """
        Run incremental training using previous model as base
        """
        try:
            from app.services.incremental_trainer import IncrementalTrainer

            trainer = IncrementalTrainer(
                base_model_path=self.model_path,
                dataset_path=dataset_path,
                output_path=self.model_path  # Overwrite existing model
            )

            result = trainer.train()

            if result["success"]:
                # Mark all pending data as trained
                pending_data = self.get_pending_training_data()
                news_ids = [d["id"] for d in pending_data]
                self.mark_as_trained(news_ids)

                return RetrainResponse(
                    success=True,
                    message=f"Model retrained successfully with {result['samples']} samples",
                    samples_used=result["samples"],
                    accuracy=result.get("accuracy"),
                    f1_score=result.get("f1_score")
                )
            else:
                return RetrainResponse(
                    success=False,
                    message=f"Training failed: {result.get('error', 'Unknown error')}",
                    samples_used=0
                )

        except Exception as e:
            print(f"Error during incremental training: {e}")
            return RetrainResponse(
                success=False,
                message=f"Training error: {str(e)}",
                samples_used=0
            )

    def get_training_history(self, limit: int = 10) -> List[Dict]:
        """Get history of training runs"""
        try:
            query = (
                self.db.collection("training_history")
                .order_by("trained_at", direction="DESCENDING")
                .limit(limit)
            )
            docs = query.stream()

            history = []
            for doc in docs:
                data = doc.to_dict()
                history.append({
                    "id": doc.id,
                    "trained_at": data.get("trained_at"),
                    "samples_used": data.get("samples_used"),
                    "accuracy": data.get("accuracy"),
                    "f1_score": data.get("f1_score"),
                    "status": data.get("status")
                })

            return history
        except Exception as e:
            print(f"Error getting training history: {e}")
            return []

    def save_training_history(self, result: RetrainResponse):
        """Save training run to history"""
        try:
            self.db.collection("training_history").add({
                "trained_at": datetime.now().isoformat(),
                "samples_used": result.samples_used,
                "accuracy": result.accuracy,
                "f1_score": result.f1_score,
                "status": "success" if result.success else "failed",
                "message": result.message
            })
        except Exception as e:
            print(f"Error saving training history: {e}")


# Global instance
training_service = TrainingService()
