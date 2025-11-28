# Data Model

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