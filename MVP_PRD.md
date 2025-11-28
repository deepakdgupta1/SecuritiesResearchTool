# MVP Product Requirements Document (PRD)
## Securities Research Tool - Pattern Recognition & Backtesting Platform

**Version:** 1.0  
**Date:** November 26, 2025  
**Status:** Draft for Review

---

## Executive Summary

### Vision
Build a systematic securities research platform to identify high-probability investment opportunities using Mark Minervini's SEPA (Specific Entry Point Analysis) methodology and validate its effectiveness through rigorous backtesting.

### Primary Objective
Validate whether Mark Minervini's SEPA methodology generates supernormal profits over time by analyzing 20 years of historical price data across Indian and US equity markets.

### Success Criteria
The system must be able to identify, at any point in time, which securities are worth investing in with good chances of generating profit in the near future, based on proven chart patterns and technical analysis.

---

## Market & User Context

### Target User
- **Profile:** Individual trader/investor with knowledge of technical analysis
- **Use Case:** Research-driven investment decision making
- **Need:** Systematic, data-driven approach to identify growth stocks using proven methodologies

### Market Coverage
- **Geography:** India (NSE/BSE), United States (NYSE/NASDAQ)
- **Asset Class:** Equities/Stocks only
- **Universe Size:** ~10,000 securities
- **Historical Data:** 20 years, daily granularity (~5 million data rows)

---

## Core Features

### 1. Data Management

#### 1.1 Data Acquisition
- **Indian Market:** Integration with Zerodha API for NSE/BSE historical data
- **US Market:** Integration with Yahoo Finance (yfinance) for NYSE/NASDAQ data
- **Granularity:** Daily OHLCV (Open, High, Low, Close, Volume)
- **Historical Depth:** 20 years of historical data
- **Data Refresh:** Batch processing mode (overnight updates)

#### 1.2 Data Storage
- Store and manage 5+ million rows of historical price data
- Efficient querying for pattern recognition across entire universe
- Support for derived metrics (moving averages, RS calculations, etc.)

### 2. Pattern Recognition Engine

#### 2.1 Mark Minervini's Trend Template
Automated detection of stocks meeting ALL criteria:
- Stock price > 150-day MA AND > 200-day MA
- 150-day MA > 200-day MA
- 200-day MA trending upward for ≥1 month
- 50-day MA > 150-day MA AND > 200-day MA
- Stock price > 130% of 52-week low (30% above)
- Stock price ≥ 75% of 52-week high (within 25%)
- Relative Strength (RS) rating > 70

#### 2.2 Chart Pattern Detection
Automated identification of:
- **Volatility Contraction Pattern (VCP)**
  - 2-4 pullback contractions
  - Each pullback shallower than previous
  - Volume contraction during pullbacks
  - 20% tolerance for pattern matching
  
- **Cup with Handle**
- **Double Bottom**
- **High-Tight Bull Flag (Power Play)**

#### 2.3 Weinstein Stage Analysis
Classify individual stocks into market stages:
- **Stage 1:** Base/Accumulation
- **Stage 2:** Advancing/Mark-up
- **Stage 3:** Top/Distribution
- **Stage 4:** Decline/Mark-down

#### 2.4 Technical Indicators
Calculate and track:
- **Moving Averages:** EMA (Exponential), 50/150/200-day for daily, 10/30/40-week for weekly
- **Momentum:** MACD, RSI
- **Volume:** Volume trends and anomalies
- **Relative Strength:** Mansfield RS (Stock price / Market index, smoothed)

#### 2.5 Multiple Timeframe Analysis
- Primary analysis on daily data
- Derived weekly and monthly views from daily data
- Different MA periods for different timeframes

### 3. Backtesting Engine

#### 3.1 Systematic Scanning (Scenario A - MVP)
1. Scan all securities daily (historical simulation)
2. Identify stocks meeting pattern criteria (e.g., Trend Template + VCP)
3. Generate trade recommendations with entry/exit rules
4. Log recommendations to `ideas.csv` alongwith date and time of logging
5. Track simulated performance over time
6. Generate performance metrics

