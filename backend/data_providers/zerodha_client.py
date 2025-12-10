"""Zerodha Kite Connect data provider for Indian market data.

Implements the BaseDataProvider interface using Kite Connect API
to fetch historical data and instrument information for Indian markets.
"""

import logging
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

import pandas as pd
from kiteconnect import KiteConnect

from backend.core.config import settings
from backend.core.constants import (
    COL_CLOSE,
    COL_DATE,
    COL_HIGH,
    COL_LOW,
    COL_OPEN,
    COL_VOLUME,
    EXCHANGE_BSE,
    EXCHANGE_NSE,
    MARKET_IN,
    ZERODHA_RATE_LIMIT,
)
from backend.data_providers.base import (
    BaseDataProvider,
    DataNotFoundError,
    DataProviderError,
)

logger = logging.getLogger(__name__)


class ZerodhaProvider(BaseDataProvider):
    """Zerodha Kite Connect data provider implementation.

    Provides access to Indian market data via Kite Connect API.

    Features:
    - Historical OHLCV data for NSE/BSE stocks
    - Instrument list for NSE/BSE
    - Symbol to instrument token mapping
    - Automatic data validation

    Rate Limit: 3 requests/second (Zerodha API limit)

    Requirements:
    - ZERODHA_API_KEY in environment
    - ZERODHA_ACCESS_TOKEN in environment

    Example:
        >>> provider = ZerodhaProvider()
        >>> data = provider.get_historical_data('RELIANCE', date(2020, 1, 1), date(2023, 12, 31))
        >>> instruments = provider.get_nse_instruments()
    """

    def __init__(self, rate_limit: float = ZERODHA_RATE_LIMIT):
        """Initialize Zerodha provider.

        Args:
            rate_limit: Maximum requests per second (default: 3, Zerodha limit)

        Raises:
            DataProviderError: If API credentials are not configured
        """
        super().__init__(rate_limit=rate_limit)

        # Initialize Kite Connect
        try:
            self.kite = KiteConnect(api_key=settings.ZERODHA_API_KEY)
            self.kite.set_access_token(settings.ZERODHA_ACCESS_TOKEN)

            # Cache for instrument tokens
            self._instruments_cache: Optional[pd.DataFrame] = None
            self._cache_timestamp: Optional[datetime] = None

            self.logger.info(
                f"Initialized ZerodhaProvider with rate_limit={rate_limit}/s")

        except Exception as e:
            raise DataProviderError(
                f"Failed to initialize Zerodha provider: {e}")

    def _get_instruments(self, force_refresh: bool = False) -> pd.DataFrame:
        """Get instruments list with caching.

        Instruments are cached for 24 hours to avoid excessive API calls.

        Args:
            force_refresh: Force refresh of cache

        Returns:
            DataFrame with instrument details
        """
        # Check if cache is valid (< 24 hours old)
        if (
            not force_refresh
            and self._instruments_cache is not None
            and self._cache_timestamp is not None
            and (datetime.now() - self._cache_timestamp) < timedelta(hours=24)
        ):
            self.logger.debug("Using cached instruments list")
            return self._instruments_cache

        # Fetch fresh instruments list
        self._enforce_rate_limit()

        try:
            self.logger.info("Fetching instruments list from Zerodha")
            instruments = self.kite.instruments()

            # Convert to DataFrame
            df = pd.DataFrame(instruments)

            # Update cache
            self._instruments_cache = df
            self._cache_timestamp = datetime.now()

            self.logger.info(f"Cached {len(df)} instruments")
            return df

        except Exception as e:
            self.logger.error(f"Error fetching instruments: {e}")
            raise DataProviderError(f"Failed to fetch instruments: {e}")

    def get_instrument_token(
            self,
            symbol: str,
            exchange: str = EXCHANGE_NSE) -> Optional[int]:
        """Get instrument token for a symbol.

        Args:
            symbol: Trading symbol (e.g., 'RELIANCE', 'TCS')
            exchange: Exchange code ('NSE' or 'BSE')

        Returns:
            Instrument token or None if not found

        Example:
            >>> provider = ZerodhaProvider()
            >>> token = provider.get_instrument_token('RELIANCE', 'NSE')
            >>> print(token)  # 738561
        """
        instruments = self._get_instruments()

        # Check if instruments DataFrame is empty
        if instruments.empty:
            self.logger.warning(f"No instruments available")
            return None

        # Filter by symbol and exchange
        matches = instruments[
            (instruments['tradingsymbol'] == symbol) &
            (instruments['exchange'] == exchange)
        ]

        if matches.empty:
            self.logger.warning(f"Instrument {symbol} not found on {exchange}")
            return None

        # Return first match (usually only one)
        token = int(matches.iloc[0]['instrument_token'])
        self.logger.debug(f"Found token {token} for {symbol} on {exchange}")
        return token

    def get_historical_data(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
        **kwargs
    ) -> pd.DataFrame:
        """Fetch historical OHLCV data from Zerodha.

        Args:
            symbol: Indian stock symbol (e.g., 'RELIANCE', 'TCS')
            start_date: Start date for historical data
            end_date: End date for historical data
            **kwargs: Additional parameters:
                - exchange: 'NSE' or 'BSE' (default: 'NSE')
                - interval: '5minute', 'day', etc. (default: 'day')
                - continuous: True/False (default: False)

        Returns:
            DataFrame with columns: date, open, high, low, close, volume, adjusted_close

        Raises:
            DataNotFoundError: If symbol data is not available
            DataProviderError: For other errors

        Example:
            >>> provider = ZerodhaProvider()
            >>> df = provider.get_historical_data('RELIANCE', date(2023, 1, 1), date(2023, 12, 31))
        """
        self._enforce_rate_limit()

        exchange = kwargs.get('exchange', EXCHANGE_NSE)
        interval = kwargs.get('interval', 'day')
        continuous = kwargs.get('continuous', False)

        try:
            # Get instrument token
            token = self.get_instrument_token(symbol, exchange)
            if token is None:
                raise DataNotFoundError(
                    f"Symbol {symbol} not found on {exchange}")

            self.logger.debug(f"Fetching {symbol} (token:{token}) from {
                              start_date} to {end_date}")

            # Fetch historical data
            # Note: Zerodha requires datetime objects with time component
            from_date = datetime.combine(start_date, datetime.min.time())
            to_date = datetime.combine(end_date, datetime.max.time())

            records = self.kite.historical_data(
                instrument_token=token,
                from_date=from_date,
                to_date=to_date,
                interval=interval,
                continuous=continuous,
            )

            if not records:
                raise DataNotFoundError(f"No data found for {symbol}")

            # Convert to DataFrame
            df = pd.DataFrame(records)

            # Rename columns to match our schema
            df = df.rename(columns={
                'date': COL_DATE,
                'open': COL_OPEN,
                'high': COL_HIGH,
                'low': COL_LOW,
                'close': COL_CLOSE,
                'volume': COL_VOLUME,
            })

            # Add adjusted_close (same as close for Indian markets)
            # TODO: Adjust for splits/bonuses if needed
            df['adjusted_close'] = df['close']

            # Convert date to date object (remove time component)
            df[COL_DATE] = pd.to_datetime(df[COL_DATE]).dt.date

            # Select required columns
            columns = [
                COL_DATE,
                COL_OPEN,
                COL_HIGH,
                COL_LOW,
                COL_CLOSE,
                COL_VOLUME,
                'adjusted_close']
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

    def get_nse_instruments(self) -> List[Dict[str, str]]:
        """Fetch list of NSE equity instruments.

        Returns:
            List of dictionaries with NSE instrument information

        Example:
            >>> provider = ZerodhaProvider()
            >>> instruments = provider.get_nse_instruments()
            >>> print(f"Found {len(instruments)} NSE instruments")
        """
        instruments = self._get_instruments()

        # Filter for NSE equities
        nse_equities = instruments[
            (instruments['exchange'] == EXCHANGE_NSE) &
            (instruments['instrument_type'] == 'EQ')
        ]

        # Convert to standard format
        symbols = []
        for _, row in nse_equities.iterrows():
            symbols.append({
                'symbol': row['tradingsymbol'],
                'name': row['name'],
                'exchange': EXCHANGE_NSE,
                'market': MARKET_IN,
                'sector': row.get('segment', 'Unknown'),
            })

        self.logger.info(f"Found {len(symbols)} NSE instruments")
        return symbols

    def get_bse_instruments(self) -> List[Dict[str, str]]:
        """Fetch list of BSE equity instruments.

        Returns:
            List of dictionaries with BSE instrument information
        """
        instruments = self._get_instruments()

        # Filter for BSE equities
        bse_equities = instruments[
            (instruments['exchange'] == EXCHANGE_BSE) &
            (instruments['instrument_type'] == 'EQ')
        ]

        # Convert to standard format
        symbols = []
        for _, row in bse_equities.iterrows():
            symbols.append({
                'symbol': row['tradingsymbol'],
                'name': row['name'],
                'exchange': EXCHANGE_BSE,
                'market': MARKET_IN,
                'sector': row.get('segment', 'Unknown'),
            })

        self.logger.info(f"Found {len(symbols)} BSE instruments")
        return symbols

    def get_symbols_list(self, **kwargs) -> List[Dict[str, str]]:
        """Fetch list of available symbols.

        Args:
            **kwargs: Optional parameters:
                - exchange: 'NSE', 'BSE', or 'ALL' (default: 'NSE')

        Returns:
            List of symbol dictionaries

        Example:
            >>> provider = ZerodhaProvider()
            >>> # Get NSE symbols
            >>> symbols = provider.get_symbols_list(exchange='NSE')
            >>> # Get all symbols
            >>> symbols = provider.get_symbols_list(exchange='ALL')
        """
        exchange = kwargs.get('exchange', 'NSE')

        if exchange == 'NSE':
            return self.get_nse_instruments()
        elif exchange == 'BSE':
            return self.get_bse_instruments()
        elif exchange == 'ALL':
            nse = self.get_nse_instruments()
            bse = self.get_bse_instruments()
            return nse + bse
        else:
            raise DataProviderError(f"Unknown exchange: {exchange}")

    def validate_symbol(self, symbol: str, **kwargs) -> bool:
        """Validate that a symbol exists in Zerodha instruments.

        Args:
            symbol: Trading symbol to validate
            **kwargs: Optional 'exchange' parameter ('NSE' or 'BSE')

        Returns:
            True if symbol exists, False otherwise

        Example:
            >>> provider = ZerodhaProvider()
            >>> provider.validate_symbol('RELIANCE', exchange='NSE')  # True
            >>> provider.validate_symbol('INVALID', exchange='NSE')  # False
        """
        exchange = kwargs.get('exchange', EXCHANGE_NSE)

        try:
            token = self.get_instrument_token(symbol, exchange)
            return token is not None

        except Exception as e:
            self.logger.warning(f"Error validating symbol {symbol}: {e}")
            return False
