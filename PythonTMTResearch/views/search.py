import streamlit as st
from data.tmt_data import search_all_data

def show():
    st.title("🔍 Search TMT Research Portal")
    st.markdown("Search across companies, news, earnings, and roundtable insights.")
    
    search_query = st.text_input(
        "Enter search terms (company name, ticker, topic, keyword, etc.)",
        placeholder="e.g., Apple, AI, streaming, 5G, cloud computing..."
    )
    
    if search_query:
        results = search_all_data(search_query)
        
        total_results = (
            len(results["companies"]) +
            len(results["news"]) +
            len(results["earnings"]) +
            len(results["roundtables"])
        )
        
        st.markdown(f"### Found {total_results} results for '{search_query}'")
        st.markdown("---")
        
        if results["companies"]:
            st.subheader(f"🏢 Companies ({len(results['companies'])})")
            for company in results["companies"]:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{company['name']}** ({company['ticker']})")
                        st.caption(company['description'])
                    with col2:
                        st.caption(company['sector'])
                        st.caption(f"Market Cap: {company['market_cap']}")
                st.markdown("---")
        
        if results["news"]:
            st.subheader(f"📰 News ({len(results['news'])})")
            for news in results["news"]:
                with st.container():
                    st.markdown(f"**{news['headline']}**")
                    st.caption(f"{news['company']} | {news['sector']} | {news['source']}")
                    st.markdown(news['summary'])
                st.markdown("---")
        
        if results["earnings"]:
            st.subheader(f"📈 Earnings ({len(results['earnings'])})")
            for earning in results["earnings"]:
                with st.container():
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"**{earning['company']}**")
                        st.caption(f"{earning['ticker']} | {earning['sector']}")
                    with col2:
                        st.caption(f"Quarter: {earning['quarter']}")
                        st.caption(f"Date: {earning['date'].strftime('%Y-%m-%d')}")
                    with col3:
                        st.caption(f"Status: {earning['status']}")
                        if earning['status'] == 'Reported':
                            st.caption(f"Result: {earning.get('beat_miss', 'N/A')}")
                st.markdown("---")
        
        if results["roundtables"]:
            st.subheader(f"💡 Roundtable Insights ({len(results['roundtables'])})")
            for roundtable in results["roundtables"]:
                with st.expander(f"{roundtable['executive']} - {roundtable['company_background']}"):
                    st.markdown(f"**Date:** {roundtable['date'].strftime('%B %d, %Y')}")
                    st.markdown(f"**Sector:** {roundtable['sector']}")
                    st.markdown(f"**Topics:** {', '.join(roundtable['topics'])}")
                    st.markdown("---")
                    st.markdown("**Key Insights:**")
                    st.info(roundtable['key_insights'])
        
        if total_results == 0:
            st.info("No results found. Try different search terms.")
    else:
        st.info("👆 Enter a search term above to find relevant information across the portal.")
