"""
Stock price adapter with caching and manual fallback.
Uses yfinance for fetching U.S. stock prices with multiple fallback methods.
"""

import yfinance as yf
from datetime import datetime, timedelta
from django.core.cache import cache
from django.utils import timezone
from decimal import Decimal
import logging
import time

logger = logging.getLogger(__name__)


class StockPriceAdapter:
    """
    Adapter for fetching stock prices with built-in caching.
    Uses multiple methods to ensure reliability.
    Falls back to manual entry when all methods fail.
    """

    CACHE_TIMEOUT = 60 * 15  # 15 minutes cache

    def __init__(self):
        self.cache_prefix = 'stock_price_'

    def get_stock_price(self, ticker):
        """
        Get current stock price for a ticker using multiple fallback methods.

        Args:
            ticker (str): Stock ticker symbol (e.g., 'AAPL')

        Returns:
            dict: {
                'price': Decimal,
                'volume': int,
                'timestamp': datetime,
                'company_name': str,
                'source': 'api' or 'cache'
            }
            Returns None if all methods fail
        """
        ticker = ticker.upper().strip()

        # Check cache first
        cache_key = f"{self.cache_prefix}{ticker}"
        cached_data = cache.get(cache_key)

        if cached_data:
            logger.info(f"Cache hit for {ticker}")
            cached_data['source'] = 'cache'
            return cached_data

        # Try multiple methods in order
        data = None

        # Method 1: Try yf.download (most reliable)
        data = self._try_download_method(ticker)

        # Method 2: If download fails, try history method
        if not data:
            data = self._try_history_method(ticker)

        # Method 3: Try fast_info (lightweight)
        if not data:
            data = self._try_fast_info_method(ticker)

        # If we got data from any method, cache it
        if data:
            cache.set(cache_key, data, self.CACHE_TIMEOUT)
            logger.info(f"Successfully fetched price for {ticker}: ${data['price']}")
            return data

        logger.error(f"All methods failed for {ticker}")
        return None

    def _try_download_method(self, ticker):
        """Try using yf.download method."""
        try:
            # Download with minimal output
            data = yf.download(ticker, period='1d', progress=False, show_errors=False)

            if data.empty:
                return None

            # Get latest data
            latest = data.iloc[-1]
            price = latest['Close']
            volume = int(latest['Volume']) if 'Volume' in latest else 0

            # Get company name separately (optional)
            company_name = ticker  # Default to ticker
            try:
                stock = yf.Ticker(ticker)
                info = stock.fast_info
                # fast_info doesn't have company name, use ticker
            except:
                pass

            return {
                'price': Decimal(str(price)),
                'volume': volume,
                'timestamp': timezone.now(),
                'company_name': company_name,
                'exchange': '',
                'source': 'api'
            }
        except Exception as e:
            logger.debug(f"Download method failed for {ticker}: {str(e)}")
            return None

    def _try_history_method(self, ticker):
        """Try using Ticker.history method."""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1d')

            if hist.empty:
                return None

            latest = hist.iloc[-1]
            price = latest['Close']
            volume = int(latest['Volume']) if 'Volume' in latest else 0

            return {
                'price': Decimal(str(price)),
                'volume': volume,
                'timestamp': timezone.now(),
                'company_name': ticker,
                'exchange': '',
                'source': 'api'
            }
        except Exception as e:
            logger.debug(f"History method failed for {ticker}: {str(e)}")
            return None

    def _try_fast_info_method(self, ticker):
        """Try using Ticker.fast_info (lightweight API)."""
        try:
            stock = yf.Ticker(ticker)
            fast_info = stock.fast_info

            # fast_info has last_price
            price = fast_info.get('lastPrice') or fast_info.get('regularMarketPrice')

            if not price:
                return None

            return {
                'price': Decimal(str(price)),
                'volume': 0,  # fast_info doesn't always have volume
                'timestamp': timezone.now(),
                'company_name': ticker,
                'exchange': '',
                'source': 'api'
            }
        except Exception as e:
            logger.debug(f"Fast info method failed for {ticker}: {str(e)}")
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
            # Use download method for better reliability
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            data = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                progress=False,
                show_errors=False
            )

            if data.empty:
                logger.warning(f"No historical data for {ticker}")
                return []

            # Convert to list of dicts
            historical_data = []
            for date, row in data.iterrows():
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
            # Try download method - quickest validation
            data = yf.download(ticker, period='5d', progress=False, show_errors=False)

            # Valid if we got any data
            return not data.empty

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

