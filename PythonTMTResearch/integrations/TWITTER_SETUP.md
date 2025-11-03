# Twitter/X Social News Integration Setup

This integration fetches tweets from financial news accounts and analyzes them using Gemini AI to extract TMT-relevant news, sentiment, and ticker mentions.

## Overview

- **Twitter Scraping**: Uses `twscrape` library (free, no API required)
- **AI Analysis**: Gemini API analyzes tweets for relevance, sentiment, and ticker extraction
- **Caching**: Only new tweets are analyzed to save on API costs
- **Refresh**: Manual refresh button + optional background service every 15 minutes

## ⚠️ Important Limitations

### Twitter Account Requirements

`twscrape` requires **actual Twitter account credentials** to work. You need to provide:
- Twitter username
- Twitter password  
- Email address
- Email password

**Risks:**
- Twitter may suspend accounts used for scraping (violates ToS)
- Use dedicated/disposable accounts you can afford to lose
- Free Twitter accounts work but may get rate-limited quickly

### Alternative Approaches

If you cannot provide Twitter accounts:

1. **Use Twitter's Official API** ($100/month Basic tier)
   - More reliable and legal
   - Better rate limits
   - No account suspension risk

2. **Use Apify** (paid service, ~$49/month)
   - Pre-built Twitter scrapers
   - No account management needed
   - Pay per tweet extracted

3. **Manual RSS/News APIs** (already implemented)
   - Stick with existing news integrations (Finnhub, Alpha Vantage, Marketaux)
   - No Twitter dependency

## Setup Instructions

### Step 1: Configure Twitter Accounts

Run the interactive setup script:

```bash
python integrations/setup_twitter_accounts.py
```

This will prompt you to add Twitter account credentials. You need at least 1 account, but 2-3 is better for rate limiting.

### Step 2: Test Manual Fetch

Test that tweet fetching works:

```bash
python integrations/social_news_service.py
```

This will fetch 10 tweets per account and analyze them with Gemini.

### Step 3: Enable Background Refresh (Optional)

To automatically refresh tweets every 15 minutes, run:

```bash
python background_tweet_refresh.py
```

This runs continuously in the background. You can run it in a separate terminal or use a process manager like `supervisord`.

## Usage in Streamlit

Once configured, the Social News tab will appear in the portal. Users can:

1. **View analyzed tweets** with sentiment, tickers, and summaries
2. **Filter by source** (@Bloomberg, @Reuters, etc.)
3. **Filter by time** (24 hours, 3 days, week, all time)
4. **Manual refresh** using the "🔄 Refresh Feed" button

## Monitored Twitter Accounts

The integration monitors these financial news accounts (18 total):

- @Bloomberg
- @Reuters
- @CNBC
- @SeekingAlpha
- @WSJ
- @FT
- @theinformation
- @faststocknews
- @mingchikuo
- @ivanaspear
- @rihardjarc
- @semianalysis_
- @wallstengine
- @stockmktnewz
- @zephyr_z9
- @ap
- @aistocksavvy
- @trendspider

## How It Works

1. **Scraping**: `twscrape` fetches recent tweets from configured accounts
2. **Deduplication**: Checks if tweet already analyzed (via `tweet_id`)
3. **Gemini Analysis**: Sends tweet to Gemini API with structured prompt:
   - Extract ticker symbols (["AAPL", "MSFT"])
   - Determine sentiment (positive/negative/neutral)
   - Score sentiment (-1.0 to +1.0)
   - Calculate relevance (0.0 to 1.0)
   - Generate headline and summary
4. **Filtering**: Only tweets with relevance > 0.5 and TMT-related content are shown
5. **Storage**: Tweet + analysis stored in PostgreSQL for fast retrieval

## Database Schema

### `tweets` table
- `tweet_id`: Unique Twitter ID
- `author`: Twitter account (@Bloomberg)
- `timestamp`: When tweet was posted
- `text`: Full tweet text
- `likes`, `retweets`: Engagement metrics
- `permalink`: Link to original tweet

### `tweet_analysis` table
- `tweet_id`: Foreign key to tweets table
- `tickers`: Array of extracted ticker symbols
- `sentiment`: positive/negative/neutral
- `sentiment_score`: -1.0 to +1.0
- `relevance_score`: 0.0 to 1.0
- `is_relevant`: Boolean filter
- `headline`: AI-generated headline
- `summary`: AI-generated summary

## Cost Considerations

- **Twitter Scraping**: Free (but requires account credentials)
- **Gemini API**: Free tier includes 1,500 requests/day for gemini-2.5-flash
- **Typical Usage**: ~70 tweets/hour × 24 = 1,680 tweets/day (fits in free tier)

## Troubleshooting

### No tweets fetched

1. Check if Twitter accounts are configured: `python integrations/setup_twitter_accounts.py`
2. Verify accounts are logged in (script shows account status)
3. Check for Twitter rate limiting errors in logs

### Tweets not showing up

1. Verify tweets are TMT-relevant (only high-relevance tweets shown)
2. Check Gemini API key is set: `echo $GEMINI_API_KEY`
3. Look for analysis errors in console output

### Account suspended

1. Twitter detected scraping activity
2. Use different/fresh accounts
3. Reduce refresh frequency (30 min instead of 15 min)
4. Consider switching to official Twitter API

## Security Notes

- **Never commit credentials** to version control
- Twitter account credentials stored in twscrape local database (~/.twscrape/)
- Gemini API key stored in Replit Secrets
- Use dedicated Twitter accounts for scraping only

## Future Enhancements

- [ ] Multi-language tweet support
- [ ] Advanced sentiment analysis with confidence scores
- [ ] Tweet thread aggregation
- [ ] Ticker mention trending/alerting
- [ ] Integration with company watchlists
- [ ] Export social news to CSV/Excel