#### 3.2 Trading Strategy Support
- **Position Types:** Long and short positions
- **Strategy Types:** Trend following, mean reversion, breakout
- **Analysis Scope:** Single security backtests (not portfolio-based)
- **Entry/Exit Complexity:** Support for complex, multi-condition rules

#### 3.3 Risk Management

**Stop-Loss Logic:**
- Initial fixed stop: 10% from entry
- Transition to trailing stop once position up X% (X to be determined)

**Take-Profit Logic:**
- Hybrid approach: Initial predetermined target
- Trailing stop for remainder of position

**Portfolio-Level Controls:**
- Maximum position size as % of total capital (configurable, e.g., 10%)
- Maximum number of concurrent positions
- Total portfolio drawdown limit (stop new positions if portfolio down X%)

#### 3.4 Performance Metrics
Generate comprehensive analytics:

**Returns:**
- Total Return
- Annualized Return
- CAGR (Compound Annual Growth Rate)

**Risk Metrics:**
- Sharpe Ratio
- Sortino Ratio
- Maximum Drawdown

**Trading Metrics:**
- Win Rate (% profitable trades)
- Profit Factor (Gross Profit / Gross Loss)

### 4. Ideas Log & Alerts

#### 4.1 Pattern Detection Logging
When a pattern is detected, append to `ideas.csv` with:
- **Symbol:** Ticker/Symbol
- **Date:** Detection timestamp
- **Pattern Type:** Which pattern(s) detected
- **Key Metrics:** Current price, volume, Mansfield RS
- **Confidence Score:** Pattern match quality (0-100)
- **Recommended Trade:** BUY or SELL
- **Entry Rules:** Specific entry price/conditions
- **Exit Rules:** Stop-loss and take-profit levels
- **Rationale:** Why this pattern/setup is significant

#### 4.2 Manual Confirmation
- Automated detection with manual review for refinement
- User can review ideas.csv to validate or dismiss suggestions

### 5. Reporting & Visualization

#### 5.1 Export Formats
- **Primary:** CSV files for pattern detections and backtest results
- **Ideas:** CSV format with structured data

#### 5.2 Charting (Future)
- Interactive charting: Out of scope for MVP
- Current MVP: Data-driven CSV outputs

---

## User Interface & Experience

### Platform Type
- **Web Application:** Browser-based interface
- **Deployment:** Local installation (localhost)
- **Users:** Single user, no authentication required

### Key User Workflows

#### Workflow 1: Historical Pattern Scan
1. User specifies date range for historical scan
2. System scans all securities for selected date
3. System identifies pattern matches
4. Results logged to `ideas.csv` with full details
5. User reviews log for investment ideas

#### Workflow 2: Backtest Strategy Validation
1. User configures strategy parameters (patterns, indicators, rules)
2. System runs historical simulation across entire universe
3. System generates trades based on rules
4. System calculates performance metrics
5. Results exported to CSV for analysis

#### Workflow 3: Data Refresh
1. User initiates data update (manual trigger)
2. System fetches latest data from Zerodha and Yahoo Finance
3. System updates database with new daily bars
4. Confirmation of successful update

---

## Technical Requirements

### Non-Functional Requirements

#### Performance
- **Batch Processing:** Overnight processing acceptable
- **Throughput:** Scan 10,000 securities within reasonable time (minutes, not hours)
- **Data Volume:** Handle 5+ million rows efficiently

#### Scalability
- Architecture should support future expansion to real-time processing
- Database design should accommodate growing historical data

#### Reliability
- Graceful error handling for API failures
- Data validation to ensure data quality
- Audit trail for all pattern detections and trades

#### Usability
- Clear, intuitive web interface
- Understandable CSV outputs
- Well-structured ideas.csv for easy parsing

### Technology Stack
- **Language:** Open to recommendation (Python highly suitable given data science libraries)
- **Database:** Open to recommendation (consider time-series or relational DB)
- **Web Framework:** Open to recommendation
- **Deployment:** Local installation

---

## Out of Scope (MVP)

The following features are explicitly **NOT** part of the MVP:

