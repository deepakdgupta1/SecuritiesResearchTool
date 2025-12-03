"""Unit tests for database models.

Tests SQLAlchemy ORM models for structure, relationships, and constraints.
"""

import pytest
from datetime import date, datetime
from decimal import Decimal

from backend.models.db_models import (
    Base,
    Symbol,
    PriceData,
    DerivedMetrics,
    PatternDetection,
    TradeRecommendation,
    BacktestResult,
    BacktestTrade,
)

# Note: db_session fixture is provided by conftest.py
# It uses the PostgreSQL database configured in .env



class TestSymbol:
    """Test suite for Symbol model."""
    
    def test_create_symbol(self, db_session, unique_symbol):
        """Test creating a Symbol record."""
        symbol = Symbol(
            symbol=unique_symbol,
            name="Apple Inc.",
            exchange="NASDAQ",
            market="US",
            sector="Technology",
            active=True,
        )
        
        db_session.add(symbol)
        db_session.commit()
        
        # Verify record was created
        retrieved = db_session.query(Symbol).filter_by(symbol=unique_symbol).first()
        assert retrieved is not None
        assert retrieved.name == "Apple Inc."
        assert retrieved.exchange == "NASDAQ"
        assert retrieved.market == "US"
        assert retrieved.sector == "Technology"
        assert retrieved.active is True
    
    def test_symbol_unique_constraint(self, db_session, unique_symbol):
        """Test that duplicate symbols are rejected."""
        symbol1 = Symbol(symbol=unique_symbol, name="Apple Inc.", exchange="NASDAQ", market="US")
        symbol2 = Symbol(symbol=unique_symbol, name="Duplicate", exchange="NASDAQ", market="US")
        
        db_session.add(symbol1)
        db_session.commit()
        
        db_session.add(symbol2)
        with pytest.raises(Exception):  # IntegrityError in PostgreSQL, generic in SQLite
            db_session.commit()
    
    def test_symbol_repr(self, db_session, unique_symbol):
        """Test Symbol __repr__ method."""
        symbol = Symbol(symbol=unique_symbol, exchange="NASDAQ")
        db_session.add(symbol)
        db_session.commit()
        
        assert unique_symbol in repr(symbol)
        assert "NASDAQ" in repr(symbol)


class TestPriceData:
    """Test suite for PriceData model."""
    
    def test_create_price_data(self, db_session, unique_symbol):
        """Test creating a PriceData record."""
        # Create parent symbol
        symbol = Symbol(symbol=unique_symbol, name="Apple Inc.", exchange="NASDAQ", market="US")
        db_session.add(symbol)
        db_session.commit()
        
        # Create price data
        price = PriceData(
            symbol_id=symbol.id,
            date=date(2023, 1, 1),
            open=Decimal("150.00"),
            high=Decimal("155.00"),
            low=Decimal("149.00"),
            close=Decimal("152.00"),
            volume=1000000,
            adjusted_close=Decimal("152.00"),
        )
        
        db_session.add(price)
        db_session.commit()
        
        # Verify
        retrieved = db_session.query(PriceData).filter_by(
            symbol_id=symbol.id, date=date(2023, 1, 1)
        ).first()
        assert retrieved is not None
        assert retrieved.close == Decimal("152.00")
        assert retrieved.volume == 1000000
    
    def test_price_data_relationship(self, db_session, unique_symbol):
        """Test relationship between Symbol and PriceData."""
        symbol = Symbol(symbol=unique_symbol, name="Apple Inc.", exchange="NASDAQ", market="US")
        db_session.add(symbol)
        db_session.commit()
        
        price1 = PriceData(
            symbol_id=symbol.id,
            date=date(2023, 1, 1),
            close=Decimal("150.00"),
        )
        price2 = PriceData(
            symbol_id=symbol.id,
            date=date(2023, 1, 2),
            close=Decimal("151.00"),
        )
        
        db_session.add_all([price1, price2])
        db_session.commit()
        
        # Test relationship
        symbol_with_prices = db_session.query(Symbol).filter_by(symbol=unique_symbol).first()
        assert len(symbol_with_prices.price_data) == 2


class TestPatternDetection:
    """Test suite for PatternDetection model."""
    
    def test_create_pattern_detection(self, db_session, unique_symbol):
        """Test creating a PatternDetection record."""
        symbol = Symbol(symbol=unique_symbol, name="Apple Inc.", exchange="NASDAQ", market="US")
        db_session.add(symbol)
        db_session.commit()
        
        pattern = PatternDetection(
            symbol_id=symbol.id,
            detection_date=date(2023, 1, 1),
            pattern_type="VCP",
            confidence_score=Decimal("85.50"),
            weinstein_stage=2,
            meets_trend_template=True,
            pattern_metadata={"contractions": 3, "depth": 0.15},
        )
        
        db_session.add(pattern)
        db_session.commit()
        
        # Verify
        retrieved = db_session.query(PatternDetection).first()
        assert retrieved is not None
        assert retrieved.pattern_type == "VCP"
        assert retrieved.confidence_score == Decimal("85.50")
        assert retrieved.weinstein_stage == 2
        assert retrieved.pattern_metadata["contractions"] == 3
    
    def test_pattern_detection_metadata_jsonb(self, db_session, unique_symbol):
        """Test JSONB field for pattern metadata."""
        symbol = Symbol(symbol=unique_symbol, name="Apple Inc.", exchange="NASDAQ", market="US")
        db_session.add(symbol)
        db_session.commit()
        
        metadata = {
            "contractions": 3,
            "depth_pct": 15.5,
            "duration_days": 45,
            "pivot_point": 150.00,
        }
        
        pattern = PatternDetection(
            symbol_id=symbol.id,
            detection_date=date(2023, 1, 1),
            pattern_type="VCP",
            pattern_metadata=metadata,
        )
        
        db_session.add(pattern)
        db_session.commit()
        
        
        retrieved = db_session.query(PatternDetection).filter_by(symbol_id=symbol.id).first()
        assert retrieved.pattern_metadata == metadata


