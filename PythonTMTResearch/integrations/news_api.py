"""
News Feed Integration Module

This module provides integration with financial news APIs for real-time TMT company news.
Supports multiple providers:
- Alpha Vantage (free tier with sentiment analysis)
- Marketaux (unlimited free plan, 5000+ sources)
- Stock News API (curated sources with sentiment)
- Finnhub (comprehensive company news with sentiment)

To use:
1. Set your API key as an environment variable (ALPHA_VANTAGE_KEY, MARKETAUX_KEY, STOCK_NEWS_KEY, or FINNHUB_API_KEY)
2. Call fetch_news() to get recent news for specific companies or sectors
3. The data is automatically formatted to match our database schema
"""

import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from db.db_operations import add_news_item

class NewsAPIIntegration:
    """Integration class for fetching real-time financial news"""
    
    def __init__(self, provider: str = "finnhub"):
        """
        Initialize the news API integration
        
        Args:
            provider: API provider to use ('alpha_vantage', 'marketaux', 'stock_news', or 'finnhub')
        """
        self.provider = provider
        
        from utils.secret_helper import get_secret
        if provider == "alpha_vantage":
            self.api_key = get_secret("ALPHA_VANTAGE_KEY")
            self.base_url = "https://www.alphavantage.co/query"
        elif provider == "marketaux":
            self.api_key = get_secret("MARKETAUX_KEY")
            self.base_url = "https://api.marketaux.com/v1/news/all"
        elif provider == "stock_news":
            self.api_key = get_secret("STOCK_NEWS_KEY")
            self.base_url = "https://stocknewsapi.com/api/v1"
        elif provider == "finnhub":
            self.api_key = get_secret("FINNHUB_API_KEY")
            self.base_url = "https://finnhub.io/api/v1"
        else:
            raise ValueError(f"Unsupported provider: {provider}. Choose 'alpha_vantage', 'marketaux', 'stock_news', or 'finnhub'.")
    
    def fetch_news(self, tickers: Optional[List[str]] = None,
                   topics: Optional[List[str]] = None,
                   limit: int = 50,
                   time_from: Optional[datetime] = None) -> List[Dict]:
        """
        Fetch financial news from the API
        
        Args:
            tickers: List of stock ticker symbols to filter by
            topics: List of topics to filter by (e.g., 'technology', 'earnings')
            limit: Maximum number of articles to fetch
            time_from: Fetch news from this date onwards (defaults to last 7 days)
            
        Returns:
            List of news articles with headline, summary, source, and sentiment
        """
        if not self.api_key:
            raise ValueError(f"API key not found. Set {self.provider.upper()}_KEY environment variable.")
        
        if time_from is None:
            time_from = datetime.now() - timedelta(days=7)
        
        if self.provider == "alpha_vantage":
            return self._fetch_alpha_vantage_news(tickers, topics, limit, time_from)
        elif self.provider == "marketaux":
            return self._fetch_marketaux_news(tickers, topics, limit, time_from)
        elif self.provider == "stock_news":
            return self._fetch_stock_news(tickers, limit, time_from)
        elif self.provider == "finnhub":
            return self._fetch_finnhub_news(tickers, limit, time_from)
    
    def _fetch_alpha_vantage_news(self, tickers: Optional[List[str]],
                                  topics: Optional[List[str]],
                                  limit: int,
                                  time_from: datetime) -> List[Dict]:
        """Fetch news from Alpha Vantage API"""
        params = {
            "function": "NEWS_SENTIMENT",
            "apikey": self.api_key,
            "limit": min(limit * 3, 200),  # Fetch extra since we'll filter by ticker
            "sort": "LATEST"
        }
        
        # Alpha Vantage's ticker filter is unreliable, so we'll fetch all and filter ourselves
        # This gives us better results
        
        if topics:
            params["topics"] = ",".join(topics)
        
        response = requests.get(self.base_url, params=params)
        
        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code}")
        
        data = response.json()
        articles = data.get("feed", [])
        
        # Filter by tickers and date
        filtered_articles = []
        ticker_set = set(tickers) if tickers else set()
        
        for article in articles:
            # Check date filter
            time_str = article.get("time_published", "")
            try:
                pub_date = datetime.strptime(time_str, "%Y%m%dT%H%M%S")
                if pub_date < time_from:
                    continue
            except (ValueError, TypeError):
                pass  # Include if date parsing fails
            
            # Check ticker filter if provided
            if ticker_set:
                article_tickers = article.get("ticker_sentiment", [])
                article_ticker_symbols = set([t.get("ticker", "") for t in article_tickers])
                # Include if any of our tickers match
                if not ticker_set.intersection(article_ticker_symbols):
                    continue
            
            filtered_articles.append(article)
            
            # Stop when we have enough
            if len(filtered_articles) >= limit:
                break
        
        return self._normalize_news_data(filtered_articles, "alpha_vantage")
    
    def _fetch_marketaux_news(self, tickers: Optional[List[str]],
                             topics: Optional[List[str]],
                             limit: int,
                             time_from: datetime) -> List[Dict]:
        """Fetch news from Marketaux API - limit 10 symbols per request"""
        all_articles = []
        
        # Marketaux has a 10-symbol limit per request, so batch if needed
        if tickers and len(tickers) > 10:
            # Split into batches of 10
            batches = [tickers[i:i+10] for i in range(0, len(tickers), 10)]
            articles_per_batch = max(1, limit // len(batches))
            
            for batch in batches:
                params = {
                    "api_token": self.api_key,
                    "limit": articles_per_batch,
                    "published_after": time_from.strftime("%Y-%m-%d"),
                    "language": "en",
                    "symbols": ",".join(batch)
                }
                
                if topics:
                    params["filter_entities"] = "true"
                
                try:
                    response = requests.get(self.base_url, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        all_articles.extend(data.get("data", []))
                    else:
                        print(f"Marketaux batch error: {response.status_code}")
                except Exception as e:
                    print(f"Marketaux batch exception: {e}")
                    continue
        else:
            # Single request for <= 10 symbols
            params = {
                "api_token": self.api_key,
                "limit": limit,
                "published_after": time_from.strftime("%Y-%m-%d"),
                "language": "en"
            }
            
            if tickers:
                params["symbols"] = ",".join(tickers[:10])  # Safeguard
            
            if topics:
                params["filter_entities"] = "true"
            
            response = requests.get(self.base_url, params=params)
            
            if response.status_code != 200:
                print(f"Marketaux error: {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            all_articles = data.get("data", [])
        
        return self._normalize_news_data(all_articles[:limit], "marketaux")
    
    def _fetch_stock_news(self, tickers: Optional[List[str]],
                         limit: int,
                         time_from: datetime) -> List[Dict]:
        """Fetch news from Stock News API"""
        params = {
            "token": self.api_key,
            "items": limit,
            "sortby": "rank",
            "date": time_from.strftime("%m%d%Y")
        }
        
        if tickers:
            params["tickers"] = ",".join(tickers)
        
        response = requests.get(self.base_url, params=params)
        
        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code}")
        
        data = response.json()
        articles = data.get("data", [])
        
        return self._normalize_news_data(articles, "stock_news")
    
    def _fetch_finnhub_news(self, tickers: Optional[List[str]],
                           limit: int,
                           time_from: datetime) -> List[Dict]:
        """Fetch news from Finnhub API"""
        all_news = []
        
        # Finnhub requires fetching news per ticker symbol
        if not tickers:
            # If no tickers specified, use some default TMT companies
            tickers = ["AAPL", "MSFT", "GOOGL", "META", "AMZN", "NVDA"]
        
        # Limit to 10 tickers to avoid rate limits
        tickers = tickers[:10]
        
        # Calculate articles per ticker with remainder distribution
        base_articles = limit // len(tickers)
        remainder = limit % len(tickers)
        
        for idx, ticker in enumerate(tickers):
            # Give extra article to first 'remainder' tickers to distribute evenly
            articles_to_fetch = base_articles + (1 if idx < remainder else 0)
            
            # Skip if calculated as zero (shouldn't happen with proper limit)
            if articles_to_fetch == 0:
                continue
                
            endpoint = f"{self.base_url}/company-news"
            
            # Finnhub wants dates in YYYY-MM-DD format
            params = {
                "symbol": ticker,
                "from": time_from.strftime("%Y-%m-%d"),
                "to": datetime.now().strftime("%Y-%m-%d"),
                "token": self.api_key
            }
            
            response = requests.get(endpoint, params=params)
            
            if response.status_code == 200:
                news_items = response.json()
                all_news.extend(news_items[:articles_to_fetch])
        
        # Sort by date descending and limit to requested amount
        all_news.sort(key=lambda x: x.get('datetime', 0), reverse=True)
        
        return self._normalize_news_data(all_news[:limit], "finnhub")
    
    def _normalize_news_data(self, raw_data: List[Dict], 
                            source: str) -> List[Dict]:
        """
        Normalize news data to our database schema
        
        Returns data in format:
        {
            'date': datetime,
            'sector': str,
            'company': str,
            'headline': str,
            'summary': str,
            'source': str,
            'url': str,
            'sentiment': str (optional)
        }
        """
        normalized = []
        
        for item in raw_data:
            try:
                if source == "alpha_vantage":
                    # Extract company tickers from ticker_sentiment field
                    tickers = item.get("ticker_sentiment", [])
                    company_str = ", ".join([t.get("ticker", "") for t in tickers[:3]]) if tickers else "TMT"
                    
                    # Parse time string
                    time_str = item.get("time_published", "")
                    try:
                        pub_date = datetime.strptime(time_str, "%Y%m%dT%H%M%S")
                    except ValueError:
                        pub_date = datetime.now()
                    
                    normalized_item = {
                        'date': pub_date,
                        'company': company_str,
                        'headline': item.get('title', ''),
                        'summary': item.get('summary', ''),
                        'source': item.get('source', 'Alpha Vantage'),
                        'url': item.get('url', ''),
                        'sector': 'Technology',  # Default, could be enhanced with mapping
                        'sentiment': item.get('overall_sentiment_label', 'Neutral')
                    }
                
                elif source == "marketaux":
                    # Marketaux includes entities (stocks mentioned)
                    entities = item.get("entities", [])
                    company_str = ", ".join([e.get("symbol", "") for e in entities[:3]]) if entities else "TMT"
                    
                    normalized_item = {
                        'date': datetime.fromisoformat(item.get('published_at', '').replace('Z', '+00:00')),
                        'company': company_str,
                        'headline': item.get('title', ''),
                        'summary': item.get('description', ''),
                        'source': item.get('source', 'Marketaux'),
                        'url': item.get('url', ''),
                        'sector': 'Technology',
                        'sentiment': item.get('sentiment', 'Neutral')
                    }
                
                elif source == "stock_news":
                    normalized_item = {
                        'date': datetime.fromisoformat(item.get('date', '')),
                        'company': ", ".join(item.get('tickers', ['TMT'])),
                        'headline': item.get('title', ''),
                        'summary': item.get('text', ''),
                        'source': item.get('source_name', 'Stock News API'),
                        'url': item.get('news_url', ''),
                        'sector': 'Technology',
                        'sentiment': item.get('sentiment', 'Neutral')
                    }
                
                elif source == "finnhub":
                    # Finnhub provides: category, datetime, headline, id, image, related, source, summary, url
                    # datetime is Unix timestamp
                    timestamp = item.get('datetime', 0)
                    pub_date = datetime.fromtimestamp(timestamp) if timestamp else datetime.now()
                    
                    # Related field contains ticker symbol
                    related = item.get('related', '')
                    company_str = related if related else 'TMT'
                    
                    normalized_item = {
                        'date': pub_date,
                        'company': company_str,
                        'headline': item.get('headline', ''),
                        'summary': item.get('summary', ''),
                        'source': item.get('source', 'Finnhub'),
                        'url': item.get('url', ''),
                        'sector': 'Technology',  # Could be enhanced with category mapping
                        'sentiment': 'Neutral'  # Finnhub doesn't provide sentiment in company news
                    }
                
                normalized.append(normalized_item)
            
            except (KeyError, ValueError) as e:
                # Skip malformed entries
                print(f"Warning: Skipping malformed news entry: {e}")
                continue
        
        return normalized
    
    def sync_to_database(self, news_data: List[Dict]) -> int:
        """
        Sync fetched news data to the database
        
        Args:
            news_data: List of normalized news dictionaries
            
        Returns:
            Number of records inserted
        """
        count = 0
        for news in news_data:
            try:
                add_news_item(
                    date=news.get('date'),
                    sector=news.get('sector', 'Technology'),
                    company=news.get('company', ''),
                    headline=news.get('headline', ''),
                    summary=news.get('summary', ''),
                    source=news.get('source', ''),
                    url=news.get('url', '')
                )
                count += 1
            except Exception as e:
                print(f"Error inserting news: {e}")
        
        return count
    
    def fetch_company_news(self, ticker: str, days_back: int = 7) -> List[Dict]:
        """
        Convenience method to fetch news for a specific company
        
        Args:
            ticker: Stock ticker symbol
            days_back: Number of days to look back
            
        Returns:
            List of news articles for the company
        """
        time_from = datetime.now() - timedelta(days=days_back)
        return self.fetch_news(tickers=[ticker], time_from=time_from)


def fetch_multi_provider_news(tickers: Optional[List[str]] = None,
                               limit: int = 50,
                               time_from: Optional[datetime] = None,
                               providers: Optional[List[str]] = None) -> List[Dict]:
    """
    Aggregate news from multiple providers (Finnhub, Alpha Vantage, Marketaux)
    and deduplicate by URL/headline for maximum source diversity
    
    Args:
        tickers: List of stock ticker symbols to filter by
        limit: Total number of articles to return (distributed across providers)
        time_from: Fetch news from this date onwards (defaults to last 3 days)
        providers: List of providers to use (defaults to ['finnhub', 'alpha_vantage', 'marketaux'])
        
    Returns:
        Deduplicated list of news articles sorted by date descending
    """
    if time_from is None:
        time_from = datetime.now() - timedelta(days=3)
    
    if providers is None:
        providers = ['finnhub', 'alpha_vantage', 'marketaux']
    
    all_news = []
    articles_per_provider = limit // len(providers)
    
    # Fetch from each provider
    for provider in providers:
        try:
            # Check if API key exists
            key_map = {
                'finnhub': 'FINNHUB_API_KEY',
                'alpha_vantage': 'ALPHA_VANTAGE_KEY',
                'marketaux': 'MARKETAUX_KEY'
            }
            
            api_key = os.getenv(key_map.get(provider, ''))
            if not api_key:
                print(f"Warning: {key_map.get(provider)} not found, skipping {provider}")
                continue
            
            integration = NewsAPIIntegration(provider=provider)
            news_items = integration.fetch_news(
                tickers=tickers,
                limit=articles_per_provider + 10,  # Fetch extra for deduplication
                time_from=time_from
            )
            all_news.extend(news_items)
            print(f"✓ Fetched {len(news_items)} articles from {provider}")
            
        except Exception as e:
            print(f"Warning: Failed to fetch from {provider}: {e}")
            continue
    
    # Deduplicate by URL and headline
    seen_urls = set()
    seen_headlines = set()
    deduplicated = []
    
    for article in all_news:
        url = article.get('url', '')
        headline = article.get('headline', '').lower().strip()
        
        # Skip if we've seen this URL or very similar headline
        if url and url in seen_urls:
            continue
        if headline and headline in seen_headlines:
            continue
        
        seen_urls.add(url)
        seen_headlines.add(headline)
        
        # Normalize timezone-aware dates to timezone-naive for consistent sorting
        article_date = article.get('date')
        if article_date and hasattr(article_date, 'tzinfo') and article_date.tzinfo is not None:
            article['date'] = article_date.replace(tzinfo=None)
        
        deduplicated.append(article)
    
    # Sort by date descending (now all dates are timezone-naive)
    deduplicated.sort(key=lambda x: x.get('date', datetime.min.replace(tzinfo=None)), reverse=True)
    
    # Return requested limit
    return deduplicated[:limit]


# Example usage
if __name__ == "__main__":
    # Example: Fetch Alpha Vantage news for TMT companies
    # Set ALPHA_VANTAGE_KEY environment variable first
    
    # integration = NewsAPIIntegration(provider="alpha_vantage")
    # tmt_tickers = ["AAPL", "MSFT", "GOOGL", "META", "NVDA", "AMZN"]
    # news = integration.fetch_news(tickers=tmt_tickers, topics=["technology"], limit=50)
    # print(f"Fetched {len(news)} news articles")
    # synced = integration.sync_to_database(news)
    # print(f"Synced {synced} records to database")
    
    print("News API integration ready.")
    print("Set ALPHA_VANTAGE_KEY, MARKETAUX_KEY, or STOCK_NEWS_KEY environment variable to use.")
