"""
Integration test for indicator calculation pipeline.
"""

import pytest
from datetime import date, timedelta
from sqlalchemy import select, delete

from backend.core.database import get_session
from backend.models.db_models import Symbol, PriceData, DerivedMetrics
from backend.indicators.manager import IndicatorManager


@pytest.fixture
def test_symbol_data():
    """Create test symbol and price data."""
    symbol_ticker = "TEST_INTEGRATION_IND"
    
    with get_session() as session:
        # Clean up existing
        existing = session.execute(select(Symbol).where(Symbol.symbol == symbol_ticker)).scalar_one_or_none()
        if existing:
            session.delete(existing)
            session.commit()
            
        # Create symbol
        symbol = Symbol(
            symbol=symbol_ticker,
            name="Test Integration Symbol",
            exchange="NSE",
            market="IN",
            active=True
        )
        session.add(symbol)
        session.flush() # Get ID
        
        # Create price data (300 days)
        prices = []
        start_date = date.today() - timedelta(days=300)
        for i in range(300):
            d = start_date + timedelta(days=i)
            # Simple linear trend
            price = 100 + i
            p = PriceData(
                symbol_id=symbol.id,
                date=d,
                open=price,
                high=price + 2,
                low=price - 2,
                close=price,
                volume=10000,
                adjusted_close=price
            )
            prices.append(p)
            
        session.add_all(prices)
        session.commit()
        
        symbol_id = symbol.id
        
    yield symbol_id, symbol_ticker
    
    # Cleanup
    with get_session() as session:
        existing = session.execute(select(Symbol).where(Symbol.symbol == symbol_ticker)).scalar_one_or_none()
        if existing:
            session.delete(existing)
            session.commit()


def test_indicator_pipeline(test_symbol_data):
    """Test the full indicator calculation pipeline."""
    symbol_id, symbol_ticker = test_symbol_data
    
    manager = IndicatorManager()
    
    # Run calculation
    # We pass empty benchmark_df so RS will be skipped (or calculated as None)
    # Ideally we should mock benchmark too, but for basic integration this is enough.
    success = manager.calculate_for_symbol(symbol_id, benchmark_df=None)
    
    assert success is True
    
    # Verify results
    with get_session() as session:
        metrics = session.execute(
            select(DerivedMetrics)
            .where(DerivedMetrics.symbol_id == symbol_id)
            .order_by(DerivedMetrics.date.desc())
        ).scalars().all()
        
        assert len(metrics) > 0
        # Should have 300 records ideally, but maybe fewer if we skip NaNs?
        # The manager saves all rows from the dataframe.
        assert len(metrics) == 300
        
        latest = metrics[0]
        
        # Check SMA
        # Price 399. SMA 50 should be approx 374.5
        assert latest.sma_50 is not None
        assert 370 < latest.sma_50 < 380
        
        # Check RSI
        # Linear trend -> RSI 100
        assert latest.rsi_14 is not None
        assert latest.rsi_14 > 90
        
        # Check Volume
        assert latest.volume_avg_50 == 10000
