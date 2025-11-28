# High Level Technical Design Document
## Securities Research Tool - Pattern Recognition & Backtesting Platform

**Version:** 1.1  
**Date:** November 27, 2025  
**Status:** Draft for Review

---

## Table of Contents
1. [System Overview](#system-overview)
2. [Engineering Standards Compliance](#engineering-standards-compliance)
3. [Architecture](#architecture)
4. [Technology Stack Recommendations (with Pricing Analysis)](#technology-stack-recommendations-with-pricing-analysis)
5. [Component Design](#component-design)
6. [Data Model](#data-model)
7. [Processing Pipeline](#processing-pipeline)
8. [Algorithms & Logic](#algorithms--logic)
9. [Code Quality Standards](#code-quality-standards)
10. [Testing Strategy](#testing-strategy)
11. [Security](#security)
12. [CI/CD Pipeline](#cicd-pipeline)
13. [API & Integration Design](#api--integration-design)
14. [Deployment Architecture](#deployment-architecture)
15. [Monitoring & Observability](#monitoring--observability)
16. [Error Handling & Resilience](#error-handling--resilience)
17. [Development Phases](#development-phases)
18. [Technical Risks & Mitigations](#technical-risks--mitigations)
19. [Performance Optimization Strategies](#performance-optimization-strategies)
20. [Documentation Requirements](#documentation-requirements)
21. [Version Control & Collaboration](#version-control--collaboration)

---

## System Overview

### Architecture Principles
- **Modularity:** Separate concerns into distinct, testable components
- **Extensibility:** Design for future expansion (real-time, more patterns, more markets)
- **Performance:** Optimize for batch processing of large datasets
- **Maintainability:** Clean code with abundant comments, clear separation of data/business logic/presentation, 
- **Documentation:** Maintain clear documentation for each component

### High-Level Architecture Style
**Layered Architecture** with the following layers:
1. **Data Layer:** Data acquisition, storage, and access
2. **Business Logic Layer:** Pattern recognition, backtesting, calculations
3. **Presentation Layer:** Web UI and reporting

---

## Engineering Standards Compliance

This design adheres to the [Engineering Standards] established for this project.

**Key Commitments:**
- **Code Quality:** SOLID principles, clean architecture, comprehensive documentation
- **Security:** OWASP ASVS Level 2 compliance, secure coding practices (CERT)
- **Testing:** ≥80% branch coverage, testing pyramid approach, automated regression testing
- **Reliability:** Resilience patterns (timeouts, retries, circuit breakers)
- **Observability:** Structured logging (JSON), metrics, distributed tracing (future)
- **CI/CD:** Automated testing, linting, security scanning on every commit
- **Documentation:** Code docstrings, ADRs, runbooks, architecture diagrams (C4 model)

All code, architecture decisions, and processes will conform to these standards unless explicitly documented otherwise via Architecture Decision Record (ADR).

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

## Technology Stack Recommendations (with Pricing Analysis)

**Philosophy:** Prioritize FREE, open-source solutions for MVP. Minimize costs while maximizing functionality.

---

### Comprehensive Technology Stack Comparison

| Component | **Recommendation** | **Price** | Alternatives Considered | **Rationale** |
|-----------|-------------------|-----------|------------------------|---------------|
| **Database** | **PostgreSQL + TimescaleDB** | **FREE** | ClickHouse (Free), InfluxDB Cloud ($49+/mo) | ✅ Best-in-class time-series support<br>✅ Mature ecosystem, excellent documentation<br>✅ Scales to millions of rows<br>✅ Zero cost |
| **US Market Data** | **yfinance** | **FREE** | Polygon.io ($29/mo), IEX Cloud (pay-as-go $0.05/call), Alpha Vantage (500 calls/day free) | ✅ **Unlimited historical data**<br>✅ No rate limits (reasonable use)<br>✅ 20+ years of history<br>✅ Zero cost |
| **Indian Market Data** | **Zerodha Kite Connect** | **FREE*** | NSE Data Feed ($100+/mo), BSE DataFeed ($) | ✅ Free with trading account<br>✅ Official, reliable API<br>✅ Good documentation<br>* Trading account required |
| **Backend Language** | **Python 3.11+** | **FREE** | None | ✅ Excellent data science libraries<br>✅ FastAPI, pandas, numpy ecosystem<br>✅ Industry standard for quant/trading |
| **Web Framework** | **FastAPI** | **FREE** | Flask (Free), Django (Free) | ✅ Modern, fast, async support<br>✅ Automatic API documentation<br>✅ Type safety with Pydantic<br>✅ Better performance than Flask |
| **Data Processing** | **pandas + numpy** | **FREE** | Polars (Free), Dask (Free) | ✅ Industry standard<br>✅ Vast ecosystem and resources<br>✅ Mature, well-tested |
| **Technical Indicators** | **pandas-ta** | **FREE** | TA-Lib (requires compilation) | ✅ Pure Python, easy install<br>✅ No compilation issues on Windows<br>✅ Good documentation |
| **Frontend** | **HTML/CSS/JavaScript** | **FREE** | React (Free), Vue (Free) | ✅ Simple UI doesn't need heavy framework<br>✅ Bootstrap/Tailwind for styling<br>✅ Vanilla JS or Alpine.js |
| **Testing** | **pytest + pytest-cov** | **FREE** | None | ✅ Industry standard<br>✅ Rich plugin ecosystem<br>✅ Coverage reporting built-in |
| **Linting/Formatting** | **Black + Ruff** | **FREE** | Pylint (Free), Flake8 (Free) | ✅ Black: opinionated, fast<br>✅ Ruff: replaces multiple tools, very fast |
| **Type Checking** | **Mypy** | **FREE** | Pyright (Free) | ✅ Most mature Python type checker<br>✅ Strict mode available |
| **Charting (Future)** | **Plotly** | **FREE** | Lightweight Charts ($), TradingView Widget ($$) | ✅ Interactive charts<br>✅ Python integration<br>✅ Export to HTML<br>❌ Paid: $50-500/month |
| **Deployment (MVP)** | **Local (localhost)** | **FREE** | Docker (Free), Cloud VPS ($5-20/mo) | ✅ No hosting costs for MVP<br>✅ Runs on developer machine |
| **Version Control** | **Git + GitHub** | **FREE** | GitLab (Free), Bitbucket (Free) | ✅ Standard, free private repos |

---

### Total MVP Cost: **$0**

All core technologies are free and open-source. The only prerequisite is a Zerodha trading account for Indian market data (free to open, no minimum balance for API access).

---

### Optional Paid Upgrades (Post-MVP)

**If budget allows or scaling requires:**

| Upgrade | Cost | Benefit |
|---------|------|---------|
| **Premium Data Provider** | $30-100/month | Lower latency, more symbols, real-time data |
| **Cloud Hosting** | $20-50/month | AWS EC2 t3.medium, Azure B2s, or GCP e2-medium |
| **Monitoring SaaS** | $15-100/month | Datadog (paid), New Relic (paid) vs. Grafana (free) |
| **Backup Storage** | $5-10/month | AWS S3, Google Cloud Storage for database backups |
| **Premium Charting** | $50-500/month | TradingView advanced charts, Lightweight Charts Pro |

**Recommended Priority:** Start with free tools. Only upgrade if specific limitations are hit (e.g., data provider rate limits, need for real-time data).

---

### Technology Stack Justification

#### Why These Choices?

**1. PostgreSQL + TimescaleDB (Database)**
- **Pros:**
  - Purpose-built for time-series data (OHLCV is time-series)
  - Excellent query performance on millions of rows
  - Continuous aggregates for weekly/monthly data (Phase 2 optimization)
  - Mature, reliable, well-documented
  - Scales horizontally if needed
- **Cons:**
  - Slightly more complex than SQLite, but worth it for performance
  - Requires PostgreSQL installation
- **Alternatives Rejected:**
  - ClickHouse: Steeper learning curve, less mature Python ecosystem
  - InfluxDB: Limited SQL support, less flexible for complex queries
  - SQLite: Cannot handle 5M+ rows efficiently

**2. yfinance (US Market Data)**
- **Pros:**
  - **FREE unlimited historical data** (biggest advantage)
  - No API key required
  - Easy Python integration
  - 20+ years of history available
  - No rate limits for reasonable use
- **Cons:**
  - Unofficial API (uses Yahoo Finance web scraping)
  - Occasional brief outages
  - No real-time data (batch only)
- **Alternatives Rejected:**
  - Polygon.io: $29/month unnecessary for MVP  
  - IEX Cloud: Pay-per-call model adds up quickly
  - Alpha Vantage: 500 calls/day limit too restrictive

**3. Zerodha Kite Connect (Indian Market Data)**
- **Pros:**
  - Free with trading account (most developers already have one)
  - Official API from largest Indian broker
  - Reliable, well-documented
  - Historical + real-time (future)
- **Cons:**
  - Requires trading account
  - Subject to rate limits (reasonable for batch processing)
- **Alternatives Rejected:**
  - NSE/BSE Official: $100+ per month, enterprise-focused
  - Third-party data vendors: $50-200/month

**4. FastAPI (Web Framework)**
- **Pros:**
  - Modern, async-first design
  - Automatic OpenAPI documentation (Swagger UI)
  - Type safety with Pydantic models
  - Fast performance (on par with Node.js)
  - Easy to learn if you know Flask
- **Cons:**
  - Slightly steeper learning curve than Flask
- **Alternatives Rejected:**
  - Flask: Simpler but lacks async, type safety, auto docs
  - Django: Too heavy for our needs, ORM not ideal

**5. pandas-ta (Technical Indicators)**
- **Pros:**
  - Pure Python, no compilation required
  - Works out-of-the-box on Windows
  - Good indicator coverage
  - Pandas integration
- **Cons:**
  - Slightly slower than TA-Lib (acceptable for batch processing)
- **Alternatives Rejected:**
  - TA-Lib: Compilation issues on Windows, harder to install
  - Custom implementation: Reinventing the wheel

---

### Deployment Strategy (MVP)

**MVP Approach:** Local development machine
- Run on `localhost:8000`
- Single user (no auth needed)
- Data stored locally in PostgreSQL
- Perfect for development and testing

**Post-MVP (Phase 2):**
- **Option A:** Cloud VM (AWS EC2, DigitalOcean Droplet)
  - Cost: $5-20/month for small VM
  - Full control, easy to manage
  
- **Option B:** Containerized (Docker + Cloud Run/AWS ECS)
  - Cost: $10-30/month
  - Better scalability, auto-restart
  
- **Option C:** Serverless (AWS Lambda + RDS)
  - Cost: Pay-per-use (potentially higher for frequent backtests)
  - Best for sporadic usage

**Recommendation for Phase 2:** Cloud VM (simplest, most cost-effective)

---

### Development Tools (All FREE)

| Tool | Purpose | Cost |
|------|---------|------|
| VS Code | IDE | FREE |
| Git | Version control | FREE |
| GitHub | Remote repository | FREE (private repos included) |
| DBeaver | Database GUI | FREE |
| Postman | API testing | FREE tier sufficient |
| Chrome DevTools | Frontend debugging | FREE |

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
from abc import ABC, abstractmethod
from datetime import date
import pandas as pd
from typing import Optional

class DataProvider(ABC):
    """
    Abstract base class for market data providers.
    
    Purpose:
        Defines uniform interface for all data providers (Zerodha, Yahoo Finance, etc.)
        Ensures consistent data acquisition regardless of source.
        Enables Strategy Pattern - swap data sources without changing client code.
        
    Design Pattern:
        Strategy Pattern - allows runtime selection of data source
        
    Implementation Requirements:
        - fetch_historical() must return standardized DataFrame format
        - Data must be validated before returning
        - Errors must use custom exception hierarchy
        
    Usage:
        provider = ZerodhaDataProvider(api_key, access_token)
        data = provider.fetch_historical('RELIANCE', start_date, end_date)
    """
    
    @abstractmethod
    def fetch_historical(
        self,
        symbol: str,
        start_date: date,
        end_date: date
    ) -> pd.DataFrame:
        """
        Fetch historical OHLCV data for a security.
        
        Purpose:
            Retrieve price and volume history for backtesting and pattern analysis.
            Data must be validated and normalized to standard format.
        
        Args:
            symbol: Stock ticker (e.g., "RELIANCE" for NSE, "AAPL" for NASDAQ)
            start_date: First date of data to retrieve (inclusive)
            end_date: Last date of data to retrieve (inclusive)
        
        Returns:
            DataFrame with columns: date, open, high, low, close, volume
            Index: DatetimeIndex in ascending chronological order
            All prices in local currency (INR for India, USD for US)
            Volume in number of shares traded
        
        Raises:
            ValueError: If start_date > end_date or symbol format invalid
            APIError: If data provider API fails
            DataValidationError: If retrieved data fails quality checks
            
        Example:
            >>> provider = ZerodhaDataProvider(api_key, token)
            >>> df = provider.fetch_historical('RELIANCE', date(2020,1,1), date(2020,12,31))
            >>> df.head()
                        date    open    high     low   close    volume
            0  2020-01-01  1450.0  1465.0  1448.0  1460.0  5000000
        """
        pass

from backend.core.constants import API_TIMEOUT_SECONDS
from kiteconnect import KiteConnect

class ZerodhaDataProvider(DataProvider):
    """
    Zerodha Kite Connect API client for Indian market data (NSE/BSE).
    
    Purpose:
        Fetch historical and (future) real-time data from Zerodha.
        Handles authentication, rate limiting, and data normalization.
        
    Authentication:
        Requires API key and daily access token.
        Access token expires daily and must be refreshed.
        
    Rate Limits:
        - Historical data: 3 requests/second
        - Retry with exponential backoff if rate limited
        
    Usage:
        provider = ZerodhaDataProvider(
            api_key="your_api_key",
            access_token="daily_token"
        )
        data = provider.fetch_historical("NSE:RELIANCE", start, end)
    """
    
    def __init__(self, api_key: str, access_token: str):
        """
        Initialize Zerodha data provider with credentials.
        
        Purpose:
            Set up authenticated connection to Kite Connect API.
        
        Args:
            api_key: Kite Connect API key from Zerodha developer console
            access_token: User-specific access token (regenerated daily)
        
        Raises:
            AuthenticationError: If credentials are invalid
        """
        self.kite = KiteConnect(api_key=api_key)
        self.kite.set_access_token(access_token)
        
    def fetch_historical(
        self,
        symbol: str,
        start_date: date,
        end_date: date
    ) -> pd.DataFrame:
        """
        Fetch historical data from Zerodha Kite Connect.
        
        Purpose:
            Retrieve OHLCV data for Indian stocks (NSE/BSE).
            Normalizes Kite Connect response to standard format.
        
        Implementation Details:
            - Kite expects instrument token, not symbol (we look it up)
            - Returns data in IST timezone
            - Handles corporate actions (splits, bonuses) automatically
        
        Args:
            symbol: Stock symbol with exchange prefix (e.g., "NSE:RELIANCE")
            start_date: Start date for data retrieval
            end_date: End date for data retrieval
            
        Returns:
            DataFrame with standardized columns and DatetimeIndex
            
        Raises:
            DataFetchError: If API call fails
            DataValidationError: If response data is invalid
        """
        try:
            # Kite uses instrument tokens, not symbols
            instrument_token = self._get_instrument_token(symbol)
            
            # Fetch from Kite API
            records = self.kite.historical_data(
                instrument_token=instrument_token,
                from_date=start_date,
                to_date=end_date,
                interval="day",
                timeout=API_TIMEOUT_SECONDS  # From constants.py
            )
            
            # Convert to DataFrame
            df = pd.DataFrame(records)
            
            # Normalize column names to standard format
            df = df.rename(columns={
                'date': 'date',
                # Kite uses OHLC, we standardize to lowercase
            })
            
            # Set datetime index
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date').sort_index()
            
            # Validate data quality
            self._validate_data(df, symbol)
            
            return df
            
        except Exception as e:
            # Log and wrap in custom exception
            logger.error(f"Zerodha fetch failed for {symbol}", exc_info=True)
            raise DataFetchError(f"Failed to fetch {symbol} from Zerodha") from e

class YahooFinanceProvider(DataProvider):
    """Yahoo Finance data provider implementation using yfinance."""
    
    def fetch_historical(self, symbol: str, start_date: date, end_date: date) -> pd.DataFrame:
        """Fetch historical data from Yahoo Finance."""
        # Implementation details
        pass

class DataIngestionOrchestrator:
    """Orchestrates data ingestion from multiple providers."""
    
    def ingest_universe(self, provider: DataProvider, symbol_list: List[str]) -> None:
        """
        Ingest historical data for all symbols in the universe.
        
        Args:
            provider: Data provider instance
            symbol_list: List of symbols to ingest
        """
        pass
    
    def schedule_daily_update(self) -> None:
        """Schedule and execute daily data updates."""
        pass
```

**Data Validation Rules:**
- Check for missing dates (non-trading days acceptable)
- Validate OHLCV integrity (High ≥ Low, Close within High-Low range)
- Volume must be non-negative
- Price must be non-negative
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

#### 1.3 Data Storage Strategy

**Multi-Timeframe Data: Phased Approach**

The system requires analysis across multiple timeframes (daily, weekly, monthly). Three approaches were considered:

| Approach | Query Performance | Storage Overhead | Complexity | Data Consistency Risk |
|----------|------------------|------------------|------------|-----------------------|
| On-the-fly derivation | Slower | Low (1x) | Low | None |
| Separate tables | Fast | High (3x) | High | Medium-High |
| **Continuous Aggregates** | **Fast** | **Medium (1.2x)** | **Medium** | **None** |

**MVP Strategy (Phase 1):**
- Store **daily OHLCV data only** in `price_data` table
- Derive weekly and monthly aggregations **on-the-fly** using SQL GROUP BY queries
- Simple SQL example:
  ```sql
  -- Weekly aggregation on-the-fly
  SELECT 
      symbol_id,
      DATE_TRUNC('week', date) AS week_start,
      FIRST_VALUE(open) AS open,
      MAX(high) AS high,
      MIN(low) AS low,
      LAST_VALUE(close) AS close,
      SUM(volume) AS volume
  FROM price_data
  WHERE symbol_id = ?
  GROUP BY symbol_id, week_start
  ORDER BY week_start;
  ```

**Rationale:**
- ✅ Simplest implementation for MVP
- ✅ Single source of truth, no sync issues
- ✅ Faster initial development
- ⚠️ Adequate performance for batch processing (overnight runs)
- Can optimize later if needed

**Phase 2 Performance Optimization (If Needed):**

If query performance becomes a bottleneck, implement **TimescaleDB Continuous Aggregates**:

```sql
-- Create materialized view for weekly data (auto-maintained)
CREATE MATERIALIZED VIEW price_data_weekly
WITH (timescaledb.continuous) AS
SELECT 
    symbol_id,
    time_bucket('7 days', date) AS week_start,
    first(open, date) AS open,
    max(high) AS high,
    min(low) AS low,
    last(close, date) AS close,
    sum(volume) AS volume
FROM price_data
GROUP BY symbol_id, week_start;

-- Automatic refresh policy (runs daily during off-peak)
SELECT add_continuous_aggregate_policy('price_data_weekly',
    start_offset => INTERVAL '1 month',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day');
```

**Benefits of Continuous Aggregates:**
- ✅ Best of both worlds: Fast queries + automatic synchronization
- ✅ Incremental updates (only new data reprocessed)
- ✅ Built-in TimescaleDB feature, minimal code changes
- ✅ Space-efficient with compression
- ✅ Query weekly/monthly data directly without GROUP BY

**Decision Criteria for Phase 2:**
Implement continuous aggregates if:
- Full universe pattern scans take > 30 minutes
- Interactive weekly/monthly analysis becomes a requirement
- Real-time or near-real-time scanning is needed

#### 1.4 Constants Module

**Overview:**

**File:** `backend/core/constants.py`

**Purpose:**  
Centralized repository for all application constants, thresholds, and configuration values. Provides single source of truth for tunable parameters with comprehensive documentation.

**Design Benefits:**
- ✅ No magic numbers scattered in code
- ✅ Self-documenting (each constant has purpose comment)
- ✅ Easy to modify for different strategies or markets
- ✅ Type-safe with Python type hints
- ✅ Testable (mock constants for edge case testing)

---

##### Categories

The constants module organizes values into logical categories:

###### 1. Pattern Recognition Thresholds
Constants defining when patterns are detected:
- `TREND_TEMPLATE_RS_THRESHOLD = 70` - Minimum RS for Trend Template
- `TREND_TEMPLATE_PRICE_ABOVE_52W_LOW_PCT = 1.30` - Price must be >30% above 52-week low
- `VCP_MIN_CONTRACTIONS = 2` - Minimum pullbacks for VCP
- `VCP_TOLERANCE_PCT = 0.20` - Allowable deviation in contraction depth
- `CUP_HANDLE_MIN_WEEKS = 6` - Minimum cup formation duration

###### 2. Risk Management Parameters
Constants controlling position sizing and risk:
- `INITIAL_CAPITAL = 100000` - Starting portfolio value
- `INITIAL_STOP_LOSS_PCT = 0.10` - 10% initial stop-loss
- `MAX_POSITION_SIZE_PCT = 0.10` - Max 10% of portfolio per position
- `MAX_PORTFOLIO_RISK_PCT = 0.02` - Max 2% portfolio risk per trade
- `MAX_POSITIONS = 10` - Maximum concurrent positions

###### 3. Performance Targets
Constants defining acceptable performance:
- `TARGET_FULL_SCAN_MINUTES = 30` - Universe scan time target
- `TARGET_BACKTEST_MINUTES = 30` - Backtest execution target
- `DATA_INGESTION_SUCCESS_RATE_TARGET = 0.99` - 99% success rate
- `DATABASE_QUERY_P95_LATENCY_MS = 500` - Database response time
- `API_RESPONSE_P95_LATENCY_MS = 2000` - API response time

###### 4. Technical Indicator Periods
Constants for indicator calculation:
- `MA_PERIOD_50 = 50` - 50-day moving average
- `MA_PERIOD_150 = 150` - 150-day moving average
- `MA_PERIOD_200 = 200` - 200-day moving average
- `MANSFIELD_RS_SMOOTH_PERIOD = 52` - 52-week RS smoothing
- `RSI_PERIOD = 14` - RSI calculation period

###### 5. Data Processing
Constants for data operations:
- `TRADING_DAYS_PER_YEAR = 252` - For annualization
- `RISK_FREE_RATE = 0.04` - 4% annual risk-free rate
- `LOOKBACK_YEARS = 20` - Historical data depth
- `MIN_TRADING_VOLUME = 100000` - Minimum daily volume filter

###### 6. Testing & Coverage
Constants for test configuration:
- `MIN_BRANCH_COVERAGE_PCT = 80` - Minimum test coverage
- `MAX_UNIT_TEST_DURATION_SECONDS = 300` - Test suite timeout

###### 7. API & Retry Configuration
Constants for resilience:
- `API_TIMEOUT_SECONDS = 30` - API call timeout
- `API_RETRY_MAX_ATTEMPTS = 3` - Maximum retry attempts
- `API_RETRY_BACKOFF_SECONDS = 1` - Initial backoff duration
- `DATA_INGESTION_RETRY_DELAY_SECONDS = 300` - Delay before retry

---

##### Usage Examples

###### Good Practice (Import Constants):

```python
from backend.core.constants import (
    TREND_TEMPLATE_RS_THRESHOLD,
    INITIAL_STOP_LOSS_PCT,
    MAX_POSITION_SIZE_PCT,
    TRADING_DAYS_PER_YEAR
)

def meets_entry_criteria(symbol_metrics: Dict) -> bool:
    """
    Check if symbol meets all entry criteria.
    
    Purpose:
        Constants make the logic self-documenting.
        Intent is clear from constant names.
    """
    return (
        symbol_metrics['mansfield_rs'] > TREND_TEMPLATE_RS_THRESHOLD and
        symbol_metrics['position_size'] <= MAX_POSITION_SIZE_PCT
    )

def calculate_annualized_return(daily_returns: pd.Series) -> float:
    """Calculate annualized return from daily returns."""
    return daily_returns.mean() * TRADING_DAYS_PER_YEAR
```

###### Bad Practice (Avoid - Magic Numbers):

```python
# ❌ DON'T DO THIS - Magic numbers with no context
def meets_entry_criteria(symbol_metrics):
    return (
        symbol_metrics['rs'] > 70 and  # Why 70? What does it represent?
        symbol_metrics['size'] <= 0.10  # Why 0.10? Portfolio %? Position %?
    )

def calculate_return(returns):
    return returns.mean() * 252  # Why 252? Days? Weeks?
```

---

##### Design Pattern

**Pattern:** Configuration Object / Constants Module

**Benefits:**
1. **Single Source of Truth:** Change once, affects entire codebase
2. **Self-Documenting:** Constant names convey meaning
3. **Type Safety:** Python type hints prevent errors
4. **Testability:** Easy to mock for testing edge cases
5. **Strategy Variations:** Create different constant files for different strategies

**Example - Testing with Different Constants:**
```python
# In tests/test_pattern_detection.py
from unittest.mock import patch

def test_vcp_detection_strict_criteria():
    """Test VCP with stricter tolerance."""
    with patch('backend.core.constants.VCP_TOLERANCE_PCT', 0.10):
        # Now VCP requires tighter contractions
        result = detect_v cp(test_data)
        assert result == expected_strict_result

def test_entry_with_higher_rs_threshold():
    """Test entries with higher RS requirement."""
    with patch('backend.core.constants.TREND_TEMPLATE_RS_THRESHOLD', 80):
        # Only consider very strong RS stocks
        entries = get_entry_signals(universe)
        assert all(e['rs'] > 80 for e in entries)
```

---

##### Future Enhancements

**Phase 2: Environment-Based Overrides**
```python
# Allow environment variables to override constants
import os

INITIAL_STOP_LOSS_PCT = float(
    os.getenv('STOP_LOSS_PCT', '0.10')
)
```

**Phase 3: Strategy Profiles**
```python
# Different constant sets for different strategies
from backend.core.constants.aggressive import *
# vs
from backend.core.constants.conservative import *
```

---

##### Architecture Diagram

```mermaid
graph TB
    subgraph "Constants Module"
        CONST[constants.py]
    end
    
    subgraph "Application Code"
        PATTERN[Pattern Recognition]
        RISK[Risk Management]
        BACKTEST[Backtesting Engine]
        METRICS[Performance Metrics]
        API[API Handlers]
    end
    
    subgraph "Tests"
        UNIT[Unit Tests]
        INTEGRATION[Integration Tests]
    end
    
    CONST --> PATTERN
    CONST --> RISK
    CONST --> BACKTEST
    CONST --> METRICS
    CONST --> API
    
    CONST -.mock.-> UNIT
    CONST -.mock.-> INTEGRATION
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
from backend.core.constants import (
    INITIAL_CAPITAL,
    MAX_POSITIONS,
    MAX_POSITION_SIZE_PCT,
    INITIAL_STOP_LOSS_PCT
)
from datetime import date, timedelta
import pandas as pd
from typing import Dict, List

class BacktestEngine:
    """
    Systematic backtesting engine with proper position management.
    
    Purpose:
        Simulate trading strategy over historical data.
        Proper order: manage existing positions before seeking new ones.
        
    Design Pattern:
        Event-driven with daily iteration loop.
        Positions-first approach prevents common backtesting errors.
    """
    
    def __init__(
        self,
        initial_capital: float = INITIAL_CAPITAL,
        max_positions: int = MAX_POSITIONS,
        max_position_size_pct: float = MAX_POSITION_SIZE_PCT
    ):
        """
        Initialize backtesting engine.
        
        Args:
            initial_capital: Starting portfolio value (from constants.py)
            max_positions: Max concurrent positions (from constants.py)
            max_position_size_pct: Max % of portfolio per position
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.max_positions = max_positions
        self.max_position_size_pct = max_position_size_pct
        
        self.positions: Dict[str, Position] = {}  # Active positions
        self.trades: List[Trade] = []  # Completed trades history
        self.equity_curve: List[float] = []  # Daily portfolio values
        
    def run_backtest(
        self,
        symbols: List[str],
        start_date: date,
        end_date: date,
        pattern_detector,
        risk_manager
    ) -> Dict:
        """
        Execute backtest over date range.
        
        Purpose:
            Simulate strategy day-by-day with proper position management.
            The order of operations is CRITICAL for accurate results.
        
        Algorithm (POSITIONS-FIRST APPROACH):
            a. Update existing positions with current prices
            b. Check exit conditions for all positions
            c. Update portfolio metrics (P&L, cash, drawdown)
            d. Scan all symbols for pattern matches
            e. Generate entry signals from patterns
            f. Check risk management constraints
            g. Execute entries (only if risk checks pass)
            h. Calculate final performance metrics
        
        Args:
            symbols: List of tickers to backtest
            start_date: Backtest start date
            end_date: Backtest end date
            pattern_detector: Pattern recognition instance
            risk_manager: Risk management instance
            
        Returns:
            Dict with performance metrics and trade history
        """
        current_date = start_date
        
        # Main backtest loop - iterate day by day
        while current_date <= end_date:
            # Get market data for all symbols on this date
            market_data = self._fetch_market_data(symbols, current_date)
            
            # ===================================================================
            # STEP A: Update existing positions with current prices
            # ===================================================================
            # WHY FIRST: We need current position values for exit checks
            #            and portfolio metrics calculations
            for symbol, position in self.positions.items():
                if symbol in market_data:
                    current_price = market_data[symbol]['close']
                    position.update_price(current_price, current_date)
            
            # ===================================================================
            # STEP B: Check exit conditions for ALL positions
            # ===================================================================
            # WHY BEFORE ENTRIES: Free up cash and position slots
            #                      before looking for new trades
            exit_signals = []
            for symbol, position in list(self.positions.items()):
                # Check stop-loss
                if position.current_price <= position.stop_loss:
                    exit_signals.append({
                        'symbol': symbol,
                        'reason': 'STOP_LOSS',
                        'price': position.current_price
                    })
                
                # Check take-profit target
                elif position.current_price >= position.take_profit:
                    exit_signals.append({
                        'symbol': symbol,
                        'reason': 'TAKE_PROFIT',
                        'price': position.current_price
                    })
                
                # Check pattern breakdown (exit signal)
                elif pattern_detector.check_exit_signal(symbol, market_data):
                    exit_signals.append({
                        'symbol': symbol,
                        'reason': 'SIGNAL',
                        'price': position.current_price
                    })
            
            # Execute all exits
            for exit_signal in exit_signals:
                self._execute_exit(
                    symbol=exit_signal['symbol'],
                    exit_price=exit_signal['price'],
                    exit_date=current_date,
                    reason=exit_signal['reason']
                )
            
            # ===================================================================
            # STEP C: Update portfolio metrics
            # ===================================================================
            # WHY NOW: After exits but before entries
            #          Gives us accurate cash available and position count
            total_position_value = sum(
                pos.current_value for pos in self.positions.values()
            )
            portfolio_value = self.cash + total_position_value
            
            # Track for equity curve and drawdown calculation
            self.equity_curve.append(portfolio_value)
            
            # Calculate current drawdown
            peak_value = max(self.equity_curve)
            current_drawdown = (peak_value - portfolio_value) / peak_value
            
            # ===================================================================
            # STEP D: Scan all symbols for pattern matches
            # ===================================================================
            # WHY AFTER POSITION MANAGEMENT: We know how many slots available
            pattern_matches = pattern_detector.scan_all_symbols(
                symbols=symbols,
                date=current_date,
                market_data=market_data
            )
            
            # ===================================================================
            # STEP E: Generate entry signals from patterns
            # ===================================================================
            entry_candidates = []
            for match in pattern_matches:
                # Only consider if pattern confidence above threshold
                if match['confidence'] >= 70:  # Could be constant
                    entry_candidates.append({
                        'symbol': match['symbol'],
                        'pattern': match['pattern_type'],
                        'entry_price': market_data[match['symbol']]['close'],
                        'confidence': match['confidence']
                    })
            
            # Sort by confidence (best opportunities first)
            entry_candidates.sort(key=lambda x: x['confidence'], reverse=True)
            
            # ===================================================================
            # STEP F: Check risk management constraints
            # ===================================================================
            # WHY CRITICAL: Prevent over-leverage, excessive risk
            approved_entries = []
            
            for candidate in entry_candidates:
                # Check #1: Do we have available position slots?
                if len(self.positions) >= self.max_positions:
                    break  # Portfolio full, no more entries today
                
                # Check #2: Calculate position size
                position_size = portfolio_value * self.max_position_size_pct
                shares = int(position_size / candidate['entry_price'])
                cost = shares * candidate['entry_price']
                
                # Check #3: Do we have enough cash?
                if cost > self.cash:
                    continue  # Skip this candidate, not enough cash
                
                # Check #4: Correlation check (avoid too many similar positions)
                if risk_manager.check_correlation_risk(
                    candidate['symbol'],
                    list(self.positions.keys())
                ):
                    continue  # Too correlated with existing positions
                
                # Check #5: Drawdown limit
                if current_drawdown > 0.20:  # Could be MAX_DRAWDOWN_LIMIT constant
                    break  # Stop trading if in significant drawdown
                
                # All checks passed - approve entry
                approved_entries.append({
                    'symbol': candidate['symbol'],
                    'shares': shares,
                    'entry_price': candidate['entry_price'],
                    'pattern': candidate['pattern']
                })
            
            # ===================================================================
            # STEP G: Execute approved entries
            # ===================================================================
            # WHY LAST: Only after all risk checks passed
            for entry in approved_entries:
                self._execute_entry(
                    symbol=entry['symbol'],
                    shares=entry['shares'],
                    entry_price=entry['entry_price'],
                    entry_date=current_date,
                    stop_loss_pct=INITIAL_STOP_LOSS_PCT  # From constants.py
                )
            
            # Move to next trading day
            current_date += timedelta(days=1)
        
        # ===================================================================
        # STEP H: Calculate final performance metrics
        # ===================================================================
        # After backtest completes, calculate all metrics
        final_metrics = self._calculate_performance_metrics()
        
        return {
            'metrics': final_metrics,
            'trades': self.trades,
            'equity_curve': pd.Series(self.equity_curve),
            'final_value': self.equity_curve[-1] if self.equity_curve else self.initial_capital
        }
    
    def _execute_entry(
        self,
        symbol: str,
        shares: int,
        entry_price: float,
        entry_date: date,
        stop_loss_pct: float
    ):
        """
        Execute position entry.
        
        Purpose:
            Open new position, update cash, track in portfolio.
        """
        cost = shares * entry_price
        stop_loss_price = entry_price * (1 - stop_loss_pct)
        
        # Create position
        position = Position(
            symbol=symbol,
            shares=shares,
            entry_price=entry_price,
            entry_date=entry_date,
            stop_loss=stop_loss_price,
            take_profit=entry_price * 1.20  # 20% target, could be constant
        )
        
        # Update portfolio
        self.positions[symbol] = position
        self.cash -= cost
        
        logger.info(
            f"ENTRY: {symbol} {shares} shares @ ${entry_price:.2f}",
            extra={'symbol': symbol, 'entry_date': entry_date}
        )
    
    def _execute_exit(
        self,
        symbol: str,
        exit_price: float,
        exit_date: date,
        reason: str
    ):
        """
        Execute position exit.
        
        Purpose:
            Close position, realize P&L, free up cash and position slot.
        """
        position = self.positions.pop(symbol)  # Remove from active positions
        
        # Calculate P&L
        proceeds = position.shares * exit_price
        profit_loss = proceeds - (position.shares * position.entry_price)
        profit_loss_pct = profit_loss / (position.shares * position.entry_price)
        
        # Update cash
        self.cash += proceeds
        
        # Record trade for history
        trade = Trade(
            symbol=symbol,
            entry_date=position.entry_date,
            entry_price=position.entry_price,
            exit_date=exit_date,
            exit_price=exit_price,
            shares=position.shares,
            profit_loss=profit_loss,
            profit_loss_pct=profit_loss_pct,
            exit_reason=reason
        )
        self.trades.append(trade)
        
        logger.info(
            f"EXIT: {symbol} {position.shares} shares @ ${exit_price:.2f} "
            f"({reason}) P&L: ${profit_loss:.2f} ({profit_loss_pct*100:.1f}%)"
        )
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
GET  /api/reports/ideas          # Download ideas.csv
GET  /api/reports/backtest/{id}  # Download backtest CSV
```

**Web Pages:**
- Dashboard (overview, recent scans, backtest results)
- Data Management (trigger updates, view status)
- Pattern Scanner (configure and run scans)
- Backtesting (configure strategy, run backtest, view results)
- Reports (download ideas.csv, backtest CSVs)

#### 3.2 Ideas CSV Writer

**Format:** CSV file with structured data for easy analysis in Excel or pandas

**Header Row:**
```csv
Timestamp,Symbol,Pattern,Price,Volume,RS,Confidence,Trade,Entry,StopLoss,TakeProfit,PositionSize,Rationale
```

**Example Data Row:**
```csv
2025-11-26 09:30:00,RELIANCE,VCP+TrendTemplate,2450.50,5200000,85,82,BUY,2455.00,2209.50,2945.00,10%,"Strong VCP with 3 contractions, volume declining on pullbacks. Meets all Trend Template criteria. Stage 2 advance."
```

**Field Descriptions:**
- **Timestamp:** Detection date and time (ISO format)
- **Symbol:** Stock ticker
- **Pattern:** Pattern type(s) detected (comma-separated if multiple)
- **Price:** Current close price
- **Volume:** Current volume
- **RS:** Mansfield Relative Strength score
- **Confidence:** Pattern confidence score (0-100)
- **Trade:** BUY or SELL recommendation
- **Entry:** Recommended entry price
- **StopLoss:** Stop-loss price
- **TakeProfit:** Take-profit target price
- **PositionSize:** Recommended position size (% of portfolio)
- **Rationale:** Text explanation (quoted to handle commas)

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
    H --> I[Append to Ideas CSV]
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

## Code Quality Standards

This project follows SOLID principles and clean architecture patterns as defined in our [Engineering Standards][def].

### SOLID Principles Application

**Single Responsibility Principle (SRP):**
- Each class has one reason to change
- Pattern recognizers focus only on pattern detection
- Data providers only fetch data
- Risk managers only handle risk logic

**Open/Closed Principle (OCP):**
- Pattern recognizers extend abstract base class
- New patterns added without modifying existing code
- Strategy pattern for entry/exit rules

**Liskov Substitution Principle (LSP):**
- All DataProvider implementations are interchangeable
- YahooFinanceProvider and ZerodhaProvider can substitute each other

**Interface Segregation Principle (ISP):**
- Focused interfaces (PatternRecognizer, DataProvider, RiskManager)
- Clients depend only on methods they use

**Dependency Inversion Principle (DIP):**
- High-level modules depend on abstractions (ABC classes)
- Database access through repository pattern
- Dependency injection for testability

### Clean Architecture Layers

```
┌─────────────────────────────────────────┐
│  Presentation Layer (FastAPI, Web UI)  │
├─────────────────────────────────────────┤
│  Business Logic Layer                   │
│  - Pattern Recognition                  │
│  - Backtesting Engine                   │
│  - Risk Management                      │
├─────────────────────────────────────────┤
│  Data Layer (Database, API Clients)    │
└─────────────────────────────────────────┘
```

**Dependency Rule:** Inner layers never depend on outer layers

### Code Style & Documentation

**Python Style:**
- Follow PEP 8 strictly
- Use `black` formatter (line length: 100)
- Use `flake8` for linting
- Use `mypy` for type checking

**Documentation Requirements:**
- Docstrings for all public classes and methods (Google style)
- Type hints throughout codebase
- Inline comments explain both - "what" and "why"
- Complex algorithms include complexity analysis

---

## Testing Strategy

Following the testing pyramid approach: heavy unit tests, moderate integration tests, minimal E2E tests.

### Testing Levels

#### Unit Tests
**Scope:** Individual functions and classes in isolation

**Coverage Target:** ≥80% branch coverage for new/changed code

**Characteristics:**
- Fast (entire suite runs in < 10 seconds)
- Deterministic (no flakiness)
- Isolated (no external dependencies, mock all I/O)

**What to Test:**
- Pattern recognition logic (each pattern detector)
- Indicator calculations (MA, RSI, MACD, Mansfield RS)
- Risk management rules (stop-loss calculations)
- Performance metrics calculations
- Data validation logic

#### Integration Tests
**Scope:** Multiple components working together

**What to Test:**
- Data ingestion → database storage → retrieval
- Indicator calculation pipeline (raw data → derived metrics)
- Pattern scanner → database → ideas.csv output
- Backtesting engine full flow

#### End-to-End Tests
**Scope:** Full user workflows via API/UI

**What to Test:**
- Complete backtest workflow (API call → results → CSV download)
- Daily batch processing job
- Ideas generation and retrieval

### Test Quality Principles

**From Engineering Standards:**
- Tests must be deterministic (no random failures)
- Use builders/factories for test data
- Avoid shared mutable state between tests
- Mock external systems (never hit real APIs in tests)
- Meaningful test names that describe behavior

### Continuous Testing

- All tests run on every commit (CI/CD)
- Pre-commit hooks run fast unit tests
- Code coverage tracked and reported
- Regression tests for every bug fix
- Property-based testing for critical algorithms (future)

---

## Security

Following OWASP ASVS Level 2 and CERT secure coding practices.

### Input Validation & Data Security

**All External Input is Untrusted:**
- User inputs from web forms
- API request parameters
- File uploads (CSV)
- Data from external APIs (Zerodha, Yahoo Finance)

**Validation Strategy:**
```python
from pydantic import BaseModel, Field, validator
from datetime import date

class BacktestRequest(BaseModel):
    """Validated backtest request model."""
    
    start_date: date = Field(..., description="Backtest start date")
    end_date: date
    strategy_name: str = Field(..., min_length=1, max_length=100, regex="^[a-zA-Z0-9_-]+$")
    symbols: list[str] = Field(..., min_items=1, max_items=100)
    
    @validator('end_date')
    def end_after_start(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v
    
    @validator('symbols', each_item=True)
    def valid_symbol(cls, v):
        if not v.isalnum() or len(v) > 20:
            raise ValueError(f'Invalid symbol format: {v}')
        return v.upper()
```

### SQL Injection Prevention

**Always use parameterized queries:**
```python
# ✅ GOOD - Parameterized query
results = session.execute(
    text("SELECT * FROM price_data WHERE symbol_id = :symbol_id"),
    {"symbol_id": symbol_id}
)

# ✅ GOOD - ORM (automatically parameterizes)
results = session.query(PriceData).filter_by(symbol_id=symbol_id).all()
```

### Secrets Management

**Never commit secrets to version control:**
- API keys, access tokens, database passwords stored in `.env`
- `.env` file in `.gitignore`
- Use environment variables for all sensitive configuration

**Example .env structure:**
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/securities_research
ZERODHA_API_KEY=your_api_key_here
ZERODHA_ACCESS_TOKEN=your_access_token_here
SECRET_KEY=generate_random_secret_key_here
DEBUG=False
```

### Logging Security & Privacy

**Structured JSON Logging:**
```python
import logging
from pythonjsonlogger import jsonlogger

# Configure JSON logging
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(handler)
```

**Never Log:**
- Passwords, API keys, tokens
- Full credit card numbers
- Social security numbers
- Personally Identifiable Information (PII) without hashing

**Example:**
```python
# ❌ BAD
logger.info(f"User logged in with password: {password}")

# ✅ GOOD
logger.info("User logged in", extra={"user_id": user_id})
```

### API Security

**Rate Limiting:**
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/backtest/run")
@limiter.limit("10/minute")  # Max 10 backtests per minute per IP
async def run_backtest(request: BacktestRequest):
    pass
```
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

## CI/CD Pipeline

Automated testing, linting, and security scanning on every commit.

### Pre-Commit Hooks

**Install pre-commit framework:**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=100]
        
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: detect-private-key  # Prevent committing secrets
```

### CI Pipeline Stages

1. **Lint & Format Check** - Code style validation
2. **Type Checking** - Static type analysis with mypy
3. **Unit Tests** - Fast isolated tests
4. **Integration Tests** - Component interaction tests
5. **Coverage Check** - Enforce ≥80% coverage
6. **Security Scanning** - SAST (Static Application Security Testing)
7. **Dependency Scanning** - Vulnerable dependencies check

### Deployment Strategy (Future)

**For MVP:** Manual deployment to localhost

**Post-MVP:**
- Blue/green deployment for zero-downtime
- Automated rollback on error rate spike
- Database migrations via Alembic

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
│   └── ideas.csv
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
## Monitoring & Observability

### Logging
- Structured logging (JSON)
- Log rotation
- Log aggregation (ELK stack)

### Metrics
- Application metrics (CPU, memory, etc.)
- Database metrics
- Custom metrics (backtest performance, etc.)

### Tracing
- Distributed tracing (future consideration)

### Alerts
- Critical alerts (e.g., high CPU usage)
- Performance alerts (e.g., slow queries)

### Observability Stack (Future)
- ELK stack for log aggregation
- Prometheus for metrics
- Grafana for dashboards
- Jaeger for distributed tracing

## Error Handling & Resilience

**Purpose:**  
Build a fault-tolerant system that gracefully handles failures, provides meaningful feedback, and automatically recovers from transient issues.

### Graceful Error Handling Patterns

#### 1. Try-Except with Context Preservation

```python
from backend.core.constants import API_TIMEOUT_SECONDS
import logging

logger = logging.getLogger(__name__)

def fetch_data_with_error_handling(symbol: str, start_date: date, end_date: date) -> pd.DataFrame:
    """
    Fetch historical data with comprehensive error handling.
    
    Purpose:
        Demonstrate proper error handling that preserves context,
        logs appropriately, and provides user-friendly messages.
        
    Args:
        symbol: Stock ticker to fetch
        start_date: Start date for data
        end_date: End date for data
        
    Returns:
        DataFrame with OHLCV data
        
    Raises:
        DataFetchError: If data cannot be retrieved after all attempts
        ValidationError: If symbol format is invalid
    """
    try:
        data = data_provider.fetch_historical(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            timeout=API_TIMEOUT_SECONDS  # From constants.py
        )
        return data
        
    except TimeoutError as e:
        # Log with context for debugging
        logger.error(
            "Data fetch timeout",
            extra={
                "symbol": symbol,
                "timeout_seconds": API_TIMEOUT_SECONDS,
                "error": str(e)
            }
        )
        # Raise custom exception with user-friendly message
        raise DataFetchError(
            f"Unable to fetch data for {symbol} - service timeout. Please try again."
        ) from e
        
    except APIRateLimitError as e:
        logger.warning(
            "API rate limit exceeded",
            extra={"symbol": symbol, "retry_after": e.retry_after}
        )
        raise DataFetchError(
            f"Rate limit exceeded. Please wait {e.retry_after} seconds."
        ) from e
        
    except ValueError as e:
        logger.error("Invalid symbol format", extra={"symbol": symbol})
        raise ValidationError(f"Invalid symbol: {symbol}") from e
        
    except Exception as e:
        # Catch-all for unexpected errors
        logger.exception(
            "Unexpected error during data fetch",
            extra={"symbol": symbol}
        )
        raise DataFetchError(
            f"Unexpected error fetching data for {symbol}"
        ) from e
```

#### 2. Custom Exception Hierarchy

```python
class SecuritiesResearchError(Exception):
    """
    Base exception for all application-specific errors.
    
    Purpose:
        Allows catching all application errors with single except clause.
        Distinguishes our errors from library/system errors.
    """
    pass

class DataError(SecuritiesResearchError):
    """Base class for data-related errors."""
    pass

class DataFetchError(DataError):
    """Failed to fetch data from external provider."""
    pass

class DataValidationError(DataError):
    """Data failed validation checks (integrity, format)."""
    pass

class PatternDetectionError(SecuritiesResearchError):
    """Error during pattern recognition."""
    pass

class BacktestError(SecuritiesResearchError):
    """Error during backtest execution."""
    pass

class RiskManagementError(SecuritiesResearchError):
    """Risk constraint violation."""
    pass
```

### Retry Logic for Transient Failures

#### Exponential Backoff with Jitter

```python
import time
import random
from backend.core.constants import (
    API_RETRY_MAX_ATTEMPTS,
    API_RETRY_BACKOFF_SECONDS
)

def fetch_with_retry(
    symbol: str, 
    max_attempts: int = API_RETRY_MAX_ATTEMPTS
) -> pd.DataFrame:
    """
    Fetch data with automatic retry on transient failures.
    
    Purpose:
        Handle temporary network issues and API hiccups without
        overwhelming the service with rapid retries.
    
    Retry Strategy:
        Exponential backoff: 1s, 2s, 4s (doubles each attempt)
        Jitter: Random 0-10% added to prevent thundering herd
        
    Args:
        symbol: Stock ticker to fetch
        max_attempts: Maximum retry attempts (from constants.py)
        
    Returns:
        DataFrame with price data
        
    Raises:
        DataFetchError: If all retries exhausted
    """
    for attempt in range(max_attempts):
        try:
            return data_provider.fetch_historical(symbol)
            
        except (TimeoutError, ConnectionError) as e:
            if attempt == max_attempts - 1:
                # Last attempt failed, give up
                logger.error(
                    f"All {max_attempts} attempts failed for {symbol}",
                    extra={"symbol": symbol, "last_error": str(e)}
                )
                raise DataFetchError(
                    f"Failed to fetch {symbol} after {max_attempts} attempts"
                ) from e
            
            # Calculate backoff: 1s, 2s, 4s (exponential)
            backoff = API_RETRY_BACKOFF_SECONDS * (2 ** attempt)
            # Add jitter to prevent all clients retrying simultaneously
            jitter = random.uniform(0, 0.1 * backoff)
            sleep_duration = backoff + jitter
            
            logger.warning(
                f"Fetch failed for {symbol}, retrying in {sleep_duration:.1f}s",
                extra={
                    "attempt": attempt + 1,
                    "max_attempts": max_attempts,
                    "backoff_seconds": sleep_duration
                }
            )
            
            time.sleep(sleep_duration)
```

### Circuit Breaker Pattern

**Purpose:** Stop sending requests to failing service, allow it to recover

```python
from datetime import datetime, timedelta
from backend.core.constants import (
    API_RETRY_MAX_ATTEMPTS,
    DATA_INGESTION_RETRY_DELAY_SECONDS
)

class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures.
    
    Purpose:
        When external service fails repeatedly, stop hammering it.
        Give it time to recover, then test with single request.
    
    States:
        CLOSED: Normal operation, all requests allowed
        OPEN: Service down, fail fast without calling
        HALF_OPEN: Testing if service recovered
    
    Usage:
        breaker = CircuitBreaker(failure_threshold=5, timeout_seconds=300)
        result = breaker.call(api_client.fetch, symbol='AAPL')
    """
    
    def __init__(self, failure_threshold: int = 5, timeout_seconds: int = 300):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Open circuit after this many failures
            timeout_seconds: Wait this long before testing recovery
        """
        self.failure_threshold = failure_threshold
        self.timeout = timedelta(seconds=timeout_seconds)
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"
    
    def call(self, func, *args, **kwargs):
        """
        Execute function through circuit breaker.
        
        Purpose:
            Protect against calling failing service repeatedly.
        """
        if self.state == "OPEN":
            # Check if timeout period has passed
            if datetime.now() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
                logger.info("Circuit breaker entering HALF_OPEN state (testing recovery)")
            else:
                # Still in timeout period, fail fast
                raise ServiceUnavailableError(
                    "Circuit breaker OPEN - service unavailable. "
                    f"Retry after {self.timeout.total_seconds()}s"
                )
        
        try:
            result = func(*args, **kwargs)
            # Success! Reset circuit breaker
            if self.failure_count > 0:
                logger.info(
                    f"Circuit breaker reset after recovery",
                    extra={"previous_failures": self.failure_count}
                )
            self.failure_count = 0
            self.state = "CLOSED"
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                logger.error(
                    f"Circuit breaker OPENED after {self.failure_count} failures",
                    extra={"timeout_seconds": self.timeout.total_seconds()}
                )
            
            raise

# Usage example
zerodha_breaker = CircuitBreaker(
    failure_threshold=API_RETRY_MAX_ATTEMPTS,
    timeout_seconds=DATA_INGESTION_RETRY_DELAY_SECONDS
)

def fetch_zerodha_data(symbol: str) -> pd.DataFrame:
    """Fetch data through circuit breaker for resilience."""
    return zerodha_breaker.call(zerodha_client.fetch_historical, symbol)
```

### User-Friendly Error Messages

#### Mapping Technical Errors to User Messages

```python
def get_user_friendly_error_message(error: Exception) -> str:
    """
    Convert technical exceptions to actionable user messages.
    
    Purpose:
        Users don't care about stack traces. Give them:
        - What went wrong (in plain English)
        - What they can do about it
        - When to contact support
    
    Args:
        error: Exception that occurred
        
    Returns:
        User-friendly error message
    """
    error_messages = {
        DataFetchError: (
            "Unable to load market data. "
            "Please check your internet connection and try again."
        ),
        APIRateLimitError: (
            "Too many requests. Please wait a moment and try again."
        ),
        DataValidationError: (
            "Data quality issue detected. "
            "This may be due to incomplete or corrupted data. "
            "Please contact support if this persists."
        ),
        PatternDetectionError: (
            "Pattern analysis failed. "
            "Try scanning fewer symbols or adjusting pattern parameters."
        ),
        BacktestError: (
            "Backtest execution failed. "
            "Please check your parameters and try again."
        ),
        RiskManagementError: (
            "Risk constraint violation. "
            "Position size or portfolio limits exceeded."
        ),
    }
    
    error_type = type(error)
    default_message = (
        "An unexpected error occurred. "
        "Please try again or contact support if the problem persists."
    )
    
    return error_messages.get(error_type, default_message)


# API error response example
from fastapi import HTTPException
from fastapi.responses import JSONResponse

@app.exception_handler(DataFetchError)
async def data_fetch_error_handler(request, exc):
    """
    Convert DataFetchError to user-friendly API response.
    
    Purpose:
        Return structured error with actionable message.
    """
    return JSONResponse(
        status_code=503,  # Service Unavailable
        content={
            "error": "data_fetch_failed",
            "message": get_user_friendly_error_message(exc),
            "retry_after": 60,  # Suggest retry after 60s
            "support_email": "support@example.com"
        }
    )
```

### Error Logging Best Practices

#### Structured Logging with Context (No Secrets)

```python
import traceback

def log_error_with_context(error: Exception, context: dict):
    """
    Log errors with full context for debugging.
    
    Purpose:
        Capture enough information to debug production issues
        without exposing sensitive data in logs.
    
    Args:
        error: Exception that occurred
        context: Additional context (symbol, dates, user_id, etc.)
    """
    # CRITICAL: Never log passwords, API keys, tokens
    safe_context = {
        k: v for k, v in context.items()
        if k not in ['password', 'api_key', 'token', 'secret', 'access_token']
    }
    
    logger.error(
        "Operation failed",
        extra={
            "error_type": type(error).__name__,
            "error_message": str(error),
            "stack_trace": traceback.format_exc(),
            **safe_context
        },
        exc_info=True  # Include full exception info
    )

# Example usage
try:
    result = process_symbol(symbol='RELIANCE')
except PatternDetectionError as e:
    log_error_with_context(
        error=e,
        context={
            "symbol": "RELIANCE",
            "pattern_type": "VCP",
            "date": "2025-01-15"
            # Note: No API keys or secrets in context
        }
    )
    raise
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
- ideas.csv writer and viewer
- CSV report generator
- Job scheduling for daily updates
- Documentation (user guide, API docs)

**Acceptance Criteria:**
- ✅ All web pages functional
- ✅ User can trigger scans and backtests via UI
- ✅ ideas.csv generated in correct CSV format
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

## Performance Optimization Strategies

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

## Documentation Requirements

### Code Documentation
- **Docstrings:** All public classes and methods (Google style)
- **Type Hints:** Throughout codebase (enforced by mypy)
- **Inline Comments:** Explain "what" and "why" - especially for complex algorithms
- **Complexity Analysis:** For performance-critical algorithms

### Architecture Documentation

**C4 Model Diagrams:**
- Context diagram (system in environment)
- Container diagram (web app, database, external APIs) - Already included in this TDD
- Component diagram (major modules within backend)
- Keep diagrams up-to-date with changes

**Architecture Decision Records (ADRs):**  
Document significant architectural decisions using ADR format:

```markdown
# ADR-001: Use PostgreSQL with TimescaleDB for Time-Series Data

## Status
Accepted

## Context
Need to store 5M+ rows of OHLCV data with efficient querying.

## Decision
Use PostgreSQL with TimescaleDB extension.

## Consequences
+ Optimized for time-series queries
+ Mature ecosystem
+ Scales to millions of rows
- Requires PostgreSQL (can't use MySQL/SQLite)
- Learning curve for TimescaleDB-specific features
```

### User Documentation

**README.md:**
- Project overview
- **How to run locally** (step-by-step setup instructions)
- Technology stack
- Project structure
- Quick start guide

**User Manual:**
- Guide to using the web UI
- Understanding ideas.csv output
- Interpreting backtest results
- Configuration options

**Troubleshooting Guide:**
- Common errors and solutions
- Database connection issues
- API rate limit handling
- Performance tuning tips

### Operational Documentation

**Runbooks:**  
Standard operating procedures for:
- Daily data update process
- Database backup and restore
- Handling pattern detection failures
- Performance degradation response

**Example Runbook Entry:**
```markdown
## Runbook: Daily Data Update Failure

### Symptoms
- No new data in database for current date
- Error logs showing API timeout

### Diagnosis
1. Check logs/application.log for errors
2. Verify Zerodha/Yahoo Finance API status
3. Check internet connectivity

### Resolution
1. If API rate limit: Wait and retry
2. If network issue: Fix network, re-run ingestion script
3. If data provider outage: Wait for service restoration
4. Manual re-run: `python scripts/data_ingestion.py --date YYYY-MM-DD`
```

### Technical Documentation

- **This TDD:** Architecture overview
- **Database Schema Documentation:** Entity-relationship diagrams, table constraints
- **API Documentation:** Auto-generated via FastAPI (OpenAPI/Swagger)
- **Algorithm Explanations:** Detailed docs for VCP detection, Trend Template logic, etc.

---

## Version Control & Collaboration

### Git Workflow

**Branching Strategy:**
- `main` branch: Production-ready code
- `develop` branch: Integration branch for features
- Feature branches: `feature/pattern-vcp-detector`
- Bugfix branches: `bugfix/indicator-calculation-error`
- Hotfix branches: `hotfix/security-patch-001`

**Branch Naming:**
- Use descriptive names
- Include ticket/issue number if applicable: `feature/PROJ-123-add-double-bottom-pattern`

### Commit Messages

**Format: Conventional Commits**
```
<type>(<scope>): <short description>

<optional longer description>

<optional footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `docs`: Documentation changes
- `chore`: Build/tooling changes

**Examples:**
```
feat(patterns): add VCP detector with configurable tolerance

fix(indicators): correct Mansfield RS calculation for edge case

refactor(backtesting): extract position management into separate class
```

### Code Review Process

**Mandatory for all production code:**
- All pull requests require at least 1 approval
- Review checklist:
  - [ ] Code follows style guide (black, flake8 pass)
  - [ ] Tests added/updated (coverage ≥80%)
  - [ ] Documentation updated
  - [ ] No security vulnerabilities introduced
  - [ ] Performance acceptable

**Focus Areas:**
- Correctness of logic
- Security implications
- Test coverage and quality
- Readability and maintainability
- (Linters handle pure style)

### Trunk-Based Development (Future)

**For MVP:** Feature branches merged to main

**Post-MVP:** Short-lived feature branches (<2 days), frequent integration, feature flags for incomplete features

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
| 1.0 | 2025-11-26 | Development Team | Initial draft |
| 1.1 | 2025-11-27 | Development Team | Aligned with updated PRD (ideas.csv format, performance targets); Added Engineering Standards compliance sections (Code Quality, Testing Strategy ≥80% coverage, Security OWASP Level 2, CI/CD Pipeline); Enhanced Monitoring & Observability (SLIs/SLOs); Expanded Documentation Requirements (ADRs, runbooks, C4 diagrams); Added Version Control best practices; Enhanced code examples with type hints and docstrings |

---

**Next Steps:**
1. Review and approve this Technical Design Document
2. Set up development environment
3. Begin Phase 1: Data Infrastructure
4. Weekly progress reviews and iterative refinement


[def]: file:///c:/Users/deepa/Desktop/SecuritiesResearchTool/SecuritiesResearchTool/Standards/Engineering%20Standards.md