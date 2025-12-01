"""Pytest configuration and fixtures."""

import os
import pytest
from dotenv import load_dotenv

# Load test environment variables
load_dotenv(".env.test", override=True)


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment variables."""
    # Set test-specific environment variables
    os.environ["DATABASE_URL"] = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql://postgres:c%40r33rDeep1@localhost:5432/securities_research_test"
    )
    os.environ["ZERODHA_API_KEY"] = "test_api_key"
    os.environ["ZERODHA_ACCESS_TOKEN"] = "test_access_token"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["ENVIRONMENT"] = "testing"
    
    yield
    
    # Cleanup after tests
    pass


@pytest.fixture
def sample_symbol_data():
    """Sample symbol data for testing."""
    return {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "exchange": "NASDAQ",
        "market": "US",
        "sector": "Technology",
        "active": True,
    }


@pytest.fixture
def sample_price_data():
    """Sample price data for testing."""
    from datetime import date
    from decimal import Decimal
    
    return {
        "date": date(2023, 1, 1),
        "open": Decimal("150.00"),
        "high": Decimal("155.00"),
        "low": Decimal("149.00"),
        "close": Decimal("152.00"),
        "volume": 1000000,
        "adjusted_close": Decimal("152.00"),
    }
