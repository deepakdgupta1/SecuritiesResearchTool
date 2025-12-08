"""Risk management module for backtesting."""
from typing import Dict, List, Optional
import pandas as pd
from .positions import Position
from .utils import calculate_atr


class RiskManager:
    """
    Manages risk controls for the backtesting engine.

    Responsibilities:
    - Stop-loss management (fixed and trailing)
    - Position sizing
    - Portfolio-level risk limits
    """

    def __init__(
        self,
        initial_stop_loss_pct: float = 0.10,
        trailing_stop_trigger_pct: float = 0.15,
        trailing_stop_atr_multiplier: float = 2.0,
        max_position_size_pct: float = 0.10,
        max_portfolio_risk_pct: float = 0.02,
        max_drawdown_limit: float = 0.20,
    ):
        """
        Initialize risk manager.

        Args:
            initial_stop_loss_pct: Initial stop-loss (default 10%)
            trailing_stop_trigger_pct: Gain % to trigger trailing stop
            trailing_stop_atr_multiplier: ATR multiplier for trailing stop
            max_position_size_pct: Max position as % of portfolio
            max_portfolio_risk_pct: Max risk per trade as % of portfolio
            max_drawdown_limit: Stop trading if drawdown exceeds this
        """
        self.initial_stop_loss_pct = initial_stop_loss_pct
        self.trailing_stop_trigger_pct = trailing_stop_trigger_pct
        self.trailing_stop_atr_multiplier = trailing_stop_atr_multiplier
        self.max_position_size_pct = max_position_size_pct
        self.max_portfolio_risk_pct = max_portfolio_risk_pct
        self.max_drawdown_limit = max_drawdown_limit

    def calculate_initial_stop_loss(self, entry_price: float) -> float:
        """Calculate initial stop-loss price."""
        return entry_price * (1 - self.initial_stop_loss_pct)

    def calculate_take_profit(
        self, entry_price: float, target_pct: float = 0.20
    ) -> float:
        """Calculate take-profit price (default 20% target)."""
        return entry_price * (1 + target_pct)

    def update_trailing_stop(
        self,
        position: Position,
        current_price: float,
        atr: Optional[float] = None,
    ) -> float:
        """
        Update stop-loss with trailing logic.

        Hybrid approach:
        - Below trigger: keep initial stop
        - Above trigger: use ATR-based trailing stop

        Args:
            position: Current position
            current_price: Current market price
            atr: Average True Range (optional)

        Returns:
            New stop-loss price
        """
        # Check if trailing stop should be activated
        gain_pct = (current_price - position.entry_price) / position.entry_price

        if gain_pct < self.trailing_stop_trigger_pct:
            # Keep initial stop-loss
            return position.stop_loss

        # Calculate trailing stop
        if atr is not None and atr > 0:
            trailing_stop = current_price - (self.trailing_stop_atr_multiplier * atr)
        else:
            # Fallback: use percentage-based trailing
            trailing_stop = current_price * (1 - self.initial_stop_loss_pct)

        # Never lower the stop-loss
        return max(position.stop_loss, trailing_stop)

    def calculate_position_size(
        self,
        portfolio_value: float,
        entry_price: float,
        stop_loss_price: float,
    ) -> int:
        """
        Calculate position size based on risk parameters.

        Uses the smaller of:
        - Max position size (% of portfolio)
        - Risk-based size (% of portfolio at risk)

        Args:
            portfolio_value: Total portfolio value
            entry_price: Entry price
            stop_loss_price: Stop-loss price

        Returns:
            Number of shares to buy
        """
        # Method 1: Max position size
        max_position_value = portfolio_value * self.max_position_size_pct
        shares_by_size = int(max_position_value / entry_price)

        # Method 2: Risk-based sizing
        risk_per_share = entry_price - stop_loss_price
        if risk_per_share <= 0:
            return shares_by_size

        max_risk_amount = portfolio_value * self.max_portfolio_risk_pct
        shares_by_risk = int(max_risk_amount / risk_per_share)

        return min(shares_by_size, shares_by_risk)

    def check_drawdown_limit(self, current_drawdown: float) -> bool:
        """
        Check if drawdown exceeds limit.

        Args:
            current_drawdown: Current drawdown as decimal

        Returns:
            True if trading should stop
        """
        return current_drawdown >= self.max_drawdown_limit

    def check_correlation_risk(
        self,
        symbol: str,
        existing_positions: List[str],
    ) -> bool:
        """
        Check if new position is too correlated with existing.

        Note: Simplified implementation - always returns False.
        Full implementation would check sector/industry overlap.

        Args:
            symbol: Symbol to check
            existing_positions: List of existing position symbols

        Returns:
            True if position should be rejected
        """
        # Simplified: just check for duplicate
        return symbol in existing_positions
