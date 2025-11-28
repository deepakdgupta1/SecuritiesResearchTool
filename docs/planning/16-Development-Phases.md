# Development Phases
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
