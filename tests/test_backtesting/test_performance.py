"""Tests for PerformanceCalculator class."""
from datetime import date
from typing import List

import pandas as pd
import pytest

from backend.backtesting.performance import PerformanceCalculator
from backend.backtesting.positions import Trade


class TestPerformanceCalculator:
    """Test suite for PerformanceCalculator."""

    @pytest.fixture
    def calc(self) -> PerformanceCalculator:
        """Create a PerformanceCalculator instance."""
        return PerformanceCalculator(risk_free_rate=0.04)

    @pytest.fixture
    def sample_trades(self) -> List[Trade]:
        """Create sample trades for testing."""
        return [
            Trade(
                symbol="AAPL",
                entry_date=date(2024, 1, 1),
                entry_price=100.0,
                exit_date=date(2024, 1, 31),
                exit_price=110.0,
                shares=100,
                profit_loss=1000.0,
                profit_loss_pct=0.10,
                exit_reason="TAKE_PROFIT",
            ),
            Trade(
                symbol="MSFT",
                entry_date=date(2024, 2, 1),
                entry_price=200.0,
                exit_date=date(2024, 2, 15),
                exit_price=190.0,
                shares=50,
                profit_loss=-500.0,
                profit_loss_pct=-0.05,
                exit_reason="STOP_LOSS",
            ),
            Trade(
                symbol="GOOG",
                entry_date=date(2024, 3, 1),
                entry_price=150.0,
                exit_date=date(2024, 3, 31),
                exit_price=165.0,
                shares=100,
                profit_loss=1500.0,
                profit_loss_pct=0.10,
                exit_reason="TAKE_PROFIT",
            ),
        ]

    def test_win_rate(
        self, calc: PerformanceCalculator, sample_trades: List[Trade]
    ) -> None:
        """Test win rate calculation."""
        win_rate = calc.calculate_win_rate(sample_trades)
        # 2 winners out of 3 trades = 66.67%
        assert win_rate == pytest.approx(2 / 3, rel=0.01)

    def test_profit_factor(
        self, calc: PerformanceCalculator, sample_trades: List[Trade]
    ) -> None:
        """Test profit factor calculation."""
        pf = calc.calculate_profit_factor(sample_trades)
        # Gross profit = 2500, gross loss = 500, PF = 5.0
        assert pf == pytest.approx(5.0, rel=0.01)

    def test_max_drawdown(self, calc: PerformanceCalculator) -> None:
        """Test max drawdown calculation."""
        # Equity curve with drawdown: peak at 115, trough at 100
        equity = pd.Series([100.0, 110.0, 105.0, 115.0, 100.0])
        mdd = calc.calculate_max_drawdown(equity)
        # Drawdown = (115 - 100) / 115 ≈ 13%
        assert mdd == pytest.approx(0.13, rel=0.05)

    def test_sharpe_ratio(self, calc: PerformanceCalculator) -> None:
        """Test Sharpe ratio calculation."""
        returns = pd.Series([0.01, 0.02, -0.01, 0.015, 0.005])
        sharpe = calc.calculate_sharpe_ratio(returns)
        # Positive returns should yield positive Sharpe
        assert sharpe > 0

    def test_sortino_ratio(self, calc: PerformanceCalculator) -> None:
        """Test Sortino ratio calculation."""
        # Returns with both positive and negative values
        returns = pd.Series([0.02, -0.015, 0.01, -0.02, 0.015, -0.01])
        sortino = calc.calculate_sortino_ratio(returns)
        # Should return a float (positive, negative, or zero)
        assert isinstance(sortino, float)

    def test_cagr(self, calc: PerformanceCalculator) -> None:
        """Test CAGR calculation."""
        # $100 -> $121 in 252 days = 21% CAGR
        cagr = calc.calculate_cagr(100.0, 121.0, 252)
        assert cagr == pytest.approx(0.21, rel=0.01)

    def test_cagr_zero_days(self, calc: PerformanceCalculator) -> None:
        """Test CAGR with zero days returns zero."""
        cagr = calc.calculate_cagr(100.0, 121.0, 0)
        assert cagr == 0.0

    def test_all_metrics(
        self, calc: PerformanceCalculator, sample_trades: List[Trade]
    ) -> None:
        """Test that all metrics are calculated correctly."""
        equity = pd.Series([100000.0, 101000.0, 100500.0, 102000.0])
        metrics = calc.calculate_all_metrics(
            trades=sample_trades,
            equity_curve=equity,
            initial_capital=100000.0,
        )

        # Verify all expected metrics are present
        assert "total_return" in metrics
        assert "sharpe_ratio" in metrics
        assert "sortino_ratio" in metrics
        assert "max_drawdown" in metrics
        assert "cagr" in metrics
        assert "win_rate" in metrics
        assert "profit_factor" in metrics

        # Verify trade counts
        assert metrics["total_trades"] == 3
        assert metrics["winning_trades"] == 2
        assert metrics["losing_trades"] == 1

    def test_empty_trades(self, calc: PerformanceCalculator) -> None:
        """Test calculations with empty trade list."""
        win_rate = calc.calculate_win_rate([])
        profit_factor = calc.calculate_profit_factor([])

        assert win_rate == 0.0
        assert profit_factor == 0.0

    def test_empty_equity_curve(self, calc: PerformanceCalculator) -> None:
        """Test max drawdown with empty equity curve."""
        mdd = calc.calculate_max_drawdown(pd.Series([], dtype=float))
        assert mdd == 0.0
