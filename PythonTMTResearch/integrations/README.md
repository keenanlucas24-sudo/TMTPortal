# TMT Research Portal - API Integrations

This directory contains integration modules for fetching real-time financial data from external APIs.

## Available Integrations

### 1. Earnings API Integration (`earnings_api.py`)

Fetches real-time earnings calendar, consensus estimates, and actual results.

**Supported Providers:**
- **Finnhub** (recommended - comprehensive TMT coverage)
  - Free tier: 60 API calls/minute
  - Includes EPS estimates, revenue estimates, and actual results
  - Get your API key: https://finnhub.io/register
  
- **Alpha Vantage**
  - Free tier: 500 requests/day
  - Get your API key: https://www.alphavantage.co/support/#api-key
  
- **Financial Modeling Prep (FMP)**
  - Free tier: 250 requests/day, paid plans from $29/month
  - Get your API key: https://site.financialmodelingprep.com/developer/docs

**Setup:**

```bash
# Set your API key as an environment variable
# For Finnhub (recommended):
export FINNHUB_API_KEY="your_api_key_here"

# OR for Alpha Vantage:
export ALPHA_VANTAGE_KEY="your_api_key_here"

# OR for FMP:
export FMP_API_KEY="your_api_key_here"
```

**Usage:**

```python
from integrations.earnings_api import EarningsAPIIntegration

# Initialize with your preferred provider (defaults to finnhub)
integration = EarningsAPIIntegration(provider="finnhub")

# Fetch earnings calendar (all companies, next 3 months)
earnings = integration.fetch_earnings_calendar()

# Fetch for specific company
earnings = integration.fetch_earnings_calendar(symbol="AAPL")

# Sync to database
count = integration.sync_to_database(earnings)
print(f"Synced {count} earnings records to database")
```

### 2. News API Integration (`news_api.py`)

Fetches real-time financial news with sentiment analysis.

**Supported Providers:**
- **Finnhub** (recommended - comprehensive company news)
  - Free tier: 60 API calls/minute
  - Company-specific news with metadata and summaries
  - Get your API key: https://finnhub.io/register
  
- **Alpha Vantage** (includes sentiment analysis)
  - Free tier: 500 requests/day
  - Get your API key: https://www.alphavantage.co/support/#api-key
  
- **Marketaux**
  - Unlimited free plan, 5000+ news sources
  - Get your API key: https://www.marketaux.com/
  
- **Stock News API**
  - Curated sources (CNBC, Bloomberg, etc.)
  - Get your API key: https://stocknewsapi.com/

**Setup:**

```bash
# Set your API key as an environment variable
# For Finnhub (recommended):
export FINNHUB_API_KEY="your_api_key_here"

# OR for Alpha Vantage:
export ALPHA_VANTAGE_KEY="your_api_key_here"

# OR for Marketaux:
export MARKETAUX_KEY="your_api_key_here"

# OR for Stock News API:
export STOCK_NEWS_KEY="your_api_key_here"
```

**Usage:**

```python
from integrations.news_api import NewsAPIIntegration
from datetime import datetime, timedelta

# Initialize with your preferred provider (defaults to finnhub)
integration = NewsAPIIntegration(provider="finnhub")

# Fetch news for TMT companies (last 7 days)
tmt_tickers = ["AAPL", "MSFT", "GOOGL", "META", "NVDA", "AMZN"]
news = integration.fetch_news(
    tickers=tmt_tickers,
    topics=["technology", "earnings"],
    limit=50
)

# Fetch news for specific company (last 2 days)
news = integration.fetch_news(
    tickers=["AAPL"],
    limit=20,
    time_from=datetime.now() - timedelta(days=2)
)

# Sync to database
count = integration.sync_to_database(news)
print(f"Synced {count} news articles to database")
```

## Setting API Keys in Replit

1. Click the **Secrets** (🔒) icon in the left sidebar
2. Click **+ New Secret**
3. Add your API key:
   - Key: `FINNHUB_API_KEY` (or `ALPHA_VANTAGE_KEY`, `FMP_API_KEY`, `MARKETAUX_KEY`, `STOCK_NEWS_KEY`)
   - Value: Your actual API key
4. Click **Add Secret**

The integrations will automatically pick up the keys from environment variables.

## Automated Data Refresh

You can create a scheduled task to automatically refresh earnings and news data. Create a file `scripts/refresh_data.py`:

```python
from integrations.earnings_api import EarningsAPIIntegration
from integrations.news_api import NewsAPIIntegration

def refresh_earnings():
    """Refresh earnings calendar data"""
    integration = EarningsAPIIntegration(provider="finnhub")
    earnings = integration.fetch_earnings_calendar(horizon="3month")
    count = integration.sync_to_database(earnings)
    print(f"✓ Refreshed {count} earnings events")

def refresh_news():
    """Refresh news feed data"""
    integration = NewsAPIIntegration(provider="finnhub")
    
    # Get your top TMT companies from database
    from db.db_operations import get_all_companies
    companies = get_all_companies()
    tickers = [c['ticker'] for c in companies[:50]]  # Top 50 companies
    
    news = integration.fetch_news(
        tickers=tickers,
        topics=["technology", "earnings"],
        limit=100
    )
    count = integration.sync_to_database(news)
    print(f"✓ Refreshed {count} news articles")

if __name__ == "__main__":
    print("Starting data refresh...")
    refresh_earnings()
    refresh_news()
    print("✓ Data refresh complete!")
```

Run it with: `python scripts/refresh_data.py`

## API Rate Limits

**Finnhub Free Tier (Recommended):**
- 60 API calls/minute
- No daily limit on free tier
- Comprehensive TMT coverage for both earnings and news
- Good for: Production use, comprehensive data needs

**Alpha Vantage Free Tier:**
- 500 requests/day
- 5 requests/minute
- Good for: Development, small projects, dual-purpose (earnings + news)

**Marketaux Free Tier:**
- 100 requests/day
- No per-minute limit
- Unlimited articles per request
- Good for: News aggregation, international coverage

**Stock News API:**
- Free trial available (limited requests)
- Paid plans start at $8/month
- 100+ articles per request
- Good for: High-quality curated news sources

**Financial Modeling Prep (FMP):**
- Free tier: 250 requests/day
- Paid plans from $29/month (unlimited requests)
- Good for: Comprehensive earnings data with transcripts

**Best Practices:**
- Cache API responses locally
- Refresh data every few hours (not every page load)
- Use batch requests when possible
- Consider upgrading to paid tier for production use

## Troubleshooting

**Error: "API key not found"**
- Make sure you've set the environment variable correctly
- Restart your Replit session after adding secrets

**Error: "API request failed: 429"**
- You've hit the rate limit
- Wait a few minutes and try again
- Consider using a different provider or upgrading

**Error: "No data returned"**
- Check that the ticker symbol is valid
- Verify the date range is reasonable
- Some companies may not have earnings data available yet

## Next Steps

1. Get your free API key from Finnhub (https://finnhub.io/register) 
2. Add it to Replit Secrets as `FINNHUB_API_KEY`
3. Run the example scripts to test the integration
4. Set up automated refresh for production use

**Why Finnhub?**
- 60 API calls/minute (faster than competitors)
- Both earnings and news in one provider
- Comprehensive TMT company coverage
- Free tier suitable for production
