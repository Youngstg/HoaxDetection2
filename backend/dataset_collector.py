"""
Dataset Collector untuk Training Model Hoax Detection

Script ini mengumpulkan data dari:
1. Media terpercaya (non-hoax label)
2. Fact-checking sites (hoax label)

Output: CSV file untuk training
"""

import feedparser
import requests
from bs4 import BeautifulSoup
import csv
import time
from datetime import datetime
import os


class DatasetCollector:
    def __init__(self):
        # Media terpercaya untuk non-hoax samples
        self.trusted_rss_feeds = [
            "https://www.antaranews.com/rss/terkini.xml",
            "https://rss.kompas.com/nasional",
            "https://rss.detik.com/index.php/detikcom",
            "https://www.tempo.co/rss/terkini",
        ]

        # Fact-checking sites untuk hoax samples
        self.factcheck_urls = [
            "https://cekfakta.tempo.co/",  # Tempo Cek Fakta
            # Tambahkan lebih banyak sources
        ]

        self.dataset = []

    def extract_content(self, url: str) -> str:
        """Extract content dari URL"""
        try:
            print(f"Fetching: {url}")
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "lxml")

            # Remove unwanted elements
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()

            # Find article content
            content_selectors = ["article", ".article-content", ".post-content", "main"]
            article_content = ""

            for selector in content_selectors:
                content_div = soup.select_one(selector)
                if content_div:
                    paragraphs = content_div.find_all("p")
                    article_content = " ".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                    if article_content:
                        break

            if not article_content:
                paragraphs = soup.find_all("p")
                article_content = " ".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])

            return article_content[:2000]  # Limit to 2000 characters

        except Exception as e:
            print(f"Error extracting {url}: {e}")
            return ""

    def collect_nonhoax_from_rss(self, max_articles=100):
        """Collect non-hoax articles dari media terpercaya"""
        print("\n=== Collecting Non-Hoax Articles ===")
        collected = 0

        for rss_url in self.trusted_rss_feeds:
            if collected >= max_articles:
                break

            try:
                print(f"\nFetching RSS: {rss_url}")
                feed = feedparser.parse(rss_url)

                for entry in feed.entries[:20]:  # Max 20 per feed
                    if collected >= max_articles:
                        break

                    title = entry.get("title", "")
                    link = entry.get("link", "")

                    # Extract content
                    content = self.extract_content(link)

                    if content and len(content) > 100:  # Minimal 100 characters
                        self.dataset.append({
                            "text": f"{title}. {content}",
                            "label": 0,  # non-hoax
                            "source": link,
                            "collected_at": datetime.now().isoformat()
                        })
                        collected += 1
                        print(f"Collected {collected}/{max_articles}: {title[:50]}...")

                    time.sleep(1)  # Rate limiting

            except Exception as e:
                print(f"Error processing RSS {rss_url}: {e}")

        print(f"\nTotal non-hoax collected: {collected}")

    def collect_hoax_manual(self):
        """
        Manual hoax collection guide.
        Anda bisa menambahkan data hoax manual dari:
        1. TurnBackHoax Twitter
        2. Cek Fakta websites
        3. Database hoax yang sudah ada
        """
        print("\n=== Manual Hoax Collection Guide ===")
        print("Untuk mengumpulkan data hoax, Anda bisa:")
        print("1. Visit: https://turnbackhoax.id/")
        print("2. Visit: https://cekfakta.tempo.co/")
        print("3. Visit: https://www.liputan6.com/cek-fakta")
        print("4. Copy paste konten hoax ke file hoax_samples.txt")
        print("   Format: satu hoax per line")
        print("\nSetelah itu, run: python dataset_collector.py --load-hoax")

    def load_hoax_from_file(self, filepath="hoax_samples.txt"):
        """Load hoax samples dari text file"""
        if not os.path.exists(filepath):
            print(f"File {filepath} tidak ditemukan.")
            print("Buat file hoax_samples.txt dan isi dengan contoh hoax (satu per line)")
            return

        print(f"\n=== Loading Hoax Samples from {filepath} ===")
        collected = 0

        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                text = line.strip()
                if text and len(text) > 50:
                    self.dataset.append({
                        "text": text,
                        "label": 1,  # hoax
                        "source": "manual",
                        "collected_at": datetime.now().isoformat()
                    })
                    collected += 1

        print(f"Total hoax loaded: {collected}")

    def save_dataset(self, filename="dataset.csv"):
        """Save dataset ke CSV file"""
        if not self.dataset:
            print("No data to save!")
            return

        print(f"\n=== Saving Dataset to {filename} ===")

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["text", "label", "source", "collected_at"])
            writer.writeheader()
            writer.writerows(self.dataset)

        print(f"Saved {len(self.dataset)} samples")
        print(f"Non-hoax: {sum(1 for d in self.dataset if d['label'] == 0)}")
        print(f"Hoax: {sum(1 for d in self.dataset if d['label'] == 1)}")

    def run(self, max_nonhoax=100):
        """Run full collection process"""
        print("=" * 60)
        print("Dataset Collection untuk Hoax Detection")
        print("=" * 60)

        # Collect non-hoax
        self.collect_nonhoax_from_rss(max_articles=max_nonhoax)

        # Guide untuk manual hoax collection
        self.collect_hoax_manual()

        # Try load existing hoax samples
        self.load_hoax_from_file()

        # Save dataset
        self.save_dataset()

        print("\n" + "=" * 60)
        print("Dataset collection completed!")
        print("Next steps:")
        print("1. Review dataset.csv")
        print("2. Add more hoax samples to hoax_samples.txt")
        print("3. Run training script: python train_model.py")
        print("=" * 60)


if __name__ == "__main__":
    import sys

    collector = DatasetCollector()

    if "--load-hoax" in sys.argv:
        # Load hoax from file and save
        collector.load_hoax_from_file()
        collector.save_dataset()
    else:
        # Full collection
        collector.run(max_nonhoax=100)
