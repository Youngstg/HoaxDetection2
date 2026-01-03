"""
Auto-Labeling Pipeline untuk Hoax Detection

Pipeline:
1. Scrape berita dari RSS (media terpercaya & fact-checking sites)
2. Auto-label menggunakan rule-based detector
3. Filter berdasarkan confidence threshold
4. Generate dataset untuk training ML model

Ini adalah "weak supervision" approach - rule-based mengajari ML model
"""

import feedparser
import requests
from bs4 import BeautifulSoup
import csv
import time
from datetime import datetime
import os
from app.services.rule_based_detector import rule_based_detector
from tqdm import tqdm


class AutoLabelingPipeline:
    def __init__(self, confidence_threshold=0.6):
        """
        Args:
            confidence_threshold: Minimal confidence untuk include data (0.0-1.0)
                                 Recommended: 0.6-0.7 untuk balance quality vs quantity
        """
        self.confidence_threshold = confidence_threshold
        self.dataset = []

        # RSS Feeds dari berbagai sumber
        self.rss_feeds = {
            # Media terpercaya (high probability non-hoax)
            "trusted": [
                {"url": "https://www.antaranews.com/rss/terkini.xml", "source": "Antara News"},
                {"url": "https://rss.kompas.com/nasional", "source": "Kompas"},
                {"url": "https://rss.detik.com/index.php/detikcom", "source": "Detik"},
                {"url": "https://www.tempo.co/rss/terkini", "source": "Tempo"},
                {"url": "https://rss.cnn.com/rss/edition.rss", "source": "CNN"},
            ],
            # Fact-checking sites (manual collection for hoax samples)
            "factcheck": [
                {"url": "https://cekfakta.tempo.co/rss", "source": "Tempo Cek Fakta"},
            ]
        }

    def extract_content(self, url: str) -> str:
        """Extract content dari URL"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "lxml")

            # Remove unwanted elements
            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe"]):
                tag.decompose()

            # Find article content
            content_selectors = [
                "article", ".article-content", ".post-content",
                ".entry-content", ".content", "main", ".detail-text"
            ]

            article_content = ""
            for selector in content_selectors:
                content_div = soup.select_one(selector)
                if content_div:
                    paragraphs = content_div.find_all("p")
                    article_content = " ".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                    if article_content and len(article_content) > 100:
                        break

            # Fallback: get all paragraphs
            if not article_content or len(article_content) < 100:
                paragraphs = soup.find_all("p")
                article_content = " ".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])

            return article_content[:3000]  # Limit to 3000 characters

        except Exception as e:
            return ""

    def scrape_rss_feed(self, feed_url: str, source_name: str, max_articles=50):
        """Scrape articles dari satu RSS feed"""
        try:
            print(f"\n📰 Fetching: {source_name}")
            feed = feedparser.parse(feed_url)

            collected = []
            for entry in feed.entries[:max_articles]:
                title = entry.get("title", "")
                link = entry.get("link", "")
                summary = entry.get("summary", "")

                # Extract full content
                content = self.extract_content(link)

                # Fallback to summary if content extraction failed
                if not content or len(content) < 100:
                    content = summary

                if content and len(content) > 50:
                    # Combine title and content
                    full_text = f"{title}. {content}"

                    # Auto-label using rule-based detector
                    prediction = rule_based_detector.predict(full_text, source=link)

                    # Only include if confidence is above threshold
                    if prediction.confidence >= self.confidence_threshold:
                        collected.append({
                            "text": full_text,
                            "label": 1 if prediction.label == "hoax" else 0,
                            "confidence": prediction.confidence,
                            "source": source_name,
                            "url": link,
                            "collected_at": datetime.now().isoformat()
                        })

                time.sleep(0.5)  # Rate limiting

            print(f"   ✅ Collected: {len(collected)} articles (confidence >= {self.confidence_threshold})")
            return collected

        except Exception as e:
            print(f"   ❌ Error: {e}")
            return []

    def collect_from_all_sources(self, max_per_source=50):
        """Collect dari semua RSS sources"""
        print("=" * 70)
        print("🤖 AUTO-LABELING PIPELINE - Starting Dataset Collection")
        print("=" * 70)
        print(f"📊 Configuration:")
        print(f"   - Confidence Threshold: {self.confidence_threshold}")
        print(f"   - Max per source: {max_per_source}")
        print()

        # Collect from trusted sources
        print("🔷 Phase 1: Collecting from TRUSTED sources (expected: non-hoax)")
        for feed_info in self.rss_feeds["trusted"]:
            articles = self.scrape_rss_feed(
                feed_info["url"],
                feed_info["source"],
                max_articles=max_per_source
            )
            self.dataset.extend(articles)
            time.sleep(2)  # Be nice to servers

        # Collect from fact-check sources
        print("\n🔶 Phase 2: Collecting from FACT-CHECK sources")
        for feed_info in self.rss_feeds["factcheck"]:
            articles = self.scrape_rss_feed(
                feed_info["url"],
                feed_info["source"],
                max_articles=max_per_source
            )
            self.dataset.extend(articles)
            time.sleep(2)

    def analyze_dataset(self):
        """Analyze collected dataset"""
        if not self.dataset:
            print("\n⚠️  No data collected!")
            return

        total = len(self.dataset)
        non_hoax = sum(1 for d in self.dataset if d["label"] == 0)
        hoax = sum(1 for d in self.dataset if d["label"] == 1)

        avg_confidence = sum(d["confidence"] for d in self.dataset) / total

        print("\n" + "=" * 70)
        print("📊 DATASET ANALYSIS")
        print("=" * 70)
        print(f"Total samples: {total}")
        print(f"   Non-Hoax: {non_hoax} ({non_hoax/total*100:.1f}%)")
        print(f"   Hoax: {hoax} ({hoax/total*100:.1f}%)")
        print(f"Average confidence: {avg_confidence:.2f}")
        print()

        # Distribution by source
        sources = {}
        for d in self.dataset:
            source = d["source"]
            sources[source] = sources.get(source, 0) + 1

        print("Distribution by source:")
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            print(f"   {source}: {count} samples")

        # Quality check
        print("\n🔍 Quality Check:")
        if total < 200:
            print("   ⚠️  WARNING: Dataset terlalu kecil (<200 samples)")
            print("      Recommendation: Lower confidence_threshold atau tambah sources")
        elif total > 2000:
            print("   ✅ GOOD: Dataset size sufficient for training")
        else:
            print("   ✅ OK: Dataset size acceptable")

        if abs(non_hoax - hoax) / total > 0.3:
            print("   ⚠️  WARNING: Dataset imbalanced (difference >30%)")
            print("      Recommendation: Balance dataset atau use class weights")
        else:
            print("   ✅ BALANCED: Dataset distribution acceptable")

    def save_dataset(self, filename="auto_labeled_dataset.csv"):
        """Save dataset ke CSV"""
        if not self.dataset:
            print("No data to save!")
            return

        print(f"\n💾 Saving dataset to: {filename}")

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                "text", "label", "confidence", "source", "url", "collected_at"
            ])
            writer.writeheader()
            writer.writerows(self.dataset)

        print(f"   ✅ Saved {len(self.dataset)} samples")

    def export_for_review(self, sample_size=50, filename="review_sample.csv"):
        """Export random samples untuk manual review"""
        import random

        if not self.dataset:
            print("No data to export!")
            return

        # Random sample
        sample = random.sample(self.dataset, min(sample_size, len(self.dataset)))

        print(f"\n📋 Exporting {len(sample)} samples for manual review: {filename}")

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                "text", "label", "confidence", "source", "is_correct"
            ])
            writer.writeheader()

            for item in sample:
                writer.writerow({
                    "text": item["text"][:200] + "...",  # Preview
                    "label": "hoax" if item["label"] == 1 else "non-hoax",
                    "confidence": item["confidence"],
                    "source": item["source"],
                    "is_correct": ""  # For manual annotation
                })

        print("   ✅ Saved. Please review and mark 'is_correct' column (yes/no)")

    def run(self, max_per_source=50):
        """Run full auto-labeling pipeline"""
        # Collect data
        self.collect_from_all_sources(max_per_source=max_per_source)

        # Analyze
        self.analyze_dataset()

        # Save
        self.save_dataset()

        # Export samples for review
        self.export_for_review(sample_size=min(50, len(self.dataset)))

        print("\n" + "=" * 70)
        print("✅ AUTO-LABELING PIPELINE COMPLETED!")
        print("=" * 70)
        print("\n📝 Next Steps:")
        print("1. Review 'review_sample.csv' untuk quality check")
        print("2. Jika quality baik (>80% correct), lanjut training:")
        print("   python train_model.py --dataset auto_labeled_dataset.csv")
        print("3. Jika quality kurang, adjust confidence_threshold dan re-run")
        print("=" * 70)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Auto-Labeling Pipeline")
    parser.add_argument(
        "--confidence",
        type=float,
        default=0.6,
        help="Confidence threshold (0.0-1.0). Default: 0.6"
    )
    parser.add_argument(
        "--max-per-source",
        type=int,
        default=50,
        help="Max articles per RSS source. Default: 50"
    )

    args = parser.parse_args()

    # Run pipeline
    pipeline = AutoLabelingPipeline(confidence_threshold=args.confidence)
    pipeline.run(max_per_source=args.max_per_source)
