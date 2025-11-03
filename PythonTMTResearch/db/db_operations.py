"""
Database operations for TMT Research Portal
Provides functions to query and manipulate data in PostgreSQL
"""
import psycopg2
import psycopg2.extras
import os
from datetime import datetime
from typing import List, Dict, Optional

def get_db_connection():
    """Get a connection to the PostgreSQL database"""
    return psycopg2.connect(os.environ['DATABASE_URL'])

def get_all_companies() -> List[Dict]:
    """Get all companies from database"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cur.execute("""
            SELECT name, ticker, sector, sub_sector, market_cap, description 
            FROM companies 
            ORDER BY sector, sub_sector, name
        """)
        companies = cur.fetchall()
        return [dict(c) for c in companies]
    finally:
        cur.close()
        conn.close()

def get_companies_by_sector(sector: str) -> List[Dict]:
    """Get companies filtered by sector"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cur.execute("""
            SELECT name, ticker, sector, sub_sector, market_cap, description 
            FROM companies 
            WHERE sector = %s
            ORDER BY sub_sector, name
        """, (sector,))
        companies = cur.fetchall()
        return [dict(c) for c in companies]
    finally:
        cur.close()
        conn.close()

def get_companies_by_sub_sector(sub_sector: str) -> List[Dict]:
    """Get companies filtered by sub-sector"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cur.execute("""
            SELECT name, ticker, sector, sub_sector, market_cap, description 
            FROM companies 
            WHERE sub_sector = %s
            ORDER BY name
        """, (sub_sector,))
        companies = cur.fetchall()
        return [dict(c) for c in companies]
    finally:
        cur.close()
        conn.close()

def get_all_sub_sectors() -> List[str]:
    """Get all unique sub-sectors from database"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT DISTINCT sub_sector 
            FROM companies 
            WHERE sub_sector IS NOT NULL
            ORDER BY sub_sector
        """)
        sub_sectors = [row[0] for row in cur.fetchall()]
        return sub_sectors
    finally:
        cur.close()
        conn.close()

def get_sub_sectors_by_sector(sector: str) -> List[str]:
    """Get sub-sectors for a specific sector"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT DISTINCT sub_sector 
            FROM companies 
            WHERE sector = %s AND sub_sector IS NOT NULL
            ORDER BY sub_sector
        """, (sector,))
        sub_sectors = [row[0] for row in cur.fetchall()]
        return sub_sectors
    finally:
        cur.close()
        conn.close()

def get_news_feed(sector_filter: Optional[str] = None, company_filter: Optional[str] = None) -> List[Dict]:
    """Get news feed with optional filters"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        query = "SELECT * FROM news WHERE 1=1"
        params = []
        
        if sector_filter:
            query += " AND sector = %s"
            params.append(sector_filter)
        
        if company_filter:
            query += " AND company = %s"
            params.append(company_filter)
        
        query += " ORDER BY date DESC"
        
        cur.execute(query, params)
        news = cur.fetchall()
        return [dict(n) for n in news]
    finally:
        cur.close()
        conn.close()

def get_earnings_calendar(status_filter: Optional[str] = None) -> List[Dict]:
    """Get earnings calendar with optional status filter"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        if status_filter:
            cur.execute("""
                SELECT * FROM earnings 
                WHERE status = %s
                ORDER BY date
            """, (status_filter,))
        else:
            cur.execute("SELECT * FROM earnings ORDER BY date")
        
        earnings = cur.fetchall()
        return [dict(e) for e in earnings]
    finally:
        cur.close()
        conn.close()

def get_roundtable_insights(sector_filter: Optional[str] = None, tag_filter: Optional[str] = None) -> List[Dict]:
    """Get roundtable insights with optional filters"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        if tag_filter:
            # Filter by tag
            cur.execute("""
                SELECT DISTINCT r.* FROM roundtables r
                JOIN roundtable_tags rt ON r.id = rt.roundtable_id
                JOIN tags t ON rt.tag_id = t.id
                WHERE t.name = %s
                ORDER BY r.date DESC
            """, (tag_filter,))
        elif sector_filter:
            cur.execute("""
                SELECT * FROM roundtables 
                WHERE sector = %s
                ORDER BY date DESC
            """, (sector_filter,))
        else:
            cur.execute("SELECT * FROM roundtables ORDER BY date DESC")
        
        roundtables = cur.fetchall()
        return [dict(r) for r in roundtables]
    finally:
        cur.close()
        conn.close()

