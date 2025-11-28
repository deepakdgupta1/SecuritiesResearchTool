# Algorithms & Logic
### Key Algorithms

#### 1. Mansfield Relative Strength
```python
from backend.core.constants import MANSFIELD_RS_SMOOTH_PERIOD
import pandas as pd
import numpy as np

def calculate_mansfield_rs(
    stock_prices: pd.Series,
    index_prices: pd.Series,
    smooth_period: int = MANSFIELD_RS_SMOOTH_PERIOD
) -> pd.Series:
    """
    Calculate Mansfield Relative Strength indicator.
    
    Purpose:
        Measure stock's performance relative to market index.
        Higher RS indicates outperformance (leadership stocks).
        Minervini looks for RS > 70 for Trend Template qualification.
    
    Algorithm:
        1. Calculate ratio: stock_price / index_price
        2. Smooth using rolling mean (default 52 weeks)
        3. Normalize to 0-100 scale (optional)
    
    Args:
        stock_prices: Series of stock close prices (DatetimeIndex)
        index_prices: Series of market index prices (same dates)
        smooth_period: Smoothing window in periods (default from constants.py)
    
    Returns:
        Series of RS values (0-100 scale, higher = stronger relative performance)
    
    Example:
        >>> stock = df['close']  # RELIANCE prices
        >>> index = nifty_df['close']  # NIFTY 50 prices  
        >>> rs = calculate_mansfield_rs(stock, index)
        >>> rs.tail()
        2025-01-10    75.3
        2025-01-11    76.1
        ...
    """
    # Calculate price ratio (stock performance relative to market)
    ratio = stock_prices / index_prices
    
    # Smooth to reduce noise (default: 52-week moving average)
    smoothed_ratio = ratio.rolling(window=smooth_period).mean()
    
    # Normalize to 0-100 scale for easier interpretation
    # This makes RS comparable across different stocks
    rs_normalized = (
        (smoothed_ratio - smoothed_ratio.min()) / 
        (smoothed_ratio.max() - smoothed_ratio.min())
    ) * 100
    
    return rs_normalized
```

#### 2. VCP Detection
```python
from backend.core.constants import (
    VCP_MIN_CONTRACTIONS,
    VCP_MAX_CONTRACTIONS,
    VCP_TOLERANCE_PCT
)
from typing import Tuple, Dict, List

def detect_vcp(
    df: pd.DataFrame,
    min_contractions: int = VCP_MIN_CONTRACTIONS,
    max_contractions: int = VCP_MAX_CONTRACTIONS,
    tolerance: float = VCP_TOLERANCE_PCT
) -> Tuple[bool, Dict[str, any]]:
    """
    Detect Volatility Contraction Pattern (VCP) in price data.
    
    Purpose:
        Identify VCP patterns where pullbacks show progressively tighter
        consolidations, indicating reduced supply before potential breakout.
        VCP is a Mark Minervini signature pattern for Stage 2 entries.
    
   Algorithm:
        1. Find pivot highs and lows in price action
        2. Identify pullback sequences (high-to-low moves)
        3. Check if each pullback is shallower than previous
        4. Verify volume contracts during pullbacks
        5. Count number of contractions (must be 2-4)
    
    Args:
        df: DataFrame with OHLCV data, DatetimeIndex
        min_contractions: Minimum pullbacks required (from constants.py)
        max_contractions: Maximum pullbacks allowed (from constants.py)
        tolerance: Allowable deviation % (from constants.py, default 20%)
    
    Returns:
        Tuple of (pattern_found: bool, details: dict)
        details includes: pullback_depths, contraction_count, confidence_score
    
    Example:
        >>> pattern_found, details = detect_vcp(reliance_df)
        >>> if pattern_found:
        ...     print(f"VCP detected with {details['contraction_count']} pullbacks")
    """
    # Step 1: Find pivot points (local highs and lows)
    pivots = find_pivot_points(df)
    
    # Step 2: Identify pullback sequences
    pullbacks = []
    for i in range(1, len(pivots)):
        if pivots[i].type == 'low' and pivots[i-1].type == 'high':
            # Calculate pullback depth as % from previous high
            depth = (pivots[i-1].price - pivots[i].price) / pivots[i-1].price
            pullbacks.append({
                'depth_pct': depth * 100,
                'high_date': pivots[i-1].date,
                'low_date': pivots[i].date,
                'volume': df.loc[pivots[i].date:pivots[i].date, 'volume'].mean()
            })
    
    # Step 3: Check for contraction (each pullback shallower than previous)
    contractions = 0
    for i in range(1, len(pullbacks)):
        prev_depth = pullbacks[i-1]['depth_pct']
        curr_depth = pullbacks[i]['depth_pct']
        
        # Allow tolerance (e.g., if prev was 5%, current can be up to 6% with 20% tolerance)
        if curr_depth <= prev_depth * (1 + tolerance):
            contractions += 1
        else:
            # Pattern broken - pullback too deep
            break
    
    # Step 4: Verify contraction count is within valid range
    pattern_found = (min_contractions <= contractions <= max_contractions)
    
    # Step 5: Check volume contraction (optional but strengthens pattern)
    volume_contracts = all(
        pullbacks[i]['volume'] < pullbacks[i-1]['volume']
        for i in range(1, len(pullbacks))
    )
    
    # Calculate confidence score (0-100)
    confidence = 0
    if pattern_found:
        # Base score for valid contraction count
        confidence += 60
        # Bonus for ideal 3-4 contractions
        if contractions >= 3:
            confidence += 20
        # Bonus for volume contraction
        if volume_contracts:
            confidence += 20
    
    return pattern_found, {
        'contraction_count': contractions,
        'pullbacks': pullbacks,
        'volume_contracts': volume_contracts,
        'confidence_score': confidence
    }
```

