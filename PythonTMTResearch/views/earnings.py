import streamlit as st
import pandas as pd
from data.tmt_data import get_earnings_calendar, get_all_companies
from datetime import datetime, timedelta
from collections import defaultdict

def show():
    st.title("📈 Earnings Calendar")
    
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.radio(
            "Status:",
            ["All", "Upcoming", "Reported"],
            horizontal=True,
            label_visibility="collapsed"
        )
    with col2:
        view_mode = st.radio(
            "View:",
            ["Weekly", "Table"],
            horizontal=True,
            label_visibility="collapsed"
        )
    
    # Get all TMT company tickers
    tmt_companies = get_all_companies()
    tmt_tickers = {c["ticker"] for c in tmt_companies}
    
    # Filter earnings to only TMT stocks
    all_earnings = get_earnings_calendar(
        status_filter if status_filter != "All" else None
    )
    earnings_data = [e for e in all_earnings if e["ticker"] in tmt_tickers]
    
    earnings_data = sorted(earnings_data, key=lambda x: x["date"])
    
    st.markdown("---")
    
    if view_mode == "Weekly":
        # Filter
        if status_filter == "Upcoming":
            filtered_data = [e for e in earnings_data if e["status"] == "Upcoming"]
        elif status_filter == "Reported":
            filtered_data = [e for e in earnings_data if e["status"] == "Reported"]
        else:
            filtered_data = earnings_data
        
        if not filtered_data:
            st.info(f"No {status_filter.lower()} earnings.".strip())
        else:
            # Group by week
            weeks = defaultdict(lambda: defaultdict(list))
            for earning in filtered_data:
                date = earning["date"]
                start_of_week = date - timedelta(days=date.weekday())
                week_key = start_of_week.strftime("%Y-%m-%d")
                day_name = date.strftime("%A")
                weeks[week_key][day_name].append(earning)
            
            # Display compact weekly view
            for week_start in sorted(weeks.keys()):
                week_start_date = datetime.strptime(week_start, "%Y-%m-%d")
                week_end_date = week_start_date + timedelta(days=4)
                
                st.markdown(f"**Week: {week_start_date.strftime('%b %d')} - {week_end_date.strftime('%b %d')}**")
                
                cols = st.columns(5)
                days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
                
                for i, day in enumerate(days):
                    with cols[i]:
                        date = week_start_date + timedelta(days=i)
                        st.caption(f"**{day[:3]} {date.strftime('%m/%d')}**")
                        
                        if day in weeks[week_start]:
                            for earning in weeks[week_start][day]:
                                time_icon = "🌅" if earning.get("time_of_day") == "BMO" else "🌆"
                                st.markdown(f"{time_icon} **{earning['ticker']}**")
                                
                                # Show actual vs estimate for reported
                                if earning["status"] == "Reported":
                                    actual_eps = earning.get('actual_eps', '-')
                                    est_eps = earning.get('consensus_eps', '-')
                                    st.caption(f"EPS: {actual_eps} vs {est_eps}")
                                else:
                                    st.caption(f"Est: {earning.get('consensus_eps', 'TBD')}")
                        else:
                            st.caption("—")
                
                st.divider()
    
    elif view_mode == "Table":
        # Compact table with more information
        for i, earning in enumerate(earnings_data[:30], 1):  # Show 30 most recent
            is_reported = earning["status"] == "Reported"
            
            col1, col2, col3, col4, col5 = st.columns([1.5, 2, 1.5, 2, 2])
            
            with col1:
                st.markdown(f"**{earning['date'].strftime('%m/%d')}**")
                time_icon = "🌅" if earning.get("time_of_day") == "BMO" else "🌆"
                st.caption(time_icon)
            
            with col2:
                st.markdown(f"**{earning['ticker']}**")
                st.caption(earning['company'][:20])
            
            with col3:
                st.markdown(f"**{earning['quarter']}**")
                st.caption(earning.get('sector', 'TMT')[:10])
            
            with col4:
                if is_reported:
                    actual = earning.get('actual_eps', 'N/A')
                    est = earning.get('consensus_eps', 'N/A')
                    st.metric("EPS", actual, delta=f"vs {est}" if actual != 'N/A' else None)
                else:
                    st.markdown("**Est EPS**")
                    st.caption(earning.get('consensus_eps', 'TBD'))
            
            with col5:
                if is_reported:
                    actual_rev = earning.get('actual_revenue', 'N/A')
                    est_rev = earning.get('consensus_revenue', 'N/A')
                    st.metric("Rev", actual_rev, delta=f"vs {est_rev}" if actual_rev != 'N/A' else None)
                else:
                    st.markdown("**Est Rev**")
                    st.caption(earning.get('consensus_revenue', 'TBD'))
            
            if i < len(earnings_data[:30]):
                st.divider()
