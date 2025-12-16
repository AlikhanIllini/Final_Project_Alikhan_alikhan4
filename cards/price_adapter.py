"""
Stock price adapter with caching and manual fallback.
Uses yfinance for fetching U.S. stock prices.
"""

import yfinance as yf
from datetime import datetime, timedelta
from django.core.cache import cache
from django.utils import timezone
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class StockPriceAdapter:
    """
    Adapter for fetching stock prices with built-in caching.
    Falls back to manual entry when API fails or rate limits are reached.
    """

    CACHE_TIMEOUT = 60 * 15  # 15 minutes cache

    def __init__(self):
        self.cache_prefix = 'stock_price_'

    def get_stock_price(self, ticker):
        """
        Get current stock price for a ticker.

        Args:
            ticker (str): Stock ticker symbol (e.g., 'AAPL')

        Returns:
            dict: {
                'price': Decimal,
                'volume': int,
                'timestamp': datetime,
                'company_name': str,
                'source': 'api' or 'cache' or 'error'
            }
            Returns None if fetch fails
        """
        ticker = ticker.upper().strip()

        # Check cache first
        cache_key = f"{self.cache_prefix}{ticker}"
        cached_data = cache.get(cache_key)

        if cached_data:
            logger.info(f"Cache hit for {ticker}")
            cached_data['source'] = 'cache'
            return cached_data

        # Fetch from API using historical data (more reliable than info)
        try:
            stock = yf.Ticker(ticker)

            # Get most recent day's data
            hist = stock.history(period='1d')

            if hist.empty:
                logger.warning(f"No price data available for {ticker}")
                return None

            # Get the latest close price
            latest = hist.iloc[-1]
            price = latest['Close']
            volume = int(latest['Volume']) if 'Volume' in latest else 0

            # Try to get company name from info (but don't fail if it errors)
            company_name = ''
            exchange = ''
            try:
                info = stock.info
                company_name = info.get('longName', info.get('shortName', ''))
                exchange = info.get('exchange', '')
            except Exception as e:
                logger.warning(f"Could not fetch company info for {ticker}: {str(e)}")

            data = {
                'price': Decimal(str(price)),
                'volume': volume,
                'timestamp': timezone.now(),
                'company_name': company_name,
                'exchange': exchange,
                'source': 'api'
            }

            # Cache the result
            cache.set(cache_key, data, self.CACHE_TIMEOUT)
            logger.info(f"Successfully fetched price for {ticker}: ${price}")

            return data

        except Exception as e:
            logger.error(f"Failed to fetch price for {ticker}: {str(e)}")
            return None

    def get_historical_prices(self, ticker, days=30):
        """
        Get historical price data for a ticker.

        Args:
            ticker (str): Stock ticker symbol
            days (int): Number of days of history to fetch

        Returns:
            list: List of dicts with 'date', 'price', 'volume'
            Returns empty list if fetch fails
        """
        ticker = ticker.upper().strip()

        try:
            stock = yf.Ticker(ticker)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Fetch historical data
            hist = stock.history(start=start_date, end=end_date)

            if hist.empty:
                logger.warning(f"No historical data for {ticker}")
                return []

            # Convert to list of dicts
            historical_data = []
            for date, row in hist.iterrows():
                historical_data.append({
                    'date': date,
                    'price': Decimal(str(row['Close'])),
                    'volume': int(row['Volume']) if 'Volume' in row else 0,
                })

            logger.info(f"Fetched {len(historical_data)} historical prices for {ticker}")
            return historical_data

        except Exception as e:
            logger.error(f"Failed to fetch historical data for {ticker}: {str(e)}")
            return []

    def validate_ticker(self, ticker):
        """
        Check if a ticker symbol is valid.

        Args:
            ticker (str): Stock ticker symbol

        Returns:
            bool: True if valid, False otherwise
        """
        ticker = ticker.upper().strip()

        try:
            stock = yf.Ticker(ticker)
            # Try to get recent history - more reliable than info
            hist = stock.history(period='5d')

            # Valid if we got any data
            return not hist.empty

        except Exception as e:
            logger.error(f"Ticker validation failed for {ticker}: {str(e)}")
            return False

    def get_stock_info(self, ticker):
        """
        Get comprehensive stock information.

        Args:
            ticker (str): Stock ticker symbol

        Returns:
            dict: Stock information including company name, sector, etc.
            Returns None if fetch fails
        """
        ticker = ticker.upper().strip()

        try:
            stock = yf.Ticker(ticker)

            # Try to get info, but use basic data if it fails
            try:
                info = stock.info
                return {
                    'ticker': ticker,
                    'company_name': info.get('longName', info.get('shortName', ticker)),
                    'sector': info.get('sector', ''),
                    'industry': info.get('industry', ''),
                    'exchange': info.get('exchange', ''),
                    'currency': info.get('currency', 'USD'),
                    'market_cap': info.get('marketCap'),
                }
            except Exception as info_error:
                logger.warning(f"Could not fetch full info for {ticker}, using basic data: {str(info_error)}")
                # Return basic info without requiring info API
                return {
                    'ticker': ticker,
                    'company_name': ticker,
                    'sector': '',
                    'industry': '',
                    'exchange': '',
                    'currency': 'USD',
                    'market_cap': None,
                }

        except Exception as e:
            logger.error(f"Failed to fetch info for {ticker}: {str(e)}")
            return None

    def clear_cache(self, ticker=None):
        """
        Clear cached price data.

        Args:
            ticker (str, optional): Specific ticker to clear. If None, clears all.
        """
        if ticker:
            cache_key = f"{self.cache_prefix}{ticker.upper()}"
            cache.delete(cache_key)
            logger.info(f"Cleared cache for {ticker}")
        else:
            # This would require a cache backend that supports pattern deletion
            logger.info("Clear all cache not implemented for this backend")


# Singleton instance
price_adapter = StockPriceAdapter()

