"""
TMT Data Module - Now using PostgreSQL database
All functions have been updated to pull from the database instead of static dictionaries
"""
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for db imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.db_operations import (
    get_all_companies as db_get_all_companies,
    get_companies_by_sector as db_get_companies_by_sector,
    get_companies_by_sub_sector as db_get_companies_by_sub_sector,
    get_all_sub_sectors as db_get_all_sub_sectors,
    get_sub_sectors_by_sector as db_get_sub_sectors_by_sector,
    get_news_feed as db_get_news_feed,
    get_earnings_calendar as db_get_earnings_calendar,
    get_roundtable_insights as db_get_roundtable_insights,
    search_all_data as db_search_all_data
)

# Legacy static data kept for seeding purposes only
TMT_COMPANIES = {
    "Technology": [
        {"name": "Apple Inc.", "ticker": "AAPL", "market_cap": "2.8T", "description": "Consumer electronics, software, and services"},
        {"name": "Microsoft Corporation", "ticker": "MSFT", "market_cap": "2.5T", "description": "Software, cloud computing, and devices"},
        {"name": "Alphabet Inc.", "ticker": "GOOGL", "market_cap": "1.7T", "description": "Search, advertising, cloud, and AI"},
        {"name": "Amazon.com Inc.", "ticker": "AMZN", "market_cap": "1.5T", "description": "E-commerce, cloud computing, and digital services"},
        {"name": "Meta Platforms Inc.", "ticker": "META", "market_cap": "1.2T", "description": "Social media, VR/AR, and digital advertising"},
        {"name": "NVIDIA Corporation", "ticker": "NVDA", "market_cap": "1.1T", "description": "Graphics processors, AI chips, and gaming"},
        {"name": "Tesla Inc.", "ticker": "TSLA", "market_cap": "800B", "description": "Electric vehicles and energy solutions"},
        {"name": "Salesforce Inc.", "ticker": "CRM", "market_cap": "250B", "description": "Cloud-based CRM and enterprise software"},
    ],
    "Media": [
        {"name": "Walt Disney Company", "ticker": "DIS", "market_cap": "180B", "description": "Entertainment, streaming, and theme parks"},
        {"name": "Netflix Inc.", "ticker": "NFLX", "market_cap": "200B", "description": "Streaming entertainment services"},
        {"name": "Comcast Corporation", "ticker": "CMCSA", "market_cap": "150B", "description": "Media, entertainment, and communications"},
        {"name": "Warner Bros. Discovery", "ticker": "WBD", "market_cap": "30B", "description": "Media and entertainment content"},
        {"name": "Paramount Global", "ticker": "PARA", "market_cap": "10B", "description": "Media, streaming, and broadcasting"},
        {"name": "Spotify Technology", "ticker": "SPOT", "market_cap": "50B", "description": "Audio streaming platform"},
        {"name": "The New York Times", "ticker": "NYT", "market_cap": "8B", "description": "Digital and print journalism"},
        {"name": "News Corporation", "ticker": "NWSA", "market_cap": "15B", "description": "News media and publishing"},
    ],
    "Telecom": [
        {"name": "Verizon Communications", "ticker": "VZ", "market_cap": "170B", "description": "Wireless and broadband communications"},
        {"name": "AT&T Inc.", "ticker": "T", "market_cap": "150B", "description": "Telecommunications and media services"},
        {"name": "T-Mobile US Inc.", "ticker": "TMUS", "market_cap": "200B", "description": "Wireless communications services"},
        {"name": "Cisco Systems Inc.", "ticker": "CSCO", "market_cap": "200B", "description": "Networking equipment and software"},
        {"name": "Qualcomm Inc.", "ticker": "QCOM", "market_cap": "180B", "description": "Wireless technology and semiconductors"},
        {"name": "Motorola Solutions", "ticker": "MSI", "market_cap": "60B", "description": "Communications infrastructure and devices"},
        {"name": "Crown Castle Inc.", "ticker": "CCI", "market_cap": "40B", "description": "Communications infrastructure"},
        {"name": "Lumen Technologies", "ticker": "LUMN", "market_cap": "6B", "description": "Fiber optic and network services"},
    ]
}

