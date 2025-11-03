"""
Company Detail Page
Shows comprehensive information about a specific company with Gemini-powered intelligence
"""
import streamlit as st
from data.tmt_data import get_news_feed, get_earnings_calendar, get_all_companies
from datetime import datetime
from integrations.volatility_service import get_volatile_stocks_from_db
from integrations.gemini_company_intel import (
    get_comprehensive_company_data,
    get_latest_earnings_analysis,
    analyze_company_news,
    get_volume_analysis
)


def show(company: dict):
    """
    Display detailed company page with factual, current data
    
    Args:
        company: Company dictionary with name, ticker, sector, etc.
    """
    ticker = company['ticker']
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(f"{company['name']} ({ticker})")
    with col2:
        if st.button("← Back", use_container_width=True):
            st.session_state.show_company_detail = False
            st.rerun()
    
    st.markdown("---")
    
    # SECTION 1: BASIC MARKET METRICS AT TOP (Real-time, factual data)
    st.subheader("📊 Market Overview")
    
    # Get real stock data from database
    try:
        volatility_data = get_volatile_stocks_from_db(threshold=0.0, max_age_minutes=60)
        all_quotes = volatility_data.get('gainers', []) + volatility_data.get('losers', [])
        ticker_quote = next((q for q in all_quotes if q['ticker'] == ticker), None)
        
        if ticker_quote:
            # Display key metrics in clean columns
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Price", f"${ticker_quote['price']:.2f}")
            with col2:
                st.metric("Change", f"${ticker_quote['change']:.2f}", delta=f"{ticker_quote['change_percent']:.2f}%")
            with col3:
                st.metric("Prev Close", f"${ticker_quote['previous_close']:.2f}")
            with col4:
                st.metric("Volume", f"{ticker_quote['volume']:,}")
            with col5:
                st.metric("Sector", company['sector'])
    except Exception as e:
        st.info("Live price data unavailable. Fetching from AI...")
    
    # Get comprehensive current data from Gemini (factual only)
    if st.button("🔄 Refresh Data", key="refresh_all_data"):
        st.session_state.pop(f'gemini_data_{ticker}', None)
        st.session_state.pop(f'gemini_earnings_{ticker}', None)
        st.session_state.pop(f'news_analysis_{ticker}', None)
    
    if f'gemini_data_{ticker}' not in st.session_state:
        with st.spinner("Fetching current market data..."):
            st.session_state[f'gemini_data_{ticker}'] = get_comprehensive_company_data(ticker, company['name'])
    
    gemini_data = st.session_state[f'gemini_data_{ticker}']
    
    with st.expander("📈 Complete Market Data (Market Cap, 52-Week Range, P/E, etc.)", expanded=False):
        if 'error' not in gemini_data:
            st.markdown(gemini_data['raw_response'])
            st.caption(f"Updated: {gemini_data['timestamp'].strftime('%H:%M:%S')}")
        else:
            st.error(gemini_data.get('error', 'Data unavailable'))
    
    st.markdown("---")
    
    # SECTION 2: NEWS & MARKET INTELLIGENCE
    st.subheader("📰 News & Market Intelligence")
    
    company_news = get_news_feed(sector_filter=None, company_filter=company['name'])
    
    if company_news:
        # AI Analysis of news
        if f'news_analysis_{ticker}' not in st.session_state:
            with st.spinner("Analyzing news..."):
                st.session_state[f'news_analysis_{ticker}'] = analyze_company_news(ticker, company['name'], company_news)
        
        st.markdown(st.session_state[f'news_analysis_{ticker}'])
        
        st.markdown("#### Recent Articles")
        for i, news in enumerate(company_news[:8], 1):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{news['headline']}**")
                st.caption(f"{news['source']} • {news['date'].strftime('%b %d, %Y')}")
            with col2:
                if news.get('url'):
                    st.link_button("Read", news['url'], use_container_width=True)
            if i < len(company_news[:8]):
                st.divider()
    else:
        st.info(f"No recent news for {company['name']}")
    
    st.markdown("---")
    
    # SECTION 3: EARNINGS (Current and factual)
    st.subheader("📈 Earnings & Financials")
    
    # AI-powered latest earnings analysis
    if f'gemini_earnings_{ticker}' not in st.session_state:
        with st.spinner("Fetching latest earnings data..."):
            st.session_state[f'gemini_earnings_{ticker}'] = get_latest_earnings_analysis(ticker, company['name'])
    
    earnings_data = st.session_state[f'gemini_earnings_{ticker}']
    
    if 'error' not in earnings_data:
        st.markdown(earnings_data['raw_response'])
        st.caption(f"Updated: {earnings_data['timestamp'].strftime('%H:%M:%S')}")
    else:
        st.error(earnings_data.get('error', 'Earnings data unavailable'))
    
    st.markdown("#### Earnings History")
    
    all_earnings = get_earnings_calendar()
    company_earnings = [e for e in all_earnings if e['ticker'] == ticker]
    
    if company_earnings:
        company_earnings.sort(key=lambda x: x['date'], reverse=True)
        
        # Clean table view
        for earning in company_earnings[:4]:
            is_reported = earning['status'] == "Reported"
            
            col1, col2, col3 = st.columns([2, 3, 3])
            with col1:
                st.markdown(f"**{earning['quarter']}**")
                st.caption(earning['date'].strftime('%b %d, %Y'))
            with col2:
                if is_reported and earning.get('actual_eps'):
                    st.metric("EPS", earning['actual_eps'], delta=f"vs {earning.get('consensus_eps', '-')}")
                else:
                    st.markdown(f"**Est EPS:** {earning.get('consensus_eps', 'N/A')}")
            with col3:
                if is_reported and earning.get('actual_revenue'):
                    st.metric("Revenue", earning['actual_revenue'], delta=f"vs {earning.get('consensus_revenue', '-')}")
                else:
                    st.markdown(f"**Est Rev:** {earning.get('consensus_revenue', 'N/A')}")
            
            st.divider()
    else:
        st.info(f"No earnings data for {ticker}")
