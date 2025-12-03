"""
Unit tests for technical indicators.
"""

import pandas as pd
import pytest
from backend.indicators.moving_averages import calculate_sma, calculate_ema, calculate_all_moving_averages


@pytest.fixture
def sample_price_data():
    """Create sample price data for testing."""
    dates = pd.date_range(start="2023-01-01", periods=300, freq="D")
    # Create a simple linear trend for easy verification
    prices = [100 + i for i in range(300)]
    df = pd.DataFrame({"close": prices}, index=dates)
    return df


def test_calculate_sma(sample_price_data):
    """Test Simple Moving Average calculation."""
    series = sample_price_data["close"]
    period = 50
    sma = calculate_sma(series, period)
    
    # Check length
    assert len(sma) == len(series)
    
    # First (period-1) values should be NaN
    assert pd.isna(sma.iloc[period-2])
    
    # Check value at index 'period-1' (50th value, index 49)
    # Sum of 100..149 = 50 * (100 + 149) / 2 = 6225
    # SMA = 6225 / 50 = 124.5
    assert sma.iloc[period-1] == 124.5
    
    # Check last value
    # Last 50 values: 350..399 (indices 250..299) -> prices 350..399
    # Wait, prices are 100 + i.
    # Last index is 299. Price is 100 + 299 = 399.
    # Window is indices 250 to 299.
    # Prices: 350, 351, ..., 399.
    # Average should be (350 + 399) / 2 = 374.5
    assert sma.iloc[-1] == 374.5


def test_calculate_ema(sample_price_data):
    """Test Exponential Moving Average calculation."""
    series = sample_price_data["close"]
    period = 50
    ema = calculate_ema(series, period)
    
    # Check length
    assert len(ema) == len(series)
    
    # EMA should not have NaNs if adjust=False is used? 
    # Wait, pandas ewm with adjust=False starts calculation from the beginning.
    # So no NaNs.
    assert not pd.isna(ema.iloc[0])
    
    # Check that EMA follows the trend
    assert ema.iloc[-1] > ema.iloc[0]


def test_calculate_all_moving_averages(sample_price_data):
    """Test wrapper function for all moving averages."""
    df = calculate_all_moving_averages(sample_price_data)
    
    expected_columns = [
        "sma_50", "sma_150", "sma_200",
        "ema_50", "ema_150", "ema_200"
    ]
    
    for col in expected_columns:
        assert col in df.columns
        # Check that we have values (at least at the end)
        assert not pd.isna(df[col].iloc[-1])


def test_calculate_rsi(sample_price_data):
    """Test RSI calculation."""
    series = sample_price_data["close"]
    from backend.indicators.momentum import calculate_rsi
    
    rsi = calculate_rsi(series, period=14)
    
    # Check length
    assert len(rsi) == len(series)
    
    # RSI should be between 0 and 100
    # First few values will be NaN, but pandas_ta might differ on exact count
    assert pd.isna(rsi.iloc[0])
    
    # Check valid values
    valid_rsi = rsi.dropna()
    assert (valid_rsi >= 0).all() and (valid_rsi <= 100).all()
    
    # For a constantly increasing price, RSI should be 100
    assert valid_rsi.iloc[-1] > 90  # Should be very high


def test_calculate_macd(sample_price_data):
    """Test MACD calculation."""
    series = sample_price_data["close"]
    from backend.indicators.momentum import calculate_macd
    
    macd_df = calculate_macd(series)
    
    # Check columns
    assert "macd" in macd_df.columns
    assert "macd_signal" in macd_df.columns
    assert "macd_histogram" in macd_df.columns
    
    # Check length
    assert len(macd_df) == len(series)
    
    # Check that we have values eventually
    assert not pd.isna(macd_df["macd"].iloc[-1])
    
    # Histogram = MACD - Signal
    # Check the relationship for the last valid row
    last_row = macd_df.iloc[-1]
    # Use approx equality for float arithmetic
    assert abs(last_row["macd_histogram"] - (last_row["macd"] - last_row["macd_signal"])) < 1e-6


