"""
Gemini API integration for analyzing tweets
Extracts tickers, sentiment, and relevance for TMT financial news
"""
import json
import os
from typing import Dict, List, Optional

from google import genai
from google.genai import types
from pydantic import BaseModel

# IMPORTANT: KEEP THIS COMMENT
# Using blueprint:python_gemini integration
# The SDK was recently renamed from google-generativeai to google-genai

# Try to import streamlit for secrets management
# Falls back to environment variables if streamlit is not available
try:
    import streamlit as st
    # Use st.secrets if available, otherwise fall back to environment variable
    API_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))
except (ImportError, FileNotFoundError):
    # Streamlit not available or secrets.toml not found, use environment variable
    API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)


class TweetAnalysis(BaseModel):
    """Structured output for tweet analysis"""
    tickers: List[str]
    sentiment: str  # "positive", "negative", "neutral"
    sentiment_score: float  # -1.0 to 1.0
    relevance_score: float  # 0.0 to 1.0
    is_relevant: bool
    headline: str
    summary: str


def analyze_tweet(tweet_text: str, author: str) -> Optional[Dict]:
    """
    Analyze a tweet using Gemini API for financial relevance
    
    Args:
        tweet_text: The text content of the tweet
        author: The Twitter account author (e.g., @Bloomberg)
    
    Returns:
        Dictionary with analysis results or None if not relevant
    """
    try:
        system_prompt = """You are a financial news analyst specializing in Technology, Media, and Telecom (TMT) sectors.
Analyze the given tweet and extract:
1. Related tickers/companies (list of stock tickers like ["AAPL", "MSFT"])
2. Sentiment (positive/negative/neutral)
3. Sentiment score (-1.0 to 1.0, where -1 is very negative, 0 is neutral, 1 is very positive)
4. Relevance score (0.0 to 1.0, how relevant to TMT financial news)
5. Is relevant (true if score > 0.5 and contains financial/business news about TMT)
6. Headline (concise 10-15 word headline summarizing the tweet)
7. Summary (1-2 sentence summary if relevant, empty string if not relevant)

Only mark as relevant if:
- Discusses publicly traded TMT companies
- Contains financial/business news (earnings, acquisitions, product launches, executive moves, market trends)
- NOT personal opinions, memes, or general tech chatter

Respond with JSON matching this exact schema."""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Content(role="user", parts=[
                    types.Part(text=f"Author: {author}\nTweet: {tweet_text}")
                ])
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=TweetAnalysis,
            ),
        )

        raw_json = response.text
        if not raw_json:
            return None

        data = json.loads(raw_json)
        analysis = TweetAnalysis(**data)
        
        # Only return if relevant
        if not analysis.is_relevant:
            return None
        
        return {
            "tickers": analysis.tickers,
            "sentiment": analysis.sentiment,
            "sentiment_score": analysis.sentiment_score,
            "relevance_score": analysis.relevance_score,
            "is_relevant": analysis.is_relevant,
            "headline": analysis.headline,
            "summary": analysis.summary
        }

    except Exception as e:
        print(f"Error analyzing tweet: {e}")
        return None


def batch_analyze_tweets(tweets: List[Dict]) -> List[Dict]:
    """
    Analyze multiple tweets in batch
    
    Args:
        tweets: List of tweet dictionaries with 'text' and 'author' keys
    
    Returns:
        List of dictionaries with tweet data and analysis results
    """
    results = []
    
    for tweet in tweets:
        analysis = analyze_tweet(tweet['text'], tweet['author'])
        if analysis:  # Only include relevant tweets
            results.append({
                **tweet,
                'analysis': analysis
            })
    
    return results
