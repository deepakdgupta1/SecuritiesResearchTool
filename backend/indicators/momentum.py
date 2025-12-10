"""
Momentum indicators calculation module.
"""

import pandas as pd
import pandas_ta as ta


def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI).

    Args:
        series: Price series (usually close price).
        period: The period for RSI calculation.

    Returns:
        pd.Series: RSI series.
    """
    return ta.rsi(series, length=period)


def calculate_macd(
    series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
) -> pd.DataFrame:
    """
    Calculate Moving Average Convergence Divergence (MACD).

    Args:
        series: Price series (usually close price).
        fast: Fast EMA period.
        slow: Slow EMA period.
        signal: Signal line EMA period.

    Returns:
        pd.DataFrame: DataFrame with columns ['macd', 'macd_signal', 'macd_histogram'].
    """
    macd_df = ta.macd(series, fast=fast, slow=slow, signal=signal)

    # pandas_ta returns columns like MACD_12_26_9, MACDs_12_26_9, MACDh_12_26_9
    # We need to rename them to standard names

    # Find the column names dynamically as they depend on the periods
    macd_col = f"MACD_{fast}_{slow}_{signal}"
    signal_col = f"MACDs_{fast}_{slow}_{signal}"
    hist_col = f"MACDh_{fast}_{slow}_{signal}"

    result = pd.DataFrame(index=series.index)
    result["macd"] = macd_df[macd_col]
    result["macd_signal"] = macd_df[signal_col]
    result["macd_histogram"] = macd_df[hist_col]

    return result


def calculate_all_momentum_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate all required momentum indicators for the DataFrame.
    Adds columns: rsi_14, macd, macd_signal, macd_histogram.

    Args:
        df: DataFrame containing 'close' column.

    Returns:
        pd.DataFrame: DataFrame with added momentum indicator columns.
    """
    if "close" not in df.columns:
        raise ValueError("DataFrame must contain 'close' column")

    df["rsi_14"] = calculate_rsi(df["close"], 14)

    macd_data = calculate_macd(df["close"])
    df["macd"] = macd_data["macd"]
    df["macd_signal"] = macd_data["macd_signal"]
    df["macd_histogram"] = macd_data["macd_histogram"]

    return df
