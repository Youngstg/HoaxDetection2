#!/usr/bin/env python3
"""
Standalone scheduler script for fetching news from RSS feed.
Can be run manually or via cron job.

Usage:
    python scheduler.py
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from app.services.news_service import news_service
from app.utils.firebase_config import initialize_firebase

def main():
    print("=== Hoax Detection News Scheduler ===")
    print("Starting RSS fetch process...")

    # Load environment variables
    load_dotenv()

    try:
        # Initialize Firebase
        print("Initializing Firebase...")
        initialize_firebase()

        # Fetch and process RSS
        print("Fetching RSS feed...")
        result = news_service.fetch_and_process_rss()

        print("\n=== Results ===")
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")
        print(f"Total articles found: {result.get('total', 0)}")
        print(f"Processed: {result.get('processed', 0)}")
        print(f"Skipped (already exists): {result.get('skipped', 0)}")
        print("\n=== Scheduler completed successfully ===")

        return 0

    except Exception as e:
        print(f"\n=== Error occurred ===")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
