"""
Social News view - Display analyzed tweets from financial Twitter accounts
Powered by Twitter scraping + Gemini AI analysis
"""
import streamlit as st
from datetime import datetime, timedelta
from integrations.social_news_service import get_social_news_feed, fetch_and_analyze_tweets

def render():
    st.title("📱 Social News Feed")
    st.markdown("Real-time financial news from Twitter, analyzed by Gemini AI")
    
    # Filters
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        author_options = [
            "All Sources",
            "@Bloomberg",
            "@Reuters", 
            "@CNBC",
            "@SeekingAlpha",
            "@WSJ",
            "@FT",
            "@theinformation",
            "@faststocknews",
            "@mingchikuo",
            "@ivanaspear",
            "@rihardjarc",
            "@semianalysis_",
            "@wallstengine",
            "@stockmktnewz"
        ]
        author_filter = st.selectbox("Filter by Source", author_options)
    
    with col2:
        time_filter = st.selectbox("Time Period", [
            "Last 24 Hours",
            "Last 3 Days",
            "Last Week",
            "All Time"
        ])
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Refresh Feed", use_container_width=True):
            with st.spinner("Fetching and analyzing new tweets..."):
                stats = fetch_and_analyze_tweets(limit_per_account=10)
                if stats['relevant'] > 0:
                    st.success(f"✓ Added {stats['relevant']} new relevant tweets!")
                    st.rerun()
                elif stats['fetched'] > 0:
                    st.info(f"Analyzed {stats['analyzed']} tweets, none were TMT-relevant")
                else:
                    st.warning("No tweets fetched. Please configure Twitter accounts.")
    
    st.markdown("---")
    
    # Convert filter to database parameter
    author_param = None if author_filter == "All Sources" else author_filter
    
    # Get social news feed
    social_news = get_social_news_feed(limit=100, author_filter=author_param)
    
    # Filter by time
    if time_filter != "All Time":
        time_delta = {
            "Last 24 Hours": timedelta(hours=24),
            "Last 3 Days": timedelta(days=3),
            "Last Week": timedelta(days=7)
        }[time_filter]
        
        cutoff_time = datetime.now() - time_delta
        social_news = [
            item for item in social_news 
            if item['timestamp'] >= cutoff_time
        ]
    
    # Display count
    st.subheader(f"📰 {len(social_news)} Relevant Tweets")
    
    if not social_news:
        st.info("""
        ### No social news yet
        
        **To get started:**
        1. Configure Twitter accounts: `python integrations/setup_twitter_accounts.py`
        2. Click "Refresh Feed" above to fetch and analyze tweets
        3. Tweets are analyzed by Gemini AI for TMT relevance, sentiment, and ticker extraction
        
        **Note:** Twitter scraping requires dedicated Twitter accounts and may violate Twitter's Terms of Service. Use at your own risk.
        """)
        return
    
    # Display social news items
    for item in social_news:
        # Sentiment badge
        sentiment_emoji = {
            "positive": "📈",
            "negative": "📉",
            "neutral": "➖"
        }.get(item.get('sentiment', 'neutral'), "➖")
        
        sentiment_color = {
            "positive": "#00ff00",
            "negative": "#ff0000",
            "neutral": "#888888"
        }.get(item.get('sentiment', 'neutral'), "#888888")
        
        # Tickers
        tickers = item.get('tickers', [])
        ticker_badges = " ".join([f"`{ticker}`" for ticker in tickers[:5]]) if tickers else ""
        
        # Time ago
        time_diff = datetime.now() - item['timestamp']
        if time_diff.total_seconds() < 3600:
            time_ago = f"{int(time_diff.total_seconds() / 60)}m ago"
        elif time_diff.total_seconds() < 86400:
            time_ago = f"{int(time_diff.total_seconds() / 3600)}h ago"
        else:
            time_ago = f"{time_diff.days}d ago"
        
        # Create card for each tweet
        with st.container():
            col_icon, col_content = st.columns([1, 20])
            
            with col_icon:
                st.markdown(f"<div style='font-size: 2em;'>{sentiment_emoji}</div>", 
                          unsafe_allow_html=True)
            
            with col_content:
                # Header: source + time
                st.markdown(f"**{item['author']}** · {time_ago}")
                
                # Headline
                st.markdown(f"### {item.get('headline', 'Tweet')}")
                
                # Tickers
                if ticker_badges:
                    st.markdown(f"**Related:** {ticker_badges}")
                
                # Summary
                if item.get('summary'):
                    st.markdown(item['summary'])
                
                # Metrics row
                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                
                with metric_col1:
                    sentiment_score = item.get('sentiment_score', 0)
                    st.metric("Sentiment", f"{sentiment_score:+.2f}", 
                            delta_color="normal" if sentiment_score >= 0 else "inverse")
                
                with metric_col2:
                    st.metric("Likes", f"{item.get('likes', 0):,}")
                
                with metric_col3:
                    st.metric("Retweets", f"{item.get('retweets', 0):,}")
                
                with metric_col4:
                    relevance = item.get('relevance_score', 0)
                    st.metric("Relevance", f"{relevance:.0%}")
                
                # View original tweet link
                if item.get('permalink'):
                    st.markdown(f"[View Original Tweet →]({item['permalink']})")
            
            st.markdown("---")
    
    # Footer info
    st.markdown("""
    <div style='text-align: center; color: #888; font-size: 0.9em; margin-top: 2em;'>
    Social news is powered by Twitter scraping + Gemini AI analysis<br>
    Tweets are analyzed for TMT relevance, sentiment, and ticker extraction<br>
    Only relevant financial news about Technology, Media, and Telecom companies is shown
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    render()
