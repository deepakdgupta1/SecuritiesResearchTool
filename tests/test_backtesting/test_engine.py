"""Tests for BacktestEngine class."""
from typing import Any, Dict, List

import numpy as np
import pandas as pd
import pytest

from backend.backtesting.engine import BacktestEngine


@pytest.fixture
def sample_price_data() -> Dict[str, pd.DataFrame]:
    """Create sample price data for one symbol."""
    dates = pd.date_range(start="2024-01-01", periods=30, freq="B")
    prices = np.linspace(100, 115, 30)  # 15% uptrend

    df = pd.DataFrame(index=dates)
    df["open"] = prices - 0.5
    df["high"] = prices + 1
    df["low"] = prices - 1
    df["close"] = prices
    df["volume"] = 1000000
    df.index = pd.Index(dates.date)

    return {"AAPL": df}


@pytest.fixture
def sample_signals() -> Dict[str, List[Dict[str, Any]]]:
    """Create sample buy signal on first day."""
    return {
        "2024-01-01": [{"symbol": "AAPL", "confidence": 85.0}]
    }


class TestBacktestEngine:
    """Test suite for BacktestEngine."""

    def test_engine_init(self) -> None:
        """Test engine initialization with custom parameters."""
        engine = BacktestEngine(initial_capital=50000.0, max_positions=5)

        assert engine.initial_capital == 50000.0
        assert engine.cash == 50000.0
        assert engine.max_positions == 5
        assert len(engine.positions) == 0
        assert len(engine.trades) == 0

    def test_reset(self) -> None:
        """Test that reset restores initial state."""
        engine = BacktestEngine(initial_capital=100000.0)

        # Simulate some state changes
        engine.cash = 50000.0
        engine.equity_curve.append(95000.0)

        engine.reset()

        assert engine.cash == engine.initial_capital
        assert len(engine.trades) == 0
        assert len(engine.equity_curve) == 0

    def test_run_backtest_empty(self) -> None:
        """Test backtest with no data returns valid structure."""
        engine = BacktestEngine()
        result = engine.run_backtest({})

        assert "metrics" in result
        assert "trades" in result
        assert "equity_curve" in result
        assert "open_positions" in result
        assert len(result["trades"]) == 0

    def test_run_backtest_with_signal(
        self,
        sample_price_data: Dict[str, pd.DataFrame],
        sample_signals: Dict[str, List[Dict[str, Any]]],
    ) -> None:
        """Test backtest executes entry when signal is present."""
        engine = BacktestEngine(initial_capital=100000.0)
        result = engine.run_backtest(
            price_data=sample_price_data,
            signals=sample_signals,
        )

        # Should have processed days
        assert len(engine.equity_curve) > 0

        # Position should exist or have been closed
        total_activity = len(result["trades"]) + len(result["open_positions"])
        assert total_activity >= 1

    def test_stop_loss_triggered(self) -> None:
        """Test that stop-loss triggers on price drop."""
        # Create price data with sharp decline (drops >10%)
        dates = pd.date_range(start="2024-01-01", periods=10, freq="B")
        prices = [100, 105, 110, 108, 95, 85, 80, 75, 70, 65]

        df = pd.DataFrame(index=dates)
        df["open"] = prices
        df["high"] = [p + 1 for p in prices]
        df["low"] = [p - 1 for p in prices]
        df["close"] = prices
        df["volume"] = 1000000
        df.index = pd.Index(dates.date)

        price_data = {"AAPL": df}
        signals: Dict[str, List[Dict[str, Any]]] = {
            "2024-01-01": [{"symbol": "AAPL", "confidence": 85.0}]
        }

        engine = BacktestEngine(initial_capital=100000.0)
        result = engine.run_backtest(price_data, signals)

        # Should have triggered stop-loss
        stop_loss_trades = [
            t for t in result["trades"] if t.exit_reason == "STOP_LOSS"
        ]
        assert len(stop_loss_trades) >= 1

    def test_max_positions_limit(self) -> None:
        """Test that max positions constraint is respected."""
        dates = pd.date_range(start="2024-01-01", periods=10, freq="B")
        price_data: Dict[str, pd.DataFrame] = {}
        signals: Dict[str, List[Dict[str, Any]]] = {"2024-01-01": []}

        # Create 5 symbols with signals
        for i, symbol in enumerate(["AAPL", "MSFT", "GOOG", "AMZN", "META"]):
            prices = np.linspace(100 + i * 10, 120 + i * 10, 10)
            df = pd.DataFrame(index=dates)
            df["open"] = prices - 0.5
            df["high"] = prices + 1
            df["low"] = prices - 1
            df["close"] = prices
            df["volume"] = 1000000
            df.index = pd.Index(dates.date)
            price_data[symbol] = df

            signals["2024-01-01"].append({
                "symbol": symbol,
                "confidence": 80.0,
            })

        # Limit to 3 positions
        engine = BacktestEngine(initial_capital=100000.0, max_positions=3)
        result = engine.run_backtest(price_data, signals)

        # Should not exceed limit
        assert len(result["open_positions"]) <= 3

    def test_portfolio_value_tracking(
        self,
        sample_price_data: Dict[str, pd.DataFrame],
        sample_signals: Dict[str, List[Dict[str, Any]]],
    ) -> None:
        """Test that portfolio value is tracked correctly."""
        engine = BacktestEngine(initial_capital=100000.0)
        result = engine.run_backtest(sample_price_data, sample_signals)

        # Equity curve should have values
        assert len(engine.equity_curve) > 0

        # All values should be positive
        assert all(v > 0 for v in engine.equity_curve)

        # Final value should be in metrics
        assert result["metrics"]["final_value"] > 0

    def test_take_profit_triggered(self) -> None:
        """Test that take-profit triggers on sufficient gain."""
        # Create price data with strong uptrend (>20% gain)
        dates = pd.date_range(start="2024-01-01", periods=10, freq="B")
        prices = [100, 102, 105, 110, 115, 120, 125, 130, 135, 140]

        df = pd.DataFrame(index=dates)
        df["open"] = prices
        df["high"] = [p + 2 for p in prices]
        df["low"] = [p - 1 for p in prices]
        df["close"] = prices
        df["volume"] = 1000000
        df.index = pd.Index(dates.date)

        price_data = {"AAPL": df}
        signals: Dict[str, List[Dict[str, Any]]] = {
            "2024-01-01": [{"symbol": "AAPL", "confidence": 85.0}]
        }

        engine = BacktestEngine(initial_capital=100000.0)
        result = engine.run_backtest(price_data, signals)

        # Should have triggered take-profit (20% default)
        take_profit_trades = [
            t for t in result["trades"] if t.exit_reason == "TAKE_PROFIT"
        ]
        assert len(take_profit_trades) >= 1

    def test_metrics_calculated(
        self,
        sample_price_data: Dict[str, pd.DataFrame],
        sample_signals: Dict[str, List[Dict[str, Any]]],
    ) -> None:
        """Test that all performance metrics are calculated."""
        engine = BacktestEngine(initial_capital=100000.0)
        result = engine.run_backtest(sample_price_data, sample_signals)

        metrics = result["metrics"]

        # Verify key metrics exist
        assert "total_return" in metrics
        assert "sharpe_ratio" in metrics
        assert "max_drawdown" in metrics
        assert "win_rate" in metrics
        assert "total_trades" in metrics
