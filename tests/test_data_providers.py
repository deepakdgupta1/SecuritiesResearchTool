"""Unit tests for data providers.

Tests YahooFinanceProvider and ZerodhaProvider with mocked external dependencies.
"""

from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

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
)
from backend.data_providers.base import DataNotFoundError, DataProviderError
from backend.data_providers.yahoo_client import YahooFinanceProvider
from backend.data_providers.zerodha_client import ZerodhaProvider


@pytest.fixture
def mock_yfinance():
    """Mock yfinance module."""
    with patch('backend.data_providers.yahoo_client.yf') as mock_yf:
        yield mock_yf


@pytest.fixture
def mock_kiteconnect():
    """Mock kiteconnect module."""
    with patch('backend.data_providers.zerodha_client.KiteConnect') as mock_kite:
        yield mock_kite


class TestYahooFinanceProvider:
    """Test suite for YahooFinanceProvider."""

    def test_get_historical_data_success(self, mock_yfinance):
        """Test successful historical data fetch."""
        # Setup mock
        mock_ticker = MagicMock()
        mock_yfinance.Ticker.return_value = mock_ticker

        # Create sample DataFrame
        data = {
            'Open': [150.0, 152.0],
            'High': [155.0, 156.0],
            'Low': [149.0, 151.0],
            'Close': [153.0, 154.0],
            'Volume': [1000000, 1200000],
            'Adj Close': [153.0, 154.0],
        }
        dates = pd.to_datetime(['2023-01-01', '2023-01-02'])
        df = pd.DataFrame(data, index=dates)
        df.index.name = 'Date'

        mock_ticker.history.return_value = df

        # Execute
        provider = YahooFinanceProvider()
        result = provider.get_historical_data(
            'AAPL', date(
                2023, 1, 1), date(
                2023, 1, 2))

        # Verify
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert COL_DATE in result.columns
        assert COL_CLOSE in result.columns
        assert result.iloc[0][COL_CLOSE] == 153.0

    def test_get_historical_data_not_found(self, mock_yfinance):
        """Test handling of missing data."""
        mock_ticker = MagicMock()
        mock_yfinance.Ticker.return_value = mock_ticker
        mock_ticker.history.return_value = pd.DataFrame()  # Empty DataFrame

        provider = YahooFinanceProvider()

        with pytest.raises(DataNotFoundError):
            provider.get_historical_data(
                'INVALID', date(
                    2023, 1, 1), date(
                    2023, 1, 2))

    def test_validate_symbol_success(self, mock_yfinance):
        """Test successful symbol validation."""
        mock_ticker = MagicMock()
        mock_yfinance.Ticker.return_value = mock_ticker
        mock_ticker.info = {'regularMarketPrice': 150.0}

        provider = YahooFinanceProvider()
        assert provider.validate_symbol('AAPL') is True

    def test_validate_symbol_failure(self, mock_yfinance):
        """Test failed symbol validation."""
        mock_ticker = MagicMock()
        mock_yfinance.Ticker.return_value = mock_ticker
        mock_ticker.info = {}  # Empty info

        provider = YahooFinanceProvider()
        assert provider.validate_symbol('INVALID') is False