class TestTradeRecommendation:
    """Test suite for TradeRecommendation model."""
    
    def test_create_trade_recommendation(self, db_session, unique_symbol):
        """Test creating a TradeRecommendation record."""
        symbol = Symbol(symbol=unique_symbol, name="Apple Inc.", exchange="NASDAQ", market="US")
        db_session.add(symbol)
        db_session.commit()
        
        recommendation = TradeRecommendation(
            symbol_id=symbol.id,
            recommendation_date=date(2023, 1, 1),
            trade_type="BUY",
            entry_price=Decimal("150.00"),
            stop_loss=Decimal("135.00"),
            take_profit=Decimal("180.00"),
            position_size_pct=Decimal("10.00"),
            rationale="VCP pattern detected with strong RS",
            status="OPEN",
        )
        
        db_session.add(recommendation)
        db_session.commit()
        
        # Verify
        retrieved = db_session.query(TradeRecommendation).first()
        assert retrieved is not None
        assert retrieved.trade_type == "BUY"
        assert retrieved.entry_price == Decimal("150.00")
        assert retrieved.status == "OPEN"


class TestBacktestResult:
    """Test suite for BacktestResult model."""
    
    def test_create_backtest_result(self, db_session):
        """Test creating a BacktestResult record."""
        result = BacktestResult(
            backtest_name="VCP Strategy 2020-2023",
            start_date=date(2020, 1, 1),
            end_date=date(2023, 12, 31),
            strategy_config={"pattern": "VCP", "rs_threshold": 70},
            total_return=Decimal("45.50"),
            cagr=Decimal("12.34"),
            sharpe_ratio=Decimal("1.85"),
            max_drawdown=Decimal("-15.20"),
            win_rate=Decimal("65.00"),
            profit_factor=Decimal("2.10"),
            total_trades=100,
            winning_trades=65,
            losing_trades=35,
        )
        
        db_session.add(result)
        db_session.commit()
        
        # Verify
        retrieved = db_session.query(BacktestResult).first()
        assert retrieved is not None
        assert retrieved.backtest_name == "VCP Strategy 2020-2023"
        assert retrieved.total_return == Decimal("45.50")
        assert retrieved.win_rate == Decimal("65.00")


class TestBacktestTrade:
    """Test suite for BacktestTrade model."""
    
    def test_create_backtest_trade(self, db_session, unique_symbol):
        """Test creating a BacktestTrade record."""
        # Create dependencies
        symbol = Symbol(symbol=unique_symbol, name="Apple Inc.", exchange="NASDAQ", market="US")
        backtest = BacktestResult(
            backtest_name="Test Backtest",
            start_date=date(2020, 1, 1),
            end_date=date(2023, 12, 31),
        )
        
        db_session.add_all([symbol, backtest])
        db_session.commit()
        
        # Create trade
        trade = BacktestTrade(
            backtest_id=backtest.id,
            symbol_id=symbol.id,
            entry_date=date(2023, 1, 1),
            entry_price=Decimal("150.00"),
            exit_date=date(2023, 2, 1),
            exit_price=Decimal("165.00"),
            position_type="LONG",
            quantity=100,
            profit_loss=Decimal("1500.00"),
            profit_loss_pct=Decimal("10.00"),
            exit_reason="TAKE_PROFIT",
        )
        
        db_session.add(trade)
        db_session.commit()
        
        # Verify
        retrieved = db_session.query(BacktestTrade).first()
        assert retrieved is not None
        assert retrieved.position_type == "LONG"
        assert retrieved.profit_loss == Decimal("1500.00")
        assert retrieved.exit_reason == "TAKE_PROFIT"
    
    def test_backtest_trade_relationships(self, db_session, unique_symbol):
        """Test relationships between BacktestResult and BacktestTrade."""
        symbol = Symbol(symbol=unique_symbol, name="Apple Inc.", exchange="NASDAQ", market="US")
        backtest = BacktestResult(backtest_name="Test Backtest")
        
        db_session.add_all([symbol, backtest])
        db_session.commit()
        
        trade1 = BacktestTrade(
            backtest_id=backtest.id,
            symbol_id=symbol.id,
            entry_date=date(2023, 1, 1),
            exit_date=date(2023, 2, 1),
        )
        trade2 = BacktestTrade(
            backtest_id=backtest.id,
            symbol_id=symbol.id,
            entry_date=date(2023, 3, 1),
            exit_date=date(2023, 4, 1),
        )
        
        db_session.add_all([trade1, trade2])
        db_session.commit()
        
        # Test relationship
        retrieved_backtest = db_session.query(BacktestResult).filter_by(id=backtest.id).first()
        assert len(retrieved_backtest.backtest_trades) == 2
