"""Core backtesting engine with positions-first algorithm."""
import logging
from datetime import date, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd

from .positions import Position, Trade
from .risk_manager import RiskManager
from .performance import PerformanceCalculator
from .utils import calculate_atr, get_trading_days

logger = logging.getLogger(__name__)


class BacktestEngine:
    """
    Systematic backtesting engine with positions-first approach.

    Algorithm order (CRITICAL for correct results):
    1. Update existing positions with current prices
    2. Check exit conditions for ALL positions
    3. Update portfolio metrics
    4. Scan for pattern matches
    5. Generate entry signals
    6. Check risk management constraints
    7. Execute approved entries
    """

    def __init__(
        self,
        initial_capital: float = 100000.0,
        max_positions: int = 10,
        risk_manager: Optional[RiskManager] = None,
    ):
        """
        Initialize backtesting engine.

        Args:
            initial_capital: Starting capital
            max_positions: Maximum concurrent positions
            risk_manager: Risk management instance
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.max_positions = max_positions
        self.risk_manager = risk_manager or RiskManager()
        self.performance_calc = PerformanceCalculator()

        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = []
        self.peak_equity = initial_capital

    def reset(self) -> None:
        """Reset engine state for new backtest."""
        self.cash = self.initial_capital
        self.positions = {}
        self.trades = []
        self.equity_curve = []
        self.peak_equity = self.initial_capital

    def run_backtest(
        self,
        price_data: Dict[str, pd.DataFrame],
        signals: Optional[Dict[str, List[Dict[str, Any]]]] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """
        Execute backtest over date range.

        Args:
            price_data: Dict of symbol -> OHLCV DataFrame
            signals: Optional pre-computed signals {date_str: [signal_dicts]}
            start_date: Backtest start date
            end_date: Backtest end date

        Returns:
            Dict with performance metrics and trade history
        """
        self.reset()

        # Determine date range from data if not provided
        all_dates = set()
        for df in price_data.values():
            all_dates.update(df.index.date if hasattr(df.index, 'date') else df.index)

        if not all_dates:
            return self._get_results()

        sorted_dates = sorted(all_dates)
        start = start_date or sorted_dates[0]
        end = end_date or sorted_dates[-1]

        # Filter to date range
        trading_dates = [d for d in sorted_dates if start <= d <= end]

        # Main backtest loop
        for current_date in trading_dates:
            self._process_day(current_date, price_data, signals)

        return self._get_results()

    def _process_day(
        self,
        current_date: date,
        price_data: Dict[str, pd.DataFrame],
        signals: Optional[Dict[str, List[Dict[str, Any]]]],
    ) -> None:
        """Process a single trading day."""
        # STEP A: Update existing positions
        self._update_positions(current_date, price_data)

        # STEP B: Check exit conditions
        self._check_exits(current_date, price_data)

        # STEP C: Update portfolio metrics
        portfolio_value = self._calculate_portfolio_value()
        self.equity_curve.append(portfolio_value)
        self.peak_equity = max(self.peak_equity, portfolio_value)

        # STEP D-G: Process entries if signals provided
        if signals:
            date_str = str(current_date)
            day_signals = signals.get(date_str, [])
            self._process_entries(current_date, day_signals, price_data)

    def _update_positions(
        self, current_date: date, price_data: Dict[str, pd.DataFrame]
    ) -> None:
        """Update all positions with current prices."""
        for symbol, position in self.positions.items():
            if symbol in price_data:
                df = price_data[symbol]
                # Get price for current date
                if current_date in df.index:
                    row = df.loc[current_date]
                    position.update_price(row["close"], current_date)

                    # Update trailing stop if applicable
                    atr_val = None
                    if len(df) >= 14:
                        atr = calculate_atr(df["high"], df["low"], df["close"])
                        if current_date in atr.index:
                            atr_val = atr.loc[current_date]

                    new_stop = self.risk_manager.update_trailing_stop(
                        position, position.current_price, atr_val
                    )
                    position.stop_loss = new_stop

    def _check_exits(
        self, current_date: date, price_data: Dict[str, pd.DataFrame]
    ) -> None:
        """Check and execute exit conditions."""
        exit_signals = []

        for symbol, position in list(self.positions.items()):
            # Check stop-loss
            if position.current_price <= position.stop_loss:
                exit_signals.append({
                    "symbol": symbol,
                    "reason": "STOP_LOSS",
                    "price": position.current_price,
                })
            # Check take-profit
            elif position.current_price >= position.take_profit:
                exit_signals.append({
                    "symbol": symbol,
                    "reason": "TAKE_PROFIT",
                    "price": position.current_price,
                })

        # Execute exits
        for exit_signal in exit_signals:
            self._execute_exit(
                symbol=exit_signal["symbol"],
                exit_price=exit_signal["price"],
                exit_date=current_date,
                reason=exit_signal["reason"],
            )

    def _process_entries(
        self,
        current_date: date,
        day_signals: List[Dict[str, Any]],
        price_data: Dict[str, pd.DataFrame],
    ) -> None:
        """Process entry signals for the day."""
        # Sort by confidence
        sorted_signals = sorted(
            day_signals, key=lambda x: x.get("confidence", 0), reverse=True
        )

        portfolio_value = self._calculate_portfolio_value()
        current_drawdown = self._calculate_current_drawdown()

        for signal in sorted_signals:
            # Check position slots
            if len(self.positions) >= self.max_positions:
                break

            # Check drawdown limit
            if self.risk_manager.check_drawdown_limit(current_drawdown):
                break

            symbol = signal.get("symbol")
            if not symbol or symbol in self.positions:
                continue

            # Get entry price
            if symbol not in price_data:
                continue
            df = price_data[symbol]
            if current_date not in df.index:
                continue

            entry_price = df.loc[current_date, "close"]
            stop_loss = self.risk_manager.calculate_initial_stop_loss(entry_price)
            take_profit = self.risk_manager.calculate_take_profit(entry_price)

            # Calculate position size
            shares = self.risk_manager.calculate_position_size(
                portfolio_value, entry_price, stop_loss
            )
            if shares <= 0:
                continue

            cost = shares * entry_price
            if cost > self.cash:
                # Reduce to affordable size
                shares = int(self.cash / entry_price)
                if shares <= 0:
                    continue
                cost = shares * entry_price

            # Execute entry
            self._execute_entry(
                symbol=symbol,
                shares=shares,
                entry_price=entry_price,
                entry_date=current_date,
                stop_loss=stop_loss,
                take_profit=take_profit,
            )

    def _execute_entry(
        self,
        symbol: str,
        shares: int,
        entry_price: float,
        entry_date: date,
        stop_loss: float,
        take_profit: float,
    ) -> None:
        """Execute position entry."""
        cost = shares * entry_price

        position = Position(
            symbol=symbol,
            shares=shares,
            entry_price=entry_price,
            entry_date=entry_date,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )

        self.positions[symbol] = position
        self.cash -= cost

        logger.info(f"ENTRY: {symbol} {shares} shares @ ${entry_price:.2f}")

    def _execute_exit(
        self,
        symbol: str,
        exit_price: float,
        exit_date: date,
        reason: str,
    ) -> None:
        """Execute position exit."""
        position = self.positions.pop(symbol)

        proceeds = position.shares * exit_price
        profit_loss = proceeds - position.cost_basis
        profit_loss_pct = profit_loss / position.cost_basis

        self.cash += proceeds

        trade = Trade(
            symbol=symbol,
            entry_date=position.entry_date,
            entry_price=position.entry_price,
            exit_date=exit_date,
            exit_price=exit_price,
            shares=position.shares,
            profit_loss=profit_loss,
            profit_loss_pct=profit_loss_pct,
            exit_reason=reason,
        )
        self.trades.append(trade)

        logger.info(
            f"EXIT: {symbol} {position.shares} shares @ ${exit_price:.2f} "
            f"({reason}) P&L: ${profit_loss:.2f} ({profit_loss_pct*100:.1f}%)"
        )

    def _calculate_portfolio_value(self) -> float:
        """Calculate total portfolio value."""
        position_value = sum(p.current_value for p in self.positions.values())
        return self.cash + position_value

    def _calculate_current_drawdown(self) -> float:
        """Calculate current drawdown from peak."""
        current_value = self._calculate_portfolio_value()
        if self.peak_equity <= 0:
            return 0.0
        return (self.peak_equity - current_value) / self.peak_equity

    def _get_results(self) -> Dict[str, Any]:
        """Compile final backtest results."""
        equity_series = pd.Series(self.equity_curve)

        metrics = self.performance_calc.calculate_all_metrics(
            trades=self.trades,
            equity_curve=equity_series,
            initial_capital=self.initial_capital,
        )

        return {
            "metrics": metrics,
            "trades": self.trades,
            "equity_curve": equity_series,
            "open_positions": list(self.positions.values()),
        }
