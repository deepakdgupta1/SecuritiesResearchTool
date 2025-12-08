import pytest
import pandas as pd
import numpy as np
from datetime import date
from backend.patterns.cup_with_handle import CupWithHandleDetector
from backend.patterns.base import PatternResult


@pytest.fixture
def cup_handle_data() -> pd.DataFrame:
    """Returns a DataFrame with a synthetic Cup & Handle pattern."""
    dates = pd.date_range(end=date.today(), periods=100)
    df = pd.DataFrame(index=dates)

    prices = np.ones(100) * 100

    # Left peak at day 10
    prices[:11] = np.linspace(90, 100, 11)

    # Drop to cup bottom at day 40 (25% drop)
    prices[10:41] = np.linspace(100, 75, 31)

    # Rise to right peak at day 70
    prices[40:71] = np.linspace(75, 98, 31)

    # Handle: small dip to day 85
    prices[70:86] = np.linspace(98, 90, 16)

    # Recovery
    prices[85:] = np.linspace(90, 97, 15)

    df["high"] = prices + 1
    df["low"] = prices - 1
    df["close"] = prices
    df["open"] = prices
    df["volume"] = np.linspace(1000000, 500000, 100)

    return df


def test_detect_cup_and_handle(cup_handle_data: pd.DataFrame) -> None:
    detector = CupWithHandleDetector()
    result = detector.detect("TEST", cup_handle_data)

    assert result is not None
    assert result.pattern_type in ["CUP_AND_HANDLE", "CUP_FORMING"]


def test_short_history() -> None:
    dates = pd.date_range(end=date.today(), periods=20)
    df = pd.DataFrame(index=dates)
    df["high"] = 100
    df["low"] = 99
    df["close"] = 99.5
    df["volume"] = 1000000

    detector = CupWithHandleDetector()
    result = detector.detect("TEST", df)
    assert result is None
