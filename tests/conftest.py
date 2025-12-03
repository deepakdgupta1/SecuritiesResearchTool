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
    # Use production database for now (we'll create a test DB later if needed)
    os.environ["DATABASE_URL"] = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/securities_research"
    )
    os.environ["ZERODHA_API_KEY"] = "test_api_key"
    os.environ["ZERODHA_ACCESS_TOKEN"] = "test_access_token"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["ENVIRONMENT"] = "testing"
    
    yield
    
    # Cleanup after tests
    pass


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create test database schema before running tests."""
    from backend.models.db_models import Base
    from backend.core.database import engine
    
    # Create all tables (if they don't exist)
    Base.metadata.create_all(bind=engine)
    
    yield
    
    # Note: We don't drop tables after tests to preserve data
    # If you want clean slate, manually drop: Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Provide a clean database session for each test.
    
    Always rolls back changes after the test completes to ensure test isolation.
    """
    from backend.core.database import SessionLocal
    
    session = SessionLocal()
    try:
        yield session
        # Always rollback to ensure tests don't leave data
        session.rollback()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


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
def unique_symbol():
    """Generate a unique symbol for testing to avoid database conflicts."""
    import uuid
    # Generate a unique symbol like "TEST_a1b2c3d4"
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"TEST_{unique_id}"


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
