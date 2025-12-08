"""Position and Trade dataclasses for backtesting."""
from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class Position:
    """
    Represents an open position in the portfolio.

    Tracks entry details, current state, and risk parameters.
    """

    symbol: str
    shares: int
    entry_price: float
    entry_date: date
    stop_loss: float
    take_profit: float
    current_price: float = field(default=0.0)
    current_date: Optional[date] = None

    def __post_init__(self) -> None:
        if self.current_price == 0.0:
            self.current_price = self.entry_price
        if self.current_date is None:
            self.current_date = self.entry_date

    @property
    def current_value(self) -> float:
        """Current market value of the position."""
        return self.shares * self.current_price

    @property
    def cost_basis(self) -> float:
        """Original cost of the position."""
        return self.shares * self.entry_price

    @property
    def unrealized_pnl(self) -> float:
        """Unrealized profit/loss in currency."""
        return self.current_value - self.cost_basis

    @property
    def unrealized_pnl_pct(self) -> float:
        """Unrealized profit/loss as percentage."""
        if self.cost_basis == 0:
            return 0.0
        return self.unrealized_pnl / self.cost_basis

    def update_price(self, price: float, dt: date) -> None:
        """Update position with current market price."""
        self.current_price = price
        self.current_date = dt


@dataclass
class Trade:
    """
    Represents a completed trade (entry + exit).

    Records full trade lifecycle for performance analysis.
    """

    symbol: str
    entry_date: date
    entry_price: float
    exit_date: date
    exit_price: float
    shares: int
    profit_loss: float
    profit_loss_pct: float
    exit_reason: str  # STOP_LOSS, TAKE_PROFIT, TRAILING_STOP, SIGNAL

    @property
    def holding_days(self) -> int:
        """Number of days position was held."""
        return (self.exit_date - self.entry_date).days

    @property
    def is_winner(self) -> bool:
        """True if trade was profitable."""
        return self.profit_loss > 0
