"""
Database Population Script
Fetches real-time data from multiple providers and populates your TMT Research Portal database
Uses multi-provider aggregation for news (Finnhub + Alpha Vantage + Marketaux)
Uses Alpha Vantage for earnings (more accurate reported/upcoming status)
"""

from integrations.earnings_api import EarningsAPIIntegration
from integrations.news_api import NewsAPIIntegration, fetch_multi_provider_news
from db.db_operations import get_all_companies
from datetime import datetime, timedelta

def populate_earnings():
    """Fetch and sync earnings calendar data from Alpha Vantage"""
    print("\n" + "="*60)
    print("📊 Populating Earnings Calendar")
    print("="*60)
    
    try:
        integration = EarningsAPIIntegration(provider="alpha_vantage")
        
        # Fetch earnings for next 3 months
        print("Fetching earnings calendar from Alpha Vantage (next 3 months)...")
        earnings = integration.fetch_earnings_calendar(horizon="3month")
        
        if earnings:
            print(f"✓ Fetched {len(earnings)} earnings events from Alpha Vantage")
            
            # Sync to database
            print("Syncing to database...")
            count = integration.sync_to_database(earnings)
            print(f"✓ Successfully added {count} earnings events to database")
            
            # Show sample
            print("\nSample upcoming earnings:")
            for event in earnings[:5]:
                print(f"  • {event['company']} ({event['ticker']}) - {event['date'].strftime('%Y-%m-%d')} - Q{event['quarter']}")
            
            return count
        else:
            print("⚠ No earnings data available for this period")
            return 0
            
    except Exception as e:
        print(f"✗ Error populating earnings: {e}")
        import traceback
        traceback.print_exc()
        return 0

def populate_news():
    """Fetch and sync news feed data from ALL providers (Finnhub + Alpha Vantage + Marketaux)"""
    print("\n" + "="*60)
    print("📰 Populating News Feed (Multi-Provider)")
    print("="*60)
    
    try:
        # Get all companies from database
        print("Loading TMT companies from database...")
        companies = get_all_companies()
        print(f"✓ Found {len(companies)} companies in database")
        
        # Focus on top 50 companies to manage rate limits
        top_companies = companies[:50]
        tickers = [c['ticker'] for c in top_companies]
        
        print(f"\nFetching news from multiple providers (Finnhub, Alpha Vantage, Marketaux)...")
        print(f"Companies: {', '.join(tickers[:10])}...")
        
        # Use multi-provider aggregation for maximum source diversity
        news = fetch_multi_provider_news(
            tickers=tickers,
            limit=150,  # Will be distributed across providers
            time_from=datetime.now() - timedelta(days=3)
        )
        
        if news:
            print(f"✓ Fetched {len(news)} deduplicated news articles from all providers")
            
            # Count unique sources
            sources = set([article.get('source', 'Unknown') for article in news])
            print(f"✓ Source diversity: {len(sources)} unique sources")
            print(f"  Sources include: {', '.join(list(sources)[:5])}...")
            
            # Sync to database
            print("\nSyncing to database...")
            integration = NewsAPIIntegration(provider="finnhub")  # Just for sync method
            count = integration.sync_to_database(news)
            print(f"✓ Successfully added {count} news articles to database")
            
            # Show sample
            print("\nSample recent news:")
            for article in news[:5]:
                print(f"  • {article['headline'][:60]}...")
                print(f"    {article['company']} - {article['date'].strftime('%Y-%m-%d %H:%M')} - {article['source']}")
            
            return count
        else:
            print("⚠ No news data available")
            return 0
            
    except Exception as e:
        print(f"✗ Error populating news: {e}")
        import traceback
        traceback.print_exc()
        return 0

def main():
    """Main database population workflow"""
    print("\n" + "="*60)
    print("🚀 TMT Research Portal - Database Population")
    print("="*60)
    print("This script fetches data from multiple premium providers:")
    print("• Earnings: Alpha Vantage (accurate reported/upcoming status)")
    print("• News: Finnhub + Alpha Vantage + Marketaux (source diversity)")
    print("="*60)
    
    start_time = datetime.now()
    
    # Populate earnings
    earnings_count = populate_earnings()
    
    # Populate news
    news_count = populate_news()
    
    # Summary
    elapsed = (datetime.now() - start_time).total_seconds()
    
    print("\n" + "="*60)
    print("✨ Database Population Complete!")
    print("="*60)
    print(f"Earnings Events: {earnings_count}")
    print(f"News Articles: {news_count}")
    print(f"Time Elapsed: {elapsed:.1f} seconds")
    print("="*60)
    
    if earnings_count > 0 or news_count > 0:
        print("\n✓ Your TMT Research Portal now has real-time data!")
        print("\nNext steps:")
        print("1. Open your Streamlit app to view the data")
        print("2. Check the Earnings Calendar page for upcoming earnings")
        print("3. Browse the News Feed for premium sources (Reuters, Bloomberg, CNBC)")
        print("4. Set up automated refresh (see scripts/refresh_data.py)")
    else:
        print("\n⚠ No data was added. Please check:")
        print("1. Your API keys are set in Replit Secrets:")
        print("   - FINNHUB_API_KEY (required)")
        print("   - ALPHA_VANTAGE_KEY (required)")
        print("   - MARKETAUX_KEY (optional)")
        print("2. Your API keys are valid")
        print("3. You haven't exceeded rate limits")

if __name__ == "__main__":
    main()
