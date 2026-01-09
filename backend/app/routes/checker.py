"""
User Checker Routes - Endpoints for users to check news for hoax

IMPORTANT: Data from user checks is NOT used for training.
This is a read-only prediction service for end users.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import hashlib
from typing import Optional

from app.models import (
    UserCheckRequest,
    UserCheckResponse,
    NewsItem,
)
from app.services.hoax_detector import hoax_detector
from app.utils.firebase_config import get_db

router = APIRouter(prefix="/api/checker", tags=["User Checker"])


@router.post("/check", response_model=UserCheckResponse)
async def check_news_hoax(request: UserCheckRequest):
    """
    Check if a news article is hoax or not.

    This endpoint is for END USERS to verify news.
    The result is NOT used for model training.

    Args:
        request: UserCheckRequest with content to check

    Returns:
        UserCheckResponse with prediction and confidence
    """
    try:
        if not request.content or len(request.content.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Content must be at least 50 characters long"
            )

        # Combine title and content for prediction
        text_to_check = ""
        if request.title:
            text_to_check = f"{request.title} "
        text_to_check += request.content

        # Get prediction from hoax detector
        prediction = hoax_detector.predict(text_to_check, source="user_check")

        # Prepare response message
        if prediction.label == "hoax":
            if prediction.confidence > 0.8:
                message = "Berita ini SANGAT MUNGKIN adalah HOAX. Harap verifikasi dari sumber terpercaya."
            elif prediction.confidence > 0.6:
                message = "Berita ini KEMUNGKINAN adalah HOAX. Sebaiknya cek fakta lebih lanjut."
            else:
                message = "Berita ini memiliki indikasi HOAX. Tetap waspada."
        else:
            if prediction.confidence > 0.8:
                message = "Berita ini KEMUNGKINAN BESAR adalah FAKTA."
            elif prediction.confidence > 0.6:
                message = "Berita ini MUNGKIN adalah FAKTA, namun tetap verifikasi."
            else:
                message = "Berita ini terlihat valid, tapi sebaiknya tetap cross-check."

        # Add warning
        warning = (
            "Hasil ini adalah prediksi AI dan bukan jaminan kebenaran. "
            "Selalu verifikasi informasi dari sumber resmi dan terpercaya."
        )

        # Optionally save to database for analytics (but NOT for training)
        await _save_user_check(request, prediction)

        return UserCheckResponse(
            prediction=prediction.label,
            confidence=prediction.confidence,
            message=message,
            warning=warning
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking news: {str(e)}")


@router.post("/check-url", response_model=UserCheckResponse)
async def check_news_by_url(url: str):
    """
    Check if a news article is hoax by providing URL.
    The system will fetch and analyze the content.

    NOTE: Data from this check is NOT used for training.
    """
    try:
        from app.services.rss_fetcher import rss_fetcher

        if not url or not url.startswith(("http://", "https://")):
            raise HTTPException(status_code=400, detail="Invalid URL format")

        # Extract content from URL
        content = rss_fetcher.extract_article_content(url)

        if not content or len(content) < 50:
            raise HTTPException(
                status_code=400,
                detail="Could not extract sufficient content from URL"
            )

        # Get prediction
        prediction = hoax_detector.predict(content, source=url)

        # Prepare response
        if prediction.label == "hoax":
            message = f"Artikel dari URL ini terindikasi HOAX dengan confidence {prediction.confidence:.1%}"
        else:
            message = f"Artikel dari URL ini terlihat VALID dengan confidence {prediction.confidence:.1%}"

        warning = (
            "Hasil ini adalah prediksi AI dan bukan jaminan kebenaran. "
            "Selalu verifikasi informasi dari sumber resmi dan terpercaya."
        )

        return UserCheckResponse(
            prediction=prediction.label,
            confidence=prediction.confidence,
            message=message,
            warning=warning
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking URL: {str(e)}")


async def _save_user_check(request: UserCheckRequest, prediction):
    """
    Save user check to database for analytics.
    This data is NEVER used for training (can_use_for_training=False).
    """
    try:
        db = get_db()

        # Generate ID from content hash
        content_hash = hashlib.md5(request.content.encode()).hexdigest()
        doc_id = f"user_check_{content_hash[:16]}"

        # Check if already exists
        existing = db.collection("user_checks").document(doc_id).get()
        if existing.exists:
            # Increment check count
            db.collection("user_checks").document(doc_id).update({
                "check_count": existing.to_dict().get("check_count", 0) + 1,
                "last_checked_at": datetime.now().isoformat()
            })
        else:
            # Create new record
            db.collection("user_checks").document(doc_id).set({
                "title": request.title,
                "content": request.content[:2000],  # Limit stored content
                "url": request.url,
                "prediction": prediction.label,
                "confidence": prediction.confidence,
                "labeled_by": "user",  # Mark as user-generated
                "can_use_for_training": False,  # NEVER use for training
                "check_count": 1,
                "created_at": datetime.now().isoformat(),
                "last_checked_at": datetime.now().isoformat(),
            })

    except Exception as e:
        # Don't fail the main request if saving fails
        print(f"Warning: Could not save user check: {e}")


@router.get("/stats", response_model=dict)
async def get_checker_stats():
    """
    Get statistics of user hoax checks.
    """
    try:
        db = get_db()

        # Get all user checks
        docs = list(db.collection("user_checks").stream())

        total_checks = 0
        hoax_predictions = 0
        non_hoax_predictions = 0

        for doc in docs:
            data = doc.to_dict()
            count = data.get("check_count", 1)
            total_checks += count

            if data.get("prediction") == "hoax":
                hoax_predictions += count
            else:
                non_hoax_predictions += count

        return {
            "total_unique_articles": len(docs),
            "total_checks": total_checks,
            "hoax_predictions": hoax_predictions,
            "non_hoax_predictions": non_hoax_predictions,
            "hoax_ratio": hoax_predictions / total_checks if total_checks > 0 else 0
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


@router.get("/recent", response_model=dict)
async def get_recent_checks(limit: int = 20):
    """
    Get recent user hoax checks (for display purposes).
    Personal data is anonymized.
    """
    try:
        db = get_db()

        query = (
            db.collection("user_checks")
            .order_by("last_checked_at", direction="DESCENDING")
            .limit(limit)
        )

        docs = list(query.stream())

        checks = []
        for doc in docs:
            data = doc.to_dict()
            checks.append({
                "title": data.get("title", "")[:100] if data.get("title") else None,
                "content_preview": data.get("content", "")[:200],
                "prediction": data.get("prediction"),
                "confidence": data.get("confidence"),
                "check_count": data.get("check_count", 1),
                "last_checked_at": data.get("last_checked_at"),
            })

        return {
            "total": len(checks),
            "checks": checks
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting recent checks: {str(e)}")
