"""
Volume indicators calculation module.
"""

import pandas as pd


def calculate_average_volume(series: pd.Series, period: int = 50) -> pd.Series:
    """
    Calculate Average Volume.

    Args:
        series: Volume series.
        period: The period for average calculation.

    Returns:
        pd.Series: Average volume series.
    """
    return series.rolling(window=period).mean()


def calculate_all_volume_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate all required volume indicators for the DataFrame.
    Adds columns: volume_avg_50.

    Args:
        df: DataFrame containing 'volume' column.

    Returns:
        pd.DataFrame: DataFrame with added volume indicator columns.
    """
    if "volume" not in df.columns:
        raise ValueError("DataFrame must contain 'volume' column")

    df["volume_avg_50"] = calculate_average_volume(df["volume"], 50)

    return df