def test_calculate_all_momentum_indicators(sample_price_data):
    """Test wrapper function for all momentum indicators."""
    from backend.indicators.momentum import calculate_all_momentum_indicators
    
    df = calculate_all_momentum_indicators(sample_price_data)
    
    expected_columns = ["rsi_14", "macd", "macd_signal", "macd_histogram"]
    
    for col in expected_columns:
        assert col in df.columns
        assert not pd.isna(df[col].iloc[-1])


def test_calculate_52_week_high_low(sample_price_data):
    """Test 52-week High/Low calculation."""
    # Add high/low columns to sample data
    df = sample_price_data.copy()
    df["high"] = df["close"] + 1
    df["low"] = df["close"] - 1
    
    from backend.indicators.price_action import calculate_52_week_high_low
    
    df = calculate_52_week_high_low(df)
    
    assert "week_52_high" in df.columns
    assert "week_52_low" in df.columns
    
    # With constantly increasing price:
    # 52-week high should be the current high (since it's the highest so far)
    # 52-week low should be the low 252 days ago (or start of data if < 252)
    
    # At index 252 (253rd day), window covers 0..252.
    # High should be high at 252.
    # Low should be low at 0.
    
    idx = 252
    if len(df) > idx:
        assert df["week_52_high"].iloc[idx] == df["high"].iloc[idx]
        # Low should be close to low at index 0 (approx)
        # Actually, rolling min of last 252 days.
        # Prices: 100, 101, ..., 352.
        # Window at 252: indices 1 to 252 (size 252).
        # Min is at index 1 (price 101).
        # Wait, rolling includes current.
        # Window at 252: indices 1 to 252 (if window=252).
        # Min is at index 1.
        assert df["week_52_low"].iloc[idx] == df["low"].iloc[idx - 251]


def test_calculate_average_volume(sample_price_data):
    """Test Average Volume calculation."""
    # Add volume column
    df = sample_price_data.copy()
    df["volume"] = 1000
    
    from backend.indicators.volume import calculate_average_volume, calculate_all_volume_indicators
    
    avg_vol = calculate_average_volume(df["volume"], period=50)
    
    # Should be 1000 everywhere (after warmup)
    assert avg_vol.iloc[-1] == 1000
    
    # Test wrapper
    df = calculate_all_volume_indicators(df)
    assert "volume_avg_50" in df.columns
    assert df["volume_avg_50"].iloc[-1] == 1000


def test_calculate_mansfield_rs(sample_price_data):
    """Test Mansfield Relative Strength calculation."""
    # Create symbol data (outperforming)
    symbol_df = sample_price_data.copy()
    # Symbol doubles in price
    symbol_df["close"] = [100 * (1 + 0.01 * i) for i in range(300)]
    
    # Create benchmark data (underperforming)
    benchmark_df = sample_price_data.copy()
    # Benchmark stays flat
    benchmark_df["close"] = [100 for _ in range(300)]
    
    from backend.indicators.relative_strength import calculate_mansfield_rs
    
    rs = calculate_mansfield_rs(symbol_df, benchmark_df)
    
    # Check length
    assert len(rs) == len(symbol_df)
    
    # First 251 values should be NaN (window=252)
    # Wait, window=252 means we need 252 points.
    # Indices 0..251 is 252 points.
    # So index 251 should have a value.
    # Index 250 should be NaN.
    # Let's check the last value.
    
    # RP = Symbol / Benchmark
    # Symbol[299] = 100 * (1 + 2.99) = 399. Benchmark[299] = 100. RP = 3.99.
    # SMA_RP is average of RP over last 252 days.
    # RP is increasing linearly from 1.0 to 3.99.
    # SMA will be roughly average of last 252 values.
    # Since RP > SMA_RP (trend is up), Mansfield RS should be positive.
    
    valid_rs = rs.dropna()
    assert len(valid_rs) > 0
    assert valid_rs.iloc[-1] > 0
    
    # Test with underperforming symbol
    symbol_down = sample_price_data.copy()
    symbol_down["close"] = [100 * (1 - 0.001 * i) for i in range(300)]
    
    rs_down = calculate_mansfield_rs(symbol_down, benchmark_df)
    valid_rs_down = rs_down.dropna()
    assert valid_rs_down.iloc[-1] < 0