class TestZerodhaProvider:
    """Test suite for ZerodhaProvider."""

    def test_initialization(self, mock_kiteconnect):
        """Test provider initialization."""
        provider = ZerodhaProvider()
        assert provider.kite is not None
        mock_kiteconnect.assert_called_once()

    def test_get_instrument_token_success(self, mock_kiteconnect):
        """Test successful token lookup."""
        # Setup mock instruments
        mock_kite_instance = mock_kiteconnect.return_value
        mock_kite_instance.instruments.return_value = [
            {'instrument_token': 123456, 'tradingsymbol': 'RELIANCE', 'exchange': EXCHANGE_NSE},
            {'instrument_token': 789012, 'tradingsymbol': 'TCS', 'exchange': EXCHANGE_NSE}
        ]

        provider = ZerodhaProvider()
        token = provider.get_instrument_token('RELIANCE', EXCHANGE_NSE)

        assert token == 123456

    def test_get_instrument_token_not_found(self, mock_kiteconnect):
        """Test token lookup failure."""
        mock_kite_instance = mock_kiteconnect.return_value
        mock_kite_instance.instruments.return_value = []

        provider = ZerodhaProvider()
        token = provider.get_instrument_token('INVALID', EXCHANGE_NSE)

        assert token is None

    def test_get_historical_data_success(self, mock_kiteconnect):
        """Test successful historical data fetch."""
        mock_kite_instance = mock_kiteconnect.return_value

        # Mock instruments for token lookup
        mock_kite_instance.instruments.return_value = [
            {'instrument_token': 123456, 'tradingsymbol': 'RELIANCE', 'exchange': EXCHANGE_NSE}
        ]

        # Mock historical data
        mock_kite_instance.historical_data.return_value = [
            {
                'date': datetime(2023, 1, 1),
                'open': 2500.0,
                'high': 2550.0,
                'low': 2490.0,
                'close': 2520.0,
                'volume': 100000
            }
        ]

        provider = ZerodhaProvider()

        result = provider.get_historical_data(
            'RELIANCE', date(
                2023, 1, 1), date(
                2023, 1, 1))

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0][COL_CLOSE] == 2520.0
        assert 'adjusted_close' in result.columns

    def test_get_nse_instruments(self, mock_kiteconnect):
        """Test fetching NSE instruments list."""
        mock_kite_instance = mock_kiteconnect.return_value
        mock_kite_instance.instruments.return_value = [
            {
                'instrument_token': 123456,
                'tradingsymbol': 'RELIANCE',
                'name': 'Reliance Industries Ltd',
                'exchange': EXCHANGE_NSE,
                'instrument_type': 'EQ',
                'segment': 'NSE'
            },
            {
                'instrument_token': 789012,
                'tradingsymbol': 'TCS',
                'name': 'Tata Consultancy Services Ltd',
                'exchange': EXCHANGE_NSE,
                'instrument_type': 'EQ',
                'segment': 'NSE'
            }
        ]

        provider = ZerodhaProvider()
        instruments = provider.get_nse_instruments()

        assert len(instruments) == 2
        assert instruments[0]['symbol'] == 'RELIANCE'
        assert instruments[0]['exchange'] == EXCHANGE_NSE
        assert instruments[0]['market'] == MARKET_IN

    def test_get_symbols_list_nse(self, mock_kiteconnect):
        """Test get_symbols_list for NSE."""
        mock_kite_instance = mock_kiteconnect.return_value
        mock_kite_instance.instruments.return_value = [
            {
                'instrument_token': 123456,
                'tradingsymbol': 'RELIANCE',
                'name': 'Reliance Industries Ltd',
                'exchange': EXCHANGE_NSE,
                'instrument_type': 'EQ',
                'segment': 'NSE'
            }
        ]

        provider = ZerodhaProvider()
        symbols = provider.get_symbols_list(exchange='NSE')

        assert len(symbols) == 1
        assert symbols[0]['symbol'] == 'RELIANCE'

    def test_validate_symbol_success(self, mock_kiteconnect):
        """Test successful symbol validation."""
        mock_kite_instance = mock_kiteconnect.return_value
        mock_kite_instance.instruments.return_value = [
            {'instrument_token': 123456, 'tradingsymbol': 'RELIANCE', 'exchange': EXCHANGE_NSE}
        ]

        provider = ZerodhaProvider()
        assert provider.validate_symbol(
            'RELIANCE', exchange=EXCHANGE_NSE) is True

    def test_validate_symbol_failure(self, mock_kiteconnect):
        """Test failed symbol validation."""
        mock_kite_instance = mock_kiteconnect.return_value
        mock_kite_instance.instruments.return_value = []

        provider = ZerodhaProvider()
        assert provider.validate_symbol(
            'INVALID', exchange=EXCHANGE_NSE) is False