#### 3. Trend Template Validation
```python
from backend.core.constants import (
    TREND_TEMPLATE_RS_THRESHOLD,
    TREND_TEMPLATE_PRICE_ABOVE_52W_LOW_PCT,
    TREND_TEMPLATE_PRICE_WITHIN_52W_HIGH_PCT,
    TREND_TEMPLATE_MA_200_TREND_DAYS
)

def check_trend_template(
    current_price: float,
    ma_50: float,
    ma_150: float,
    ma_200: float,
    ma_200_trend: pd.Series,
    week_52_low: float,
    week_52_high: float,
    mansfield_rs: float
) -> Tuple[bool, Dict[str, bool]]:
    """
    Check if stock meets all Minervini Trend Template criteria.
    
    Purpose:
        Identify stocks in Stage 2 advance (uptrend with momentum).
        Trend Template is Minervini's primary filter for finding leaders.
        All 8 criteria must pass for qualification.
    
    Criteria (all must be TRUE):
        1. Current price > 150-day MA
        2. Current price > 200-day MA
        3. 150-day MA > 200-day MA
        4. 200-day MA trending UP for ≥1 month
        5. 50-day MA > 150-day MA
        6. 50-day MA > 200-day MA
        7. Price > 30% above 52-week low
        8. Price within 25% of 52-week high
        9. Mansfield RS > 70
    
    Args:
        current_price: Latest close price
        ma_50, ma_150, ma_200: Current moving average values
        ma_200_trend: Series of 200-MA values for trend check
        week_52_low, week_52_high: 52-week price extremes
        mansfield_rs: Current Mansfield RS value
    
    Returns:
        Tuple of (passes_all: bool, individual_checks: dict)
    
    Example:
        >>> passes, checks = check_trend_template(...)
        >>> if passes:
        ...     print("Stage 2 stock - consider for entry")
        >>> else:
        ...     print(f"Failed: {[k for k, v in checks.items() if not v]}")
    """
    checks = {}
    
    # Criterion 1: Price above 150-day MA (confirms uptrend)
    checks['price_above_ma150'] = current_price > ma_150
    
    # Criterion 2: Price above 200-day MA (confirms long-term uptrend)  
    checks['price_above_ma200'] = current_price > ma_200
    
    # Criterion 3: 150-MA above 200-MA (MAs in proper order)
    checks['ma150_above_ma200'] = ma_150 > ma_200
    
    # Criterion 4: 200-MA trending upward (not flat or declining)
    # Check if MA today > MA 30 days ago
    days_ago = TREND_TEMPLATE_MA_200_TREND_DAYS  # From constants.py
    checks['ma200_trending_up'] = (
        ma_200_trend.iloc[-1] > ma_200_trend.iloc[-days_ago]
    )
    
    # Criterion 5: 50-MA above 150-MA (short-term strength)
    checks['ma50_above_ma150'] == ma_50 > ma_150
    
    # Criterion 6: 50-MA above 200-MA
    checks['ma50_above_ma200'] = ma_50 > ma_200
    
    # Criterion 7: Price > 30% above 52-week low
    # Use constant from constants.py
    checks['price_above_52w_low'] = (
        current_price > (week_52_low * TREND_TEMPLATE_PRICE_ABOVE_52W_LOW_PCT)
    )
    
    # Criterion 8: Price within 25% of 52-week high  
    # Use constant from constants.py
    checks['price_near_52w_high'] = (
        current_price >= (week_52_high * TREND_TEMPLATE_PRICE_WITHIN_52W_HIGH_PCT)
    )
    
    # Criterion 9: RS rating > 70 (relative strength vs market)
    # Use constant from constants.py
    checks['rs_rating'] = mansfield_rs > TREND_TEMPLATE_RS_THRESHOLD
    
    # All criteria must pass
    passes_template = all(checks.values())
    
    return passes_template, checks
```

