import pytest
import pandas as pd
import numpy as np
from datetime import date
from backend.patterns.stage_analysis import WeinsteinStageAnalyzer
from backend.patterns.base import PatternResult


@pytest.fixture
def stage2_data() -> pd.DataFrame:
    """Returns a DataFrame representing Stage 2 (Advancing)."""
    dates = pd.date_range(end=date.today(), periods=200)
    df = pd.DataFrame(index=dates)

    # Uptrending price above rising MA
    close = np.linspace(80, 150, 200)
    sma_150 = pd.Series(close).rolling(window=150).mean().values

    df["close"] = close
    df["sma_150"] = sma_150
    df["high"] = close + 2
    df["low"] = close - 2
    df["volume"] = 1000000

    return df


@pytest.fixture
def stage4_data() -> pd.DataFrame:
    """Returns a DataFrame representing Stage 4 (Declining)."""
    dates = pd.date_range(end=date.today(), periods=200)
    df = pd.DataFrame(index=dates)

    # Downtrending price below falling MA
    close = np.linspace(150, 80, 200)
    sma_150 = pd.Series(close).rolling(window=150).mean().values

    df["close"] = close
    df["sma_150"] = sma_150
    df["high"] = close + 2
    df["low"] = close - 2
    df["volume"] = 1000000

    return df


def test_detect_stage2(stage2_data: pd.DataFrame) -> None:
    analyzer = WeinsteinStageAnalyzer()
    result = analyzer.detect("TEST", stage2_data)

    assert result is not None
    assert result.pattern_type == "WEINSTEIN_STAGE"
    assert result.weinstein_stage == 2
    assert result.confirmed is True


def test_detect_stage4(stage4_data: pd.DataFrame) -> None:
    analyzer = WeinsteinStageAnalyzer()
    result = analyzer.detect("TEST", stage4_data)

    assert result is not None
    assert result.weinstein_stage == 4
    assert result.confirmed is False


def test_short_history() -> None:
    dates = pd.date_range(end=date.today(), periods=50)
    df = pd.DataFrame(index=dates)
    df["close"] = 100
    df["sma_150"] = 100
    df["volume"] = 1000000

    analyzer = WeinsteinStageAnalyzer()
    result = analyzer.detect("TEST", df)
    assert result is None
