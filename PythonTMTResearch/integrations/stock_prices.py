"""
Stock Price API Integration
Fetches real-time stock quotes and calculates percentage changes
Uses Alpha Vantage and Finnhub APIs
"""
import os
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import time


def get_stock_quote_alphavantage(ticker: str) -> Optional[Dict]:
    """
    Get real-time stock quote from Alpha Vantage
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')
    
    Returns:
        Dict with price, change, change_percent, or None if error
    """
    api_key = os.environ.get("ALPHA_VANTAGE_KEY")
    if not api_key:
        return None
    
    try:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={api_key}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if "Global Quote" in data and data["Global Quote"]:
            quote = data["Global Quote"]
            return {
                "ticker": ticker,
                "price": float(quote.get("05. price", 0)),
                "change": float(quote.get("09. change", 0)),
                "change_percent": float(quote.get("10. change percent", "0").replace("%", "")),
                "volume": int(quote.get("06. volume", 0)),
                "previous_close": float(quote.get("08. previous close", 0)),
                "timestamp": quote.get("07. latest trading day"),
                "source": "Alpha Vantage"
            }
        
        return None
        
    except Exception as e:
        print(f"Error fetching quote for {ticker} from Alpha Vantage: {e}")
        return None


def get_stock_quote_finnhub(ticker: str) -> Optional[Dict]:
    """
    Get real-time stock quote from Finnhub
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')
    
    Returns:
        Dict with price, change, change_percent, or None if error
    """
    api_key = os.environ.get("FINNHUB_API_KEY")
    if not api_key:
        return None
    
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={api_key}"
        response = requests.get(url, timeout=10)
        
        # Handle rate limiting explicitly
        if response.status_code == 429:
            print(f"Rate limit hit for {ticker} from Finnhub, skipping...")
            return None
        
        response.raise_for_status()
        
        data = response.json()
        
        if data and data.get("c"):  # Current price exists
            current = data.get("c", 0)
            previous = data.get("pc", 0)
            change = current - previous
            change_percent = (change / previous * 100) if previous > 0 else 0
            
            return {
                "ticker": ticker,
                "price": current,
                "change": change,
                "change_percent": change_percent,
                "volume": data.get("v", 0),
                "previous_close": previous,
                "high": data.get("h", 0),
                "low": data.get("l", 0),
                "timestamp": datetime.fromtimestamp(data.get("t", 0)).strftime("%Y-%m-%d"),
                "source": "Finnhub"
            }
        
        return None
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            print(f"Rate limit hit for {ticker} from Finnhub, skipping...")
        else:
            print(f"HTTP error fetching quote for {ticker} from Finnhub: {e}")
        return None
    except Exception as e:
        print(f"Error fetching quote for {ticker} from Finnhub: {e}")
        return None


def get_stock_quote(ticker: str, preferred_source: str = "finnhub") -> Optional[Dict]:
    """
    Get stock quote with fallback between sources
    
    Args:
        ticker: Stock ticker symbol
        preferred_source: 'finnhub' or 'alphavantage'
    
    Returns:
        Stock quote data or None
    """
    if preferred_source == "finnhub":
        quote = get_stock_quote_finnhub(ticker)
        if quote:
            return quote
        # Fallback to Alpha Vantage
        return get_stock_quote_alphavantage(ticker)
    else:
        quote = get_stock_quote_alphavantage(ticker)
        if quote:
            return quote
        # Fallback to Finnhub
        return get_stock_quote_finnhub(ticker)


def get_batch_quotes(tickers: List[str], delay: float = 1.1, max_tickers: int = 50) -> List[Dict]:
    """
    Get quotes for multiple tickers with rate limiting
    
    Args:
        tickers: List of ticker symbols
        delay: Delay between requests in seconds (default 1.1 for Finnhub 60/min limit)
        max_tickers: Maximum number of tickers to fetch (default 50 to stay within limits)
    
    Returns:
        List of quote dictionaries
    """
    quotes = []
    
    # Limit tickers to avoid rate limits
    limited_tickers = tickers[:max_tickers]
    
    for ticker in limited_tickers:
        quote = get_stock_quote(ticker, preferred_source="finnhub")
        if quote:
            quotes.append(quote)
        
        # Rate limiting - 1.1 seconds = ~54 requests/minute (safely under 60/min)
        if delay > 0:
            time.sleep(delay)
    
    return quotes


def get_volatile_stocks(tickers: List[str], threshold: float = 2.0) -> Dict:
    """
    Find stocks with significant price movements
    
    Args:
        tickers: List of ticker symbols to check
        threshold: Minimum absolute percentage change (default 2.0%)
    
    Returns:
        Dict with 'gainers' (List), 'losers' (List), 'total_checked' (int), and 'volatile_count' (int)
    """
    quotes = get_batch_quotes(tickers)
    
    gainers = []
    losers = []
    
    for quote in quotes:
        change_pct = quote.get("change_percent", 0)
        
        if change_pct >= threshold:
            gainers.append(quote)
        elif change_pct <= -threshold:
            losers.append(quote)
    
    # Sort by absolute change percentage
    gainers.sort(key=lambda x: x["change_percent"], reverse=True)
    losers.sort(key=lambda x: x["change_percent"])
    
    return {
        "gainers": gainers,
        "losers": losers,
        "total_checked": len(quotes),
        "volatile_count": len(gainers) + len(losers)
    }


def format_price_change(change: float, change_percent: float) -> str:
    """
    Format price change with color indicators
    
    Args:
        change: Absolute price change
        change_percent: Percentage change
    
    Returns:
        Formatted string
    """
    sign = "+" if change >= 0 else ""
    return f"{sign}${change:.2f} ({sign}{change_percent:.2f}%)"