def search_all_data(query: str) -> Dict[str, List]:
    """Search across all data types"""
    query_lower = query.lower()
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    results = {
        "companies": [],
        "news": [],
        "earnings": [],
        "roundtables": []
    }
    
    try:
        # Search companies
        cur.execute("""
            SELECT name, ticker, sector, sub_sector, market_cap, description 
            FROM companies 
            WHERE LOWER(name) LIKE %s 
               OR LOWER(ticker) LIKE %s 
               OR LOWER(description) LIKE %s
               OR LOWER(COALESCE(sub_sector, '')) LIKE %s
        """, (f'%{query_lower}%', f'%{query_lower}%', f'%{query_lower}%', f'%{query_lower}%'))
        results["companies"] = [dict(c) for c in cur.fetchall()]
        
        # Search news
        cur.execute("""
            SELECT * FROM news 
            WHERE LOWER(headline) LIKE %s 
               OR LOWER(summary) LIKE %s 
               OR LOWER(company) LIKE %s
            ORDER BY date DESC
        """, (f'%{query_lower}%', f'%{query_lower}%', f'%{query_lower}%'))
        results["news"] = [dict(n) for n in cur.fetchall()]
        
        # Search earnings
        cur.execute("""
            SELECT * FROM earnings 
            WHERE LOWER(company) LIKE %s 
               OR LOWER(ticker) LIKE %s
            ORDER BY date DESC
        """, (f'%{query_lower}%', f'%{query_lower}%'))
        results["earnings"] = [dict(e) for e in cur.fetchall()]
        
        # Search roundtables
        cur.execute("""
            SELECT * FROM roundtables 
            WHERE LOWER(executive) LIKE %s 
               OR LOWER(company_background) LIKE %s 
               OR LOWER(key_insights) LIKE %s
            ORDER BY date DESC
        """, (f'%{query_lower}%', f'%{query_lower}%', f'%{query_lower}%'))
        results["roundtables"] = [dict(r) for r in cur.fetchall()]
        
        return results
    finally:
        cur.close()
        conn.close()

def add_news_item(date: datetime, sector: str, company: str, headline: str, 
                  summary: str, source: str, url: Optional[str] = None) -> int:
    """Add a new news item to the database (skips if URL already exists)"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Check if URL already exists to prevent duplicates
        if url:
            cur.execute("SELECT id FROM news WHERE url = %s", (url,))
            existing = cur.fetchone()
            if existing:
                return existing[0]  # Return existing ID, don't insert duplicate
        
        cur.execute("""
            INSERT INTO news (date, sector, company, headline, summary, source, url)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (date, sector, company, headline, summary, source, url))
        news_id = cur.fetchone()[0]
        conn.commit()
        return news_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def add_earnings_data(company: str, ticker: str, sector: str, date: datetime,
                      quarter: str, consensus_eps: str, consensus_revenue: str,
                      actual_eps: Optional[str] = None, actual_revenue: Optional[str] = None,
                      status: str = "Upcoming", beat_miss: Optional[str] = None,
                      key_analyst_focus: Optional[str] = None) -> int:
    """Add earnings data to the database"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO earnings (company, ticker, sector, date, quarter, consensus_eps, 
                                 consensus_revenue, actual_eps, actual_revenue, status, beat_miss, key_analyst_focus)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (company, ticker, sector, date, quarter, consensus_eps, consensus_revenue,
              actual_eps, actual_revenue, status, beat_miss, key_analyst_focus))
        earnings_id = cur.fetchone()[0]
        conn.commit()
        return earnings_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

# Alias for backwards compatibility
add_earnings_item = add_earnings_data

def add_roundtable(date: datetime, executive: str, company_background: str, sector: str,
                   topics: List[str], key_insights: str, attendees: int, 
                   client_firms: List[str]) -> int:
    """Add a roundtable insight to the database"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO roundtables (date, executive, company_background, sector, topics,
                                    key_insights, attendees, client_firms)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (date, executive, company_background, sector, topics, key_insights, attendees, client_firms))
        roundtable_id = cur.fetchone()[0]
        conn.commit()
        return roundtable_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def add_roundtable_document(roundtable_id: int, filename: str, file_path: str, file_size: int) -> int:
    """Add a document to a roundtable"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO roundtable_documents (roundtable_id, filename, file_path, file_size)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (roundtable_id, filename, file_path, file_size))
        doc_id = cur.fetchone()[0]
        conn.commit()
        return doc_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def get_roundtable_documents(roundtable_id: int) -> List[Dict]:
    """Get all documents for a roundtable"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cur.execute("""
            SELECT * FROM roundtable_documents 
            WHERE roundtable_id = %s
            ORDER BY uploaded_at DESC
        """, (roundtable_id,))
        docs = cur.fetchall()
        return [dict(d) for d in docs]
    finally:
        cur.close()
        conn.close()

def get_all_tags() -> List[Dict]:
    """Get all tags"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cur.execute("SELECT * FROM tags ORDER BY name")
        tags = cur.fetchall()
        return [dict(t) for t in tags]
    finally:
        cur.close()
        conn.close()

