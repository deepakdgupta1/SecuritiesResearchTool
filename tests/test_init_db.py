"""Integration tests for database initialization.

Tests the end-to-end database setup process.
"""

import pytest
from sqlalchemy import create_engine, text, inspect
from backend.models.db_models import Base


class TestDatabaseInitialization:
    """Test suite for database initialization."""
    
    def test_all_tables_created(self):
        """Test that all 7 tables are created."""
        # Use in-memory database
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        
        # Get inspector
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        # Verify all 7 tables exist
        expected_tables = {
"symbols",
            "price_data",
            "derived_metrics",
            "pattern_detections",
            "trade_recommendations",
            "backtest_results",
            "backtest_trades",
        }
        
        assert set(tables) == expected_tables
    
    def test_symbols_table_structure(self):
        """Test symbols table has correct columns."""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        
        inspector = inspect(engine)
        columns = {col["name"] for col in inspector.get_columns("symbols")}
        
        expected_columns = {
            "id", "symbol", "name", "exchange", 
            "market", "sector", "active", "created_at"
        }
        
        assert expected_columns.issubset(columns)
    
    def test_price_data_table_structure(self):
        """Test price_data table has correct columns."""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        
        inspector = inspect(engine)
        columns = {col["name"] for col in inspector.get_columns("price_data")}
        
        expected_columns = {
            "symbol_id", "date", "open", "high", "low",
            "close", "volume", "adjusted_close"
        }
        
        assert expected_columns.issubset(columns)
    
    def test_foreign_keys_exist(self):
        """Test that foreign key relationships are defined."""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        
        inspector = inspect(engine)
        
        # Check price_data has FK to symbols
        fks = inspector.get_foreign_keys("price_data")
        assert len(fks) > 0
        assert fks[0]["referred_table"] == "symbols"
        
        # Check pattern_detections has FK to symbols
        fks = inspector.get_foreign_keys("pattern_detections")
        assert len(fks) > 0
        assert fks[0]["referred_table"] == "symbols"
    
    def test_indexes_created(self):
        """Test that indexes are created on key columns."""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        
        inspector = inspect(engine)
        
        # Check symbols table indexes
        indexes = inspector.get_indexes("symbols")
        index_columns = {idx["column_names"][0] for idx in indexes if len(idx["column_names"]) == 1}
        
        # Should have indexes on symbol, exchange, market, active
        assert "symbol" in index_columns or any("symbol" in str(idx) for idx in indexes)
