import streamlit as st
import pandas as pd
from data.tmt_data import get_news_feed, get_all_companies
from integrations.news_api import fetch_multi_provider_news, NewsAPIIntegration
from datetime import datetime, timedelta

def show():
    st.title("📰 News Feed")
    
    # Refresh button at the top
    col_title, col_refresh = st.columns([4, 1])
    with col_title:
        st.markdown("Latest TMT industry news and updates.")
    with col_refresh:
        if st.button("🔄 Refresh News", use_container_width=True):
            with st.spinner("Fetching latest news from all providers..."):
                try:
                    # Get all company tickers
                    all_companies = get_all_companies()
                    tickers = [c["ticker"] for c in all_companies[:50]]  # Top 50 companies
                    
                    # Fetch from all providers
                    news = fetch_multi_provider_news(
                        tickers=tickers,
                        limit=120,
                        time_from=datetime.now() - timedelta(days=3)
                    )
                    
                    # Sync to database
                    integration = NewsAPIIntegration(provider='finnhub')
                    count = integration.sync_to_database(news)
                    
                    st.success(f"✅ Refreshed! Added {count} new articles from premium sources.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error refreshing news: {str(e)}")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sector_filter = st.selectbox(
            "Filter by Sector",
            ["All", "Technology", "Media", "Telecom"]
        )
    
    with col2:
        all_companies = get_all_companies()
        company_names = ["All"] + [c["name"] for c in all_companies]
        company_filter = st.selectbox(
            "Filter by Company",
            company_names
        )
    
    with col3:
        sort_by = st.selectbox(
            "Sort by",
            ["Most Recent", "Oldest First"]
        )
    
    news_items = get_news_feed(
        sector_filter if sector_filter != "All" else None,
        company_filter if company_filter != "All" else None
    )
    
    if sort_by == "Oldest First":
        news_items = sorted(news_items, key=lambda x: x["date"])
    else:
        news_items = sorted(news_items, key=lambda x: x["date"], reverse=True)
    
    st.markdown("---")
    
    if news_items:
        for news in news_items:
            with st.container():
                col_date, col_content = st.columns([1, 4])
                
                with col_date:
                    time_diff = datetime.now() - news["date"]
                    total_seconds = int(time_diff.total_seconds())
                    
                    if time_diff.days == 0:
                        if total_seconds < 3600:
                            time_str = f"{total_seconds // 60} min ago"
                        else:
                            time_str = f"{total_seconds // 3600} hours ago"
                    else:
                        time_str = f"{time_diff.days} days ago"
                    
                    st.caption(time_str)
                    st.caption(f"**{news['sector']}**")
                
                with col_content:
                    # Make headline clickable if URL exists
                    if news.get('url'):
                        st.markdown(f"### [{news['headline']}]({news['url']})")
                    else:
                        st.markdown(f"### {news['headline']}")
                    
                    st.markdown(f"**{news['company']}**")
                    st.markdown(news['summary'])
                    
                    # Add "Read more" link if URL exists
                    if news.get('url'):
                        st.caption(f"Source: {news['source']} • [Read full article →]({news['url']})")
                    else:
                        st.caption(f"Source: {news['source']}")
                
                st.markdown("---")
    else:
        st.info("No news items found for the selected filters.")
