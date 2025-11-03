"""
Test script for Finnhub API integration
Run this to verify your Finnhub API key is working correctly
"""

from integrations.earnings_api import EarningsAPIIntegration
from integrations.news_api import NewsAPIIntegration
from datetime import datetime, timedelta

def test_finnhub_earnings():
    """Test Finnhub earnings calendar integration"""
    print("\n" + "="*60)
    print("Testing Finnhub Earnings Integration")
    print("="*60)
    
    try:
        integration = EarningsAPIIntegration(provider="finnhub")
        print("✓ Finnhub earnings integration initialized")
        
        # Fetch earnings for a specific company
        print("\nFetching earnings calendar for AAPL...")
        earnings = integration.fetch_earnings_calendar(symbol="AAPL", horizon="3month")
        
        if earnings:
            print(f"✓ Successfully fetched {len(earnings)} earnings events")
            print("\nSample earnings data:")
            for i, event in enumerate(earnings[:3], 1):
                print(f"\n  Event {i}:")
                print(f"    Company: {event.get('company')}")
                print(f"    Ticker: {event.get('ticker')}")
                print(f"    Date: {event.get('date')}")
                print(f"    Quarter: {event.get('quarter')}")
                print(f"    Consensus EPS: {event.get('consensus_eps')}")
                print(f"    Status: {event.get('status')}")
        else:
            print("⚠ No earnings data returned (this may be normal if no upcoming earnings)")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing earnings integration: {e}")
        return False

def test_finnhub_news():
    """Test Finnhub news integration"""
    print("\n" + "="*60)
    print("Testing Finnhub News Integration")
    print("="*60)
    
    try:
        integration = NewsAPIIntegration(provider="finnhub")
        print("✓ Finnhub news integration initialized")
        
        # Fetch news for TMT companies
        tickers = ["AAPL", "MSFT", "GOOGL"]
        print(f"\nFetching news for {', '.join(tickers)} (last 7 days)...")
        
        news = integration.fetch_news(
            tickers=tickers,
            limit=10,
            time_from=datetime.now() - timedelta(days=7)
        )
        
        if news:
            print(f"✓ Successfully fetched {len(news)} news articles")
            print("\nSample news articles:")
            for i, article in enumerate(news[:3], 1):
                print(f"\n  Article {i}:")
                print(f"    Company: {article.get('company')}")
                print(f"    Headline: {article.get('headline')[:80]}...")
                print(f"    Date: {article.get('date')}")
                print(f"    Source: {article.get('source')}")
        else:
            print("⚠ No news data returned")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing news integration: {e}")
        return False

def main():
    """Run all Finnhub integration tests"""
    print("\n🧪 Finnhub API Integration Test Suite")
    print("="*60)
    print("This script tests your Finnhub API key and integration")
    print("="*60)
    
    earnings_ok = test_finnhub_earnings()
    news_ok = test_finnhub_news()
    
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"Earnings Integration: {'✓ PASS' if earnings_ok else '✗ FAIL'}")
    print(f"News Integration: {'✓ PASS' if news_ok else '✗ FAIL'}")
    
    if earnings_ok and news_ok:
        print("\n🎉 All tests passed! Your Finnhub integration is working correctly.")
        print("\nNext steps:")
        print("1. Sync data to database using integration.sync_to_database()")
        print("2. View the data in your Streamlit app")
        print("3. Set up automated refresh (see integrations/README.md)")
    else:
        print("\n⚠ Some tests failed. Please check:")
        print("1. Your FINNHUB_API_KEY is correctly set in Replit Secrets")
        print("2. Your API key is valid (test at https://finnhub.io/)")
        print("3. You haven't exceeded rate limits (60 calls/minute)")

if __name__ == "__main__":
    main()
