"""Tests for RiskManager class."""
import pytest
from datetime import date
from backend.backtesting.risk_manager import RiskManager
from backend.backtesting.positions import Position


class TestRiskManager:
    def test_initial_stop_loss(self) -> None:
        rm = RiskManager(initial_stop_loss_pct=0.10)
        stop = rm.calculate_initial_stop_loss(100.0)
        assert stop == 90.0

    def test_take_profit(self) -> None:
        rm = RiskManager()
        tp = rm.calculate_take_profit(100.0, target_pct=0.20)
        assert tp == 120.0

    def test_position_size_by_max_size(self) -> None:
        rm = RiskManager(
            max_position_size_pct=0.10, max_portfolio_risk_pct=0.05
        )
        # Large risk budget, so max_position_size wins
        shares = rm.calculate_position_size(
            portfolio_value=100000.0,
            entry_price=100.0,
            stop_loss_price=50.0,  # 50% stop = high risk per share
        )
        # Max position = 10000, shares = 100
        assert shares == 100

    def test_position_size_by_risk(self) -> None:
        rm = RiskManager(
            max_position_size_pct=0.50,  # Very large
            max_portfolio_risk_pct=0.02,
        )
        # Tight risk budget, so risk sizing wins
        shares = rm.calculate_position_size(
            portfolio_value=100000.0,
            entry_price=100.0,
            stop_loss_price=95.0,  # $5 risk per share
        )
        # Max risk = 2000, risk/share = 5, shares = 400
        assert shares == 400

    def test_trailing_stop_not_triggered(self) -> None:
        rm = RiskManager(trailing_stop_trigger_pct=0.15)
        pos = Position(
            symbol="AAPL",
            shares=100,
            entry_price=100.0,
            entry_date=date(2024, 1, 1),
            stop_loss=90.0,
            take_profit=120.0,
        )
        # Only 5% gain, below trigger
        new_stop = rm.update_trailing_stop(pos, 105.0, atr=2.0)
        assert new_stop == 90.0  # Keep original

    def test_trailing_stop_triggered(self) -> None:
        rm = RiskManager(
            trailing_stop_trigger_pct=0.15,
            trailing_stop_atr_multiplier=2.0,
        )
        pos = Position(
            symbol="AAPL",
            shares=100,
            entry_price=100.0,
            entry_date=date(2024, 1, 1),
            stop_loss=90.0,
            take_profit=120.0,
        )
        # 20% gain, above trigger
        new_stop = rm.update_trailing_stop(pos, 120.0, atr=5.0)
        # Trailing stop = 120 - (2 * 5) = 110
        assert new_stop == 110.0

    def test_drawdown_limit(self) -> None:
        rm = RiskManager(max_drawdown_limit=0.20)
        assert rm.check_drawdown_limit(0.15) is False
        assert rm.check_drawdown_limit(0.20) is True
        assert rm.check_drawdown_limit(0.25) is True

    def test_correlation_check(self) -> None:
        rm = RiskManager()
        # Should reject duplicate
        assert rm.check_correlation_risk("AAPL", ["AAPL", "MSFT"]) is True
        assert rm.check_correlation_risk("GOOG", ["AAPL", "MSFT"]) is False
