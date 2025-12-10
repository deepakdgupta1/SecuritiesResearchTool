from datetime import date

import numpy as np
import pandas as pd
import pytest

from backend.patterns.double_bottom import DoubleBottomDetector


@pytest.fixture
def double_bottom_data() -> pd.DataFrame:
    """Returns a DataFrame with a synthetic Double Bottom pattern."""
    dates = pd.date_range(end=date.today(), periods=80)
    df = pd.DataFrame(index=dates)

    prices = np.ones(80) * 100

    # First drop to low at day 20
    prices[:21] = np.linspace(100, 80, 21)

    # Rise to middle peak at day 40
    prices[20:41] = np.linspace(80, 95, 21)

    # Second drop to low at day 55 (slightly undercut)
    prices[40:56] = np.linspace(95, 79, 16)

    # Recovery
    prices[55:] = np.linspace(79, 98, 25)

    df["high"] = prices + 1
    df["low"] = prices - 1
    df["close"] = prices
    df["open"] = prices
    df["volume"] = np.linspace(1000000, 500000, 80)

    return df


def test_detect_double_bottom(double_bottom_data: pd.DataFrame) -> None:
    detector = DoubleBottomDetector()
    result = detector.detect("TEST", double_bottom_data)

    assert result is not None
    assert result.pattern_type == "DOUBLE_BOTTOM"
    assert result.meta_data["is_undercut"] is True


def test_no_pattern_flat_data() -> None:
    dates = pd.date_range(end=date.today(), periods=80)
    df = pd.DataFrame(index=dates)
    df["high"] = 100
    df["low"] = 99
    df["close"] = 99.5
    df["volume"] = 1000000

    detector = DoubleBottomDetector()
    result = detector.detect("TEST", df)
    assert result is None
