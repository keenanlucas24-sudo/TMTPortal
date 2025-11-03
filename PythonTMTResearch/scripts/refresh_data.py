"""
Automated Data Refresh Script
Refreshes earnings and news data from Finnhub on a scheduled basis
"""

import sys
import os
# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.earnings_api import EarningsAPIIntegration
from integrations.news_api import NewsAPIIntegration
from db.db_operations import get_all_companies
from datetime import datetime, timedelta
import time

def refresh_earnings():
    """Refresh earnings calendar data"""
    print("\n[EARNINGS] Starting refresh...")
    
    try:
        integration = EarningsAPIIntegration(provider="finnhub")
        earnings = integration.fetch_earnings_calendar(horizon="3month")
        count = integration.sync_to_database(earnings)
        print(f"[EARNINGS] ✓ Refreshed {count} earnings events")
        return count
        
    except Exception as e:
        print(f"[EARNINGS] ✗ Error: {e}")
        return 0

def refresh_news():
    """Refresh news feed data"""
    print("\n[NEWS] Starting refresh...")
    
    try:
        integration = NewsAPIIntegration(provider="finnhub")
        
        # Get top companies
        companies = get_all_companies()
        tickers = [c['ticker'] for c in companies[:50]]
        
        # Fetch news from last 2 days (most recent)
        news = integration.fetch_news(
            tickers=tickers,
            limit=100,
            time_from=datetime.now() - timedelta(days=2)
        )
        count = integration.sync_to_database(news)
        print(f"[NEWS] ✓ Refreshed {count} news articles")
        return count
        
    except Exception as e:
        print(f"[NEWS] ✗ Error: {e}")
        return 0

def refresh_all():
    """Refresh all data sources"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("\n" + "="*60)
    print(f"🔄 Data Refresh Started - {timestamp}")
    print("="*60)
    
    start = time.time()
    
    earnings_count = refresh_earnings()
    news_count = refresh_news()
    
    elapsed = time.time() - start
    
    print("\n" + "="*60)
    print(f"✓ Data Refresh Complete - {elapsed:.1f}s")
    print(f"  Earnings: {earnings_count} | News: {news_count}")
    print("="*60)
    
    return earnings_count, news_count

if __name__ == "__main__":
    # Run refresh
    refresh_all()
    
    # Optional: Add continuous refresh loop
    # Uncomment the lines below to run refresh every 4 hours
    
    # print("\n💡 Tip: Set up a cron job or scheduled task to run this script regularly")
    # print("   Example: Run every 4 hours to keep data fresh")
    # 
    # REFRESH_INTERVAL = 4 * 60 * 60  # 4 hours in seconds
    # 
    # while True:
    #     refresh_all()
    #     print(f"\n⏰ Next refresh in {REFRESH_INTERVAL // 3600} hours...")
    #     time.sleep(REFRESH_INTERVAL)
