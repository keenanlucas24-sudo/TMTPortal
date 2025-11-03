# TMT Research Portal

## Overview
The TMT Research Portal is a Streamlit-based web application designed to provide comprehensive research and insights for Technology, Media, and Telecom (TMT) companies. It aggregates information from various data sources, including company profiles, news feeds, earnings calendars, and executive roundtable insights, to offer a centralized hub for TMT industry research and analysis. The project aims to provide a robust tool for analyzing market trends, company performance, and industry-specific news within the TMT sector.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
The application uses Streamlit for rapid development, featuring a multi-page architecture with modular organization. Key pages include a Dashboard with company search and volatility widgets, a Companies directory with hierarchical filtering, a Unified News feed combining various sources, an Earnings Calendar, a comprehensive Company Detail page, and a global AI Assistant accessible via the sidebar. Global sector filtering is implemented using sidebar buttons, persisting across relevant pages via session state. The layout is wide, utilizing Streamlit's column system for responsiveness.

### Backend Architecture
A PostgreSQL database with `psycopg2` is used for data persistence, storing company data (over 134 TMT companies with detailed sub-sector classifications), news articles, social media news (with Gemini AI analysis for tickers, sentiment, and relevance), earnings data, and executive roundtable insights. The business logic is managed through Python functions in `db/db_operations.py` for efficient data querying and manipulation. Web scraping for content enrichment is handled by Trafilatura. Search functionality allows cross-collection text matching across all data types. Streamlit's session state and widget keys manage application state and filter persistence.

## External Dependencies

### Core Frameworks
- **Streamlit**: Python web application framework.
- **Pandas**: Data manipulation and analysis.

### Web Scraping
- **Trafilatura**: For extracting clean text content from web pages.

### Database
- **PostgreSQL**: Relational database, accessed via `psycopg2-binary`.

### API Integrations
- **News Feed**: Aggregates from Finnhub, Alpha Vantage, and Marketaux for diverse news sources, with intelligent deduplication.
- **Earnings Data**: Primarily uses Alpha Vantage for real-time earnings calendars, estimates, and actuals.
- **Social News**: Integrates `twscrape` for fetching tweets from financial accounts. Gemini 2.5 Flash model analyzes tweets for tickers, sentiment, relevance, and generates headlines/summaries.
- **Volatility Screener**: Utilizes Finnhub/Alpha Vantage APIs to track stock prices for all TMT companies, with database caching and chunked refresh to manage API limits.