"""Abstract base class for data providers.

This module defines the interface that all data provider implementations
must follow. Includes common functionality like retry logic, rate limiting,
and error handling.

Implementations:
- YahooFinanceProvider: US market data via yfinance
- ZerodhaProvider: Indian market data via Kite Connect API
"""

import logging
import time
from abc import ABC, abstractmethod
from datetime import date
from typing import Dict, List, Optional

import pandas as pd
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from backend.core.constants import API_RETRY_BACKOFF_SECONDS, API_RETRY_MAX_ATTEMPTS

logger = logging.getLogger(__name__)


class DataProviderError(Exception):
    """Base exception for data provider errors."""


class RateLimitError(DataProviderError):
    """Raised when rate limit is exceeded."""


class DataNotFoundError(DataProviderError):
    """Raised when requested data is not available."""


class BaseDataProvider(ABC):
    """Abstract base class for all data providers.

    All data provider implementations must inherit from this class
    and implement the required abstract methods.

    Provides:
    - Automatic retry with exponential backoff
    - Rate limiting functionality
    - Common error handling
    - Logging infrastructure

    Attributes:
        rate_limit: Maximum requests per second
        last_request_time: Timestamp of last API request
    """

    def __init__(self, rate_limit: float = 10.0):
        """Initialize the data provider.

        Args:
            rate_limit: Maximum requests per second (default: 10)
        """
        self.rate_limit = rate_limit
        self.last_request_time: Optional[float] = None
        self.logger = logging.getLogger(self.__class__.__name__)

    def _enforce_rate_limit(self) -> None:
        """Enforce rate limiting by sleeping if necessary.

        Calculates time elapsed since last request and sleeps
        if needed to stay within rate limit.
        """
        if self.last_request_time is None:
            self.last_request_time = time.time()
            return

        # Calculate minimum time between requests
        min_interval = 1.0 / self.rate_limit

        # Calculate time elapsed since last request
        elapsed = time.time() - self.last_request_time

        # Sleep if needed to enforce rate limit
        if elapsed < min_interval:
            sleep_time = min_interval - elapsed
            self.logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)

        # Update last request time
        self.last_request_time = time.time()

    @retry(
        stop=stop_after_attempt(API_RETRY_MAX_ATTEMPTS),
        wait=wait_exponential(
            multiplier=API_RETRY_BACKOFF_SECONDS,
            min=API_RETRY_BACKOFF_SECONDS,
            max=60,
        ),
        retry=retry_if_exception_type((RateLimitError, ConnectionError)),
        reraise=True,
    )
    def _retry_on_failure(self, func, *args, **kwargs):
        """Execute function with automatic retry on failure.

        Args:
            func: Function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result of func execution

        Raises:
            Exception: If all retry attempts fail
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.logger.warning(f"Request failed, will retry: {e}")
            raise

    @abstractmethod
    def get_historical_data(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
        **kwargs
    ) -> pd.DataFrame:
        """Fetch historical OHLCV data for a symbol.

        Args:
            symbol: Ticker symbol (e.g., 'AAPL', 'RELIANCE')
            start_date: Start date for historical data
            end_date: End date for historical data
            **kwargs: Provider-specific parameters

        Returns:
            DataFrame with columns: date, open, high, low, close, volume, adjusted_close

        Raises:
            DataNotFoundError: If symbol data is not available
            RateLimitError: If rate limit is exceeded
            DataProviderError: For other provider-specific errors
        """

    @abstractmethod
    def get_symbols_list(self, **kwargs) -> List[Dict[str, str]]:
        """Fetch list of available symbols.

        Args:
            **kwargs: Provider-specific parameters (e.g., exchange, market)

        Returns:
            List of dictionaries with symbol metadata:
            [
                {
                    'symbol': 'AAPL',
                    'name': 'Apple Inc.',
                    'exchange': 'NASDAQ',
                    'market': 'US',
                    'sector': 'Technology'
                },
                ...
            ]

        Raises:
            DataProviderError: If unable to fetch symbols list
        """

    @abstractmethod
    def validate_symbol(self, symbol: str, **kwargs) -> bool:
        """Validate that a symbol exists and is tradeable.

        Args:
            symbol: Ticker symbol to validate
            **kwargs: Provider-specific parameters

        Returns:
            True if symbol is valid and tradeable, False otherwise
        """

    def validate_data(self, df: pd.DataFrame) -> bool:
        """Validate OHLCV data quality.

        Checks for:
        - Required columns present
        - No null values in critical columns
        - OHLC relationships (high >= close >= low, etc.)
        - Positive volume

        Args:
            df: DataFrame to validate

        Returns:
            True if data passes validation, False otherwise
        """
        required_columns = ['open', 'high', 'low', 'close', 'volume']

        # Check required columns present
        if not all(col in df.columns for col in required_columns):
            self.logger.error(
                f"Missing required columns. Found: {
                    df.columns.tolist()}")
            return False

        # Check for null values
        if df[required_columns].isnull().any().any():
            null_counts = df[required_columns].isnull().sum()
            self.logger.warning(f"Null values found: {
                                null_counts[null_counts > 0].to_dict()}")
            return False

        # Validate OHLC relationships
        invalid_ohlc = (
            (df['high'] < df['low']) |
            (df['high'] < df['open']) |
            (df['high'] < df['close']) |
            (df['low'] > df['open']) |
            (df['low'] > df['close'])
        )

        if invalid_ohlc.any():
            self.logger.error(
                f"Invalid OHLC relationships in {
                    invalid_ohlc.sum()} rows")
            return False

        # Check for non-positive volume
        if (df['volume'] <= 0).any():
            self.logger.error(
                f"Non-positive volume in {(df['volume'] <= 0).sum()} rows")
            return False

        self.logger.debug(f"Data validation passed for {len(df)} rows")
        return True

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(rate_limit={self.rate_limit})>"
