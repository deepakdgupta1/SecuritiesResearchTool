"""
Moving averages calculation module.
"""

import pandas as pd


def calculate_sma(series: pd.Series, period: int) -> pd.Series:
    """
    Calculate Simple Moving Average (SMA).

    Args:
        series: Price series (usually close price).
        period: The period for SMA calculation.

    Returns:
        pd.Series: SMA series.
    """
    return series.rolling(window=period).mean()


def calculate_ema(series: pd.Series, period: int) -> pd.Series:
    """
    Calculate Exponential Moving Average (EMA).

    Args:
        series: Price series (usually close price).
        period: The period for EMA calculation.

    Returns:
        pd.Series: EMA series.
    """
    return series.ewm(span=period, adjust=False).mean()


def calculate_all_moving_averages(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate all required moving averages for the DataFrame.
    Adds columns: sma_50, sma_150, sma_200, ema_50, ema_150, ema_200.

    Args:
        df: DataFrame containing 'close' column.

    Returns:
        pd.DataFrame: DataFrame with added moving average columns.
    """
    if "close" not in df.columns:
        raise ValueError("DataFrame must contain 'close' column")

    df["sma_50"] = calculate_sma(df["close"], 50)
    df["sma_150"] = calculate_sma(df["close"], 150)
    df["sma_200"] = calculate_sma(df["close"], 200)

    df["ema_50"] = calculate_ema(df["close"], 50)
    df["ema_150"] = calculate_ema(df["close"], 150)
    df["ema_200"] = calculate_ema(df["close"], 200)

    return df
