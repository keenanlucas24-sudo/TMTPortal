import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(
    page_title="TMT Research Portal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.title("📊 TMT Research Portal")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Dashboard", "🏢 Companies", "📰 Unified News", "📈 Earnings Calendar", "🔍 Search"]
)

st.sidebar.markdown("---")

# Clickable sector filters
st.sidebar.markdown("**Sectors:**")
if "selected_sector" not in st.session_state:
    st.session_state.selected_sector = "All"

sector_col1, sector_col2 = st.sidebar.columns([1, 1])
with sector_col1:
    if st.sidebar.button("📱 Technology", use_container_width=True, key="sector_tech"):
        st.session_state.selected_sector = "Technology"
        st.rerun()
    if st.sidebar.button("🎬 Media", use_container_width=True, key="sector_media"):
        st.session_state.selected_sector = "Media"
        st.rerun()
with sector_col2:
    if st.sidebar.button("📡 Telecom", use_container_width=True, key="sector_telecom"):
        st.session_state.selected_sector = "Telecom"
        st.rerun()
    if st.sidebar.button("🌐 All", use_container_width=True, key="sector_all"):
        st.session_state.selected_sector = "All"
        st.rerun()

if st.session_state.selected_sector != "All":
    st.sidebar.info(f"Filtered: {st.session_state.selected_sector}")

# Add AI Assistant to sidebar (available on all pages)
from components.ai_assistant import render_sidebar_assistant
render_sidebar_assistant()

if page == "🏠 Dashboard":
    from data.tmt_data import get_all_companies, get_news_feed, get_earnings_calendar
    
    # Check if we should show company detail page
    if st.session_state.get('show_company_detail', False) and st.session_state.get('selected_company'):
        from views import company_detail
        company_detail.show(st.session_state.selected_company)
    else:
        st.title("TMT Research Portal Dashboard")
        st.markdown("### Welcome to the TMT Research Hub")
        st.markdown("Access comprehensive research, news, and earnings data for Technology, Media, and Telecom companies.")
        
        # Search bar at top of dashboard
        st.markdown("---")
        st.markdown("### 🔍 Search Companies")
        
        companies = get_all_companies()
        
        # Create searchable dropdown
        company_options = {f"{c['name']} ({c['ticker']})": c for c in companies}
        selected = st.selectbox(
            "Search by company name or ticker:",
            [""] + list(company_options.keys()),
            placeholder="Start typing to search..."
        )
        
        if selected:
            # Navigate to company detail page
            st.session_state.selected_company = company_options[selected]
            st.session_state.show_company_detail = True
            st.rerun()
        
        st.markdown("---")
        
        # Add volatility screener
        from components.volatility_screener import render_compact_volatility_widget
        with st.expander("📈 Volatility Alert - Stocks Moving >2% Today", expanded=True):
            render_compact_volatility_widget(threshold=2.0)
        
        st.markdown("---")
        
        # Get news for recent activity
        all_news = get_news_feed()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Recent Activity")
            # Show actual recent news from database
            recent_news = sorted(all_news, key=lambda x: x["date"], reverse=True)[:5]
            for news in recent_news:
                time_diff = datetime.now() - news["date"]
                if time_diff.days == 0:
                    if time_diff.total_seconds() < 3600:
                        time_str = f"{int(time_diff.total_seconds() // 60)} min ago"
                    else:
                        time_str = f"{int(time_diff.total_seconds() // 3600)} hours ago"
                else:
                    time_str = f"{time_diff.days} days ago"
                
                st.info(f"📰 {news['company']}: {news['headline'][:60]}... - {time_str}")
        
        with col2:
            st.subheader("Quick Links")
            st.markdown("- [View All Companies](#)")
            st.markdown("- [Latest News Feed](#)")
            st.markdown("- [This Week's Earnings](#)")
            st.markdown("- [Search Companies & News](#)")

elif page == "🏢 Companies":
    from views import companies
    companies.show()

elif page == "📰 Unified News":
    from views import unified_news
    unified_news.show()

elif page == "📈 Earnings Calendar":
    from views import earnings
    earnings.show()

elif page == "🔍 Search":
    from views import search
    search.show()