def add_tag(name: str, category: Optional[str] = None) -> int:
    """Add a new tag"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO tags (name, category)
            VALUES (%s, %s)
            ON CONFLICT (name) DO NOTHING
            RETURNING id
        """, (name, category))
        result = cur.fetchone()
        tag_id = result[0] if result else None
        
        # If tag already exists, get its ID
        if not tag_id:
            cur.execute("SELECT id FROM tags WHERE name = %s", (name,))
            tag_id = cur.fetchone()[0]
        
        conn.commit()
        return tag_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def add_tag_to_roundtable(roundtable_id: int, tag_id: int):
    """Associate a tag with a roundtable"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO roundtable_tags (roundtable_id, tag_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """, (roundtable_id, tag_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def get_roundtable_tags(roundtable_id: int) -> List[Dict]:
    """Get all tags for a roundtable"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cur.execute("""
            SELECT t.* FROM tags t
            JOIN roundtable_tags rt ON t.id = rt.tag_id
            WHERE rt.roundtable_id = %s
            ORDER BY t.name
        """, (roundtable_id,))
        tags = cur.fetchall()
        return [dict(t) for t in tags]
    finally:
        cur.close()
        conn.close()

# Tweet and Social News Operations

def add_tweet(tweet_id: str, author: str, timestamp: datetime, text: str, 
              likes: int = 0, retweets: int = 0, permalink: str = "") -> Optional[int]:
    """
    Add a new tweet to database
    
    Returns:
        Tweet ID if new, or existing tweet ID if duplicate
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Check if tweet already exists by tweet_id
        cur.execute("SELECT id FROM tweets WHERE tweet_id = %s", (tweet_id,))
        existing = cur.fetchone()
        
        if existing:
            return existing[0]
        
        # Insert new tweet
        cur.execute("""
            INSERT INTO tweets (tweet_id, author, timestamp, text, likes, retweets, permalink)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (tweet_id, author, timestamp, text, likes, retweets, permalink))
        
        new_id = cur.fetchone()[0]
        conn.commit()
        return new_id
        
    except Exception as e:
        conn.rollback()
        print(f"Error adding tweet: {e}")
        return None
    finally:
        cur.close()
        conn.close()

def add_tweet_analysis(tweet_db_id: int, tickers: List[str], sentiment: str, 
                      sentiment_score: float, relevance_score: float, 
                      is_relevant: bool, headline: str, summary: str) -> bool:
    """
    Add Gemini analysis results for a tweet
    
    Returns:
        True if successful, False otherwise
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO tweet_analysis 
            (tweet_id, tickers, sentiment, sentiment_score, relevance_score, 
             is_relevant, headline, summary)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (tweet_id) DO UPDATE SET
                tickers = EXCLUDED.tickers,
                sentiment = EXCLUDED.sentiment,
                sentiment_score = EXCLUDED.sentiment_score,
                relevance_score = EXCLUDED.relevance_score,
                is_relevant = EXCLUDED.is_relevant,
                headline = EXCLUDED.headline,
                summary = EXCLUDED.summary,
                analyzed_at = CURRENT_TIMESTAMP
        """, (tweet_db_id, tickers, sentiment, sentiment_score, relevance_score, 
              is_relevant, headline, summary))
        
        conn.commit()
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"Error adding tweet analysis: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def get_social_news(limit: int = 50, author_filter: Optional[str] = None) -> List[Dict]:
    """
    Get analyzed tweets (social news feed)
    
    Args:
        limit: Maximum number of tweets to return
        author_filter: Filter by author (e.g., "@Bloomberg")
    
    Returns:
        List of tweets with analysis data
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        query = """
            SELECT 
                t.id,
                t.tweet_id,
                t.author,
                t.timestamp,
                t.text,
                t.likes,
                t.retweets,
                t.permalink,
                ta.tickers,
                ta.sentiment,
                ta.sentiment_score,
                ta.relevance_score,
                ta.headline,
                ta.summary
            FROM tweets t
            JOIN tweet_analysis ta ON t.id = ta.tweet_id
            WHERE ta.is_relevant = TRUE
        """
        params = []
        
        if author_filter:
            query += " AND t.author = %s"
            params.append(author_filter)
        
        query += " ORDER BY t.timestamp DESC LIMIT %s"
        params.append(limit)
        
        cur.execute(query, params)
        tweets = cur.fetchall()
        return [dict(tweet) for tweet in tweets]
        
    finally:
        cur.close()
        conn.close()

def check_tweet_analyzed(tweet_id: str) -> bool:
    """
    Check if a tweet has already been analyzed
    
    Args:
        tweet_id: The Twitter tweet ID
    
    Returns:
        True if analyzed, False otherwise
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT EXISTS(
                SELECT 1 FROM tweets t
                JOIN tweet_analysis ta ON t.id = ta.tweet_id
                WHERE t.tweet_id = %s
            )
        """, (tweet_id,))
        return cur.fetchone()[0]
    finally:
        cur.close()
        conn.close()
