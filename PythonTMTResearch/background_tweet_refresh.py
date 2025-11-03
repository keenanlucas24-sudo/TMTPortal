"""
Background service to refresh social news tweets every 15 minutes
Runs continuously and fetches/analyzes new tweets from financial accounts
"""
import time
import schedule
from datetime import datetime
from integrations.social_news_service import fetch_and_analyze_tweets


def refresh_social_news():
    """Fetch and analyze new tweets"""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting social news refresh...")
    
    try:
        stats = fetch_and_analyze_tweets(limit_per_account=10)
        print(f"✓ Refresh complete: {stats['fetched']} fetched, "
              f"{stats['new']} new, {stats['relevant']} relevant")
    except Exception as e:
        print(f"✗ Error during refresh: {e}")


def run_background_service():
    """Run the background refresh service"""
    print("=" * 60)
    print("Social News Background Refresh Service")
    print("=" * 60)
    print("Fetches tweets from financial accounts every 15 minutes")
    print("Analyzes with Gemini AI for TMT relevance and sentiment")
    print()
    
    # Run immediately on start
    refresh_social_news()
    
    # Schedule every 15 minutes
    schedule.every(15).minutes.do(refresh_social_news)
    
    print(f"\n✓ Background service started. Refreshing every 15 minutes...")
    print("Press Ctrl+C to stop\n")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    run_background_service()
