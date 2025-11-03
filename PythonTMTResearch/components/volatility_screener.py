"""
Volatility Screener Component
Displays stocks with significant price movements (>2%)
"""
import streamlit as st
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from integrations.stock_prices import format_price_change
from integrations.volatility_service import get_volatile_stocks_from_db, refresh_all_tickers, init_volatility_table
from data.tmt_data import get_all_companies


def get_cached_volatility_data(tickers: List[str], threshold: float = 2.0, cache_minutes: int = 60) -> Dict:
    """
    Get volatility data from database cache
    
    Args:
        tickers: List of ticker symbols (for potential refresh)
        threshold: Percentage threshold
        cache_minutes: How long to accept cached results (default 15 minutes)
    
    Returns:
        Volatility data dict
    """
    # Initialize table if needed
    try:
        init_volatility_table()
    except:
        pass
    
    # Get data from database cache
    results = get_volatile_stocks_from_db(threshold=threshold, max_age_minutes=cache_minutes)
    
    # If no recent data, show helpful message
    if results['total_checked'] == 0:
        return {
            "gainers": [],
            "losers": [],
            "total_checked": 0,
            "volatile_count": 0,
            "needs_refresh": True
        }
    
    return results


def render_volatility_screener(threshold: float = 2.0, max_display: int = 10):
    """
    Render volatility screener showing stocks with significant movements
    
    Args:
        threshold: Minimum percentage change to display (default 2.0%)
        max_display: Maximum stocks to display in each category
    """
    st.subheader("📈 Volatility Screener")
    st.caption(f"TMT stocks with ±{threshold}% or more movement today")
    
    # Get all company tickers
    companies = get_all_companies()
    tickers = [c['ticker'] for c in companies if c.get('ticker')]
    
    # Create ticker to company name mapping
    ticker_to_name = {c['ticker']: c['name'] for c in companies if c.get('ticker')}
    
    # Add refresh button
    col1, col2 = st.columns([1, 4])
    with col1:
        refresh = st.button("🔄 Refresh", key="volatility_refresh", use_container_width=True)
    
    # Manual refresh if button clicked
    if refresh:
        with st.spinner(f"Refreshing all {len(tickers)} tickers (this may take 3-5 minutes)..."):
            refresh_all_tickers(tickers, chunk_size=58)
            st.success("Refresh complete!")
            st.rerun()
    
    # Fetch volatile stocks (from database cache)
    with st.spinner("Loading volatility data..."):
        results = get_cached_volatility_data(tickers, threshold=threshold)
    
    gainers = results.get("gainers", [])
    losers = results.get("losers", [])
    
    # Display summary
    if results.get('needs_refresh'):
        st.warning("⚠️ No recent data available. Click 'Refresh' to fetch latest prices (takes 3-5 minutes for all tickers).")
    else:
        st.markdown(f"**{results['volatile_count']} of {results['total_checked']} stocks showing significant movement**")
        st.caption(f"Cache age: {results.get('cache_age', 'Unknown')}")
    
    # Create two columns for gainers and losers
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🟢 Top Gainers")
        if gainers:
            for i, stock in enumerate(gainers[:max_display], 1):
                ticker = stock['ticker']
                company_name = ticker_to_name.get(ticker, ticker)
                
                with st.container():
                    st.markdown(f"**{i}. {ticker}** - {company_name}")
                    st.markdown(f"💰 ${stock['price']:.2f}")
                    st.markdown(f"<span style='color: green; font-weight: bold;'>▲ {format_price_change(stock['change'], stock['change_percent'])}</span>", unsafe_allow_html=True)
                    st.markdown("---")
        else:
            st.info(f"No stocks gaining >{threshold}% today")
    
    with col2:
        st.markdown("### 🔴 Top Losers")
        if losers:
            for i, stock in enumerate(losers[:max_display], 1):
                ticker = stock['ticker']
                company_name = ticker_to_name.get(ticker, ticker)
                
                with st.container():
                    st.markdown(f"**{i}. {ticker}** - {company_name}")
                    st.markdown(f"💰 ${stock['price']:.2f}")
                    st.markdown(f"<span style='color: red; font-weight: bold;'>▼ {format_price_change(stock['change'], stock['change_percent'])}</span>", unsafe_allow_html=True)
                    st.markdown("---")
        else:
            st.info(f"No stocks losing >{threshold}% today")
    
    # Additional info with actual update time
    cache_age = results.get('cache_age', 'Unknown')
    st.caption(f"Data source: {gainers[0]['source'] if gainers else losers[0]['source'] if losers else 'Finnhub/Alpha Vantage'} | Last updated: {cache_age}")


def render_compact_volatility_widget(threshold: float = 2.0):
    """
    Render compact version for dashboard with scrollable lists
    
    Args:
        threshold: Minimum percentage change to display
    """
    # Get all company tickers
    companies = get_all_companies()
    tickers = [c['ticker'] for c in companies if c.get('ticker')]
    ticker_to_name = {c['ticker']: c['name'] for c in companies if c.get('ticker')}
    
    # Fetch volatile stocks (from database cache)
    results = get_cached_volatility_data(tickers, threshold=threshold)
    
    gainers = results.get("gainers", [])
    losers = results.get("losers", [])
    
    # Show summary with cache age
    if results.get('needs_refresh'):
        st.info("⚠️ No recent data. Click refresh on the full screener page.")
    else:
        cache_age = results.get('cache_age', 'Unknown')
        st.caption(f"{results['volatile_count']} of {results['total_checked']} stocks moving >2% | Updated: {cache_age}")
    
    # Show all movers in scrollable columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🟢 Gainers**")
        if gainers:
            # Create scrollable container using markdown with HTML
            gainers_html = '<div style="max-height: 300px; overflow-y: auto;">'
            for stock in gainers:
                ticker = stock['ticker']
                name = ticker_to_name.get(ticker, ticker)
                gainers_html += f'<div style="margin: 5px 0;"><b>{ticker}</b> ({name[:15]}...) <span style="color: green; font-weight: bold;">+{stock["change_percent"]:.1f}%</span></div>'
            gainers_html += '</div>'
            st.markdown(gainers_html, unsafe_allow_html=True)
        else:
            st.caption("None today")
    
    with col2:
        st.markdown("**🔴 Losers**")
        if losers:
            # Create scrollable container using markdown with HTML
            losers_html = '<div style="max-height: 300px; overflow-y: auto;">'
            for stock in losers:
                ticker = stock['ticker']
                name = ticker_to_name.get(ticker, ticker)
                losers_html += f'<div style="margin: 5px 0;"><b>{ticker}</b> ({name[:15]}...) <span style="color: red; font-weight: bold;">{stock["change_percent"]:.1f}%</span></div>'
            losers_html += '</div>'
            st.markdown(losers_html, unsafe_allow_html=True)
        else:
            st.caption("None today")
