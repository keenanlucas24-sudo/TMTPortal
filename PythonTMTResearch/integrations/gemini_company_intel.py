"""
Gemini-powered company intelligence
Fetches real-time, comprehensive company data using Gemini API
"""
import os
from google import genai
from google.genai import types
from typing import Dict, Optional, List
from datetime import datetime


client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


def get_comprehensive_company_data(ticker: str, company_name: str) -> Dict:
    """
    Get comprehensive real-time company data using Gemini API
    
    Args:
        ticker: Stock ticker symbol
        company_name: Full company name
    
    Returns:
        Dictionary with market data, volume analysis, fundamentals
    """
    prompt = f"""
You are a financial data analyst. Provide ONLY factual, current information about {company_name} ({ticker}).

CRITICAL: Use ONLY real, current data from today {datetime.now().strftime('%Y-%m-%d')}. 
Do NOT provide hypothetical, estimated, or outdated information.
If data is not available, explicitly state "Data not available" - do NOT make up numbers.

Provide the following in a clean, structured format:

**Market Data** (Current as of today):
- Market Cap: [exact current value in billions]
- Current Price: [today's actual price]
- 52-Week High: [actual high]
- 52-Week Low: [actual low]
- P/E Ratio: [current ratio]
- Average Daily Volume: [3-month actual average]

**Company Fundamentals**:
- Annual Revenue: [most recent fiscal year actual]
- Number of Employees: [current count]
- Headquarters: [city, state/country]

**Business**: [1-2 sentence factual description]

IMPORTANT: Only include factual data you can verify. If uncertain about any metric, write "Data not available" for that specific item.
"""
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,  # Low temperature for factual data
            ),
        )
        
        return {
            'raw_response': response.text,
            'timestamp': datetime.now(),
            'ticker': ticker,
            'company_name': company_name
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'raw_response': f"Unable to fetch data: {str(e)}",
            'timestamp': datetime.now(),
            'ticker': ticker,
            'company_name': company_name
        }


def get_latest_earnings_analysis(ticker: str, company_name: str) -> Dict:
    """
    Get comprehensive analysis of most recent earnings report using Gemini
    
    Args:
        ticker: Stock ticker symbol
        company_name: Full company name
    
    Returns:
        Dictionary with earnings analysis
    """
    prompt = f"""
Provide ONLY factual information about {company_name}'s ({ticker}) most recent earnings report.

Today's date: {datetime.now().strftime('%Y-%m-%d')}

CRITICAL: Use ONLY real, reported data. Do NOT speculate or provide hypothetical information.

**Most Recent Earnings** (provide exact date and quarter):
- Report Date: [exact date]
- Quarter: [Q1/Q2/Q3/Q4 YYYY]

**Actual Results** (report only if available):
- Revenue: [actual reported] vs [consensus estimate]
- EPS: [actual reported] vs [consensus estimate]
- Result: [Beat/Miss/In-line - be specific]
- YoY Growth: [actual percentage]

**Guidance** (only if provided):
- [exact guidance numbers if given, otherwise state "No guidance provided"]

**Next Earnings**:
- Expected Date: [if known, otherwise "Not announced"]

If ANY data is not available or you're unsure, explicitly state "Data not available" - do NOT estimate or guess.
Be concise and factual.
"""
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
            ),
        )
        
        return {
            'raw_response': response.text,
            'timestamp': datetime.now(),
            'ticker': ticker,
            'company_name': company_name
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'raw_response': f"Unable to fetch earnings data: {str(e)}",
            'timestamp': datetime.now(),
            'ticker': ticker,
            'company_name': company_name
        }


def analyze_company_news(ticker: str, company_name: str, news_articles: List[Dict]) -> str:
    """
    Analyze company news using Gemini to provide insights
    
    Args:
        ticker: Stock ticker symbol
        company_name: Full company name
        news_articles: List of news article dictionaries with headline, summary, date
    
    Returns:
        Analysis text
    """
    if not news_articles:
        return "No recent news available for analysis."
    
    # Format news for prompt
    news_text = "\n".join([
        f"- {article.get('date', 'Recent').strftime('%Y-%m-%d') if isinstance(article.get('date'), datetime) else 'Recent'}: {article.get('headline', 'No headline')} - {article.get('summary', '')[:200]}"
        for article in news_articles[:10]
    ])
    
    prompt = f"""
Analyze these ACTUAL recent news articles about {company_name} ({ticker}):

{news_text}

Provide factual analysis only:

**Key Themes**: [What topics dominate the news?]
**Overall Sentiment**: [Positive/Negative/Mixed - based on actual articles]
**Major Developments**: [2-3 most important factual developments]
**Potential Impact**: [Brief assessment based on the actual news]

Be concise. Base analysis ONLY on the provided articles - do not add external speculation.
"""
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
            ),
        )
        
        return response.text or "Unable to analyze news."
        
    except Exception as e:
        return f"Error analyzing news: {str(e)}"


def get_volume_analysis(ticker: str, current_volume: int, avg_volume: int) -> str:
    """
    Get AI analysis of volume patterns
    
    Args:
        ticker: Stock ticker
        current_volume: Today's volume
        avg_volume: Average volume
    
    Returns:
        Analysis text
    """
    ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
    
    prompt = f"""
Stock ticker {ticker} is trading at {current_volume:,} shares today.
The 3-month average volume is {avg_volume:,} shares.
The current volume is {ratio:.1f}x the average.

Provide a brief (2-3 sentence) analysis:
- Is this volume higher/lower than usual?
- What might this indicate about trading activity?
- Should investors pay attention to this?
"""
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
            ),
        )
        
        return response.text or f"Volume is {ratio:.1f}x average."
        
    except Exception as e:
        return f"Current volume: {current_volume:,} ({ratio:.1f}x average)"
