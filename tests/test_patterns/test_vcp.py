import pytest
import pandas as pd
import numpy as np
from datetime import date, timedelta
from backend.patterns.vcp import VCPDetector
from backend.patterns.base import PatternResult


@pytest.fixture
def vcp_data() -> pd.DataFrame:
    """Returns a DataFrame with a synthetic VCP pattern."""
    # Create 200 days of data
    processed_dates = pd.date_range(end=date.today(), periods=200)
    df = pd.DataFrame(index=processed_dates)

    # Base pattern:
    # We construct a series of waves.
    # Wave 1: High at 100, Lowat 80 (-20%), High at 95
    # Wave 2: High at 95, Low at 88 (-7%), High at 94
    # Wave 3: High at 94, Low at 91 (-3%), High at 94

    prices = np.ones(200) * 100

    # We need to manually set the oscillation to ensure local extrema are detected
    # find_local_extrema uses order=5 (5 days lookback/forward)
    # So pivots need to be spaced out by at least 5-6 days.

    # Set Start High at day 50
    prices[50] = 100

    # Drop to Low 1 at day 70 (20% drop -> 80)
    prices[70] = 80
    # Linearly interpolate 50->70
    prices[50:71] = np.linspace(100, 80, 21)

    # Rally to High 2 at day 100 (95)
    prices[100] = 95
    prices[70:101] = np.linspace(80, 95, 31)

    # Drop to Low 2 at day 120 (88)
    prices[120] = 88
    prices[100:121] = np.linspace(95, 88, 21)

    # Rally to High 3 at day 140 (94)
    prices[140] = 94
    prices[120:141] = np.linspace(88, 94, 21)

    # Drop to Low 3 at day 160 (91)
    prices[160] = 91
    prices[140:161] = np.linspace(94, 91, 21)

    # Rally to finish at day 180 (94)
    prices[180] = 94
    prices[160:181] = np.linspace(91, 94, 21)

    # Flat/Tight finish
    prices[181:] = 94

    # Add some noise so flat lines don't mess up extrema detection?
    # Or rely on the sharp points being extrema.
    # The simple extrema check: val > neighbors.
    # With linear interpolation, intermediate points are not local extrema.
    # But the pivot points (50, 70, 100, 120, 140, 160, 180) are indeed extrema
    # (provided the previous/next points are lower/higher).
    # e.g. at 50: 100. Prev is 100 (flat).
    # Wait, my init was `ones * 100`. So before 50 it is 100.
    # So 50 is not strictly > neighbors (it is >=).
    # `find_local_extrema` used `>`.
    # I should lower the prices before 50.
    prices[:50] = np.linspace(90, 99, 50)

    df['high'] = prices
    df['low'] = prices - 1  # Low is slightly below high
    df['close'] = prices - 0.5
    df['open'] = prices - 0.5

    # Volume decreasing
    # Start high volume, end low volume
    vol = np.linspace(1000000, 200000, 200)
    # Add some noise
    vol = vol * np.random.normal(1, 0.1, 200)
    df['volume'] = vol

    return df


def test_detect_vcp_match(vcp_data: pd.DataFrame) -> None:
    detector = VCPDetector()
    result = detector.detect("TEST", vcp_data)

    assert result is not None, "VCP should be detected"
    assert result.pattern_type == "VCP"
    assert result.meta_data['contractions'] >= 2
    assert result.meta_data['volume_dry_up'] is True

    # Verify depths are decreasing
    depths = result.meta_data['depths']
    assert depths[0] > depths[1]


def test_detect_fail_increasing_volatility(vcp_data: pd.DataFrame) -> None:
    # Make the second contraction deeper than first
    # First drop: 100 -> 80 (20%)
    # Second drop: originally 95 -> 88.
    # Change Low 2 to 60 (huge drop from 95 -> 60 is ~36%)
    # Since prices is numpy array in fixture, we can modify df directly

    # We need to modify Highs/Lows around the pivot points
    # Pivot Low 2 is at index 120.
    # Pivot High 2 is at index 100 (95).
    # Let's make Low 2 at index 120 be 60.
    # And interpolate.

    # Note: vcp_data is a fixture, we modify the DF
    df = vcp_data.copy()

    # Reconstruct the drop from 100 to 120
    # 100 -> 120: 95 down to 60
    # We need to update 'high' and 'low'
    new_prices = np.linspace(95, 60, 21)
    # Indices 100 to 120 - use loc for pandas 3.0 compatibility
    df.loc[df.index[100:121], 'high'] = new_prices
    df.loc[df.index[100:121], 'low'] = new_prices - 1

    # And rally back up? Or just leave the rest.
    # If we drop to 60, detecting the NEXT high at 140 (94) which was previously set
    # might still happen.
    # The contraction would be 95 -> 60 (36%).
    # Previous was 20%.
    # 36 > 20 -> Fail.

    detector = VCPDetector()
    result = detector.detect("TEST", df)

    assert result is None


def test_short_history(vcp_data: pd.DataFrame) -> None:
    # Pass only 30 days
    detector = VCPDetector()
    result = detector.detect("TEST", vcp_data.iloc[-30:])
    assert result is None