NEWS_DATA = [
    {
        "date": datetime.now() - timedelta(hours=2),
        "sector": "Technology",
        "company": "Apple Inc.",
        "headline": "Apple Announces New AI Features for iPhone 16",
        "summary": "Apple unveils groundbreaking AI capabilities integrated into iOS 18, focusing on privacy-first approach to machine learning.",
        "source": "Tech News Daily"
    },
    {
        "date": datetime.now() - timedelta(hours=5),
        "sector": "Media",
        "company": "Netflix Inc.",
        "headline": "Netflix Subscriber Growth Exceeds Expectations in Q3",
        "summary": "Streaming giant adds 8.2M subscribers, driven by password sharing crackdown and content investments.",
        "source": "Media Insider"
    },
    {
        "date": datetime.now() - timedelta(hours=8),
        "sector": "Telecom",
        "company": "T-Mobile US Inc.",
        "headline": "T-Mobile Expands 5G Ultra Capacity Network to Rural Areas",
        "summary": "Carrier announces significant infrastructure investment to bring high-speed 5G to underserved markets.",
        "source": "Telecom Weekly"
    },
    {
        "date": datetime.now() - timedelta(days=1),
        "sector": "Technology",
        "company": "Microsoft Corporation",
        "headline": "Microsoft Azure Revenue Growth Accelerates with AI Services",
        "summary": "Cloud division posts 29% YoY growth as enterprises adopt AI-powered solutions and OpenAI integrations.",
        "source": "Cloud Computing Today"
    },
    {
        "date": datetime.now() - timedelta(days=1),
        "sector": "Media",
        "company": "Walt Disney Company",
        "headline": "Disney+ Raises Prices Amid Content Expansion",
        "summary": "Streaming service increases subscription fees while announcing major content deals and exclusive releases.",
        "source": "Entertainment News"
    },
    {
        "date": datetime.now() - timedelta(days=2),
        "sector": "Telecom",
        "company": "AT&T Inc.",
        "headline": "AT&T Reports Strong Fiber Broadband Additions",
        "summary": "Telecom giant adds 273K fiber subscribers, demonstrating success of infrastructure investment strategy.",
        "source": "Broadband Journal"
    },
    {
        "date": datetime.now() - timedelta(days=2),
        "sector": "Technology",
        "company": "NVIDIA Corporation",
        "headline": "NVIDIA Unveils Next-Gen AI Chips for Data Centers",
        "summary": "New Blackwell architecture promises 30x performance improvement for large language model training.",
        "source": "Semiconductor News"
    },
    {
        "date": datetime.now() - timedelta(days=3),
        "sector": "Technology",
        "company": "Meta Platforms Inc.",
        "headline": "Meta Announces Major VR Headset Price Cuts",
        "summary": "Quest 3 price reduced by $200 as company pushes for mainstream metaverse adoption.",
        "source": "VR Today"
    },
    {
        "date": datetime.now() - timedelta(days=3),
        "sector": "Media",
        "company": "Spotify Technology",
        "headline": "Spotify Launches AI-Powered Playlist Generation",
        "summary": "Music streaming platform introduces ChatGPT-powered feature for personalized playlist creation.",
        "source": "Music Tech News"
    },
    {
        "date": datetime.now() - timedelta(days=4),
        "sector": "Telecom",
        "company": "Verizon Communications",
        "headline": "Verizon Partners with Amazon for IoT Solutions",
        "summary": "Strategic collaboration aims to deliver enterprise IoT services combining 5G and AWS cloud.",
        "source": "IoT Business News"
    },
]

