from app.utils.firebase_config import get_db
from app.models import NewsItem, NewsResponse
from app.services.hoax_detector import hoax_detector
from app.services.rss_fetcher import rss_fetcher
from datetime import datetime
from typing import List, Optional
import hashlib


class NewsService:
    def __init__(self):
        self.collection_name = "news"

    def _generate_id(self, link: str) -> str:
        return hashlib.md5(link.encode()).hexdigest()

    def save_news(self, news_item: NewsItem) -> str:
        db = get_db()

        # Generate ID from link if not provided
        if not news_item.id:
            news_item.id = self._generate_id(news_item.link)

        # Convert to dict
        news_dict = news_item.model_dump()

        # Convert datetime to string for Firestore
        if news_dict.get("published_time"):
            news_dict["published_time"] = news_dict["published_time"].isoformat()
        if news_dict.get("created_at"):
            news_dict["created_at"] = news_dict["created_at"].isoformat()
        if news_dict.get("labeled_at"):
            news_dict["labeled_at"] = news_dict["labeled_at"].isoformat()

        # Save to Firestore
        db.collection(self.collection_name).document(news_item.id).set(news_dict)
        print(f"News saved: {news_item.id}")

        return news_item.id

    def get_news_by_id(self, news_id: str) -> Optional[NewsResponse]:
        db = get_db()
        doc = db.collection(self.collection_name).document(news_id).get()

        if doc.exists:
            data = doc.to_dict()
            data["id"] = doc.id
            # Handle missing new fields for backward compatibility
            data.setdefault("labeled_by", "system")
            data.setdefault("manual_label", None)
            data.setdefault("is_verified", False)
            data.setdefault("can_use_for_training", False)
            data.setdefault("trained", False)
            data.setdefault("labeled_at", None)
            return NewsResponse(**data)

        return None

    def get_all_news(self, limit: int = 50) -> List[NewsResponse]:
        db = get_db()
        docs = db.collection(self.collection_name).order_by("created_at", direction="DESCENDING").limit(limit).stream()

        news_list = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            # Handle missing new fields for backward compatibility
            data.setdefault("labeled_by", "system")
            data.setdefault("manual_label", None)
            data.setdefault("is_verified", False)
            data.setdefault("can_use_for_training", False)
            data.setdefault("trained", False)
            data.setdefault("labeled_at", None)
            news_list.append(NewsResponse(**data))

        return news_list

    def check_news_exists(self, link: str) -> bool:
        news_id = self._generate_id(link)
        db = get_db()
        doc = db.collection(self.collection_name).document(news_id).get()
        return doc.exists

    def fetch_and_process_rss(self) -> dict:
        articles = rss_fetcher.fetch_rss()

        if not articles:
            return {"status": "error", "message": "No articles fetched", "processed": 0, "skipped": 0}

        processed = 0
        skipped = 0

        for article in articles:
            # Check if article already exists
            if self.check_news_exists(article["link"]):
                print(f"Article already exists: {article['title']}")
                skipped += 1
                continue

            # Extract full content
            content = rss_fetcher.extract_article_content(article["link"])

            if not content:
                content = article.get("summary", "")

            # Perform hoax detection with source info
            prediction = hoax_detector.predict(content, source=article["link"])

            # Create news item with new fields
            news_item = NewsItem(
                title=article["title"],
                link=article["link"],
                content=content,
                source="RSS Feed",
                published_time=article.get("published"),
                hoax_label=prediction.label,
                confidence=prediction.confidence,
                # New fields - system auto-labeled
                labeled_by="system",
                manual_label=None,
                is_verified=False,
                can_use_for_training=False,  # System labels NOT for training
                trained=False,
                labeled_at=datetime.now()
            )

            # Save to database
            self.save_news(news_item)
            processed += 1

        return {
            "status": "success",
            "message": f"Processed {processed} articles, skipped {skipped} existing articles",
            "processed": processed,
            "skipped": skipped,
            "total": len(articles)
        }

    def get_news_by_label_source(
        self,
        labeled_by: str = None,
        is_verified: bool = None,
        can_use_for_training: bool = None,
        limit: int = 50
    ) -> List[NewsResponse]:
        """
        Get news filtered by labeling source and status.

        Args:
            labeled_by: Filter by who labeled ("system", "admin", "user")
            is_verified: Filter by verification status
            can_use_for_training: Filter by training eligibility
            limit: Maximum number of results
        """
        db = get_db()
        query = db.collection(self.collection_name)

        if labeled_by:
            query = query.where("labeled_by", "==", labeled_by)
        if is_verified is not None:
            query = query.where("is_verified", "==", is_verified)
        if can_use_for_training is not None:
            query = query.where("can_use_for_training", "==", can_use_for_training)

        query = query.order_by("created_at", direction="DESCENDING").limit(limit)

        docs = query.stream()

        news_list = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            data.setdefault("labeled_by", "system")
            data.setdefault("manual_label", None)
            data.setdefault("is_verified", False)
            data.setdefault("can_use_for_training", False)
            data.setdefault("trained", False)
            data.setdefault("labeled_at", None)
            news_list.append(NewsResponse(**data))

        return news_list

    def update_news_label(
        self,
        news_id: str,
        label: str,
        labeled_by: str,
        notes: str = None
    ) -> bool:
        """
        Update news label.

        Args:
            news_id: ID of news to update
            label: New label ("hoax" or "non-hoax")
            labeled_by: Who is labeling ("admin" or "user")
            notes: Optional notes
        """
        try:
            db = get_db()
            news_ref = db.collection(self.collection_name).document(news_id)

            if not news_ref.get().exists:
                return False

            update_data = {
                "manual_label": label,
                "labeled_by": labeled_by,
                "labeled_at": datetime.now().isoformat(),
            }

            # Only admin labels can be used for training
            if labeled_by == "admin":
                update_data["is_verified"] = True
                update_data["can_use_for_training"] = True
                update_data["trained"] = False  # Mark as not yet trained
            else:
                # User labels are NOT for training
                update_data["is_verified"] = False
                update_data["can_use_for_training"] = False

            if notes:
                update_data["label_notes"] = notes

            news_ref.update(update_data)
            return True

        except Exception as e:
            print(f"Error updating news label: {e}")
            return False

    def get_training_stats(self) -> dict:
        """Get statistics about training data."""
        db = get_db()

        # Count by labeled_by
        system_count = len(list(db.collection(self.collection_name)
            .where("labeled_by", "==", "system").stream()))
        admin_count = len(list(db.collection(self.collection_name)
            .where("labeled_by", "==", "admin").stream()))

        # Count pending training
        pending_count = len(list(db.collection(self.collection_name)
            .where("can_use_for_training", "==", True)
            .where("trained", "==", False).stream()))

        # Count already trained
        trained_count = len(list(db.collection(self.collection_name)
            .where("trained", "==", True).stream()))

        return {
            "system_labeled": system_count,
            "admin_labeled": admin_count,
            "pending_training": pending_count,
            "already_trained": trained_count,
            "total": system_count + admin_count
        }


# Global instance
news_service = NewsService()
