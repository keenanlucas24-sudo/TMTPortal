"""
Earnings Data Integration Module

This module provides integration with financial data APIs for real-time earnings calendar,
consensus estimates, and actual results. Supports multiple providers:
- Alpha Vantage (free tier available)
- Financial Modeling Prep (FMP)
- Finnhub (comprehensive financial data)

To use:
1. Set your API key as an environment variable (ALPHA_VANTAGE_KEY, FMP_API_KEY, or FINNHUB_API_KEY)
2. Call fetch_earnings_calendar() to get upcoming earnings
3. The data is automatically formatted to match our database schema
"""

import os
import requests
from datetime import datetime
from typing import List, Dict, Optional
from db.db_operations import add_earnings_item

class EarningsAPIIntegration:
    """Integration class for fetching real-time earnings data"""
    
    def __init__(self, provider: str = "alpha_vantage"):
        """
        Initialize the earnings API integration
        
        Args:
            provider: API provider to use ('alpha_vantage', 'fmp', or 'finnhub')
        """
        self.provider = provider
        
        if provider == "alpha_vantage":
            self.api_key = os.getenv("ALPHA_VANTAGE_KEY")
            self.base_url = "https://www.alphavantage.co/query"
        elif provider == "fmp":
            self.api_key = os.getenv("FMP_API_KEY")
            self.base_url = "https://financialmodelingprep.com/api/v3"
        elif provider == "finnhub":
            self.api_key = os.getenv("FINNHUB_API_KEY")
            self.base_url = "https://finnhub.io/api/v1"
        else:
            raise ValueError(f"Unsupported provider: {provider}. Choose 'alpha_vantage', 'fmp', or 'finnhub'.")
    
    def fetch_earnings_calendar(self, symbol: Optional[str] = None, 
                                horizon: str = "3month") -> List[Dict]:
        """
        Fetch earnings calendar data from the API
        
        Args:
            symbol: Stock ticker symbol (optional, fetches all if None)
            horizon: Time horizon for upcoming earnings (3month, 6month, 12month)
            
        Returns:
            List of earnings events with dates, estimates, and actuals
        """
        if not self.api_key:
            raise ValueError(f"API key not found. Set {self.provider.upper()}_API_KEY environment variable.")
        
        if self.provider == "alpha_vantage":
            return self._fetch_alpha_vantage_earnings(symbol, horizon)
        elif self.provider == "fmp":
            return self._fetch_fmp_earnings(symbol, horizon)
        elif self.provider == "finnhub":
            return self._fetch_finnhub_earnings(symbol, horizon)
    
    def _fetch_alpha_vantage_earnings(self, symbol: Optional[str], 
                                     horizon: str) -> List[Dict]:
        """Fetch earnings from Alpha Vantage API"""
        params = {
            "function": "EARNINGS_CALENDAR",
            "horizon": horizon,
            "apikey": self.api_key
        }
        
        if symbol:
            params["symbol"] = symbol
        
        response = requests.get(self.base_url, params=params)
        
        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code}")
        
        # Alpha Vantage returns CSV, parse it
        earnings_list = []
        lines = response.text.strip().split('\n')
        
        if len(lines) > 1:
            headers = lines[0].split(',')
            for line in lines[1:]:
                values = line.split(',')
                if len(values) >= len(headers):
                    earnings_list.append(dict(zip(headers, values)))
        
        return self._normalize_earnings_data(earnings_list, "alpha_vantage")
    
    def _fetch_fmp_earnings(self, symbol: Optional[str], horizon: str) -> List[Dict]:
        """Fetch earnings from Financial Modeling Prep API"""
        # Map horizon to date range
        from datetime import datetime, timedelta
        today = datetime.now()
        
        if horizon == "3month":
            end_date = today + timedelta(days=90)
        elif horizon == "6month":
            end_date = today + timedelta(days=180)
        else:
            end_date = today + timedelta(days=365)
        
        endpoint = f"{self.base_url}/earning_calendar"
        params = {
            "from": today.strftime("%Y-%m-%d"),
            "to": end_date.strftime("%Y-%m-%d"),
            "apikey": self.api_key
        }
        
        response = requests.get(endpoint, params=params)
        
        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code}")
        
        earnings_list = response.json()
        
        if symbol:
            earnings_list = [e for e in earnings_list if e.get("symbol") == symbol]
        
        return self._normalize_earnings_data(earnings_list, "fmp")
    
    def _fetch_finnhub_earnings(self, symbol: Optional[str], horizon: str) -> List[Dict]:
        """Fetch earnings from Finnhub API"""
        from datetime import datetime, timedelta
        today = datetime.now()
        
        if horizon == "3month":
            end_date = today + timedelta(days=90)
        elif horizon == "6month":
            end_date = today + timedelta(days=180)
        else:
            end_date = today + timedelta(days=365)
        
        # Finnhub earnings calendar endpoint
        endpoint = f"{self.base_url}/calendar/earnings"
        params = {
            "from": today.strftime("%Y-%m-%d"),
            "to": end_date.strftime("%Y-%m-%d"),
            "token": self.api_key
        }
        
        if symbol:
            params["symbol"] = symbol
        
        response = requests.get(endpoint, params=params)
        
        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code} - {response.text}")
        
        data = response.json()
        earnings_list = data.get("earningsCalendar", [])
        
        return self._normalize_earnings_data(earnings_list, "finnhub")
    
    def _normalize_earnings_data(self, raw_data: List[Dict], 
                                 source: str) -> List[Dict]:
        """
        Normalize earnings data to our database schema
        
        Returns data in format:
        {
            'company': str,
            'ticker': str,
            'sector': str,
            'date': datetime,
            'quarter': str,
            'consensus_eps': str,
            'actual_eps': str,
            'consensus_revenue': str,
            'actual_revenue': str,
            'status': str,
            'beat_miss': str,
            'key_analyst_focus': str (optional)
        }
        """
        normalized = []
        
        for item in raw_data:
            try:
                if source == "alpha_vantage":
                    # Parse actual EPS if reported
                    actual_eps = item.get('actual')
                    is_reported = actual_eps is not None and actual_eps != ''
                    
                    normalized_item = {
                        'ticker': item.get('symbol', ''),
                        'company': item.get('name', item.get('symbol', '')),
                        'date': datetime.strptime(item.get('reportDate', ''), '%Y-%m-%d'),
                        'quarter': item.get('fiscalDateEnding', '')[:7],  # YYYY-MM format
                        'consensus_eps': str(item.get('estimate', 'N/A')),
                        'actual_eps': str(actual_eps) if is_reported else None,
                        'consensus_revenue': 'N/A',  # Alpha Vantage doesn't provide revenue estimates
                        'actual_revenue': None,
                        'status': 'Reported' if is_reported else 'Upcoming',
                        'sector': 'Technology',  # Would need company lookup for accurate sector
                        'key_analyst_focus': None  # Can be manually populated or set via provider notes
                    }
                    
                    # Determine beat/miss if reported
                    if is_reported:
                        try:
                            actual = float(actual_eps)
                            estimate = float(item.get('estimate', 0))
                            normalized_item['beat_miss'] = 'Beat' if actual >= estimate else 'Miss'
                        except (ValueError, TypeError):
                            normalized_item['beat_miss'] = 'N/A'
                
                elif source == "fmp":
                    is_reported = item.get('eps') is not None
                    
                    normalized_item = {
                        'ticker': item.get('symbol', ''),
                        'company': item.get('symbol', ''),  # FMP doesn't always include full name
                        'date': datetime.strptime(item.get('date', ''), '%Y-%m-%d'),
                        'quarter': item.get('fiscalDateEnding', 'Q?'),
                        'consensus_eps': str(item.get('epsEstimated', 'N/A')),
                        'actual_eps': str(item.get('eps')) if is_reported else None,
                        'consensus_revenue': str(item.get('revenueEstimated', 'N/A')),
                        'actual_revenue': str(item.get('revenue')) if item.get('revenue') else None,
                        'status': 'Reported' if is_reported else 'Upcoming',
                        'sector': 'Technology',  # Would need company lookup for accurate sector
                        'key_analyst_focus': None  # Can be populated based on company/sector analysis
                    }
                    
                    # Determine beat/miss if reported
                    if is_reported:
                        try:
                            actual = float(item.get('eps', 0))
                            estimate = float(item.get('epsEstimated', 0))
                            normalized_item['beat_miss'] = 'Beat' if actual >= estimate else 'Miss'
                        except (ValueError, TypeError):
                            normalized_item['beat_miss'] = 'N/A'
                    else:
                        normalized_item['beat_miss'] = None
                
                elif source == "finnhub":
                    # Finnhub provides: symbol, date, epsActual, epsEstimate, revenueActual, revenueEstimate, quarter, year
                    is_reported = item.get('epsActual') is not None
                    
                    # Construct quarter string from year and quarter
                    year = item.get('year', '')
                    quarter = item.get('quarter', '')
                    quarter_str = f"{year}-Q{quarter}" if year and quarter else 'Q?'
                    
                    normalized_item = {
                        'ticker': item.get('symbol', ''),
                        'company': item.get('symbol', ''),  # Finnhub doesn't always include company name
                        'date': datetime.strptime(item.get('date', ''), '%Y-%m-%d'),
                        'quarter': quarter_str,
                        'consensus_eps': str(item.get('epsEstimate', 'N/A')),
                        'actual_eps': str(item.get('epsActual')) if is_reported else None,
                        'consensus_revenue': str(item.get('revenueEstimate', 'N/A')),
                        'actual_revenue': str(item.get('revenueActual')) if item.get('revenueActual') else None,
                        'status': 'Reported' if is_reported else 'Upcoming',
                        'sector': 'Technology',  # Would need company lookup for accurate sector
                        'key_analyst_focus': None  # Can be populated based on company/sector analysis
                    }
                    
                    # Determine beat/miss if reported
                    if is_reported:
                        try:
                            actual = float(item.get('epsActual', 0))
                            estimate = float(item.get('epsEstimate', 0))
                            normalized_item['beat_miss'] = 'Beat' if actual >= estimate else 'Miss'
                        except (ValueError, TypeError):
                            normalized_item['beat_miss'] = 'N/A'
                    else:
                        normalized_item['beat_miss'] = None
                
                normalized.append(normalized_item)
            
            except (KeyError, ValueError) as e:
                # Skip malformed entries
                print(f"Warning: Skipping malformed earnings entry: {e}")
                continue
        
        return normalized
    
    def sync_to_database(self, earnings_data: List[Dict]) -> int:
        """
        Sync fetched earnings data to the database
        
        Args:
            earnings_data: List of normalized earnings dictionaries
            
        Returns:
            Number of records inserted
        """
        count = 0
        for earning in earnings_data:
            try:
                add_earnings_item(
                    company=earning.get('company', ''),
                    ticker=earning.get('ticker', ''),
                    sector=earning.get('sector', 'Technology'),
                    date=earning.get('date'),
                    quarter=earning.get('quarter', ''),
                    consensus_eps=earning.get('consensus_eps'),
                    actual_eps=earning.get('actual_eps'),
                    consensus_revenue=earning.get('consensus_revenue'),
                    actual_revenue=earning.get('actual_revenue'),
                    status=earning.get('status', 'Upcoming'),
                    beat_miss=earning.get('beat_miss'),
                    key_analyst_focus=earning.get('key_analyst_focus')
                )
                count += 1
            except Exception as e:
                print(f"Error inserting earnings for {earning.get('ticker')}: {e}")
        
        return count


# Example usage
if __name__ == "__main__":
    # Example: Fetch Alpha Vantage earnings
    # Set ALPHA_VANTAGE_KEY environment variable first
    
    # integration = EarningsAPIIntegration(provider="alpha_vantage")
    # earnings = integration.fetch_earnings_calendar()
    # print(f"Fetched {len(earnings)} earnings events")
    # synced = integration.sync_to_database(earnings)
    # print(f"Synced {synced} records to database")
    
    print("Earnings API integration ready.")
    print("Set ALPHA_VANTAGE_KEY or FMP_API_KEY environment variable to use.")