EARNINGS_DATA = [
    {
        "company": "Apple Inc.",
        "ticker": "AAPL",
        "sector": "Technology",
        "date": datetime.now() + timedelta(days=3),
        "quarter": "Q4 2024",
        "consensus_eps": "$1.54",
        "consensus_revenue": "$89.5B",
        "status": "Upcoming"
    },
    {
        "company": "Microsoft Corporation",
        "ticker": "MSFT",
        "sector": "Technology",
        "date": datetime.now() + timedelta(days=7),
        "quarter": "Q4 2024",
        "consensus_eps": "$2.65",
        "consensus_revenue": "$56.2B",
        "status": "Upcoming"
    },
    {
        "company": "Alphabet Inc.",
        "ticker": "GOOGL",
        "sector": "Technology",
        "date": datetime.now() + timedelta(days=10),
        "quarter": "Q4 2024",
        "consensus_eps": "$1.85",
        "consensus_revenue": "$76.3B",
        "status": "Upcoming"
    },
    {
        "company": "Meta Platforms Inc.",
        "ticker": "META",
        "sector": "Technology",
        "date": datetime.now() - timedelta(days=2),
        "quarter": "Q3 2024",
        "consensus_eps": "$4.50",
        "actual_eps": "$4.72",
        "consensus_revenue": "$38.5B",
        "actual_revenue": "$39.1B",
        "status": "Reported",
        "beat_miss": "Beat"
    },
    {
        "company": "Amazon.com Inc.",
        "ticker": "AMZN",
        "sector": "Technology",
        "date": datetime.now() + timedelta(days=14),
        "quarter": "Q4 2024",
        "consensus_eps": "$1.12",
        "consensus_revenue": "$155.3B",
        "status": "Upcoming"
    },
    {
        "company": "Netflix Inc.",
        "ticker": "NFLX",
        "sector": "Media",
        "date": datetime.now() - timedelta(days=5),
        "quarter": "Q3 2024",
        "consensus_eps": "$4.52",
        "actual_eps": "$4.88",
        "consensus_revenue": "$8.5B",
        "actual_revenue": "$8.7B",
        "status": "Reported",
        "beat_miss": "Beat"
    },
    {
        "company": "Walt Disney Company",
        "ticker": "DIS",
        "sector": "Media",
        "date": datetime.now() + timedelta(days=21),
        "quarter": "Q4 2024",
        "consensus_eps": "$1.10",
        "consensus_revenue": "$22.3B",
        "status": "Upcoming"
    },
    {
        "company": "Verizon Communications",
        "ticker": "VZ",
        "sector": "Telecom",
        "date": datetime.now() + timedelta(days=5),
        "quarter": "Q4 2024",
        "consensus_eps": "$1.19",
        "consensus_revenue": "$33.2B",
        "status": "Upcoming"
    },
    {
        "company": "T-Mobile US Inc.",
        "ticker": "TMUS",
        "sector": "Telecom",
        "date": datetime.now() - timedelta(days=8),
        "quarter": "Q3 2024",
        "consensus_eps": "$2.40",
        "actual_eps": "$2.61",
        "consensus_revenue": "$19.8B",
        "actual_revenue": "$20.2B",
        "status": "Reported",
        "beat_miss": "Beat"
    },
    {
        "company": "AT&T Inc.",
        "ticker": "T",
        "sector": "Telecom",
        "date": datetime.now() + timedelta(days=12),
        "quarter": "Q4 2024",
        "consensus_eps": "$0.57",
        "consensus_revenue": "$31.5B",
        "status": "Upcoming"
    },
]

