"""Utility functions for backtesting."""
from typing import List

import pandas as pd


def calculate_atr(
    high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14
) -> pd.Series:
    """
    Calculate Average True Range (ATR).

    ATR is used for trailing stop calculations.

    Args:
        high: High prices
        low: Low prices
        close: Close prices
        period: ATR period (default 14)

    Returns:
        ATR values as pandas Series
    """
    high_low = high - low
    high_close_prev = abs(high - close.shift(1))
    low_close_prev = abs(low - close.shift(1))

    tr = pd.concat([high_low, high_close_prev, low_close_prev],
                   axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()

    return atr


def get_trading_days(
    start_date: pd.Timestamp, end_date: pd.Timestamp
) -> List[pd.Timestamp]:
    """
    Generate list of trading days between dates.

    Uses pandas business day frequency.

    Args:
        start_date: Start date
        end_date: End date

    Returns:
        List of trading day timestamps
    """
    return list(pd.bdate_range(start=start_date, end=end_date))


def annualize_return(total_return: float, days: int) -> float:
    """
    Annualize a return based on holding period.

    Args:
        total_return: Total return as decimal (0.10 = 10%)
        days: Number of trading days

    Returns:
        Annualized return as decimal
    """
    if days <= 0:
        return 0.0

    trading_days_per_year = 252
    years = days / trading_days_per_year

    if years <= 0:
        return 0.0

    # CAGR formula: (1 + total_return) ^ (1/years) - 1
    return float((1 + total_return) ** (1 / years) - 1)
