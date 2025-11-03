"""
Social News Service - Orchestrates Twitter scraping and Gemini analysis
Fetches tweets, analyzes them with Gemini, and stores in database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict
from integrations.twitter_scraper import fetch_financial_tweets_sync
from integrations.gemini_analysis import analyze_tweet
from db.db_operations import (
    add_tweet, 
    add_tweet_analysis, 
    check_tweet_analyzed,
    get_social_news
)


def fetch_and_analyze_tweets(limit_per_account: int = 10) -> Dict[str, int]:
    """
    Fetch tweets from financial accounts and analyze with Gemini
    
    Args:
        limit_per_account: Number of tweets to fetch per Twitter account
    
    Returns:
        Dictionary with statistics: fetched, new, analyzed, relevant
    """
    stats = {
        'fetched': 0,
        'new': 0,
        'analyzed': 0,
        'relevant': 0,
        'errors': 0
    }
    
    try:
        # Fetch tweets from all financial accounts
        print("Fetching tweets from financial accounts...")
        tweets = fetch_financial_tweets_sync(limit_per_account)
        stats['fetched'] = len(tweets)
        print(f"Fetched {stats['fetched']} tweets")
        
        if not tweets:
            print("No tweets fetched. Check Twitter account setup.")
            return stats
        
        # Process each tweet
        for tweet in tweets:
            try:
                tweet_id = tweet['tweet_id']
                
                # Check if already analyzed (cache)
                if check_tweet_analyzed(tweet_id):
                    continue
                
                # Add tweet to database
                db_tweet_id = add_tweet(
                    tweet_id=tweet_id,
                    author=tweet['author'],
                    timestamp=tweet['timestamp'],
                    text=tweet['text'],
                    likes=tweet['likes'],
                    retweets=tweet['retweets'],
                    permalink=tweet['permalink']
                )
                
                if not db_tweet_id:
                    stats['errors'] += 1
                    continue
                
                stats['new'] += 1
                
                # Analyze with Gemini
                print(f"Analyzing tweet from {tweet['author']}...")
                analysis = analyze_tweet(tweet['text'], tweet['author'])
                
                if not analysis:
                    # Not relevant - still store analysis with is_relevant=False
                    add_tweet_analysis(
                        tweet_db_id=db_tweet_id,
                        tickers=[],
                        sentiment="neutral",
                        sentiment_score=0.0,
                        relevance_score=0.0,
                        is_relevant=False,
                        headline="",
                        summary=""
                    )
                    stats['analyzed'] += 1
                    continue
                
                # Store analysis
                success = add_tweet_analysis(
                    tweet_db_id=db_tweet_id,
                    tickers=analysis['tickers'],
                    sentiment=analysis['sentiment'],
                    sentiment_score=analysis['sentiment_score'],
                    relevance_score=analysis['relevance_score'],
                    is_relevant=analysis['is_relevant'],
                    headline=analysis['headline'],
                    summary=analysis['summary']
                )
                
                if success:
                    stats['analyzed'] += 1
                    if analysis['is_relevant']:
                        stats['relevant'] += 1
                        print(f"✓ Relevant: {analysis['headline']}")
                else:
                    stats['errors'] += 1
                    
            except Exception as e:
                print(f"Error processing tweet {tweet.get('tweet_id', 'unknown')}: {e}")
                stats['errors'] += 1
        
        print(f"\nStats: {stats['fetched']} fetched, {stats['new']} new, "
              f"{stats['analyzed']} analyzed, {stats['relevant']} relevant")
        
    except Exception as e:
        print(f"Error in fetch_and_analyze_tweets: {e}")
        stats['errors'] += 1
    
    return stats


def get_social_news_feed(limit: int = 50, author_filter: str = None) -> List[Dict]:
    """
    Get the social news feed (analyzed tweets)
    
    Args:
        limit: Maximum number of items to return
        author_filter: Filter by author (e.g., "@Bloomberg")
    
    Returns:
        List of social news items
    """
    return get_social_news(limit=limit, author_filter=author_filter)


if __name__ == "__main__":
    # Run manual fetch and analysis
    print("Starting social news fetch and analysis...")
    stats = fetch_and_analyze_tweets(limit_per_account=10)
    print(f"\nCompleted! Stats: {stats}")
