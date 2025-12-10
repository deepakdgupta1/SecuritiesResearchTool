from typing import List, Tuple

import numpy as np
import pandas as pd


def find_local_extrema(
        data: pd.Series, order: int = 5) -> Tuple[List[int], List[int]]:
    """
    Finds local maxima and minima in the data.

    Args:
        data: Series of prices (usually Highs or Lows)
        order: Number of points on each side to use for comparison

    Returns:
        Tuple of (indices_of_maxima, indices_of_minima)
    """
    # Using simple rolling window check or specialized library logic if imports allowed
    # Implementing a simple vectorized approach using scipy.signal.argrelextrema equivalent logic
    # but avoiding extra heavy dependencies if possible.
    # Let's stick to a robust standard implementation.

    # We can iterate or use shift comparison for efficiency
    # For MVP, a simple loop or shift logic is fine.

    # Standard argrelextrema equivalent using pandas shifts
    # (checking if point is higher/lower than neighbors)

    is_max = np.ones(len(data), dtype=bool)
    is_min = np.ones(len(data), dtype=bool)

    for i in range(1, order + 1):
        is_max &= (data > data.shift(i)) & (data > data.shift(-i))
        is_min &= (data < data.shift(i)) & (data < data.shift(-i))

    local_max_indices = np.where(is_max)[0]
    local_min_indices = np.where(is_min)[0]

    return local_max_indices.tolist(), local_min_indices.tolist()


def calculate_slope(series: pd.Series) -> float:
    """
    Calculates the linear regression slope of a series.

    Args:
        series: Time series data

    Returns:
        Slope value
    """
    y = series.values
    x = np.arange(len(y))
    if len(y) < 2:
        return 0.0
    slope, _ = np.polyfit(x, y, 1)
    return slope


def is_volume_drying_up(
        volume: pd.Series,
        window: int = 20,
        threshold_ratio: float = 0.8) -> bool:
    """
    Checks if volume is contracting (drying up).

    Args:
        volume: Volume series
        window: Lookback period
        threshold_ratio: Ratio of current avg volume to past avg volume to consider 'dry'

    Returns:
        True if volume is significantly lower than average
    """
    if len(volume) < window * 2:
        return False

    current_vol = volume.iloc[-window:].mean()
    past_vol = volume.iloc[-window * 2:-window].mean()

    return bool(current_vol < (past_vol * threshold_ratio))


def calculate_percentage_change(start_price: float, end_price: float) -> float:
    """Calculates percentage change between two prices."""
    if start_price == 0:
        return 0.0
    return ((end_price - start_price) / start_price) * 100.0
