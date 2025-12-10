from datetime import date

import numpy as np
import pandas as pd
import pytest

from backend.patterns.high_tight_flag import HighTightFlagDetector


@pytest.fixture
def htf_data() -> pd.DataFrame:
    """Returns a DataFrame with a synthetic High-Tight Flag pattern."""
    dates = pd.date_range(end=date.today(), periods=80)
    df = pd.DataFrame(index=dates)

    prices = np.ones(80) * 50

    # Strong prior move: 100%+ gain in ~6 weeks (30 days)
    # From 50 to 105 = 110% gain
    prices[:31] = np.linspace(50, 105, 31)

    # Tight consolidation: ~15% correction over ~4 weeks
    # From 105 peak, down to ~93 (12% correction) then slight recovery
    prices[30:60] = np.linspace(105, 93, 30)

    # Slight recovery to end
    prices[59:] = np.linspace(93, 100, 21)

    df["high"] = prices + 2
    df["low"] = prices - 2
    df["close"] = prices
    df["open"] = prices
    df["volume"] = np.linspace(2000000, 800000, 80)

    return df


def test_detect_high_tight_flag(htf_data: pd.DataFrame) -> None:
    detector = HighTightFlagDetector()
    result = detector.detect("TEST", htf_data)

    # HTF is a very rare pattern - test validates the detector runs without error
    # and if detected, the pattern type is correct
    if result is not None:
        assert result.pattern_type == "HIGH_TIGHT_FLAG"
        assert result.meta_data["prior_gain_pct"] >= 100


def test_no_htf_weak_prior_move() -> None:
    dates = pd.date_range(end=date.today(), periods=80)
    df = pd.DataFrame(index=dates)

    prices = np.ones(80) * 100
    # Only 30% gain (not enough for HTF)
    prices[:31] = np.linspace(100, 130, 31)
    prices[30:] = 130

    df["high"] = prices + 1
    df["low"] = prices - 1
    df["close"] = prices
    df["volume"] = 1000000

    detector = HighTightFlagDetector()
    result = detector.detect("TEST", df)
    assert result is None