#### 4. Performance Metrics
```python
from backend.core.constants import TRADING_DAYS_PER_YEAR, RISK_FREE_RATE
import numpy as np

def calculate_sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = RISK_FREE_RATE,
    periods_per_year: int = TRADING_DAYS_PER_YEAR
) -> float:
    """
    Calculate Sharpe Ratio for risk-adjusted returns.
    
    Purpose:
        Measure excess return per unit of risk.
        Higher Sharpe = better risk-adjusted performance.
        Industry standard: >1.0 good, >2.0 excellent, >3.0 exceptional.
    
    Formula:
        Sharpe = (Mean Return - Risk Free Rate) / Std Dev of Returns
        Annualized by multiplying by sqrt(periods_per_year)
    
    Args:
        returns: Series of period returns (daily, weekly, etc.)
        risk_free_rate: Annual risk-free rate (default from constants.py)
        periods_per_year: Number of periods in a year (default 252 trading days)
    
    Returns:
        Annualized Sharpe Ratio
    
    Example:
        >>> daily_returns = portfolio_value.pct_change()
        >>> sharpe = calculate_sharpe_ratio(daily_returns)
        >>> print(f"Sharpe Ratio: {sharpe:.2f}")
        Sharpe Ratio: 1.85
    """
    # Calculate excess returns (returns above risk-free rate)
    # Convert annual risk-free rate to period rate
    period_rf_rate = risk_free_rate / periods_per_year
    excess_returns = returns - period_rf_rate
    
    # Sharpe = mean excess return / standard deviation
    # Annualize by multiplying by sqrt(periods per year)
    sharpe = (
        excess_returns.mean() / excess_returns.std()
    ) * np.sqrt(periods_per_year)
    
    return sharpe

def calculate_max_drawdown(equity_curve: pd.Series) -> float:
    """
    Calculate maximum peak-to-trough decline in portfolio value.
    
    Purpose:
        Measure worst loss from any peak.
        Critical risk metric - shows how much capital was at risk.
        Helps size positions and set expectations.
    
    Algorithm:
        1. Track running maximum (peak) portfolio value
        2. Calculate drawdown at each point: (current - peak) / peak
        3. Find the minimum (most negative) drawdown
    
    Args:
        equity_curve: Series of portfolio values over time
    
    Returns:
        Maximum drawdown as positive percentage (e.g., 0.25 = 25% drawdown)
    
    Example:
        >>> portfolio_values = pd.Series([100, 110, 105, 90, 95, 100])
        >>> max_dd = calculate_max_drawdown(portfolio_values)
        >>> print(f"Max Drawdown: {max_dd*100:.1f}%")
        Max Drawdown: 18.2%  # From 110 to 90
    """
    # Calculate running maximum (peak portfolio value so far)
    running_max = equity_curve.expanding().max()
    
    # Calculate drawdown at each point
    # Negative values indicate we're below the peak
    drawdown = (equity_curve - running_max) / running_max
    
    # Find the maximum (most negative) drawdown
    # Use abs() to return as positive number
    max_drawdown = abs(drawdown.min())
    
    return max_drawdown

def calculate_profit_factor(trades: pd.DataFrame) -> float:
    """
    Calculate Profit Factor (gross profit / gross loss ratio).
    
    Purpose:
        Measure overall profitability of trading system.
        PF > 1.0 = profitable, PF > 2.0 = strong, PF > 3.0 = excellent.
        Advantage: Easy to understand, no assumptions needed.
    
    Formula:
        Profit Factor = Sum(Winning Trades) / Abs(Sum(Losing Trades))
    
    Args:
        trades: DataFrame with 'pnl' column (profit/loss per trade)
    
    Returns:
        Profit Factor as ratio (e.g., 2.5 means $2.50 profit per $1.00 loss)
        Returns infinity if no losing trades
   
   Example:
        >>> trades_df = pd.DataFrame({'pnl': [100, -50, 200, -75, 150]})
        >>> pf = calculate_profit_factor(trades_df)
        >>> print(f"Profit Factor: {pf:.2f}")
        Profit Factor: 3.60  # (100+200+150) / (50+75)
    """
    # Separate winning and losing trades
    winning_trades = trades[trades['pnl'] > 0]
    losing_trades = trades[trades['pnl'] < 0]
    
    # Calculate gross profit and loss
    gross_profit = winning_trades['pnl'].sum()
    gross_loss = abs(losing_trades['pnl'].sum())  # Make positive for ratio
    
    # Handle edge case: no losing trades
    if gross_loss == 0:
        return float('inf') if gross_profit > 0 else 0.0
    
    # Calculate ratio
    profit_factor = gross_profit / gross_loss
    
    return profit_factor
```

---
