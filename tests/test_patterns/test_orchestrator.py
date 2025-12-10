from datetime import date
from typing import Dict

import numpy as np
import pandas as pd
import pytest

from backend.patterns.orchestrator import PatternScanner
from backend.patterns.trend_template import TrendTemplateDetector


@pytest.fixture
def sample_data() -> pd.DataFrame:
    """Returns sample OHLCV data for testing."""
    dates = pd.date_range(end=date.today(), periods=200)
    df = pd.DataFrame(index=dates)

    # Create uptrending data that should trigger some patterns
    close = np.linspace(80, 150, 200)
    df["open"] = close - 1
    df["high"] = close + 2
    df["low"] = close - 2
    df["close"] = close
    df["volume"] = np.linspace(1000000, 500000, 200)

    # Add indicators for Trend Template
    df["sma_50"] = pd.Series(close).rolling(50).mean().values
    df["sma_150"] = pd.Series(close).rolling(150).mean().values
    df["sma_200"] = pd.Series(close).rolling(200).mean().values
    df["week_52_high"] = close[-1] * 1.05
    df["week_52_low"] = 80
    df["mansfield_rs"] = 1.0

    return df


def test_scanner_init_default() -> None:
    scanner = PatternScanner()
    assert len(scanner.detectors) == 6


def test_scanner_init_custom() -> None:
    scanner = PatternScanner(detectors=[TrendTemplateDetector()])
    assert len(scanner.detectors) == 1


def test_scan_symbol(sample_data: pd.DataFrame) -> None:
    scanner = PatternScanner()
    results = scanner.scan_symbol("TEST", sample_data)

    # Should return a list (possibly empty)
    assert isinstance(results, list)


def test_scan_universe(sample_data: pd.DataFrame) -> None:
    scanner = PatternScanner()
    universe: Dict[str, pd.DataFrame] = {
        "TEST1": sample_data,
        "TEST2": sample_data.copy(),
    }
    results = scanner.scan_universe(universe)

    assert isinstance(results, dict)


def test_get_actionable_setups(sample_data: pd.DataFrame) -> None:
    scanner = PatternScanner()
    universe: Dict[str, pd.DataFrame] = {"TEST": sample_data}
    results = scanner.get_actionable_setups(universe, min_confidence=50.0)

    assert isinstance(results, list)
    # Results should be sorted by confidence
    for i in range(len(results) - 1):
        assert results[i].confidence_score >= results[i + 1].confidence_score
