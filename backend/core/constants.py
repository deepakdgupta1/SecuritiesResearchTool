"""
Application-wide constants and configuration values.

Purpose:
    Centralized location for all magic numbers, thresholds, and configuration
    constants used throughout the application. This promotes maintainability
    and makes it easier to tune the system without hunting through code.

Design Philosophy:
    - All constants are grouped by functional area for easy navigation
    - Each constant includes a descriptive comment explaining its purpose
    - Values can be overridden via environment variables in production

Usage:
    from backend.core.constants import TREND_TEMPLATE_RS_THRESHOLD

    if mansfield_rs > TREND_TEMPLATE_RS_THRESHOLD:
        # Stock meets RS criteria
"""

# ============================================================================
# PATTERN RECOGNITION THRESHOLDS
# ============================================================================

# -----------------------------------------------------------------------------
# Minervini Trend Template Criteria
# -----------------------------------------------------------------------------

TREND_TEMPLATE_RS_THRESHOLD = 70
"""
Minimum Mansfield Relative Strength score for Trend Template qualification.

Purpose: Filter out stocks with weak relative performance vs. market.
Rationale: Minervini's research shows stocks with RS > 70 have higher
           probability of sustained upward moves.
"""

TREND_TEMPLATE_PRICE_ABOVE_52W_LOW_PCT = 1.30
"""
Price must be at least 30% above 52-week low (1.30x multiplier).

Purpose: Ensure stock has demonstrated significant recovery from lows.
Rationale: Stocks still near 52-week lows are in Stage 4 decline or early Stage 1,
           not ideal for trend-following strategies.
"""

TREND_TEMPLATE_PRICE_WITHIN_52W_HIGH_PCT = 0.75
"""
Price must be within 25% of 52-week high (0.75x multiplier).

Purpose: Identify stocks in or near Stage 2 advance (leadership phase).
Rationale: Stocks far from highs may have lost momentum or be consolidating.
"""

TREND_TEMPLATE_MA_200_TREND_DAYS = 30
"""
Number of days to lookback for 200-day MA uptrend validation.

Purpose: Confirm long-term moving average is sloping upward, not flat or down.
Rationale: Upward-sloping 200-day MA indicates healthy long-term trend.
"""

# -----------------------------------------------------------------------------
# VCP (Volatility Contraction Pattern) Detection
# -----------------------------------------------------------------------------

VCP_MIN_CONTRACTIONS = 2
"""
Minimum number of pullback contractions required for valid VCP pattern.

Purpose: Ensure pattern has sufficient structure to be meaningful.
Rationale: Fewer than 2 contractions doesn't demonstrate the "tightening"
           characteristic of VCP.
"""

VCP_MAX_CONTRACTIONS = 4
"""
Maximum number of pullback contractions for valid VCP pattern.

Purpose: Prevent overly complex or extended patterns.
Rationale: Too many contractions may indicate indecision or weakening pattern.
"""

VCP_TOLERANCE_PCT = 0.20
"""
Tolerance (20%) for VCP pattern matching flexibility.

Purpose: Allow for real-world price action imperfections.
Rationale: Strict rules would miss many valid patterns due to minor variations.
Example: If previous pullback was 5%, next pullback up to 6% (5% * 1.20) is acceptable.
"""

# -----------------------------------------------------------------------------
# Cup and Handle Pattern
# -----------------------------------------------------------------------------

CUP_MIN_WEEKS = 7
"""
Minimum duration in weeks for cup formation.

Purpose: Distinguish between valid cups and short-term consolidations.
Rationale: Shorter consolidations lack the base-building characteristic.
"""

CUP_MAX_WEEKS = 65
"""
Maximum duration in weeks for cup formation.

Purpose: Prevent excessively long consolidations (may indicate weakness).
Rationale: Patterns lasting over a year often lose their predictive power.
"""

