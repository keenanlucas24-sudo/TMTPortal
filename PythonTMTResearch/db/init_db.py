import psycopg2
import os
from datetime import datetime

def get_db_connection():
    """Get a connection to the PostgreSQL database"""
    return psycopg2.connect(os.environ['DATABASE_URL'])

def init_database():
    """Initialize the database schema and tables"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Create companies table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                ticker VARCHAR(10) NOT NULL UNIQUE,
                sector VARCHAR(50) NOT NULL,
                sub_sector VARCHAR(100),
                market_cap VARCHAR(50),
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create news table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS news (
                id SERIAL PRIMARY KEY,
                date TIMESTAMP NOT NULL,
                sector VARCHAR(50) NOT NULL,
                company VARCHAR(255) NOT NULL,
                headline TEXT NOT NULL,
                summary TEXT,
                source VARCHAR(255),
                url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create earnings table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS earnings (
                id SERIAL PRIMARY KEY,
                company VARCHAR(255) NOT NULL,
                ticker VARCHAR(10) NOT NULL,
                sector VARCHAR(50) NOT NULL,
                date TIMESTAMP NOT NULL,
                quarter VARCHAR(20) NOT NULL,
                consensus_eps VARCHAR(20),
                actual_eps VARCHAR(20),
                consensus_revenue VARCHAR(20),
                actual_revenue VARCHAR(20),
                status VARCHAR(20) NOT NULL,
                beat_miss VARCHAR(20),
                key_analyst_focus TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create roundtables table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS roundtables (
                id SERIAL PRIMARY KEY,
                date TIMESTAMP NOT NULL,
                executive VARCHAR(255) NOT NULL,
                company_background VARCHAR(255) NOT NULL,
                sector VARCHAR(50) NOT NULL,
                topics TEXT[],
                key_insights TEXT,
                attendees INTEGER,
                client_firms TEXT[],
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create roundtable documents table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS roundtable_documents (
                id SERIAL PRIMARY KEY,
                roundtable_id INTEGER REFERENCES roundtables(id) ON DELETE CASCADE,
                filename VARCHAR(255) NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create tags table for advanced filtering
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                category VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create roundtable_tags junction table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS roundtable_tags (
                roundtable_id INTEGER REFERENCES roundtables(id) ON DELETE CASCADE,
                tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
                PRIMARY KEY (roundtable_id, tag_id)
            );
        """)
        
        # Create tweets table for social media news
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tweets (
                id SERIAL PRIMARY KEY,
                tweet_id VARCHAR(50) UNIQUE NOT NULL,
                author VARCHAR(100) NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                text TEXT NOT NULL,
                likes INTEGER DEFAULT 0,
                retweets INTEGER DEFAULT 0,
                permalink TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create tweet_analysis table for Gemini AI analysis results
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tweet_analysis (
                id SERIAL PRIMARY KEY,
                tweet_id INTEGER REFERENCES tweets(id) ON DELETE CASCADE,
                tickers TEXT[],
                sentiment VARCHAR(20),
                sentiment_score FLOAT,
                relevance_score FLOAT,
                is_relevant BOOLEAN DEFAULT TRUE,
                headline TEXT,
                summary TEXT,
                analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(tweet_id)
            );
        """)
        
        # Create indexes for better query performance
        cur.execute("CREATE INDEX IF NOT EXISTS idx_companies_sector ON companies(sector);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_companies_sub_sector ON companies(sub_sector);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_news_date ON news(date DESC);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_news_sector ON news(sector);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_earnings_date ON earnings(date);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_earnings_status ON earnings(status);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_roundtables_date ON roundtables(date DESC);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_roundtables_sector ON roundtables(sector);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_tweets_timestamp ON tweets(timestamp DESC);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_tweets_author ON tweets(author);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_tweet_analysis_relevance ON tweet_analysis(is_relevant);")
        
        conn.commit()
        print("Database schema created successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"Error creating database schema: {e}")
        raise
    finally:
        cur.close()
        conn.close()

def seed_database():
    """Seed the database with initial news, earnings, and roundtable data
    
    Note: Companies should be seeded using db/seed_comprehensive_companies.py
    """
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from data.tmt_data import NEWS_DATA, EARNINGS_DATA, ROUNDTABLE_DATA
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Check if data already exists
        cur.execute("SELECT COUNT(*) FROM news")
        if cur.fetchone()[0] > 0:
            print("Database already seeded. Skipping...")
            return
        
        # Skip companies - use db/seed_comprehensive_companies.py instead
        print("Skipping company seed (use db/seed_comprehensive_companies.py for companies)")
        
        # Insert news
        for news in NEWS_DATA:
            cur.execute("""
                INSERT INTO news (date, sector, company, headline, summary, source)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (news['date'], news['sector'], news['company'], news['headline'], news['summary'], news['source']))
        
        # Insert earnings
        for earning in EARNINGS_DATA:
            cur.execute("""
                INSERT INTO earnings (company, ticker, sector, date, quarter, consensus_eps, 
                                     actual_eps, consensus_revenue, actual_revenue, status, beat_miss)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                earning['company'], earning['ticker'], earning['sector'], earning['date'],
                earning['quarter'], earning.get('consensus_eps'), earning.get('actual_eps'),
                earning.get('consensus_revenue'), earning.get('actual_revenue'),
                earning['status'], earning.get('beat_miss')
            ))
        
        # Insert roundtables
        for roundtable in ROUNDTABLE_DATA:
            cur.execute("""
                INSERT INTO roundtables (date, executive, company_background, sector, topics, 
                                        key_insights, attendees, client_firms)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                roundtable['date'], roundtable['executive'], roundtable['company_background'],
                roundtable['sector'], roundtable['topics'], roundtable['key_insights'],
                roundtable['attendees'], roundtable['client_firms']
            ))
        
        conn.commit()
        print(f"Database seeded with {len(NEWS_DATA)} news items, "
              f"{len(EARNINGS_DATA)} earnings records, and {len(ROUNDTABLE_DATA)} roundtable sessions!")
        print("For companies, run: python db/seed_comprehensive_companies.py")
        
    except Exception as e:
        conn.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    init_database()
    seed_database()
