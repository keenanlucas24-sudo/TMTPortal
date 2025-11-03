"""
Unified News Feed - Combines regular news and social media news
"""
import streamlit as st
import pandas as pd
from data.tmt_data import get_news_feed, get_all_companies
from integrations.news_api import fetch_multi_provider_news, NewsAPIIntegration
from integrations.social_news_service import get_social_news_feed, fetch_and_analyze_tweets
from datetime import datetime, timedelta
from typing import List, Dict


def get_sector_from_ticker(ticker: str, companies: List[Dict]) -> str:
    """Get sector for a ticker from companies database"""
    for company in companies:
        if company['ticker'] == ticker:
            return company['sector']
    return 'Technology'  # Default fallback


def deduplicate_news(news_items: List[Dict], social_items: List[Dict], companies: List[Dict]) -> List[Dict]:
    """
    Deduplicate news items by checking for similar headlines or matching URLs
    
    Args:
        news_items: Regular news articles
        social_items: Social media posts
        companies: List of companies for sector lookup
    
    Returns:
        Combined and deduplicated list of news items
    """
    unified = []
    seen_urls = set()
    seen_headlines = set()
    
    # Process regular news first (higher priority)
    for news in news_items:
        url = news.get('url', '').lower().strip()
        headline = news['headline'].lower().strip()
        
        # Check for duplicates
        if url and url in seen_urls:
            continue
        if headline in seen_headlines:
            continue
        
        # Mark as seen
        if url:
            seen_urls.add(url)
        seen_headlines.add(headline)
        
        # Add source type
        unified.append({
            **news,
            'source_type': 'news_api',
            'timestamp': news['date']
        })
    
    # Process social news
    for social in social_items:
        permalink = social.get('permalink', '').lower().strip()
        headline = social.get('headline', '').lower().strip()
        
        # Check for duplicates
        if permalink and permalink in seen_urls:
            continue
        if headline and headline in seen_headlines:
            continue
        
        # Mark as seen
        if permalink:
            seen_urls.add(permalink)
        if headline:
            seen_headlines.add(headline)
        
        # Get sector from first ticker if available
        tickers = social.get('tickers', [])
        sector = get_sector_from_ticker(tickers[0], companies) if tickers else 'Technology'
        
        # Convert social format to news format
        unified.append({
            'date': social['timestamp'],
            'timestamp': social['timestamp'],
            'sector': sector,
            'company': ', '.join(tickers[:3]) or 'Multiple',
            'headline': social.get('headline', social['text'][:100]),
            'summary': social.get('summary', social['text']),
            'source': social['author'],
            'url': social.get('permalink'),
            'source_type': 'social_media',
            'sentiment': social.get('sentiment'),
            'sentiment_score': social.get('sentiment_score'),
            'tickers': tickers,
            'likes': social.get('likes', 0),
            'retweets': social.get('retweets', 0)
        })
    
    return unified