HANDLE_MAX_DEPTH_PCT = 0.12
"""
Maximum depth of handle as percentage of cup depth (12%).

Purpose: Ensure handle is shallow consolidation, not a deep pullback.
Rationale: Deep handles may indicate distribution rather than healthy pause.
"""

# ============================================================================
# RISK MANAGEMENT PARAMETERS
# ============================================================================

INITIAL_CAPITAL = 100000
"""
Initial portfolio capital for backtesting ($100,000).

Purpose: Standard starting capital for backtest simulations.
Rationale: Provides meaningful dollar amounts while being achievable for
           individual investors.
"""

INITIAL_STOP_LOSS_PCT = 0.10
"""
Initial fixed stop-loss: 10% below entry price.

Purpose: Limit maximum loss on any single trade.
Rationale: Minervini's 7-8% rule, rounded to 10% for conservative approach.
"""

TRAILING_STOP_TRIGGER_PCT = 0.15
"""
Switch to trailing stop when position is up 15% from entry.

Purpose: Lock in profits while allowing winners to run.
Rationale: Once position is profitable, use trailing stop to protect gains
           while giving room for continued upside.
"""

TRAILING_STOP_ATR_MULTIPLIER = 2.0
"""
Trailing stop distance: 2x Average True Range (ATR) below current price.

Purpose: Set dynamic stop based on stock's volatility.
Rationale: More volatile stocks need wider stops; ATR adapts automatically.
"""

MAX_POSITION_SIZE_PCT = 0.10
"""
Maximum position size as percentage of total portfolio (10%).

Purpose: Enforce diversification and limit single-position risk.
Rationale: No single position should dominate portfolio; 10% allows for
           10 positions minimum.
"""

MAX_CONCURRENT_POSITIONS = 10
"""
Maximum number of open positions at any time.

Purpose: Balance diversification with manageability.
Rationale: Too few positions = concentrated risk; too many = diluted returns
           and difficult to monitor.
"""

PORTFOLIO_DRAWDOWN_LIMIT_PCT = 0.20
"""
Halt new entries if portfolio drawdown exceeds 20%.

Purpose: Protect capital during adverse market conditions.
Rationale: 20% drawdown suggests systematic issues (bear market, strategy
           mismatch); pause to reassess before deploying more capital.
"""

# ============================================================================
# PERFORMANCE TARGETS & THRESHOLDS
# ============================================================================

TARGET_FULL_SCAN_MINUTES = 30
"""
Target: Complete full universe scan (10,000 symbols) in under 30 minutes.

Purpose: Performance benchmark for pattern scanning efficiency.
Rationale: 30 minutes allows overnight batch processing while leaving buffer
           for other tasks. 15 minutes is ideal target.
"""

TARGET_BACKTEST_MINUTES = 30
"""
Target: Complete 20-year backtest (10,000 symbols) in under 30 minutes.

Purpose: Performance benchmark for backtesting engine efficiency.
Rationale: Enables rapid iteration on strategy parameters without long waits.
"""

DATA_INGESTION_SUCCESS_RATE_TARGET = 0.99
"""
Target: 99% success rate for daily data ingestion.

Purpose: Service Level Indicator (SLI) for data pipeline reliability.
Rationale: Occasional failures are acceptable (API outages), but consistent
           failures indicate systemic issues requiring attention.
"""

DATABASE_QUERY_P95_LATENCY_MS = 500
"""
Target: 95th percentile database query latency under 500ms.

Purpose: Ensure database performance remains acceptable under load.
Rationale: 500ms is fast enough for batch processing; queries slower than
           this should be optimized (indexing, query structure).
"""

API_RESPONSE_P95_LATENCY_MS = 2000
"""
Target: 95th percentile API response time under 2 seconds.

Purpose: Ensure web UI remains responsive for user interactions.
Rationale: 2 seconds is upper bound for acceptable UX; faster is better.
"""

# ============================================================================
# DATA PROCESSING PARAMETERS
# ============================================================================

