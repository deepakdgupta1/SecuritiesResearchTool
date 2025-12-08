"""Tests for Position and Trade dataclasses."""
import pytest
from datetime import date
from backend.backtesting.positions import Position, Trade


class TestPosition:
    def test_position_creation(self) -> None:
        pos = Position(
            symbol="AAPL",
            shares=100,
            entry_price=150.0,
            entry_date=date(2024, 1, 1),
            stop_loss=135.0,
            take_profit=180.0,
        )

        assert pos.symbol == "AAPL"
        assert pos.shares == 100
        assert pos.current_price == 150.0  # Defaults to entry price

    def test_current_value(self) -> None:
        pos = Position(
            symbol="AAPL",
            shares=100,
            entry_price=150.0,
            entry_date=date(2024, 1, 1),
            stop_loss=135.0,
            take_profit=180.0,
        )

        assert pos.current_value == 15000.0
        assert pos.cost_basis == 15000.0

    def test_unrealized_pnl(self) -> None:
        pos = Position(
            symbol="AAPL",
            shares=100,
            entry_price=150.0,
            entry_date=date(2024, 1, 1),
            stop_loss=135.0,
            take_profit=180.0,
        )
        pos.update_price(165.0, date(2024, 1, 15))

        assert pos.unrealized_pnl == 1500.0
        assert pos.unrealized_pnl_pct == 0.10

    def test_update_price(self) -> None:
        pos = Position(
            symbol="AAPL",
            shares=100,
            entry_price=150.0,
            entry_date=date(2024, 1, 1),
            stop_loss=135.0,
            take_profit=180.0,
        )
        pos.update_price(160.0, date(2024, 1, 10))

        assert pos.current_price == 160.0
        assert pos.current_date == date(2024, 1, 10)


class TestTrade:
    def test_trade_creation(self) -> None:
        trade = Trade(
            symbol="AAPL",
            entry_date=date(2024, 1, 1),
            entry_price=150.0,
            exit_date=date(2024, 2, 1),
            exit_price=165.0,
            shares=100,
            profit_loss=1500.0,
            profit_loss_pct=0.10,
            exit_reason="TAKE_PROFIT",
        )

        assert trade.symbol == "AAPL"
        assert trade.holding_days == 31
        assert trade.is_winner is True

    def test_losing_trade(self) -> None:
        trade = Trade(
            symbol="AAPL",
            entry_date=date(2024, 1, 1),
            entry_price=150.0,
            exit_date=date(2024, 1, 15),
            exit_price=135.0,
            shares=100,
            profit_loss=-1500.0,
            profit_loss_pct=-0.10,
            exit_reason="STOP_LOSS",
        )

        assert trade.is_winner is False