ROUNDTABLE_DATA = [
    {
        "date": datetime.now() - timedelta(days=1),
        "executive": "Former Meta VP of Product",
        "company_background": "Meta Platforms",
        "sector": "Technology",
        "topics": ["AI Strategy", "VR/AR Development", "Content Moderation"],
        "key_insights": "Discussed Meta's pivot to AI and the challenges of balancing innovation with regulatory compliance. Highlighted significant internal debates about VR investment ROI. Emphasized that content moderation costs are higher than publicly disclosed.",
        "attendees": 8,
        "client_firms": ["Goldman Sachs", "Morgan Stanley", "JP Morgan"]
    },
    {
        "date": datetime.now() - timedelta(days=5),
        "executive": "Former Netflix CFO",
        "company_background": "Netflix Inc.",
        "sector": "Media",
        "topics": ["Streaming Economics", "Content Investment", "International Growth"],
        "key_insights": "Revealed that password sharing crackdown has exceeded internal expectations. International markets showing stronger growth than anticipated. Content budget optimization through data analytics is becoming increasingly sophisticated.",
        "attendees": 12,
        "client_firms": ["Fidelity", "BlackRock", "Vanguard", "T. Rowe Price"]
    },
    {
        "date": datetime.now() - timedelta(days=7),
        "executive": "Former AT&T CTO",
        "company_background": "AT&T Inc.",
        "sector": "Telecom",
        "topics": ["5G Deployment", "Fiber Strategy", "Network Infrastructure"],
        "key_insights": "5G revenue opportunities remain unclear despite massive infrastructure spend. Fiber broadband is proving to be better ROI than expected. Edge computing integration with 5G could unlock new enterprise revenue streams.",
        "attendees": 6,
        "client_firms": ["Wells Fargo", "Citigroup"]
    },
    {
        "date": datetime.now() - timedelta(days=10),
        "executive": "Former Apple SVP of Services",
        "company_background": "Apple Inc.",
        "sector": "Technology",
        "topics": ["Services Growth", "App Store Economics", "Subscription Strategy"],
        "key_insights": "Services margin expansion is driven by scale, not pricing power. App Store regulatory challenges creating strategic uncertainty. Bundling strategy (Apple One) has higher retention but mixed profitability by component.",
        "attendees": 15,
        "client_firms": ["Berkshire Hathaway", "State Street", "Capital Group"]
    },
    {
        "date": datetime.now() - timedelta(days=12),
        "executive": "Former Amazon AWS GM",
        "company_background": "Amazon.com Inc.",
        "sector": "Technology",
        "topics": ["Cloud Competition", "AI Infrastructure", "Enterprise Sales"],
        "key_insights": "AWS market share pressure coming more from Microsoft than Google. AI workloads creating massive compute demand but margin profiles differ from traditional cloud. Enterprise customers increasingly multi-cloud, reducing switching costs.",
        "attendees": 10,
        "client_firms": ["Franklin Templeton", "Invesco", "PIMCO"]
    },
    {
        "date": datetime.now() - timedelta(days=15),
        "executive": "Former Disney Streaming Executive",
        "company_background": "Walt Disney Company",
        "sector": "Media",
        "topics": ["Disney+ Strategy", "Content ROI", "Bundling Approach"],
        "key_insights": "Disney+ profitability timeline extended due to sports content costs. Bundle with Hulu creating operational complexities. Linear TV decline accelerating faster than streaming can offset.",
        "attendees": 9,
        "client_firms": ["Fidelity", "BlackRock", "Wellington"]
    },
    {
        "date": datetime.now() - timedelta(days=18),
        "executive": "Former Verizon VP of Consumer",
        "company_background": "Verizon Communications",
        "sector": "Telecom",
        "topics": ["Wireless Competition", "Fixed Wireless", "Customer Retention"],
        "key_insights": "Fixed wireless access (FWA) is a game changer for broadband market. Customer churn improving but promotional intensity remains high. Premium unlimited plan attachment rates critical to ARPU growth.",
        "attendees": 7,
        "client_firms": ["AllianceBernstein", "Neuberger Berman"]
    },
    {
        "date": datetime.now() - timedelta(days=21),
        "executive": "Former Microsoft Azure Director",
        "company_background": "Microsoft Corporation",
        "sector": "Technology",
        "topics": ["Azure Growth", "AI Integration", "Enterprise Adoption"],
        "key_insights": "OpenAI partnership creating significant competitive advantages. Azure adoption accelerating in financial services and healthcare. Microsoft 365 + Azure integration driving enterprise lock-in.",
        "attendees": 11,
        "client_firms": ["T. Rowe Price", "Capital Group", "MFS"]
    },
    {
        "date": datetime.now() - timedelta(days=24),
        "executive": "Former Spotify VP of Product",
        "company_background": "Spotify Technology",
        "sector": "Media",
        "topics": ["Podcasting Strategy", "Music Economics", "AI Features"],
        "key_insights": "Podcasting investment not yet delivering expected returns. Music label negotiations becoming more challenging. AI-driven discovery improving engagement metrics significantly.",
        "attendees": 6,
        "client_firms": ["Baillie Gifford", "Ark Invest"]
    },
    {
        "date": datetime.now() - timedelta(days=28),
        "executive": "Former T-Mobile Network Officer",
        "company_background": "T-Mobile US Inc.",
        "sector": "Telecom",
        "topics": ["Network Coverage", "Sprint Integration", "5G Home Internet"],
        "key_insights": "Sprint integration ahead of schedule on network synergies. 5G home internet TAM larger than initially projected. Un-carrier strategy evolution needed as market commoditizes.",
        "attendees": 8,
        "client_firms": ["Janus Henderson", "Dimensional Fund"]
    },
    {
        "date": datetime.now() - timedelta(days=30),
        "executive": "Former NVIDIA Enterprise GM",
        "company_background": "NVIDIA Corporation",
        "sector": "Technology",
        "topics": ["AI Chip Demand", "Data Center Growth", "Competition"],
        "key_insights": "AI chip demand exceeding supply by wide margin. Enterprise AI adoption still early innings. AMD and custom chip competition real but not immediate threat to dominance.",
        "attendees": 14,
        "client_firms": ["Fidelity", "Vanguard", "BlackRock", "State Street"]
    },
    {
        "date": datetime.now() - timedelta(days=35),
        "executive": "Former Comcast Cable President",
        "company_background": "Comcast Corporation",
        "sector": "Media",
        "topics": ["Broadband Competition", "Streaming Strategy", "Cable Cord-Cutting"],
        "key_insights": "Broadband subscriber trends stabilizing but growth era over. Peacock strategy still evolving, profitability uncertain. Cable video business in managed decline, focus on broadband and business services.",
        "attendees": 9,
        "client_firms": ["Dodge & Cox", "Primecap"]
    },
]

