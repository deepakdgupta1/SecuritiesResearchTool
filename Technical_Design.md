# High Level Technical Design Document
## Securities Research Tool - Pattern Recognition & Backtesting Platform

**Version:** 1.0  
**Date:** November 26, 2025  
**Status:** Draft for Review

---

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Component Design](#component-design)
5. [Data Model](#data-model)
6. [Processing Pipeline](#processing-pipeline)
7. [Algorithms & Logic](#algorithms--logic)
8. [API & Integration Design](#api--integration-design)
9. [Deployment Architecture](#deployment-architecture)
10. [Development Phases](#development-phases)
11. [Technical Risks & Mitigations](#technical-risks--mitigations)

---

## System Overview

### Architecture Principles
- **Modularity:** Separate concerns into distinct, testable components
- **Extensibility:** Design for future expansion (real-time, more patterns, more markets)
- **Performance:** Optimize for batch processing of large datasets
- **Maintainability:** Clean code, clear separation of data/business logic/presentation

### High-Level Architecture Style
**Layered Architecture** with the following layers:
1. **Data Layer:** Data acquisition, storage, and access
2. **Business Logic Layer:** Pattern recognition, backtesting, calculations
3. **Presentation Layer:** Web UI and reporting

---

## Architecture

### System Architecture Diagram

```mermaid
graph TB
    subgraph "External Data Sources"
        DS1[Zerodha API<br/>Indian Market]
        DS2[Yahoo Finance<br/>US Market]
    end
    
    subgraph "Data Layer"
        DI[Data Ingestion<br/>Service]
        DB[(Time-Series<br/>Database)]
        DV[Data Validation<br/>& Cleansing]
    end
    
    subgraph "Business Logic Layer"
        IM[Indicator Module<br/>MA, MACD, RSI, RS]
        PR[Pattern Recognition<br/>Engine]
        SA[Stage Analysis<br/>Module]
        BT[Backtesting<br/>Engine]
        RM[Risk Management<br/>Module]
        PM[Performance Metrics<br/>Calculator]
    end
    
    subgraph "Presentation Layer"
        WEB[Web UI<br/>Flask/FastAPI]
        LOG[Ideas Log<br/>Writer]
        REP[CSV Report<br/>Generator]
    end
    
    subgraph "User"
        USER[Browser]
    end
    
    DS1 --> DI
    DS2 --> DI
    DI --> DV
    DV --> DB
    
    DB --> IM
    DB --> PR
    DB --> SA
    DB --> BT
    
    IM --> PR
    IM --> SA
    IM --> BT
    
    PR --> BT
    SA --> PR
    BT --> RM
    BT --> PM
    
    WEB --> PR
    WEB --> BT
    PR --> LOG
    BT --> REP
    PM --> REP
    
    USER --> WEB
    USER -.reads.-> LOG
    USER -.reads.-> REP
```

### Component Interaction Flow

**Data Ingestion Flow:**
```
Zerodha/Yahoo Finance → Data Ingestion → Validation → Database → Ready for Analysis
```

**Pattern Scanning Flow:**
```
User Request → Web UI → Pattern Recognition Engine → Indicator Module → Database
                                ↓
                         Stage Analysis Module
                                ↓
                         Pattern Matches → Ideas Log
```

**Backtesting Flow:**
```
User Config → Backtesting Engine → Load Historical Data → Simulate Trades
                    ↓                                            ↓
            Risk Management Module                    Track Positions
                    ↓                                            ↓
            Performance Metrics ← Calculate Returns/Risk ← Final P&L
                    ↓
            CSV Report Generator
```

---

## Technology Stack

### Recommended Stack

#### Backend
- **Language:** Python 3.11+
  - *Rationale:* Excellent data science ecosystem (pandas, numpy), API libraries (requests), web frameworks
  
- **Web Framework:** FastAPI
  - *Rationale:* Modern, fast, async support, automatic API documentation, type hints
  - *Alternative:* Flask (simpler, more traditional)

- **Data Processing:** 
  - pandas (DataFrames for OHLCV data)
  - numpy (numerical calculations)
  - TA-Lib or pandas-ta (technical indicators)

- **Data Acquisition:**
  - kiteconnect (Zerodha API client)
  - yfinance (Yahoo Finance wrapper)

#### Database
- **Primary Choice:** PostgreSQL with TimescaleDB extension
  - *Rationale:* 
    - TimescaleDB optimized for time-series data (OHLCV)
    - Excellent query performance for large datasets
    - Supports complex SQL queries needed for pattern matching
    - Mature, reliable, well-documented
    - Scales well to millions of rows
  
- **Alternative:** ClickHouse
  - *Rationale:* Columnar database, extremely fast for analytical queries
  - *Trade-off:* Less mature ecosystem, steeper learning curve

#### Frontend
- **HTML/CSS/JavaScript:** Vanilla or lightweight framework
  - Bootstrap or Tailwind CSS for styling
  - Vanilla JS or Alpine.js for interactivity
  - *Rationale:* Simple UI requirements don't warrant heavy framework (React/Vue)

#### Deployment
- **Web Server:** Uvicorn (ASGI server for FastAPI)
- **Process Management:** systemd or Docker Compose
- **Environment Management:** venv or conda

### Technology Justification Matrix

| Component | Technology | Justification |
|-----------|------------|---------------|
| Backend Language | Python 3.11+ | Rich data science libraries, rapid development, readability |
| Web Framework | FastAPI | Modern, performant, async, auto-docs, type safety |
| Database | PostgreSQL + TimescaleDB | Time-series optimization, SQL power, scalability, reliability |
| Data Processing | pandas + numpy | Industry standard for financial data analysis |
| Technical Indicators | pandas-ta / TA-Lib | Pre-built indicator libraries, battle-tested |
| Frontend | HTML/CSS/JS (Bootstrap) | Lightweight, sufficient for MVP UI needs |
| API Clients | kiteconnect, yfinance | Official/popular libraries for data sources |

---

## Component Design

### 1. Data Layer

#### 1.1 Data Ingestion Service

**Responsibilities:**
- Fetch historical and daily data from Zerodha and Yahoo Finance
- Handle API rate limits and retries
- Schedule overnight batch updates
- Validate and cleanse incoming data

**Key Classes:**
```python
class DataProvider(ABC):
    def fetch_historical(symbol, start_date, end_date) -> DataFrame
    def fetch_latest(symbol) -> DataFrame

class ZerodhaProvider(DataProvider):
    # Zerodha-specific implementation

class YahooFinanceProvider(DataProvider):
    # Yahoo Finance-specific implementation

class DataIngestionOrchestrator:
    def ingest_universe(provider, symbol_list)
    def schedule_daily_update()
```

**Data Validation Rules:**
- Check for missing dates (non-trading days acceptable)
- Validate OHLCV integrity (High ≥ Low, Close within High-Low range)
- Volume must be non-negative
- Handle stock splits and dividends (adjusted prices)

#### 1.2 Database Schema

**Tables:**

**symbols**
```sql
CREATE TABLE symbols (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(200),
    exchange VARCHAR(20), -- NSE, BSE, NYSE, NASDAQ
    market VARCHAR(10), -- IN, US
    sector VARCHAR(100),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**price_data** (TimescaleDB hypertable)
```sql
CREATE TABLE price_data (
    symbol_id INTEGER REFERENCES symbols(id),
    date DATE NOT NULL,
    open NUMERIC(12,2),
    high NUMERIC(12,2),
    low NUMERIC(12,2),
    close NUMERIC(12,2),
    volume BIGINT,
    adjusted_close NUMERIC(12,2),
    PRIMARY KEY (symbol_id, date)
);

-- Convert to hypertable for time-series optimization
SELECT create_hypertable('price_data', 'date');
```

**derived_metrics** (Cached calculations)
```sql
CREATE TABLE derived_metrics (
    symbol_id INTEGER REFERENCES symbols(id),
    date DATE NOT NULL,
    ema_50 NUMERIC(12,4),
    ema_150 NUMERIC(12,4),
    ema_200 NUMERIC(12,4),
    sma_50 NUMERIC(12,4),
    sma_150 NUMERIC(12,4),
    sma_200 NUMERIC(12,4),
    rsi_14 NUMERIC(6,2),
    macd NUMERIC(12,4),
    macd_signal NUMERIC(12,4),
    macd_histogram NUMERIC(12,4),
    mansfield_rs NUMERIC(12,4),
    week_52_high NUMERIC(12,2),
    week_52_low NUMERIC(12,2),
    volume_avg_50 BIGINT,
    PRIMARY KEY (symbol_id, date)
);
```

**pattern_detections**
```sql
CREATE TABLE pattern_detections (
    id SERIAL PRIMARY KEY,
    symbol_id INTEGER REFERENCES symbols(id),
    detection_date DATE NOT NULL,
    pattern_type VARCHAR(50), -- VCP, CUP_HANDLE, TREND_TEMPLATE, etc.
    confidence_score NUMERIC(5,2),
    weinstein_stage INTEGER, -- 1, 2, 3, 4
    meets_trend_template BOOLEAN,
    metadata JSONB, -- Pattern-specific details
    created_at TIMESTAMP DEFAULT NOW()
);
```

**trade_recommendations**
```sql
CREATE TABLE trade_recommendations (
    id SERIAL PRIMARY KEY,
    pattern_detection_id INTEGER REFERENCES pattern_detections(id),
    symbol_id INTEGER REFERENCES symbols(id),
    recommendation_date DATE NOT NULL,
    trade_type VARCHAR(10), -- BUY, SELL
    entry_price NUMERIC(12,2),
    stop_loss NUMERIC(12,2),
    take_profit NUMERIC(12,2),
    position_size_pct NUMERIC(5,2),
    rationale TEXT,
    status VARCHAR(20), -- OPEN, CLOSED, CANCELLED
    created_at TIMESTAMP DEFAULT NOW()
);
```

**backtest_results**
```sql
CREATE TABLE backtest_results (
    id SERIAL PRIMARY KEY,
    backtest_name VARCHAR(200),
    start_date DATE,
    end_date DATE,
    strategy_config JSONB,
    total_return NUMERIC(10,4),
    annualized_return NUMERIC(10,4),
    cagr NUMERIC(10,4),
    sharpe_ratio NUMERIC(10,4),
    sortino_ratio NUMERIC(10,4),
    max_drawdown NUMERIC(10,4),
    win_rate NUMERIC(5,2),
    profit_factor NUMERIC(10,4),
    total_trades INTEGER,
    winning_trades INTEGER,
    losing_trades INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**backtest_trades**
```sql
CREATE TABLE backtest_trades (
    id SERIAL PRIMARY KEY,
    backtest_id INTEGER REFERENCES backtest_results(id),
    symbol_id INTEGER REFERENCES symbols(id),
    entry_date DATE,
    entry_price NUMERIC(12,2),
    exit_date DATE,
    exit_price NUMERIC(12,2),
    position_type VARCHAR(10), -- LONG, SHORT
    quantity INTEGER,
    profit_loss NUMERIC(12,2),
    profit_loss_pct NUMERIC(10,4),
    exit_reason VARCHAR(50) -- STOP_LOSS, TAKE_PROFIT, TRAILING_STOP, SIGNAL
);
```

### 2. Business Logic Layer

#### 2.1 Indicator Module

**Responsibilities:**
- Calculate technical indicators from price data
- Support both real-time and batch calculation
- Cache results in derived_metrics table

**Key Classes:**
```python
class IndicatorCalculator:
    def calculate_moving_averages(df: DataFrame) -> DataFrame
    def calculate_rsi(df: DataFrame, period=14) -> Series
    def calculate_macd(df: DataFrame) -> DataFrame
    def calculate_mansfield_rs(stock_df: DataFrame, index_df: DataFrame) -> Series
    def calculate_52week_high_low(df: DataFrame) -> tuple
    def calculate_volume_average(df: DataFrame, period=50) -> Series
```

**Indicator Calculation Pipeline:**
```
Raw OHLCV Data → Calculate Indicators → Validate Results → Store in derived_metrics
```

#### 2.2 Pattern Recognition Engine

**Responsibilities:**
- Identify chart patterns from price data and indicators
- Apply Mark Minervini's Trend Template criteria
- Detect VCP, Cup & Handle, Double Bottom, High-Tight Flag
- Assign confidence scores

**Key Classes:**
```python
class PatternRecognizer(ABC):
    def detect(df: DataFrame, metrics: DataFrame) -> List[PatternMatch]
    def calculate_confidence(match: PatternMatch) -> float

class TrendTemplateRecognizer(PatternRecognizer):
    def check_criteria(df, metrics) -> bool
    # Implements 7 trend template criteria

class VCPRecognizer(PatternRecognizer):
    def find_contractions(df) -> List[Contraction]
    def validate_vcp_pattern(contractions) -> PatternMatch

class CupAndHandleRecognizer(PatternRecognizer):
    def detect_cup(df) -> CupPattern
    def detect_handle(df, cup) -> HandlePattern

class DoubleBottomRecognizer(PatternRecognizer):
    def find_bottoms(df) -> List[Bottom]
    def validate_double_bottom(bottoms) -> PatternMatch

class HighTightFlagRecognizer(PatternRecognizer):
    def detect_power_play(df) -> PatternMatch

class PatternScanOrchestrator:
    def scan_all_symbols(date: Date) -> List[PatternDetection]
    def scan_symbol(symbol, date) -> List[PatternDetection]
```

**Trend Template Logic:**
```python
def check_trend_template(symbol_id, date):
    # Load price data and metrics
    # Check each criterion:
    # 1. price > ma_150 and price > ma_200
    # 2. ma_150 > ma_200
    # 3. ma_200 trending up (compare with 30 days ago)
    # 4. ma_50 > ma_150 and ma_50 > ma_200
    # 5. price > 1.3 * week_52_low
    # 6. price >= 0.75 * week_52_high
    # 7. mansfield_rs > 70
    # Return boolean and details
```

**VCP Detection Algorithm:**
```python
def detect_vcp(df, tolerance=0.20):
    # 1. Identify pullbacks (peaks to troughs)
    # 2. Count contractions (2-4 required)
    # 3. Verify each pullback is shallower than previous
    # 4. Check volume contraction during pullbacks
    # 5. Apply tolerance (20%) for flexibility
    # 6. Return VCP match with confidence score
```

#### 2.3 Stage Analysis Module

**Responsibilities:**
- Classify stocks into Weinstein's 4 stages
- Use moving averages and price action

**Stage Classification Logic:**
```python
def classify_weinstein_stage(df, metrics):
    # Stage 1 (Base): Sideways, MA flattening
    # Stage 2 (Advance): Price > rising MA, higher highs
    # Stage 3 (Top): Sideways, MA flattening after rise
    # Stage 4 (Decline): Price < falling MA, lower lows
    # Return stage number (1-4)
```

#### 2.4 Backtesting Engine

**Responsibilities:**
- Simulate historical trades based on strategy rules
- Track positions, calculate P&L
- Apply risk management rules
- Generate trade log and performance metrics

**Key Classes:**
```python
class BacktestEngine:
    def run_backtest(strategy: Strategy, start_date, end_date) -> BacktestResult
    def simulate_day(date: Date) -> List[Trade]
    def execute_trade(trade: Trade)
    def update_positions(date: Date)

class Strategy:
    def generate_signals(date: Date) -> List[Signal]
    def entry_rules() -> EntryRules
    def exit_rules() -> ExitRules

class Position:
    symbol: str
    entry_date: Date
    entry_price: float
    quantity: int
    current_price: float
    stop_loss: float
    take_profit: float
    
    def update_stop_loss(new_stop)
    def check_exit_conditions(current_price) -> bool

class TradeLogger:
    def log_entry(position: Position)
    def log_exit(position: Position, exit_price, reason)
```

**Backtesting Algorithm:**
```python
def run_systematic_backtest(start_date, end_date):
    portfolio = Portfolio(initial_capital=100000)
    
    for date in date_range(start_date, end_date):
        # 1. Scan all symbols for pattern matches
        patterns = pattern_scan_orchestrator.scan_all_symbols(date)
        
        # 2. Generate entry signals from patterns
        entry_signals = strategy.generate_entry_signals(patterns)
        
        # 3. Check risk management constraints
        valid_entries = risk_manager.filter_entries(entry_signals, portfolio)
        
        # 4. Execute entries
        for signal in valid_entries:
            position = portfolio.enter_position(signal)
            trade_logger.log_entry(position)
        
        # 5. Update existing positions with current prices
        portfolio.update_positions(date)
        
        # 6. Check exit conditions for all positions
        for position in portfolio.positions:
            if position.check_exit_conditions():
                exit_price = get_price(position.symbol, date)
                portfolio.exit_position(position, exit_price)
                trade_logger.log_exit(position)
        
        # 7. Update portfolio metrics
        portfolio.update_metrics(date)
    
    # 8. Calculate final performance metrics
    return performance_calculator.calculate(portfolio)
```

#### 2.5 Risk Management Module

**Responsibilities:**
- Apply stop-loss and take-profit rules
- Enforce portfolio-level risk limits
- Position sizing

**Key Functions:**
```python
class RiskManager:
    def calculate_stop_loss(entry_price, strategy) -> float
    def calculate_take_profit(entry_price, strategy) -> float
    def update_trailing_stop(position: Position, current_price)
    def check_portfolio_drawdown(portfolio) -> bool
    def check_position_limits(portfolio, new_trade) -> bool
    def calculate_position_size(signal, portfolio) -> int
```

**Hybrid Stop-Loss Logic:**
```python
def update_stop_loss(position, current_price):
    # Initial: Fixed 10% stop
    if position.unrealized_pnl_pct < X_PERCENT:
        stop = position.entry_price * 0.90
    else:
        # Switch to trailing stop after X% gain
        atr = calculate_atr(position.symbol)
        trailing_stop = current_price - (2 * atr)  # 2x ATR trailing
        stop = max(position.stop_loss, trailing_stop)
    
    position.stop_loss = stop
```

#### 2.6 Performance Metrics Calculator

**Responsibilities:**
- Calculate all required performance metrics
- Generate backtest reports

**Key Metrics:**
```python
class PerformanceCalculator:
    def calculate_total_return(portfolio) -> float
    def calculate_annualized_return(portfolio, days) -> float
    def calculate_cagr(portfolio, years) -> float
    def calculate_sharpe_ratio(returns, risk_free_rate=0) -> float
    def calculate_sortino_ratio(returns, risk_free_rate=0) -> float
    def calculate_max_drawdown(equity_curve) -> float
    def calculate_win_rate(trades) -> float
    def calculate_profit_factor(trades) -> float
```

### 3. Presentation Layer

#### 3.1 Web UI (FastAPI)

**Responsibilities:**
- Provide user interface for triggering scans and backtests
- Display results and reports
- Allow configuration of strategies

**Key Endpoints:**
```python
# Data management
POST /api/data/ingest          # Trigger data ingestion
GET  /api/data/status           # Check data status

# Pattern scanning
POST /api/scan/patterns         # Trigger pattern scan
GET  /api/scan/results/{date}   # Get scan results

# Backtesting
POST /api/backtest/run          # Run backtest
GET  /api/backtest/results/{id} # Get backtest results
GET  /api/backtest/list         # List all backtests

# Reports
GET  /api/reports/ideas-log     # Download ideas.log
GET  /api/reports/backtest/{id} # Download backtest CSV
```

**Web Pages:**
- Dashboard (overview, recent scans, backtest results)
- Data Management (trigger updates, view status)
- Pattern Scanner (configure and run scans)
- Backtesting (configure strategy, run backtest, view results)
- Reports (download ideas.log, backtest CSVs)

#### 3.2 Ideas Log Writer

**Format:**
```
2025-11-26 09:30:00 | RELIANCE | VCP+TrendTemplate | Price: 2450.50 | Vol: 5.2M | RS: 85 | Confidence: 82/100
Recommended: BUY @ 2455 | Stop: 2209.50 (10%) | Target: 2945 (20%) | Max Position: 10%
Rationale: Strong VCP with 3 contractions, volume declining on pullbacks. Meets all Trend Template criteria. Stage 2 advance.
---
```

#### 3.3 CSV Report Generator

**Backtest Results CSV Structure:**
```csv
Backtest Name, Start Date, End Date, Total Return, Annualized Return, CAGR, Sharpe, Sortino, Max Drawdown, Win Rate, Profit Factor, Total Trades
```

**Trades CSV Structure:**
```csv
Symbol, Entry Date, Entry Price, Exit Date, Exit Price, Position, Quantity, P&L, P&L %, Exit Reason
```

---

## Processing Pipeline

### Daily Batch Processing Pipeline

```mermaid
graph LR
    A[Trigger Daily Job] --> B[Fetch Latest Data]
    B --> C[Validate & Store]
    C --> D[Calculate Indicators]
    D --> E[Update Derived Metrics]
    E --> F[Run Pattern Scan]
    F --> G[Detect Patterns]
    G --> H[Generate Trade Recommendations]
    H --> I[Append to Ideas Log]
    I --> J[Send Completion Notification]
```

### Historical Backtest Pipeline

```mermaid
graph LR
    A[User Config] --> B[Load Historical Data]
    B --> C[Initialize Portfolio]
    C --> D[Iterate Through Days]
    D --> E[Scan for Patterns]
    E --> F[Generate Signals]
    F --> G[Apply Risk Rules]
    G --> H[Execute Trades]
    H --> I[Update Positions]
    I --> J{More Days?}
    J -->|Yes| D
    J -->|No| K[Calculate Metrics]
    K --> L[Generate Reports]
    L --> M[Save Results]
```

---

## Algorithms & Logic

### Key Algorithms

#### 1. Mansfield Relative Strength
```python
def calculate_mansfield_rs(stock_prices, index_prices, smooth_period=52):
    """
    Mansfield RS = (Stock Price / Index Price) smoothed over period
    """
    ratio = stock_prices / index_prices
    smoothed_ratio = ratio.rolling(window=smooth_period).mean()
    
    # Normalize to 0-100 scale (optional)
    rs_normalized = ((smoothed_ratio - smoothed_ratio.min()) / 
                     (smoothed_ratio.max() - smoothed_ratio.min())) * 100
    
    return rs_normalized
```

#### 2. VCP Detection
```python
def detect_vcp(df, min_contractions=2, max_contractions=4, tolerance=0.20):
    """
    Detect Volatility Contraction Pattern
    """
    # Find pivot highs and lows
    pivots = find_pivot_points(df)
    
    # Identify pullbacks (sequences of high-to-low)
    pullbacks = []
    for i in range(1, len(pivots)):
        if pivots[i].type == 'low' and pivots[i-1].type == 'high':
            depth = (pivots[i-1].price - pivots[i].price) / pivots[i-1].price
            avg_volume = df[pivots[i-1].date:pivots[i].date]['volume'].mean()
            pullbacks.append({
                'depth': depth,
                'avg_volume': avg_volume,
                'start': pivots[i-1].date,
                'end': pivots[i].date
            })
    
    # Check VCP criteria
    if not (min_contractions <= len(pullbacks) <= max_contractions):
        return None
    
    # Each pullback should be shallower than previous
    for i in range(1, len(pullbacks)):
        if pullbacks[i]['depth'] > pullbacks[i-1]['depth'] * (1 + tolerance):
            return None
        
        # Volume should contract
        if pullbacks[i]['avg_volume'] > pullbacks[i-1]['avg_volume']:
            return None
    
    # VCP detected
    confidence = calculate_vcp_confidence(pullbacks)
    return VCPPattern(pullbacks=pullbacks, confidence=confidence)
```

#### 3. Trend Template Validation
```python
def validate_trend_template(symbol_id, date, metrics):
    """
    Check all 7 Minervini Trend Template criteria
    """
    checks = {}
    
    # Criterion 1: Price > 150-day and 200-day MA
    checks['price_above_ma'] = (metrics.close > metrics.ma_150 and 
                                 metrics.close > metrics.ma_200)
    
    # Criterion 2: 150-day > 200-day MA
    checks['ma_150_above_ma_200'] = metrics.ma_150 > metrics.ma_200
    
    # Criterion 3: 200-day MA trending up for >= 1 month
    ma_200_30days_ago = get_metric(symbol_id, date - 30, 'ma_200')
    checks['ma_200_trending_up'] = metrics.ma_200 > ma_200_30days_ago
    
    # Criterion 4: 50-day > 150-day and 200-day MA
    checks['ma_50_above_others'] = (metrics.ma_50 > metrics.ma_150 and 
                                     metrics.ma_50 > metrics.ma_200)
    
    # Criterion 5: Price > 30% above 52-week low
    checks['price_above_52w_low'] = metrics.close > (metrics.week_52_low * 1.30)
    
    # Criterion 6: Price within 25% of 52-week high
    checks['price_near_52w_high'] = metrics.close >= (metrics.week_52_high * 0.75)
    
    # Criterion 7: RS rating > 70
    checks['rs_rating'] = metrics.mansfield_rs > 70
    
    # All criteria must pass
    passes_template = all(checks.values())
    
    return passes_template, checks
```

#### 4. Performance Metrics
```python
def calculate_sharpe_ratio(returns, risk_free_rate=0.0, periods_per_year=252):
    """
    Sharpe Ratio = (Average Return - Risk Free Rate) / Std Dev of Returns
    Annualized for daily returns
    """
    excess_returns = returns - risk_free_rate
    sharpe = (excess_returns.mean() / excess_returns.std()) * np.sqrt(periods_per_year)
    return sharpe

def calculate_max_drawdown(equity_curve):
    """
    Maximum peak-to-trough decline
    """
    running_max = equity_curve.expanding().max()
    drawdown = (equity_curve - running_max) / running_max
    max_drawdown = drawdown.min()
    return abs(max_drawdown)

def calculate_profit_factor(trades):
    """
    Profit Factor = Gross Profit / Gross Loss
    """
    winning_trades = trades[trades['pnl'] > 0]
    losing_trades = trades[trades['pnl'] < 0]
    
    gross_profit = winning_trades['pnl'].sum()
    gross_loss = abs(losing_trades['pnl'].sum())
    
    if gross_loss == 0:
        return float('inf')
    
    return gross_profit / gross_loss
```

---

## API & Integration Design

### External API Integration

#### Zerodha Integration
```python
class ZerodhaClient:
    def __init__(self, api_key, access_token):
        self.kite = KiteConnect(api_key=api_key)
        self.kite.set_access_token(access_token)
    
    def get_historical_data(self, instrument_token, from_date, to_date, interval='day'):
        """
        Fetch historical OHLCV data
        """
        data = self.kite.historical_data(
            instrument_token=instrument_token,
            from_date=from_date,
            to_date=to_date,
            interval=interval
        )
        return pd.DataFrame(data)
    
    def get_instruments(self, exchange='NSE'):
        """
        Get list of all instruments
        """
        return self.kite.instruments(exchange)
```

#### Yahoo Finance Integration
```python
class YahooFinanceClient:
    def get_historical_data(self, symbol, start_date, end_date):
        """
        Fetch historical data using yfinance
        """
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date)
        return df
    
    def get_all_sp500_symbols(self):
        """
        Fetch S&P 500 constituent list
        """
        # Use pandas to scrape Wikipedia or other source
        # Return list of symbols
```

### Internal REST API

**API Design Principles:**
- RESTful design
- JSON request/response
- Async processing for long-running jobs (backtests)
- Job status polling endpoints

**Example API Workflow:**
```
1. POST /api/backtest/run
   → Response: { "job_id": "bt_12345", "status": "queued" }

2. GET /api/backtest/status/bt_12345
   → Response: { "job_id": "bt_12345", "status": "running", "progress": 45 }

3. GET /api/backtest/status/bt_12345
   → Response: { "job_id": "bt_12345", "status": "completed" }

4. GET /api/backtest/results/bt_12345
   → Response: { ..complete results.. }

5. GET /api/backtest/report/bt_12345.csv
   → Download CSV file
```

---

## Deployment Architecture

### Local Development Setup

```
Project Structure:
SecuritiesResearchTool/
├── backend/
│   ├── api/                 # FastAPI routes
│   ├── core/                # Business logic
│   │   ├── indicators/
│   │   ├── patterns/
│   │   ├── backtesting/
│   │   └── risk_management/
│   ├── data/                # Data layer
│   │   ├── ingestion/
│   │   ├── models/          # SQLAlchemy models
│   │   └── repositories/
│   ├── utils/
│   ├── config.py
│   └── main.py              # FastAPI app entry
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   └── templates/           # Jinja2 HTML templates
├── database/
│   ├── migrations/          # Alembic migrations
│   └── init.sql             # Initial schema
├── scripts/
│   ├── data_ingestion.py    # CLI for data updates
│   └── backtest_runner.py   # CLI for backtests
├── tests/
│   ├── unit/
│   └── integration/
├── logs/
│   └── ideas.log
├── reports/                 # Generated CSV reports
├── .env                     # Environment variables
├── requirements.txt
├── docker-compose.yml       # Optional: containerized deployment
└── README.md
```

### Environment Configuration

**.env file:**
```
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/securities_research

# Zerodha
ZERODHA_API_KEY=your_api_key
ZERODHA_ACCESS_TOKEN=your_access_token

# Application
SECRET_KEY=your_secret_key
DEBUG=True
LOG_LEVEL=INFO

# Backtesting
INITIAL_CAPITAL=100000
MAX_POSITION_SIZE_PCT=10
MAX_CONCURRENT_POSITIONS=10
PORTFOLIO_DRAWDOWN_LIMIT=20

# Risk Management
INITIAL_STOP_LOSS_PCT=10
TRAILING_STOP_TRIGGER_PCT=15
TRAILING_STOP_ATR_MULTIPLIER=2
```

### Database Setup

```bash
# Install PostgreSQL and TimescaleDB
# Create database
createdb securities_research

# Run migrations
alembic upgrade head

# Initial data load
python scripts/data_ingestion.py --initial-load
```

### Running the Application

```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start FastAPI server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Access web UI
# Navigate to http://localhost:8000
```

### Scheduled Jobs

**Using cron (Linux/Mac) or Task Scheduler (Windows):**

```bash
# Daily data update at 11 PM
0 23 * * * /path/to/venv/bin/python /path/to/scripts/data_ingestion.py --update

# Daily pattern scan at midnight
0 0 * * * /path/to/venv/bin/python /path/to/scripts/pattern_scan.py --date today
```

**Alternative: Python scheduling (APScheduler):**
```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(daily_data_update, 'cron', hour=23, minute=0)
scheduler.add_job(daily_pattern_scan, 'cron', hour=0, minute=0)
scheduler.start()
```

---

## Development Phases

### Phase 1: Data Infrastructure (Weeks 1-2)
**Deliverables:**
- Database schema created (PostgreSQL + TimescaleDB)
- Data ingestion scripts for Zerodha and Yahoo Finance
- Symbol management (loading universe of 10,000 stocks)
- Historical data loaded (20 years)
- Data validation and cleansing

**Acceptance Criteria:**
- ✅ Database schema deployed
- ✅ 20 years of daily data loaded for Indian markets
- ✅ 20 years of daily data loaded for US markets
- ✅ Data quality checks passing (no missing critical data)

### Phase 2: Indicator Calculation (Weeks 3-4)
**Deliverables:**
- Technical indicator calculation module
- Moving averages (50, 150, 200-day, weekly periods)
- RSI, MACD
- Mansfield RS calculation
- 52-week high/low tracking
- Volume metrics
- Batch processing for all symbols
- derived_metrics table populated

**Acceptance Criteria:**
- ✅ All indicators calculated for entire dataset
- ✅ Spot checks validate indicator accuracy
- ✅ Performance acceptable (full universe processed in reasonable time)

### Phase 3: Pattern Recognition (Weeks 5-7)
**Deliverables:**
- Trend Template recognizer
- VCP detector
- Cup & Handle detector
- Double Bottom detector
- High-Tight Flag detector
- Weinstein Stage Analysis
- Pattern confidence scoring
- Pattern scanning orchestrator

**Acceptance Criteria:**
- ✅ Each pattern detector implemented and unit tested
- ✅ Known historical patterns detected correctly (manual validation)
- ✅ Confidence scores reasonable and consistent
- ✅ Full universe scan completes successfully

### Phase 4: Backtesting Engine (Weeks 8-10)
**Deliverables:**
- Backtesting engine core
- Position management
- Trade execution simulator
- Risk management module (stop-loss, take-profit, hybrid logic)
- Portfolio-level risk controls
- Performance metrics calculator
- Trade logging

**Acceptance Criteria:**
- ✅ Backtest runs from start to end date without errors
- ✅ Trades executed according to rules
- ✅ Risk management rules enforced correctly
- ✅ Performance metrics calculated accurately
- ✅ Results match manual calculations on sample data

### Phase 5: Web UI & Reporting (Weeks 11-12)
**Deliverables:**
- FastAPI application with endpoints
- Web UI pages (Dashboard, Data Management, Scanner, Backtesting, Reports)
- Ideas.log writer and viewer
- CSV report generator
- Job scheduling for daily updates
- Documentation (user guide, API docs)

**Acceptance Criteria:**
- ✅ All web pages functional
- ✅ User can trigger scans and backtests via UI
- ✅ Ideas.log generated in correct format
- ✅ CSV reports downloadable
- ✅ Scheduled jobs running reliably

### Phase 6: Integration Testing & Validation (Weeks 13-14)
**Deliverables:**
- End-to-end testing of complete workflow
- Validation of SEPA methodology backtest
- Performance optimization
- Bug fixes
- Final documentation

**Acceptance Criteria:**
- ✅ Complete workflow tested (data → scan → backtest → report)
- ✅ SEPA methodology backtest results generated
- ✅ System performance acceptable for 10,000 securities
- ✅ All critical bugs resolved
- ✅ User documentation complete

---

## Technical Risks & Mitigations

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|------------|--------|---------------------|
| **Data Quality Issues** | High | High | Implement robust validation; cross-check with multiple sources; manual spot checks |
| **API Rate Limits** | Medium | Medium | Implement rate limiting; caching; batch requests; exponential backoff on retries |
| **Pattern Detection Accuracy** | High | High | Start with well-defined patterns; configurable tolerance; manual confirmation workflow; iterative refinement |
| **Performance Bottlenecks** | Medium | Medium | Database indexing; query optimization; parallel processing; incremental calculations |
| **Overfitting in Backtesting** | Medium | High | Walk-forward testing (future phase); out-of-sample validation; conservative metrics |
| **Database Scalability** | Low | Medium | TimescaleDB designed for time-series; compression; data retention policies |
| **Code Complexity** | Medium | Medium | Modular design; comprehensive unit tests; code reviews; documentation |
| **Ambiguous Requirements** | Medium | High | Iterative development; frequent user feedback; clear acceptance criteria |

### Performance Optimization Strategies

1. **Database Indexing:**
   ```sql
   CREATE INDEX idx_price_data_symbol_date ON price_data(symbol_id, date DESC);
   CREATE INDEX idx_derived_metrics_symbol_date ON derived_metrics(symbol_id, date DESC);
   CREATE INDEX idx_pattern_detections_date ON pattern_detections(detection_date DESC);
   ```

2. **Caching:**
   - Cache indicator calculations in derived_metrics table
   - Use Redis for frequently accessed data (optional)

3. **Parallel Processing:**
   - Process symbols in parallel using multiprocessing or async I/O
   - Batch database inserts

4. **Query Optimization:**
   - Use TimescaleDB continuous aggregates for pre-computed metrics
   - Limit query result sets
   - Use database views for complex queries

5. **Incremental Processing:**
   - Only calculate new data points, not entire history
   - Track last processed date per symbol

---

## Testing Strategy

### Unit Testing
- Test each pattern recognizer in isolation
- Test indicator calculations against known values
- Test risk management logic

### Integration Testing
- Test data ingestion → indicator calculation pipeline
- Test pattern scan → ideas log workflow
- Test backtesting engine end-to-end

### Validation Testing
- Compare indicator values with established charting platforms (TradingView)
- Manually validate pattern detections on known historical examples
- Cross-check backtest results with manual calculations

### Performance Testing
- Benchmark database queries
- Test full universe scan time
- Test backtest performance on 20-year dataset

---

## Security Considerations

### Data Security
- Store API keys and credentials in .env file (not in code)
- Use environment variables for sensitive configuration
- .gitignore for .env file

### Application Security
- Input validation on all user inputs
- SQL injection prevention (use parameterized queries)
- Rate limiting on API endpoints (future consideration)

### Access Control
- MVP: Single user, no authentication
- Future: Add user authentication and role-based access control

---

## Monitoring & Logging

### Application Logging
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/application.log'),
        logging.StreamHandler()
    ]
)
```

### Key Metrics to Monitor
- Data ingestion success/failure rates
- Pattern detection counts and trends
- Backtest execution time
- Database query performance
- API response times

### Error Handling
- Graceful error handling with informative messages
- Retry logic for transient failures (network issues)
- Error logging with stack traces
- User-friendly error messages in UI

---

## Documentation Requirements

### Code Documentation
- Docstrings for all classes and functions
- Inline comments for complex logic
- Type hints throughout codebase

### User Documentation
- Installation guide
- User manual for web UI
- Configuration guide
- Troubleshooting guide

### Technical Documentation
- Architecture overview (this document)
- Database schema documentation
- API documentation (auto-generated via FastAPI)
- Algorithm explanations

---

## Future Enhancements (Post-MVP)

### Phase 2 Features
- Interactive charting (Plotly, LightweightCharts)
- Real-time data streaming
- Advanced position sizing
- Parameter optimization

### Phase 3 Features
- Cloud deployment (AWS, Azure, GCP)
- Multi-user support with authentication
- Collaboration features
- Mobile app

### Phase 4 Features
- Machine learning for pattern recognition
- Sentiment analysis integration
- Options/derivatives support
- Portfolio management

---

## Appendices

### Appendix A: Technology Learning Resources
- **FastAPI:** https://fastapi.tiangolo.com/
- **TimescaleDB:** https://docs.timescale.com/
- **pandas:** https://pandas.pydata.org/docs/
- **TA-Lib:** https://mrjbq7.github.io/ta-lib/

### Appendix B: Data Sources
- **Zerodha Kite Connect:** https://kite.trade/docs/connect/v3/
- **yfinance:** https://github.com/ranaroussi/yfinance

### Appendix C: Mark Minervini Resources
- **Books:** "Trade Like a Stock Market Wizard", "Think & Trade Like a Champion"
- **Trend Template:** https://www.minervini.com/

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-26 | [Author] | Initial draft |

---

**Next Steps:**
1. Review and approve this Technical Design Document
2. Set up development environment
3. Begin Phase 1: Data Infrastructure
4. Weekly progress reviews and iterative refinement