def show():
    st.title("📰 Unified News Feed")
    
    # Check Twitter status (show in sidebar to reduce clutter)
    try:
        from integrations.twitter_scraper import pool
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        accounts = loop.run_until_complete(pool.accounts_info())
        loop.close()
        twitter_active = len(accounts) > 0
    except:
        twitter_active = False
    
    # Refresh buttons at the top
    col_title, col_refresh1, col_refresh2 = st.columns([3, 1, 1])
    with col_title:
        pass
    with col_refresh1:
        if st.button("🔄 Refresh News APIs", use_container_width=True):
            with st.spinner("Fetching from news providers..."):
                try:
                    all_companies = get_all_companies()
                    tickers = [c["ticker"] for c in all_companies[:50]]
                    news = fetch_multi_provider_news(
                        tickers=tickers,
                        limit=120,
                        time_from=datetime.now() - timedelta(days=3)
                    )
                    integration = NewsAPIIntegration(provider='finnhub')
                    count = integration.sync_to_database(news)
                    st.success(f"✅ Added {count} new articles!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with col_refresh2:
        if st.button("🐦 Refresh Social", use_container_width=True):
            with st.spinner("Fetching tweets..."):
                try:
                    stats = fetch_and_analyze_tweets(limit_per_account=10)
                    if stats['relevant'] > 0:
                        st.success(f"✅ Added {stats['relevant']} relevant tweets!")
                        st.rerun()
                    else:
                        st.info("No new relevant tweets found")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    
    # Filters
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        source_type = st.selectbox(
            "Source Type",
            ["All", "News APIs", "Social Media"]
        )
    
    with col2:
        sector_filter = st.selectbox(
            "Sector",
            ["All", "Technology", "Media", "Telecom"]
        )
    
    with col3:
        # Company filter
        all_companies = get_all_companies()
        company_names = ["All"] + [c["name"] for c in all_companies]
        company_filter = st.selectbox(
            "Company",
            company_names
        )
    
    with col4:
        time_filter = st.selectbox(
            "Time Period",
            ["Last 24 Hours", "Last 3 Days", "Last Week", "All Time"]
        )
    
    with col5:
        sort_by = st.selectbox(
            "Sort by",
            ["Most Recent", "Oldest First"]
        )
    
    # Get data from both sources
    news_items = get_news_feed(
        sector_filter if sector_filter != "All" else None,
        company_filter if company_filter != "All" else None
    )
    
    social_items = get_social_news_feed(limit=100)
    
    # Combine and deduplicate
    unified_items = deduplicate_news(news_items, social_items, all_companies)
    
    # Apply sector filter to all items (both news and social)
    if sector_filter != "All":
        unified_items = [item for item in unified_items if item['sector'] == sector_filter]
    
    # Apply source type filter
    if source_type == "News APIs":
        unified_items = [item for item in unified_items if item['source_type'] == 'news_api']
    elif source_type == "Social Media":
        unified_items = [item for item in unified_items if item['source_type'] == 'social_media']
    
    # Apply company filter for social media (check if ticker matches)
    if company_filter != "All":
        # Get the ticker for the selected company
        selected_company = next((c for c in all_companies if c['name'] == company_filter), None)
        if selected_company:
            selected_ticker = selected_company['ticker']
            # Filter: keep news_api items (already filtered) and social items mentioning this ticker
            unified_items = [
                item for item in unified_items
                if item['source_type'] == 'news_api' or 
                   (item['source_type'] == 'social_media' and selected_ticker in item.get('tickers', []))
            ]
    
    # Apply time filter
    if time_filter != "All Time":
        time_delta = {
            "Last 24 Hours": timedelta(hours=24),
            "Last 3 Days": timedelta(days=3),
            "Last Week": timedelta(days=7)
        }[time_filter]
        cutoff_time = datetime.now() - time_delta
        unified_items = [item for item in unified_items if item['timestamp'] >= cutoff_time]
    
    # Sort
    unified_items = sorted(
        unified_items,
        key=lambda x: x['timestamp'],
        reverse=(sort_by == "Most Recent")
    )
    
    st.markdown("---")
    st.subheader(f"📊 {len(unified_items)} News Items")
    
    if not unified_items:
        st.info("No news items found for the selected filters.")
        return
    
    # Display unified news
    for item in unified_items:
        with st.container():
            # Source type badge
            if item['source_type'] == 'social_media':
                type_badge = "🐦 Social"
                type_color = "#1DA1F2"
            else:
                type_badge = "📰 News"
                type_color = "#4CAF50"
            
            col_badge, col_content = st.columns([1, 9])
            
            with col_badge:
                st.markdown(f"<div style='background-color: {type_color}; color: white; padding: 5px 10px; border-radius: 5px; text-align: center; font-size: 0.8em;'>{type_badge}</div>", unsafe_allow_html=True)
                
                # Time ago
                time_diff = datetime.now() - item['timestamp']
                if time_diff.total_seconds() < 3600:
                    time_str = f"{int(time_diff.total_seconds() / 60)}m ago"
                elif time_diff.total_seconds() < 86400:
                    time_str = f"{int(time_diff.total_seconds() / 3600)}h ago"
                else:
                    time_str = f"{time_diff.days}d ago"
                st.caption(time_str)
            
            with col_content:
                # Headline with link
                if item.get('url'):
                    st.markdown(f"### [{item['headline']}]({item['url']})")
                else:
                    st.markdown(f"### {item['headline']}")
                
                # Company/ticker info
                if item['source_type'] == 'social_media' and item.get('tickers'):
                    ticker_badges = " ".join([f"`{t}`" for t in item['tickers'][:5]])
                    st.markdown(f"**Related:** {ticker_badges}")
                else:
                    st.markdown(f"**{item['company']}** • {item['sector']}")
                
                # Summary
                st.markdown(item['summary'])
                
                # Metrics for social media
                if item['source_type'] == 'social_media':
                    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                    
                    with metric_col1:
                        sentiment_score = item.get('sentiment_score', 0)
                        sentiment_emoji = "📈" if sentiment_score > 0 else ("📉" if sentiment_score < 0 else "➖")
                        st.metric(f"{sentiment_emoji} Sentiment", f"{sentiment_score:+.2f}")
                    
                    with metric_col2:
                        st.metric("👍 Likes", f"{item.get('likes', 0):,}")
                    
                    with metric_col3:
                        st.metric("🔁 Retweets", f"{item.get('retweets', 0):,}")
                    
                    with metric_col4:
                        st.caption(f"Source: {item['source']}")
                else:
                    # Source for regular news
                    if item.get('url'):
                        st.caption(f"Source: {item['source']} • [Read full article →]({item['url']})")
                    else:
                        st.caption(f"Source: {item['source']}")
            
            st.markdown("---")


if __name__ == "__main__":
    show()