class TestYahooFinanceProviderExtended:
    """Extended test suite for YahooFinanceProvider."""

    def test_get_symbols_list(self, mock_yfinance):
        """Test get_symbols_list method."""
        # Mock the get_sp500_symbols method to avoid lxml dependency
        with patch.object(YahooFinanceProvider, 'get_sp500_symbols') as mock_sp500:
            mock_sp500.return_value = [{'symbol': 'AAPL',
                                        'name': 'Apple Inc.',
                                        'exchange': 'NASDAQ',
                                        'market': 'US',
                                        'sector': 'Technology'},
                                       {'symbol': 'MSFT',
                                        'name': 'Microsoft Corp.',
                                        'exchange': 'NASDAQ',
                                        'market': 'US',
                                        'sector': 'Technology'}]

            provider = YahooFinanceProvider()
            symbols = provider.get_symbols_list()
            assert isinstance(symbols, list)
            assert len(symbols) > 0
            assert all('symbol' in s for s in symbols)

    def test_data_validation_success(self, mock_yfinance):
        """Test data validation with valid data."""
        provider = YahooFinanceProvider()

        # Create valid DataFrame
        data = {
            COL_DATE: [date(2023, 1, 1)],
            COL_OPEN: [150.0],
            COL_HIGH: [155.0],
            COL_LOW: [149.0],
            COL_CLOSE: [153.0],
            COL_VOLUME: [1000000],
            'adjusted_close': [153.0]
        }
        df = pd.DataFrame(data)

        assert provider.validate_data(df) is True

    def test_data_validation_missing_columns(self, mock_yfinance):
        """Test data validation with missing columns."""
        provider = YahooFinanceProvider()

        # Create DataFrame with missing columns
        data = {
            COL_DATE: [date(2023, 1, 1)],
            COL_CLOSE: [153.0]
        }
        df = pd.DataFrame(data)

        assert provider.validate_data(df) is False

    def test_data_validation_empty_dataframe(self, mock_yfinance):
        """Test data validation with empty DataFrame."""
        provider = YahooFinanceProvider()
        df = pd.DataFrame()

        assert provider.validate_data(df) is False

    def test_error_handling_api_failure(self, mock_yfinance):
        """Test error handling when API fails."""
        mock_ticker = MagicMock()
        mock_yfinance.Ticker.return_value = mock_ticker
        mock_ticker.history.side_effect = Exception("API Error")

        provider = YahooFinanceProvider()

        with pytest.raises(DataProviderError):
            provider.get_historical_data(
                'AAPL', date(
                    2023, 1, 1), date(
                    2023, 1, 2))


