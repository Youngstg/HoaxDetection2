import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
import os

class RSSFetcher:
    def __init__(self, rss_url: Optional[str] = None):
        self.rss_url = rss_url or os.getenv("RSS_FEED_URL", "")

    def fetch_rss(self) -> List[Dict]:
        # Re-read from environment in case it changed
        if not self.rss_url:
            self.rss_url = os.getenv("RSS_FEED_URL", "")

        if not self.rss_url:
            print("No RSS feed URL configured")
            print(f"Environment variables: {os.environ.get('RSS_FEED_URL', 'NOT SET')}")
            return []

        try:
            print(f"Fetching RSS from: {self.rss_url}")
            feed = feedparser.parse(self.rss_url)

            articles = []
            for entry in feed.entries:
                article = {
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "published": self._parse_date(entry.get("published", "")),
                    "summary": entry.get("summary", ""),
                }
                articles.append(article)

            print(f"Fetched {len(articles)} articles from RSS")
            return articles

        except Exception as e:
            print(f"Error fetching RSS: {e}")
            return []

    def _parse_date(self, date_string: str) -> Optional[datetime]:
        if not date_string:
            return None

        try:
            # Try parsing common RSS date formats
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_string)
        except:
            try:
                return datetime.fromisoformat(date_string)
            except:
                return None

    def extract_article_content(self, url: str) -> str:
        try:
            print(f"Extracting content from: {url}")
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "lxml")

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Try to find article content
            # This is a generic approach - you may need to customize for specific news sites
            article_content = ""

            # Common article content selectors
            content_selectors = [
                "article",
                ".article-content",
                ".post-content",
                ".entry-content",
                ".content",
                "main"
            ]

            for selector in content_selectors:
                content_div = soup.select_one(selector)
                if content_div:
                    paragraphs = content_div.find_all("p")
                    article_content = " ".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                    if article_content:
                        break

            # Fallback: get all paragraphs
            if not article_content:
                paragraphs = soup.find_all("p")
                article_content = " ".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])

            return article_content[:5000]  # Limit to 5000 characters

        except Exception as e:
            print(f"Error extracting content: {e}")
            return ""

# Global instance
rss_fetcher = RSSFetcher()