TRADING_DAYS_PER_YEAR = 252
"""
Approximate number of trading days per year for return annualization.

Purpose: Convert daily returns to annualized returns for performance metrics.
Rationale: US markets: ~252 trading days/year (365 - weekends - holidays).
"""

RISK_FREE_RATE = 0.0
"""
Risk-free rate for Sharpe/Sortino ratio calculations (default: 0%).

Purpose: Baseline rate of return for risk-adjusted metrics.
Rationale: Use 0% for simplicity in MVP; can be updated to T-bill rate
           (typically 2-5%) for production.
"""

MANSFIELD_RS_SMOOTH_PERIOD = 52
"""
Smoothing period for Mansfield Relative Strength calculation (52 weeks).

Purpose: Reduce noise in RS calculation while maintaining responsiveness.
Rationale: 52-week (1 year) smoothing balances trend detection with lag.
"""

INDICATOR_LOOKBACK_DAYS = 300
"""
Default lookback period for indicator calculations (300 days).

Purpose: Ensure sufficient data for 200-day MA and other long-period indicators.
Rationale: 200-day MA needs 200 days; 300 provides buffer for weekends/holidays.
"""

# ============================================================================
# TECHNICAL INDICATOR PERIODS
# ============================================================================

# Moving Averages (Daily Timeframe)
MA_PERIOD_50_DAY = 50
"""50-day moving average period for daily charts."""

MA_PERIOD_150_DAY = 150
"""150-day moving average period for daily charts."""

MA_PERIOD_200_DAY = 200
"""200-day moving average period for daily charts."""

# Moving Averages (Weekly Timeframe)
MA_PERIOD_10_WEEK = 10
"""10-week moving average period for weekly charts (~ 50-day equivalent)."""

MA_PERIOD_30_WEEK = 30
"""30-week moving average period for weekly charts (~ 150-day equivalent)."""

MA_PERIOD_40_WEEK = 40
"""40-week moving average period for weekly charts (~ 200-day equivalent)."""

# RSI (Relative Strength Index)
RSI_PERIOD = 14
"""Default RSI period (14 days/periods)."""

RSI_OVERBOUGHT_THRESHOLD = 70
"""RSI above 70 considered overbought."""

RSI_OVERSOLD_THRESHOLD = 30
"""RSI below 30 considered oversold."""

# MACD (Moving Average Convergence Divergence)
MACD_FAST_PERIOD = 12
"""MACD fast EMA period (12 days)."""

MACD_SLOW_PERIOD = 26
"""MACD slow EMA period (26 days)."""

MACD_SIGNAL_PERIOD = 9
"""MACD signal line period (9 days)."""

# ATR (Average True Range)
ATR_PERIOD = 14
"""Default ATR period (14 days) for volatility measurement."""

# ============================================================================
# TESTING & COVERAGE
# ============================================================================

MIN_BRANCH_COVERAGE_PCT = 80
"""
Minimum branch coverage required for new/changed code (80%).

Purpose: Enforce testing standards via CI/CD pipeline.
Rationale: 80% is achievable while allowing for edge cases and error paths
           that are difficult to test.
"""

UNIT_TEST_MAX_DURATION_SECONDS = 10
"""
Maximum duration for entire unit test suite (10 seconds).

Purpose: Keep unit tests fast to encourage frequent running.
Rationale: Slow tests discourage TDD and reduce productivity.
"""

# ============================================================================
# DATA VALIDATION THRESHOLDS
# ============================================================================

MAX_PRICE_CHANGE_PCT_PER_DAY = 0.50
"""
Maximum acceptable single-day price change (50%) for data validation.

Purpose: Flag potential data errors (bad ticks, stock splits not adjusted).
Rationale: While extreme moves happen, 50%+ moves are rare and should be
           manually reviewed.
"""

