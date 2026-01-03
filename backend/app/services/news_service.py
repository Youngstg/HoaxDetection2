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
            return NewsResponse(**data)

        return None

    def get_all_news(self, limit: int = 50) -> List[NewsResponse]:
        db = get_db()
        docs = db.collection(self.collection_name).order_by("created_at", direction="DESCENDING").limit(limit).stream()

        news_list = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
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

            # Create news item
            news_item = NewsItem(
                title=article["title"],
                link=article["link"],
                content=content,
                source="RSS Feed",
                published_time=article.get("published"),
                hoax_label=prediction.label,
                confidence=prediction.confidence
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

# Global instance
news_service = NewsService()
