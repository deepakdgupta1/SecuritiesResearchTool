"""Yahoo Finance data provider for US market data.

Implements the BaseDataProvider interface using yfinance library
to fetch historical data and symbol information for US markets.
"""

import logging
from datetime import date, datetime
from typing import Dict, List, Optional

import pandas as pd
import yfinance as yf

from backend.core.constants import (
    YAHOO_RATE_LIMIT,
    MARKET_US,
    EXCHANGE_NYSE,
    EXCHANGE_NASDAQ,
    EXCHANGE_UNKNOWN,
    INTERVAL_DAILY,
    URL_SP500_WIKIPEDIA,
    COL_OPEN,
    COL_HIGH,
    COL_LOW,
    COL_CLOSE,
    COL_VOLUME,
    COL_ADJ_CLOSE,
    COL_DATE,
)
from backend.data_providers.base import (
    BaseDataProvider,
    DataProviderError,
    DataNotFoundError,
    RateLimitError,
)

logger = logging.getLogger(__name__)


class YahooFinanceProvider(BaseDataProvider):
    """Yahoo Finance data provider implementation.
    
    Provides access to US market data via yfinance library.
    
    Features:
    - Historical OHLCV data for US stocks
    - S&P 500 constituent list
    - Symbol validation
    - Automatic data validation
    
    Rate Limit: 10 requests/second (configurable)
    
    Example:
        >>> provider = YahooFinanceProvider()
        >>> data = provider.get_historical_data('AAPL', date(2020, 1, 1), date(2023, 12, 31))
        >>> symbols = provider.get_sp500_symbols()
    """
    
    def __init__(self, rate_limit: float = YAHOO_RATE_LIMIT):
        """Initialize Yahoo Finance provider.
        
        Args:
            rate_limit: Maximum requests per second (default: 10)
        """
        super().__init__(rate_limit=rate_limit)
        self.logger.info(f"Initialized YahooFinanceProvider with rate_limit={rate_limit}/s")
    
    def get_historical_data(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
        **kwargs
    ) -> pd.DataFrame:
        """Fetch historical OHLCV data from Yahoo Finance.
        
        Args:
            symbol: US ticker symbol (e.g., 'AAPL', 'MSFT')
            start_date: Start date for historical data
            end_date: End date for historical data
            **kwargs: Additional yfinance parameters (e.g., interval='1d')
            
        Returns:
            DataFrame with columns: date, open, high, low, close, volume, adjusted_close
            
        Raises:
            DataNotFoundError: If symbol data is not available
            DataProviderError: For other errors
            
        Example:
            >>> provider = YahooFinanceProvider()
            >>> df = provider.get_historical_data('AAPL', date(2023, 1, 1), date(2023, 12, 31))
            >>> print(df.head())
        """
        self._enforce_rate_limit()
        
        try:
            self.logger.debug(f"Fetching {symbol} from {start_date} to {end_date}")
            
            # Create ticker object
            ticker = yf.Ticker(symbol)
            
            # Fetch historical data
            interval = kwargs.get('interval', INTERVAL_DAILY)
            df = ticker.history(
                start=start_date,
                end=end_date,
                interval=interval,
                auto_adjust=False,  # Get raw prices and adjusted close separately
            )
            
            if df.empty:
                raise DataNotFoundError(f"No data found for symbol {symbol}")
            
            # Rename columns to match our schema
            df = df.rename(columns={
                'Open': COL_OPEN,
                'High': COL_HIGH,
                'Low': COL_LOW,
                'Close': COL_CLOSE,
                'Volume': COL_VOLUME,
                'Adj Close': COL_ADJ_CLOSE,
            })
            
            # Reset index to have date as column
            df = df.reset_index()
            df = df.rename(columns={'Date': COL_DATE})
            
            # Convert date to date object (remove time component)
            df[COL_DATE] = pd.to_datetime(df[COL_DATE]).dt.date
            
            # Select required columns
            columns = [COL_DATE, COL_OPEN, COL_HIGH, COL_LOW, COL_CLOSE, COL_VOLUME, COL_ADJ_CLOSE]
            df = df[columns]
            
            # Validate data
            if not self.validate_data(df):
                raise DataProviderError(f"Data validation failed for {symbol}")
            
            self.logger.info(f"Fetched {len(df)} rows for {symbol}")
            return df
            
        except DataNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {e}")
            raise DataProviderError(f"Failed to fetch data for {symbol}: {e}")
    
    def get_sp500_symbols(self) -> List[Dict[str, str]]:
        """Fetch S&P 500 constituent symbols from Wikipedia.
        
        Returns:
            List of dictionaries with S&P 500 company information
            
        Raises:
            DataProviderError: If unable to fetch S&P 500 list
            
        Example:
            >>> provider = YahooFinanceProvider()
            >>> symbols = provider.get_sp500_symbols()
            >>> print(f"Found {len(symbols)} S&P 500 companies")
        """
        try:
            self.logger.info("Fetching S&P 500 constituents from Wikipedia")
            
            # Fetch S&P 500 table from Wikipedia
            url = URL_SP500_WIKIPEDIA
            tables = pd.read_html(url)
            sp500_table = tables[0]
            
            # Extract relevant columns
            symbols = []
            for _, row in sp500_table.iterrows():
                symbols.append({
                    'symbol': row['Symbol'],
                    'name': row['Security'],
                    'exchange': EXCHANGE_NYSE if 'NYSE' in str(row.get('Exchange', '')) else EXCHANGE_NASDAQ,
                    'market': MARKET_US,
                    'sector': row.get('GICS Sector', 'Unknown'),
                })
            
            self.logger.info(f"Fetched {len(symbols)} S&P 500 symbols")
            return symbols
            
        except Exception as e:
            self.logger.error(f"Error fetching S&P 500 list: {e}")
            raise DataProviderError(f"Failed to fetch S&P 500 list: {e}")
    
    def get_symbols_list(self, **kwargs) -> List[Dict[str, str]]:
        """Fetch list of available symbols.
        
        For Yahoo Finance, this returns the S&P 500 list.
        For custom symbol lists, pass them via kwargs.
        
        Args:
            **kwargs: Optional 'symbols' list for custom symbols
            
        Returns:
            List of symbol dictionaries
            
        Example:
            >>> provider = YahooFinanceProvider()
            >>> # Get S&P 500
            >>> symbols = provider.get_symbols_list()
            >>> # Or provide custom list
            >>> symbols = provider.get_symbols_list(symbols=['AAPL', 'MSFT', 'GOOGL'])
        """
        custom_symbols = kwargs.get('symbols')
        
        if custom_symbols:
            # Convert custom symbols to standard format
            return [
                {
                    'symbol': symbol,
                    'name': symbol,  # Name will be fetched separately if needed
                    'exchange': EXCHANGE_UNKNOWN,
                    'market': MARKET_US,
                    'sector': 'Unknown',
                }
                for symbol in custom_symbols
            ]
        
        # Default: return S&P 500
        return self.get_sp500_symbols()
    
    def validate_symbol(self, symbol: str, **kwargs) -> bool:
        """Validate that a symbol exists in Yahoo Finance.
        
        Args:
            symbol: Ticker symbol to validate
            **kwargs: Unused
            
        Returns:
            True if symbol exists, False otherwise
            
        Example:
            >>> provider = YahooFinanceProvider()
            >>> provider.validate_symbol('AAPL')  # True
            >>> provider.validate_symbol('INVALID_SYMBOL')  # False
        """
        self._enforce_rate_limit()
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Check if we got valid info back
            if not info or 'regularMarketPrice' not in info:
                self.logger.warning(f"Symbol {symbol} not found or no data available")
                return False
            
            self.logger.debug(f"Symbol {symbol} validated successfully")
            return True
            
        except Exception as e:
            self.logger.warning(f"Error validating symbol {symbol}: {e}")
            return False
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, str]]:
        """Get detailed information about a symbol.
        
        Args:
            symbol: Ticker symbol
            
        Returns:
            Dictionary with symbol information or None if not found
            
        Example:
            >>> provider = YahooFinanceProvider()
            >>> info = provider.get_symbol_info('AAPL')
            >>> print(info['name'], info['sector'])
        """
        self._enforce_rate_limit()
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info:
                return None
            
            return {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'exchange': info.get('exchange', EXCHANGE_UNKNOWN),
                'market': MARKET_US,
                'sector': info.get('sector', 'Unknown'),
            }
            
        except Exception as e:
            self.logger.error(f"Error getting info for {symbol}: {e}")
            return None