MIN_VOLUME = 1
"""
Minimum acceptable volume (1 share).

Purpose: Flag data errors where volume is zero or negative.
Rationale: Even thinly traded stocks have some volume; zero likely indicates
           data quality issue.
"""

MAX_DAYS_MISSING_DATA = 10
"""
Maximum consecutive days of missing data before flagging symbol as stale.

Purpose: Identify delisted or suspended stocks.
Rationale: More than 10 consecutive missing days suggests stock is no longer
           actively trading.
"""

# ============================================================================
# FILE PATHS & NAMING
# ============================================================================

IDEAS_LOG_FILENAME = "ideas.csv"
"""Filename for pattern detection ideas log."""

BACKTEST_RESULTS_PREFIX = "backtest_results"
"""Prefix for backtest result CSV files (datetime appended)."""

APPLICATION_LOG_FILENAME = "application.log"
"""Filename for application logs."""

# ============================================================================
# API RATE LIMITING
# ============================================================================

API_RATE_LIMIT_BACKTEST_PER_MINUTE = 10
"""Maximum backtest API calls per minute per IP."""

API_RATE_LIMIT_SCAN_PER_MINUTE = 20
"""Maximum pattern scan API calls per minute per IP."""

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

DB_CONNECTION_POOL_SIZE = 10
"""Database connection pool size."""

DB_CONNECTION_TIMEOUT_SECONDS = 30
"""Database connection timeout (30 seconds)."""

DB_QUERY_TIMEOUT_SECONDS = 60
"""Maximum query execution time before timeout (60 seconds)."""

# ============================================================================
# RETRY & RESILIENCE
# ============================================================================

API_RETRY_MAX_ATTEMPTS = 3
"""Maximum retry attempts for failed API calls."""

API_RETRY_BACKOFF_SECONDS = 1.0
"""Initial backoff duration for exponential retry (doubles each attempt)."""

API_TIMEOUT_SECONDS = 30
"""HTTP request timeout (30 seconds)."""

DATA_INGESTION_RETRY_DELAY_SECONDS = 300
"""Wait 5 minutes before retrying failed data ingestion."""

# ============================================================================
# MARKET & EXCHANGE CONSTANTS
# ============================================================================

MARKET_US = "US"
"""United States Market Code."""

MARKET_IN = "IN"
"""Indian Market Code."""

EXCHANGE_NSE = "NSE"
"""National Stock Exchange of India."""

EXCHANGE_BSE = "BSE"
"""Bombay Stock Exchange."""

EXCHANGE_NYSE = "NYSE"
"""New York Stock Exchange."""

EXCHANGE_NASDAQ = "NASDAQ"
"""Nasdaq Stock Market."""

EXCHANGE_UNKNOWN = "UNKNOWN"
"""Unknown Exchange."""

# ============================================================================
# DATA PROVIDER CONFIGURATION
# ============================================================================

YAHOO_RATE_LIMIT = 10.0
"""Yahoo Finance API rate limit (requests per second).

Purpose: Prevent rate limiting from Yahoo Finance.
Rationale: Yahoo Finance is lenient, but 10 req/s is conservative and safe.
"""

ZERODHA_RATE_LIMIT = 3.0
"""Zerodha Kite Connect API rate limit (requests per second).

Purpose: Comply with Zerodha API rate limits.
Rationale: Kite Connect has documented limit of 3 req/s per API key.
"""

INTERVAL_DAILY = "1d"
"""Daily data interval for Yahoo Finance."""

INTERVAL_5MIN = "5m"
"""5-minute data interval."""

BATCH_SIZE_INSERT = 100
"""Batch size for database insertions."""

URL_SP500_WIKIPEDIA = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
"""URL for fetching S&P 500 constituents."""

# Column Mapping
COL_OPEN = "open"
COL_HIGH = "high"
COL_LOW = "low"
COL_CLOSE = "close"
COL_VOLUME = "volume"
COL_ADJ_CLOSE = "adjusted_close"
COL_DATE = "date"