# Public API - all functions now use database
def get_all_companies():
    """Get all companies from database"""
    try:
        return db_get_all_companies()
    except Exception as e:
        print(f"Error fetching companies: {e}")
        return []

def get_companies_by_sector(sector):
    """Get companies by sector from database"""
    try:
        return db_get_companies_by_sector(sector)
    except Exception as e:
        print(f"Error fetching companies by sector: {e}")
        return []

def get_companies_by_sub_sector(sub_sector):
    """Get companies by sub-sector from database"""
    try:
        return db_get_companies_by_sub_sector(sub_sector)
    except Exception as e:
        print(f"Error fetching companies by sub-sector: {e}")
        return []

def get_all_sub_sectors():
    """Get all sub-sectors from database"""
    try:
        return db_get_all_sub_sectors()
    except Exception as e:
        print(f"Error fetching sub-sectors: {e}")
        return []

def get_sub_sectors_by_sector(sector):
    """Get sub-sectors for a specific sector from database"""
    try:
        return db_get_sub_sectors_by_sector(sector)
    except Exception as e:
        print(f"Error fetching sub-sectors by sector: {e}")
        return []

def get_news_feed(sector_filter=None, company_filter=None):
    """Get news feed from database with optional filters"""
    try:
        # Convert "All" to None for database queries
        if sector_filter == "All":
            sector_filter = None
        if company_filter == "All":
            company_filter = None
        return db_get_news_feed(sector_filter, company_filter)
    except Exception as e:
        print(f"Error fetching news feed: {e}")
        return []

def get_earnings_calendar(status_filter=None):
    """Get earnings calendar from database with optional status filter"""
    try:
        # Convert "All" to None for database queries
        if status_filter == "All":
            status_filter = None
        return db_get_earnings_calendar(status_filter)
    except Exception as e:
        print(f"Error fetching earnings calendar: {e}")
        return []

def get_roundtable_insights(sector_filter=None):
    """Get roundtable insights from database with optional sector filter"""
    try:
        # Convert "All" to None for database queries
        if sector_filter == "All":
            sector_filter = None
        return db_get_roundtable_insights(sector_filter)
    except Exception as e:
        print(f"Error fetching roundtable insights: {e}")
        return []

def search_all_data(query):
    """Search across all data in database"""
    try:
        return db_search_all_data(query)
    except Exception as e:
        print(f"Error searching data: {e}")
        return {"companies": [], "news": [], "earnings": [], "roundtables": []}
