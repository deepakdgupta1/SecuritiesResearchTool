"""Performance metrics calculator for backtesting."""
import numpy as np
import pandas as pd
from typing import List, Dict, Any
from .positions import Trade


class PerformanceCalculator:
    """
    Calculates performance metrics from backtest results.

    Metrics:
    - Total Return, Annualized Return, CAGR
    - Sharpe Ratio, Sortino Ratio
    - Max Drawdown
    - Win Rate, Profit Factor
    """

    def __init__(self, risk_free_rate: float = 0.04):
        """
        Initialize calculator.

        Args:
            risk_free_rate: Annual risk-free rate (default 4%)
        """
        self.risk_free_rate = risk_free_rate
        self.trading_days_per_year = 252

    def calculate_all_metrics(
        self,
        trades: List[Trade],
        equity_curve: pd.Series,
        initial_capital: float,
    ) -> Dict[str, Any]:
        """
        Calculate all performance metrics.

        Args:
            trades: List of completed trades
            equity_curve: Daily portfolio values
            initial_capital: Starting capital

        Returns:
            Dict with all metrics
        """
        if not equity_curve.empty:
            final_value = equity_curve.iloc[-1]
            total_return = (final_value - initial_capital) / initial_capital
            days = len(equity_curve)
        else:
            final_value = initial_capital
            total_return = 0.0
            days = 0

        returns = equity_curve.pct_change().dropna() if len(equity_curve) > 1 else pd.Series([])

        return {
            "total_return": total_return,
            "annualized_return": self.calculate_annualized_return(
                total_return, days
            ),
            "cagr": self.calculate_cagr(initial_capital, final_value, days),
            "sharpe_ratio": self.calculate_sharpe_ratio(returns),
            "sortino_ratio": self.calculate_sortino_ratio(returns),
            "max_drawdown": self.calculate_max_drawdown(equity_curve),
            "win_rate": self.calculate_win_rate(trades),
            "profit_factor": self.calculate_profit_factor(trades),
            "total_trades": len(trades),
            "winning_trades": sum(1 for t in trades if t.is_winner),
            "losing_trades": sum(1 for t in trades if not t.is_winner),
            "final_value": final_value,
        }

    def calculate_annualized_return(
        self, total_return: float, days: int
    ) -> float:
        """Annualize return based on trading days."""
        if days <= 0:
            return 0.0
        years = days / self.trading_days_per_year
        if years <= 0:
            return 0.0
        return float((1 + total_return) ** (1 / years) - 1)

    def calculate_cagr(
        self, initial_value: float, final_value: float, days: int
    ) -> float:
        """Calculate Compound Annual Growth Rate."""
        if days <= 0 or initial_value <= 0:
            return 0.0
        years = days / self.trading_days_per_year
        if years <= 0:
            return 0.0
        return float((final_value / initial_value) ** (1 / years) - 1)

    def calculate_sharpe_ratio(self, returns: pd.Series) -> float:
        """
        Calculate Sharpe Ratio.

        Sharpe = (Mean Return - Risk Free Rate) / Std Dev of Returns
        Annualized by sqrt(252)
        """
        if returns.empty or returns.std() == 0:
            return 0.0

        daily_rf = self.risk_free_rate / self.trading_days_per_year
        excess_returns = returns - daily_rf
        sharpe = excess_returns.mean() / excess_returns.std()

        # Annualize
        return float(sharpe * np.sqrt(self.trading_days_per_year))

    def calculate_sortino_ratio(self, returns: pd.Series) -> float:
        """
        Calculate Sortino Ratio.

        Like Sharpe, but only uses downside deviation.
        """
        if returns.empty:
            return 0.0

        daily_rf = self.risk_free_rate / self.trading_days_per_year
        excess_returns = returns - daily_rf

        # Downside deviation (only negative returns)
        downside = excess_returns[excess_returns < 0]
        if downside.empty or downside.std() == 0:
            return 0.0

        downside_std = downside.std()
        sortino = excess_returns.mean() / downside_std

        return float(sortino * np.sqrt(self.trading_days_per_year))

    def calculate_max_drawdown(self, equity_curve: pd.Series) -> float:
        """
        Calculate Maximum Drawdown.

        Max drawdown = largest peak-to-trough decline
        """
        if equity_curve.empty:
            return 0.0

        peak = equity_curve.expanding().max()
        drawdown = (equity_curve - peak) / peak
        return float(abs(drawdown.min()))

    def calculate_win_rate(self, trades: List[Trade]) -> float:
        """Calculate percentage of winning trades."""
        if not trades:
            return 0.0
        winners = sum(1 for t in trades if t.is_winner)
        return winners / len(trades)

    def calculate_profit_factor(self, trades: List[Trade]) -> float:
        """
        Calculate Profit Factor.

        Profit Factor = Gross Profit / Gross Loss
        """
        gross_profit = sum(t.profit_loss for t in trades if t.profit_loss > 0)
        gross_loss = abs(sum(t.profit_loss for t in trades if t.profit_loss < 0))

        if gross_loss == 0:
            return float("inf") if gross_profit > 0 else 0.0

        return gross_profit / gross_loss
