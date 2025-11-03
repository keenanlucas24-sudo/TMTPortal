# TMT Research Portal - Automation Guide

## Overview

Your TMT Research Portal now has two powerful automation scripts to keep your data fresh and accurate using real-time Finnhub API data.

## Available Scripts

### 1. Database Population (`populate_database.py`)

**Purpose**: One-time script to initially populate your database with real earnings and news data.

**Usage**:
```bash
python populate_database.py
```

**What it does**:
- Fetches earnings calendar for next 3 months from Finnhub
- Fetches recent news (last 7 days) for your top 50 TMT companies
- Syncs all data to your PostgreSQL database
- Shows progress and summary statistics

**When to use**:
- First-time setup
- After clearing your database
- When you want to refresh all historical data

### 2. Automated Refresh (`scripts/refresh_data.py`)

**Purpose**: Scheduled script to keep your data up-to-date with the latest market information.

**Usage**:
```bash
python scripts/refresh_data.py
```

**What it does**:
- Refreshes earnings calendar (3-month horizon)
- Fetches latest news (last 2 days) to stay current
- Optimized for frequent updates
- Logs progress with timestamps

**When to use**:
- Daily/hourly automated runs
- Set up as a cron job or scheduled task
- Continuous data refresh workflow

## Current Database Status

✅ **Populated with Real Data**:
- **530 earnings events** from Finnhub
- **10 news articles** from Finnhub
- **Upcoming earnings** for major TMT companies (AAPL, MSFT, GOOGL, AMZN, etc.)

## Setting Up Automation

### Option 1: Manual Refresh (Recommended for now)

Run the refresh script whenever you want to update your data:

```bash
python scripts/refresh_data.py
```

### Option 2: Scheduled Automation

#### Using Replit Cron Jobs (if available)

1. Create a new cron job in your Replit workspace
2. Set schedule: `0 */4 * * *` (every 4 hours)
3. Command: `python scripts/refresh_data.py`

#### Using Python Continuous Loop

Edit `scripts/refresh_data.py` and uncomment the continuous refresh loop at the bottom:

```python
# Uncomment these lines for continuous 4-hour refresh
REFRESH_INTERVAL = 4 * 60 * 60  # 4 hours

while True:
    refresh_all()
    print(f"\n⏰ Next refresh in {REFRESH_INTERVAL // 3600} hours...")
    time.sleep(REFRESH_INTERVAL)
```

Then run it as a background process:
```bash
python scripts/refresh_data.py &
```

### Option 3: External Cron (if deploying elsewhere)

Add to your crontab:
```bash
# Refresh every 4 hours
0 */4 * * * cd /path/to/project && python scripts/refresh_data.py >> logs/refresh.log 2>&1

# Or refresh twice daily (8 AM and 8 PM)
0 8,20 * * * cd /path/to/project && python scripts/refresh_data.py >> logs/refresh.log 2>&1
```

## API Rate Limits

**Finnhub Free Tier**:
- 60 API calls per minute
- No daily limit
- Perfect for production use

**Recommended Refresh Frequency**:
- **Earnings**: Every 4-6 hours (data doesn't change that often)
- **News**: Every 2-4 hours (stays current without overloading API)
- **Combined**: Every 4 hours is optimal

## Monitoring Data Freshness

Check when data was last updated:

```sql
-- Latest earnings date
SELECT MAX(date) as latest_earnings FROM earnings WHERE status = 'Upcoming';

-- Latest news date
SELECT MAX(date) as latest_news FROM news;
```

View in your Streamlit app:
- **Earnings Calendar** page shows all upcoming earnings
- **News Feed** page shows recent articles with timestamps

## Troubleshooting

### Script Times Out
- Normal for large initial population (1500+ records)
- Data is still being added in background
- Check database to confirm: `SELECT COUNT(*) FROM earnings;`

### No New Data Added
- Check if data already exists (script avoids duplicates)
- Verify FINNHUB_API_KEY is set correctly
- Check rate limits (60 calls/minute)

### API Errors
- Verify your Finnhub API key at https://finnhub.io/
- Check your internet connection
- Wait a minute if you hit rate limits

## Best Practices

1. **Start with manual refresh**: Run `python scripts/refresh_data.py` to test
2. **Monitor first few runs**: Check logs to ensure data is updating correctly
3. **Adjust frequency**: Based on your needs (2-6 hours is good for most cases)
4. **Check data quality**: Verify earnings dates and news are accurate in your app

## Next Steps

1. ✅ Database populated with real Finnhub data
2. ✅ Test the Streamlit app to view your real data
3. 🔄 Set up automated refresh (choose an option above)
4. 📊 Monitor data freshness and adjust schedule as needed

## Support

For issues or questions:
- Check `integrations/README.md` for API documentation
- Run `python test_finnhub_integration.py` to verify API connectivity
- Review Finnhub API docs: https://finnhub.io/docs/api
