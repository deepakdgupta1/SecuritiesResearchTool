"""
Price action indicators calculation module.
"""

import pandas as pd


def calculate_52_week_high_low(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate 52-week High and Low.
    Adds columns: week_52_high, week_52_low.

    Args:
        df: DataFrame containing 'high' and 'low' columns, indexed by date.

    Returns:
        pd.DataFrame: DataFrame with added 52-week high/low columns.
    """
    if "high" not in df.columns or "low" not in df.columns:
        raise ValueError("DataFrame must contain 'high' and 'low' columns")

    # 52 weeks * 5 trading days = 260 days (approx)
    # Using 252 trading days is standard for a year
    window = 252

    df["week_52_high"] = df["high"].rolling(window=window, min_periods=1).max()
    df["week_52_low"] = df["low"].rolling(window=window, min_periods=1).min()

    return df
