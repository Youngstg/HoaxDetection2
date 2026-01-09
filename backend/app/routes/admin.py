"""
Admin Routes - Endpoints for admin to label news for training

Features:
- Label news as hoax/non-hoax (will be used for training)
- View training queue status
- Manually trigger retraining
- View training history
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import List, Optional

from app.models import (
    AdminLabelRequest,
    AdminLabelResponse,
    TrainingQueueStatus,
    RetrainResponse,
    NewsResponse,
)
from app.utils.firebase_config import get_db
from app.services.training_service import training_service

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.post("/label", response_model=AdminLabelResponse)
async def label_news(request: AdminLabelRequest):
    """
    Admin labels a news article as hoax or non-hoax.
    This data WILL be used for model training.
    """
    try:
        db = get_db()
        news_ref = db.collection("news").document(request.news_id)
        news_doc = news_ref.get()

        if not news_doc.exists:
            raise HTTPException(status_code=404, detail="News not found")

        # Update news with admin label
        update_data = {
            "manual_label": request.label,
            "labeled_by": "admin",
            "is_verified": True,
            "can_use_for_training": True,  # Admin data CAN be used for training
            "trained": False,  # Not yet used in training
            "labeled_at": datetime.now().isoformat(),
        }

        if request.notes:
            update_data["admin_notes"] = request.notes

        news_ref.update(update_data)

        return AdminLabelResponse(
            success=True,
            message=f"News labeled as '{request.label}' by admin. Will be used for training.",
            news_id=request.news_id,
            label=request.label,
            can_use_for_training=True
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error labeling news: {str(e)}")


@router.post("/label-bulk", response_model=dict)
async def label_news_bulk(requests: List[AdminLabelRequest]):
    """
    Admin labels multiple news articles at once.
    All labeled data WILL be used for model training.
    """
    try:
        db = get_db()
        results = {"success": 0, "failed": 0, "errors": []}

        for req in requests:
            try:
                news_ref = db.collection("news").document(req.news_id)
                news_doc = news_ref.get()

                if not news_doc.exists:
                    results["failed"] += 1
                    results["errors"].append(f"News {req.news_id} not found")
                    continue

                update_data = {
                    "manual_label": req.label,
                    "labeled_by": "admin",
                    "is_verified": True,
                    "can_use_for_training": True,
                    "trained": False,
                    "labeled_at": datetime.now().isoformat(),
                }

                if req.notes:
                    update_data["admin_notes"] = req.notes

                news_ref.update(update_data)
                results["success"] += 1

            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"Error labeling {req.news_id}: {str(e)}")

        return {
            "total": len(requests),
            "success": results["success"],
            "failed": results["failed"],
            "errors": results["errors"][:10]  # Limit errors shown
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in bulk labeling: {str(e)}")


@router.get("/training-queue", response_model=TrainingQueueStatus)
async def get_training_queue_status():
    """
    Get current status of training queue.
    Shows how many admin-labeled items are pending for training.
    """
    try:
        return training_service.get_training_queue_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting queue status: {str(e)}")


@router.get("/pending-training", response_model=dict)
async def get_pending_training_data():
    """
    Get list of news articles pending for training.
    These are admin-labeled but not yet used in model training.
    """
    try:
        pending = training_service.get_pending_training_data()
        return {
            "total": len(pending),
            "items": pending[:100]  # Limit to 100 items
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting pending data: {str(e)}")


@router.post("/trigger-retrain", response_model=RetrainResponse)
async def trigger_retraining(force: bool = False):
    """
    Manually trigger model retraining.

    Args:
        force: If True, retrain even if threshold not met
    """
    try:
        status = training_service.get_training_queue_status()

        if not force and not status.ready_for_training:
            return RetrainResponse(
                success=False,
                message=f"Threshold not met. Need {status.threshold} samples, have {status.total_pending}. Use force=true to override.",
                samples_used=0
            )

        if status.total_pending == 0:
            return RetrainResponse(
                success=False,
                message="No pending training data available",
                samples_used=0
            )

        # Trigger retraining
        result = training_service.check_and_trigger_retrain()

        # Save to history
        training_service.save_training_history(result)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering retrain: {str(e)}")


@router.get("/training-history", response_model=dict)
async def get_training_history(limit: int = 10):
    """
    Get history of model training runs.
    """
    try:
        history = training_service.get_training_history(limit)
        return {
            "total": len(history),
            "history": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting history: {str(e)}")


@router.get("/unlabeled", response_model=dict)
async def get_unlabeled_news(limit: int = 50):
    """
    Get news articles that haven't been labeled by admin yet.
    Useful for admin to find articles to label.
    """
    try:
        db = get_db()

        # Get news where labeled_by is "system" (auto-labeled) or not set
        query = (
            db.collection("news")
            .where("labeled_by", "==", "system")
            .order_by("created_at", direction="DESCENDING")
            .limit(limit)
        )

        docs = list(query.stream())

        news_list = []
        for doc in docs:
            data = doc.to_dict()
            news_list.append({
                "id": doc.id,
                "title": data.get("title", ""),
                "content": data.get("content", "")[:500],  # Preview only
                "source": data.get("source", ""),
                "hoax_label": data.get("hoax_label"),  # System's prediction
                "confidence": data.get("confidence"),
                "created_at": data.get("created_at"),
            })

        return {
            "total": len(news_list),
            "news": news_list
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting unlabeled news: {str(e)}")


@router.get("/labeled", response_model=dict)
async def get_admin_labeled_news(
    limit: int = 50,
    trained: Optional[bool] = None
):
    """
    Get news articles that have been labeled by admin.

    Args:
        limit: Maximum number of items to return
        trained: Filter by trained status (True/False/None for all)
    """
    try:
        db = get_db()

        query = db.collection("news").where("labeled_by", "==", "admin")

        if trained is not None:
            query = query.where("trained", "==", trained)

        query = query.order_by("labeled_at", direction="DESCENDING").limit(limit)

        docs = list(query.stream())

        news_list = []
        for doc in docs:
            data = doc.to_dict()
            news_list.append({
                "id": doc.id,
                "title": data.get("title", ""),
                "content": data.get("content", "")[:500],
                "source": data.get("source", ""),
                "manual_label": data.get("manual_label"),
                "labeled_at": data.get("labeled_at"),
                "trained": data.get("trained", False),
            })

        return {
            "total": len(news_list),
            "news": news_list
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting labeled news: {str(e)}")
