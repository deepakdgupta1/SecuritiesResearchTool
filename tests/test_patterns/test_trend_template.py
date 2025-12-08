import pytest
import pandas as pd
import numpy as np
from datetime import date, timedelta
from backend.patterns.trend_template import TrendTemplateDetector
from backend.patterns.base import PatternResult


@pytest.fixture
def perfect_trend_data() -> pd.DataFrame:
    """Returns a DataFrame that perfectly matches all Trend Template criteria."""
    dates = pd.date_range(end=date.today(), periods=30)
    df = pd.DataFrame(index=dates)

    # 1. Price > 150 > 200
    # 200 SMA trending up
    sma_200 = np.linspace(100, 110, 30)  # Trending up
    sma_150 = sma_200 + 10  # 150 > 200
    sma_50 = sma_150 + 10  # 50 > 150
    close = sma_50 + 5  # Price > 50

    df['close'] = close
    df['sma_50'] = sma_50
    df['sma_150'] = sma_150
    df['sma_200'] = sma_200

    # 52 week high/low
    # Price should be within 25% of high and > 30% above low
    current_price = close[-1]
    df['week_52_high'] = current_price * 1.05  # Close is 95% of high (within 25%)
    df['week_52_low'] = current_price * 0.5  # Close is 200% of low (> 30% above)

    df['mansfield_rs'] = 1.0  # Positive RS

    return df


def test_detect_match(perfect_trend_data: pd.DataFrame) -> None:
    detector = TrendTemplateDetector()
    result = detector.detect("TEST", perfect_trend_data)

    assert result is not None
    assert isinstance(result, PatternResult)
    assert result.pattern_type == "TREND_TEMPLATE"
    assert result.symbol == "TEST"
    assert result.confirmed is True
    assert result.meets_trend_template is True


def test_detect_fail_price_below_50sma(perfect_trend_data: pd.DataFrame) -> None:
    # Modify data so price is below 50 SMA
    idx = perfect_trend_data.index[-1]
    perfect_trend_data.loc[idx, 'close'] = perfect_trend_data['sma_50'].iloc[-1] - 1

    detector = TrendTemplateDetector()
    result = detector.detect("TEST", perfect_trend_data)

    assert result is None


def test_detect_fail_200sma_downtrend(perfect_trend_data: pd.DataFrame) -> None:
    # 200 SMA trending down
    perfect_trend_data['sma_200'] = np.linspace(110, 100, 30)
    # Ensure other ordering criteria still met relative to this new 200 SMA
    perfect_trend_data['sma_150'] = perfect_trend_data['sma_200'] + 10
    perfect_trend_data['sma_50'] = perfect_trend_data['sma_150'] + 10
    perfect_trend_data['close'] = perfect_trend_data['sma_50'] + 5

    detector = TrendTemplateDetector()
    result = detector.detect("TEST", perfect_trend_data)

    assert result is None


def test_detect_fail_near_low(perfect_trend_data: pd.DataFrame) -> None:
    # Price near 52 week low (< 30% above low)
    current_price = perfect_trend_data['close'].iloc[-1]
    idx = perfect_trend_data.index[-1]
    perfect_trend_data.loc[idx, 'week_52_low'] = current_price * 0.9
    # Now price is only ~11% above low

    detector = TrendTemplateDetector()
    result = detector.detect("TEST", perfect_trend_data)

    assert result is None


def test_missing_data(perfect_trend_data: pd.DataFrame) -> None:
    # Drop required column
    df = perfect_trend_data.drop(columns=['sma_200'])
    detector = TrendTemplateDetector()
    result = detector.detect("TEST", df)
    assert result is None


def test_empty_data() -> None:
    detector = TrendTemplateDetector()
    result = detector.detect("TEST", pd.DataFrame())
    assert result is None
