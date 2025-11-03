import streamlit as st
import pandas as pd
from data.tmt_data import (
    get_all_companies, 
    get_companies_by_sector,
    get_companies_by_sub_sector,
    get_all_sub_sectors,
    get_sub_sectors_by_sector
)

def show():
    st.title("🏢 TMT Companies")
    st.markdown("Browse and explore Technology, Media, and Telecom companies across all sub-sectors.")
    
    # Use global sector filter if set
    global_sector = st.session_state.get('selected_sector', 'All')
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("### Filters")
        
        # Show current global filter if active
        if global_sector != "All":
            st.info(f"🔍 Filtered by: {global_sector}")
        
        sector_filter = st.radio(
            "Primary Sector",
            ["All", "Technology", "Media", "Telecom"],
            index=["All", "Technology", "Media", "Telecom"].index(global_sector) if global_sector in ["All", "Technology", "Media", "Telecom"] else 0
        )
        
        st.markdown("---")
        
        try:
            if sector_filter == "All":
                all_sub_sectors = get_all_sub_sectors()
                sub_sector_options = ["All"] + all_sub_sectors
            else:
                sector_sub_sectors = get_sub_sectors_by_sector(sector_filter)
                sub_sector_options = ["All"] + sector_sub_sectors
        except Exception as e:
            st.error(f"Error loading sub-sectors: {e}")
            sub_sector_options = ["All"]
        
        sub_sector_filter = st.selectbox(
            "Sub-Sector",
            sub_sector_options
        )
        
        st.markdown("---")
        st.markdown("**Quick Stats**")
        try:
            all_companies = get_all_companies()
            st.metric("Total Companies", len(all_companies))
            
            tech_count = len([c for c in all_companies if c.get('sector') == 'Technology'])
            media_count = len([c for c in all_companies if c.get('sector') == 'Media'])
            telecom_count = len([c for c in all_companies if c.get('sector') == 'Telecom'])
            
            st.metric("Technology", tech_count)
            st.metric("Media", media_count)
            st.metric("Telecom", telecom_count)
        except Exception as e:
            st.error(f"Error loading stats: {e}")
    
    with col2:
        try:
            if sub_sector_filter != "All":
                companies = get_companies_by_sub_sector(sub_sector_filter)
                st.subheader(f"{sub_sector_filter} ({len(companies)} companies)")
            elif sector_filter == "All":
                companies = get_all_companies()
                st.subheader(f"All TMT Companies ({len(companies)} companies)")
            else:
                companies = get_companies_by_sector(sector_filter)
                st.subheader(f"{sector_filter} Companies ({len(companies)} companies)")
        except Exception as e:
            st.error(f"Error loading companies: {e}")
            return
        
        if not companies:
            st.info("No companies found for the selected filters.")
        else:
            current_sub_sector = None
            for company in companies:
                if sub_sector_filter == "All" and company.get('sub_sector') != current_sub_sector:
                    current_sub_sector = company.get('sub_sector')
                    if current_sub_sector:
                        st.markdown(f"### {current_sub_sector}")
                
                with st.expander(f"**{company['name']}** ({company['ticker']})"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Market Cap", company["market_cap"])
                    with col_b:
                        st.metric("Sector", company["sector"])
                    
                    if company.get('sub_sector'):
                        st.markdown(f"**Sub-Sector:** {company['sub_sector']}")
                    
                    st.markdown(f"**Description:** {company['description']}")
                    
                    col1_btn, col2_btn, col3_btn = st.columns(3)
                    with col1_btn:
                        st.button("📈 View Earnings", key=f"earn_{company['ticker']}")
                    with col2_btn:
                        st.button("📰 View News", key=f"news_{company['ticker']}")
                    with col3_btn:
                        st.button("💡 View Insights", key=f"insight_{company['ticker']}")
