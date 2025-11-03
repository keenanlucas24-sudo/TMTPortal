"""
Twitter/X scraping integration using twscrape
Fetches tweets from financial news accounts without API
"""
import asyncio
import os
from datetime import datetime, timezone
from typing import List, Dict, Optional
from twscrape import API, gather
from twscrape.models import Tweet

# Financial Twitter accounts to monitor
FINANCIAL_ACCOUNTS = [
    "Bloomberg",
    "Reuters",
    "CNBC",
    "SeekingAlpha",
    "WSJ",
    "FT",
    "theinformation",
    "faststocknews",
    "mingchikuo",
    "ivanaspear",
    "rihardjarc",
    "semianalysis_",
    "wallstengine",
    "stockmktnewz",
    "zephyr_z9",
    "ap",
    "aistocksavvy",
    "trendspider"
]


class TwitterScraperService:
    """Service for scraping tweets from financial news accounts"""
    
    def __init__(self):
        self.api = API()
        self._initialized = False
    
    async def initialize(self):
        """
        Initialize the Twitter scraper
        
        NOTE: This requires Twitter account credentials to be added via:
        await api.pool.add_account("username", "password", "email", "email_password")
        
        For security, accounts should be added once via a setup script, not in code.
        """
        if self._initialized:
            return
        
        # Check if any accounts are logged in
        accounts = await self.api.pool.accounts_info()
        if not accounts:
            print("WARNING: No Twitter accounts configured for scraping.")
            print("To add accounts, run: python integrations/setup_twitter_accounts.py")
            print("Or use the Twitter account management interface")
            return
        
        # Login all accounts
        await self.api.pool.login_all()
        self._initialized = True
    
    async def fetch_user_tweets(self, username: str, limit: int = 20) -> List[Dict]:
        """
        Fetch recent tweets from a specific user
        
        Args:
            username: Twitter username (without @)
            limit: Number of tweets to fetch
        
        Returns:
            List of tweet dictionaries
        """
        await self.initialize()
        
        if not self._initialized:
            return []
        
        try:
            tweets = []
            async for tweet in self.api.user_tweets(username, limit=limit):
                tweets.append(self._format_tweet(tweet, username))
            return tweets
        except Exception as e:
            print(f"Error fetching tweets from @{username}: {e}")
            return []
    
    async def fetch_all_financial_tweets(self, limit_per_account: int = 10) -> List[Dict]:
        """
        Fetch recent tweets from all financial news accounts
        
        Args:
            limit_per_account: Number of tweets to fetch per account
        
        Returns:
            List of tweet dictionaries from all accounts
        """
        all_tweets = []
        
        for account in FINANCIAL_ACCOUNTS:
            tweets = await self.fetch_user_tweets(account, limit=limit_per_account)
            all_tweets.extend(tweets)
        
        # Sort by timestamp, newest first
        all_tweets.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return all_tweets
    
    def _format_tweet(self, tweet: Tweet, username: str) -> Dict:
        """
        Format tweet object into standardized dictionary
        
        Args:
            tweet: twscrape Tweet object
            username: Twitter username
        
        Returns:
            Dictionary with tweet data
        """
        # Convert tweet date to UTC datetime
        timestamp = tweet.date
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        
        return {
            'tweet_id': str(tweet.id),
            'author': f"@{username}",
            'timestamp': timestamp,
            'text': tweet.rawContent or "",
            'likes': tweet.likeCount or 0,
            'retweets': tweet.retweetCount or 0,
            'permalink': tweet.url or f"https://twitter.com/{username}/status/{tweet.id}"
        }


# Synchronous wrapper functions for easy integration
def fetch_financial_tweets_sync(limit_per_account: int = 10) -> List[Dict]:
    """
    Synchronous wrapper to fetch tweets from all financial accounts
    
    Args:
        limit_per_account: Number of tweets per account
    
    Returns:
        List of tweet dictionaries
    """
    scraper = TwitterScraperService()
    return asyncio.run(scraper.fetch_all_financial_tweets(limit_per_account))


def fetch_user_tweets_sync(username: str, limit: int = 20) -> List[Dict]:
    """
    Synchronous wrapper to fetch tweets from a specific user
    
    Args:
        username: Twitter username (without @)
        limit: Number of tweets to fetch
    
    Returns:
        List of tweet dictionaries
    """
    scraper = TwitterScraperService()
    return asyncio.run(scraper.fetch_user_tweets(username, limit))