### Advanced Features
- Position sizing optimization
- Pyramid/scale-in/out capabilities
- Parameter optimization
- Walk-forward testing
- Monte Carlo simulation
- Slippage modeling
- Commission/brokerage fee modeling
- Market impact modeling
- Gap handling (overnight/weekend)

### UI/UX Features
- Interactive charting with annotations
- Drag-and-drop capabilities
- Visual strategy builder
- Scripting interface for advanced users
- Comparative analysis dashboards

### Integration & Collaboration
- TradingView integration
- Excel integration
- Multi-user support
- User authentication
- Collaboration features
- Cloud deployment
- Import/Export to external systems

### Data Features
- Intraday data (1min, 5min, 15min, hourly)
- Real-time data streaming
- Options, futures, forex, commodities, cryptocurrencies

---

## Success Metrics

### Quantitative Metrics
1. **Coverage:** Successfully analyze 100% of securities in target universe
2. **Historical Depth:** Access and process 20 years of historical data
3. **Pattern Detection:** Identify measurable occurrences of each pattern type
4. **Backtest Completion:** Generate complete performance metrics for SEPA strategy

### Qualitative Metrics
1. **Insight Quality:** Does the system identify historically profitable setups?
2. **SEPA Validation:** Does backtesting confirm or refute Minervini's methodology?
3. **Usability:** Can user effectively use ideas.csv to make investment decisions?

### Acceptance Criteria
- ✅ System successfully loads 20 years of daily data for Indian and US markets
- ✅ Pattern detection engine identifies all specified patterns with acceptable accuracy
- ✅ Backtesting engine simulates trades and calculates all specified metrics
- ✅ Ideas.csv provides actionable investment ideas with clear rationale
- ✅ Performance metrics demonstrate whether SEPA methodology outperforms market

---

## Assumptions & Dependencies

### Assumptions
- Zerodha API provides sufficient historical data and rate limits
- Yahoo Finance data quality is acceptable for backtesting
- User has basic understanding of technical analysis and Minervini's methodology
- User can interpret CSV outputs and ideas.csv entries

### Dependencies
- Zerodha API access and credentials
- Internet connectivity for data fetching
- Local compute resources sufficient for batch processing

### Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Data provider API changes/limits | Medium | High | Abstract data layer; support multiple providers |
| Pattern detection accuracy varies | High | Medium | Configurable tolerance; manual confirmation workflow |
| Large data volume performance issues | Medium | Medium | Optimize database queries; incremental processing |
| Interpretation of Minervini criteria ambiguous | Medium | Medium | Clear documentation; iterative refinement with user |

---

## Timeline & Phasing

### MVP Development Phases
1. **Phase 1:** Data infrastructure and ingestion
2. **Phase 2:** Pattern recognition engine
3. **Phase 3:** Backtesting engine
4. **Phase 4:** Web UI and reporting
5. **Phase 5:** Integration testing and validation

### Post-MVP Roadmap
- **v2.0:** Interactive charting and visual analysis
- **v3.0:** Advanced backtesting (optimization, walk-forward, Monte Carlo)
- **v4.0:** Real-time scanning and alerts
- **v5.0:** Portfolio management and position sizing

---

## Glossary

- **SEPA:** Specific Entry Point Analysis - Minervini's methodology for identifying growth stocks
- **VCP:** Volatility Contraction Pattern - Chart pattern showing decreasing volatility before breakout
- **RS:** Relative Strength - Performance of stock vs. market benchmark
- **Mansfield RS:** Relative Strength calculation (Stock/Index, smoothed)
- **OHLCV:** Open, High, Low, Close, Volume - Standard price bar data
- **CAGR:** Compound Annual Growth Rate
- **Drawdown:** Peak-to-trough decline in portfolio value

---

## Approval & Sign-off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Product Owner | [User] | | |
| Technical Lead | [TBD] | | |

---

**Next Steps:**
1. Review and approve this PRD
2. Review High Level Technical Design Document
3. Refine requirements based on feedback
4. Proceed to detailed technical design and implementation planning
