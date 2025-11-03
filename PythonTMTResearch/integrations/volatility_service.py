"""
Volatility Service
Background service to fetch and cache stock prices for all TMT tickers
Stores results in database for instant dashboard access
"""
import os
import psycopg2
from typing import List, Dict
from datetime import datetime, timedelta
import time
from integrations.stock_prices import get_batch_quotes


def init_volatility_table():
    """Create stock_prices table if it doesn't exist"""
    conn = _get_db_conn()
    if conn is None:
        # Database not configured; nothing to initialize
        return
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock_prices (
            ticker VARCHAR(10) PRIMARY KEY,
            price DECIMAL(10, 2),
            change DECIMAL(10, 2),
            change_percent DECIMAL(10, 2),
            volume BIGINT,
            previous_close DECIMAL(10, 2),
            source VARCHAR(50),
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()


def store_quotes(quotes: List[Dict]):
    """Store stock quotes in database"""
    if not quotes:
        return
    conn = _get_db_conn()
    if conn is None:
        # No DB configured; skip storing
        return
    cur = conn.cursor()
    
    for quote in quotes:
        cur.execute("""
            INSERT INTO stock_prices (ticker, price, change, change_percent, volume, previous_close, source, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (ticker)
            DO UPDATE SET
                price = EXCLUDED.price,
                change = EXCLUDED.change,
                change_percent = EXCLUDED.change_percent,
                volume = EXCLUDED.volume,
                previous_close = EXCLUDED.previous_close,
                source = EXCLUDED.source,
                updated_at = EXCLUDED.updated_at
        """, (
            quote['ticker'],
            quote['price'],
            quote['change'],
            quote['change_percent'],
            quote.get('volume', 0),
            quote.get('previous_close', 0),
            quote['source'],
            datetime.now()
        ))
    
    conn.commit()
    cur.close()
    conn.close()


def get_cached_quotes(max_age_minutes: int = 15) -> List[Dict]:
    """Get cached quotes from database"""
    conn = _get_db_conn()
    if conn is None:
        return []
    cur = conn.cursor()
    cutoff_time = datetime.now() - timedelta(minutes=max_age_minutes)
    
    cur.execute("""
        SELECT ticker, price, change, change_percent, volume, previous_close, source, updated_at
        FROM stock_prices
        WHERE updated_at > %s
        ORDER BY ticker
    """, (cutoff_time,))
    
    quotes = []
    for row in cur.fetchall():
        quotes.append({
            'ticker': row[0],
            'price': float(row[1]),
            'change': float(row[2]),
            'change_percent': float(row[3]),
            'volume': int(row[4]),
            'previous_close': float(row[5]),
            'source': row[6],
            'timestamp': row[7].strftime("%Y-%m-%d")
        })
    
    cur.close()
    conn.close()
    
    return quotes


def refresh_all_tickers(tickers: List[str], chunk_size: int = 58):
    """
    Refresh all tickers in chunks with proper rate limiting
    
    Args:
        tickers: List of all tickers to refresh
        chunk_size: Number of tickers per chunk (default 58 for 60/min limit)
    """
    init_volatility_table()
    
    total_chunks = (len(tickers) + chunk_size - 1) // chunk_size
    
    for i in range(0, len(tickers), chunk_size):
        chunk = tickers[i:i + chunk_size]
        chunk_num = (i // chunk_size) + 1
        
        print(f"Fetching chunk {chunk_num}/{total_chunks} ({len(chunk)} tickers)...")
        
        # Fetch quotes for this chunk
        quotes = get_batch_quotes(chunk, delay=1.05, max_tickers=chunk_size)
        
        # Store in database
        if quotes:
            store_quotes(quotes)
            print(f"Stored {len(quotes)} quotes from chunk {chunk_num}")
        
        # Wait 60 seconds before next chunk (rate limit window)
        if chunk_num < total_chunks:
            print(f"Waiting 60 seconds before next chunk...")
            time.sleep(60)


def get_volatile_stocks_from_db(threshold: float = 2.0, max_age_minutes: int = 15) -> Dict:
    """
    Get volatile stocks from database cache
    
    Args:
        threshold: Minimum percentage change
        max_age_minutes: Maximum age of cached data
    
    Returns:
        Dict with gainers, losers, total_checked, volatile_count, cache_age
    """
    # Get quotes with actual updated_at timestamp
    conn = _get_db_conn()
    if conn is None:
        return {
            "gainers": [],
            "losers": [],
            "total_checked": 0,
            "volatile_count": 0,
            "cache_age": "No DB configured",
            "latest_update": None
        }
    cur = conn.cursor()
    
    cutoff_time = datetime.now() - timedelta(minutes=max_age_minutes)
    
    cur.execute("""
        SELECT ticker, price, change, change_percent, volume, previous_close, source, updated_at
        FROM stock_prices
        WHERE updated_at > %s
        ORDER BY ticker
    """, (cutoff_time,))
    
    quotes = []
    latest_update = None
    
    for row in cur.fetchall():
        updated_at = row[7]
        if latest_update is None or updated_at > latest_update:
            latest_update = updated_at
            
        quotes.append({
            'ticker': row[0],
            'price': float(row[1]),
            'change': float(row[2]),
            'change_percent': float(row[3]),
            'volume': int(row[4]),
            'previous_close': float(row[5]),
            'source': row[6],
            'updated_at': updated_at
        })
    
    cur.close()
    conn.close()
    
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
    
    # Calculate actual cache age
    if latest_update:
        age_minutes = int((datetime.now() - latest_update).total_seconds() / 60)
        if age_minutes < 60:
            cache_age = f"{age_minutes} min ago"
        else:
            hours = age_minutes // 60
            cache_age = f"{hours}h {age_minutes % 60}m ago"
    else:
        cache_age = "No data"
    
    return {
        "gainers": gainers,
        "losers": losers,
        "total_checked": len(quotes),
        "volatile_count": len(gainers) + len(losers),
        "cache_age": cache_age,
        "latest_update": latest_update
    }


if __name__ == "__main__":
    # Manual refresh script
    from data.tmt_data import get_all_companies
    
    companies = get_all_companies()
    tickers = [c['ticker'] for c in companies if c.get('ticker')]
    
    print(f"Starting refresh of {len(tickers)} tickers...")
    refresh_all_tickers(tickers)
    print("Refresh complete!")


def _get_db_conn():
    """Return a psycopg2 connection or None if DATABASE_URL not configured or connection fails."""
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        return None
    try:
        return psycopg2.connect(db_url)
    except Exception:
        return None
