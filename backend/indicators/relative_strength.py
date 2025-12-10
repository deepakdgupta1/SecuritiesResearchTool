"""
Relative strength indicators calculation module.
"""

import pandas as pd


def calculate_mansfield_rs(
        symbol_df: pd.DataFrame,
        benchmark_df: pd.DataFrame,
        period: int = 52) -> pd.Series:
    """
    Calculate Mansfield Relative Strength.

    Formula:
    1. Calculate Relative Performance (RP) = Symbol Close / Benchmark Close
    2. Calculate 52-week SMA of RP (SMA_RP)
    3. Mansfield RS = ((RP / SMA_RP) - 1) * 10

    Args:
        symbol_df: DataFrame for the symbol containing 'close' column.
        benchmark_df: DataFrame for the benchmark containing 'close' column.
        period: Period for SMA calculation (default 52 weeks = 252 days approx).
                Using 52 weeks is standard, but daily data implies ~252 days.
                Let's use 252 days as default for daily data.

    Returns:
        pd.Series: Mansfield RS series.
    """
    if "close" not in symbol_df.columns:
        raise ValueError("Symbol DataFrame must contain 'close' column")
    if "close" not in benchmark_df.columns:
        raise ValueError("Benchmark DataFrame must contain 'close' column")

    # Align dates
    # We need to ensure both series share the same index
    common_index = symbol_df.index.intersection(benchmark_df.index)

    if len(common_index) == 0:
        # Return empty series with correct index
        return pd.Series(index=symbol_df.index, dtype=float)

    s_close = symbol_df.loc[common_index, "close"]
    b_close = benchmark_df.loc[common_index, "close"]

    # 1. Relative Performance
    rp = s_close / b_close

    # 2. SMA of RP
    # 52 weeks * 5 days = 260 days. Standard is often 52 weeks.
    # If we assume daily data, 252 is a trading year.
    sma_rp = rp.rolling(window=252).mean()

    # 3. Mansfield RS
    mansfield_rs = ((rp / sma_rp) - 1) * 10

    # Reindex to original symbol index to keep shape (fill missing with NaN)
    return mansfield_rs.reindex(symbol_df.index)


def calculate_all_rs_indicators(
    df: pd.DataFrame, benchmark_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate all required relative strength indicators.
    Adds columns: mansfield_rs.

    Args:
        df: Symbol DataFrame.
        benchmark_df: Benchmark DataFrame.

    Returns:
        pd.DataFrame: DataFrame with added RS columns.
    """
    df["mansfield_rs"] = calculate_mansfield_rs(df, benchmark_df)
    return df