class TestZerodhaProviderExtended:
    """Extended test suite for ZerodhaProvider."""

    def test_instruments_caching(self, mock_kiteconnect):
        """Test that instruments are cached."""
        mock_kite_instance = mock_kiteconnect.return_value
        mock_kite_instance.instruments.return_value = [
            {'instrument_token': 123456, 'tradingsymbol': 'RELIANCE', 'exchange': EXCHANGE_NSE}
        ]

        provider = ZerodhaProvider()

        # First call
        provider.get_instrument_token('RELIANCE', EXCHANGE_NSE)

        # Second call should use cache
        provider.get_instrument_token('RELIANCE', EXCHANGE_NSE)

        # instruments() should only be called once (caching works)
        assert mock_kite_instance.instruments.call_count == 1

    def test_get_historical_data_not_found(self, mock_kiteconnect):
        """Test handling of symbol not found."""
        mock_kite_instance = mock_kiteconnect.return_value
        mock_kite_instance.instruments.return_value = []

        provider = ZerodhaProvider()

        with pytest.raises(DataNotFoundError):
            provider.get_historical_data(
                'INVALID', date(
                    2023, 1, 1), date(
                    2023, 1, 2))

    def test_get_bse_instruments(self, mock_kiteconnect):
        """Test fetching BSE instruments list."""
        mock_kite_instance = mock_kiteconnect.return_value
        mock_kite_instance.instruments.return_value = [
            {
                'instrument_token': 123456,
                'tradingsymbol': 'RELIANCE',
                'name': 'Reliance Industries Ltd',
                'exchange': EXCHANGE_BSE,
                'instrument_type': 'EQ',
                'segment': 'BSE'
            }
        ]

        provider = ZerodhaProvider()
        instruments = provider.get_bse_instruments()

        assert len(instruments) == 1
        assert instruments[0]['exchange'] == EXCHANGE_BSE

    def test_get_symbols_list_all(self, mock_kiteconnect):
        """Test get_symbols_list for all exchanges."""
        mock_kite_instance = mock_kiteconnect.return_value
        mock_kite_instance.instruments.return_value = [
            {
                'instrument_token': 123456,
                'tradingsymbol': 'RELIANCE',
                'name': 'Reliance Industries Ltd',
                'exchange': EXCHANGE_NSE,
                'instrument_type': 'EQ',
                'segment': 'NSE'
            },
            {
                'instrument_token': 789012,
                'tradingsymbol': 'RELIANCE',
                'name': 'Reliance Industries Ltd',
                'exchange': EXCHANGE_BSE,
                'instrument_type': 'EQ',
                'segment': 'BSE'
            }
        ]

        provider = ZerodhaProvider()
        symbols = provider.get_symbols_list(exchange='ALL')

        # Should get both NSE and BSE
        assert len(symbols) == 2

    def test_get_symbols_list_invalid_exchange(self, mock_kiteconnect):
        """Test get_symbols_list with invalid exchange."""
        provider = ZerodhaProvider()

        with pytest.raises(DataProviderError):
            provider.get_symbols_list(exchange='INVALID')


if __name__ == "__main__":
    # Manual test runner for debugging
    print("Running manual tests...")

    # Mock setup
    mock_yf_patcher = patch('backend.data_providers.yahoo_client.yf')
    mock_yf = mock_yf_patcher.start()

    mock_kite_patcher = patch(
        'backend.data_providers.zerodha_client.KiteConnect')
    mock_kite = mock_kite_patcher.start()

    try:
        # Test YahooFinanceProvider
        print("Testing YahooFinanceProvider...")
        test_yahoo = TestYahooFinanceProvider()

        # test_get_historical_data_success
        mock_ticker = MagicMock()
        mock_yf.Ticker.return_value = mock_ticker
        data = {
            'Open': [150.0, 152.0],
            'High': [155.0, 156.0],
            'Low': [149.0, 151.0],
            'Close': [153.0, 154.0],
            'Volume': [1000000, 1200000],
            'Adj Close': [153.0, 154.0],
        }
        dates = pd.to_datetime(['2023-01-01', '2023-01-02'])
        df = pd.DataFrame(data, index=dates)
        df.index.name = 'Date'
        mock_ticker.history.return_value = df

        provider = YahooFinanceProvider()
        result = provider.get_historical_data(
            'AAPL', date(
                2023, 1, 1), date(
                2023, 1, 2))
        print(f"  get_historical_data: {'OK' if len(result) == 2 else 'FAIL'}")

        # Test ZerodhaProvider
        print("Testing ZerodhaProvider...")
        test_zerodha = TestZerodhaProvider()

        # test_get_instrument_token_success
        mock_kite_instance = mock_kite.return_value
        mock_kite_instance.instruments.return_value = [
            {'instrument_token': 123456, 'tradingsymbol': 'RELIANCE', 'exchange': EXCHANGE_NSE}
        ]
        provider = ZerodhaProvider()
        token = provider.get_instrument_token('RELIANCE', EXCHANGE_NSE)
        print(f"  get_instrument_token: {'OK' if token == 123456 else 'FAIL'}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        mock_yf_patcher.stop()
        mock_kite_patcher.stop()
