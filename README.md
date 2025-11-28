# Securities Research Tool

A comprehensive, automated securities analysis platform designed to validate Mark Minervini's SEPA (Specific Entry Point Analysis) methodology through data-driven pattern recognition and systematic backtesting.

---

## 🎯 Project Vision

This tool integrates **20 years of historical market data**, **advanced pattern recognition**, and **systematic backtesting** to answer a critical question: **Does Mark Minervini's SEPA methodology generate supernormal profits over time?**

The platform analyzes ~10,000 securities across Indian (NSE/BSE) and US (NYSE/NASDAQ) markets to identify high-probability investment opportunities using proven chart patterns and technical analysis.

---

## 🚀 Key Features

### 📊 Automated Data Management
- **Market Coverage**: India (via Zerodha API) and US (via Yahoo Finance)
- **Historical Depth**: 20 years of daily OHLCV data (~5 million rows)
- **Efficient Storage**: PostgreSQL with TimescaleDB for time-series optimization
- **Batch Processing**: Overnight data updates and metric calculations

### 🔍 Advanced Pattern Recognition
- **Trend Template**: Automated detection of Minervini's 8-point Stage 2 criteria
- **Chart Patterns**:
  - **Volatility Contraction Pattern (VCP)**: Detects 2-4 contractions with decreasing volatility
  - **Cup with Handle**: Classic continuation pattern
  - **Double Bottom**: Reversal pattern identification
  - **High-Tight Bull Flag**: Power play detection
- **Weinstein Stage Analysis**: Classify stocks into 4 market stages (Base, Advance, Top, Decline)
- **Mansfield Relative Strength**: Identify market leaders outperforming the index
- **Multiple Timeframes**: Daily, weekly, and monthly analysis

### 🧪 Systematic Backtesting Engine
- **Positions-First Algorithm**: Accurately simulates trading by managing existing positions before new entries
- **Risk Management**:
  - Hybrid stop-loss: 10% fixed initial, transitioning to trailing stop
  - Portfolio-level controls: Position sizing, max concurrent positions, drawdown limits
- **Performance Metrics**: Sharpe Ratio, Sortino Ratio, Max Drawdown, CAGR, Win Rate, Profit Factor
- **Trade Logging**: All recommendations logged to `ideas.csv` with entry/exit rules and rationale

### 📈 Ideas Generation
Automated pattern detection appends to `ideas.csv` with:
- Symbol, detection date, pattern type
- Key metrics (price, volume, Mansfield RS)
- Confidence score (0-100)
- Recommended trade (BUY/SELL) with specific entry/exit rules
- Detailed rationale for the setup

---

## 📚 Documentation

The technical documentation is organized into a modular 20-file structure within the `docs/` directory:

### 🏗️ Architecture
- [**TDD Overview**](docs/architecture/00-TDD-Overview.md) - Master index and document control
- [**System Architecture**](docs/architecture/01-System-Architecture.md) - High-level design, layered architecture, and component interaction
- [**Technology Stack**](docs/architecture/02-Technology-Stack.md) - Tech choices, pricing analysis, and performance targets
- [**Data Model**](docs/architecture/03-Data-Model.md) - Database schema, table design, and data flow

### 🎨 Design
- [**Component Design**](docs/design/04-Component-Design.md) - Detailed class and module design (Data Providers, Pattern Recognizers, Backtesting Engine)
- [**Algorithms & Logic**](docs/design/05-Algorithms-And-Logic.md) - Core algorithms (Mansfield RS, VCP Detection, Trend Template, Performance Metrics)
- [**API Integration Design**](docs/design/06-API-Integration-Design.md) - Zerodha and Yahoo Finance integration, internal REST API design
- [**Processing Pipelines**](docs/design/07-Processing-Pipelines.md) - Daily batch processing and backtesting workflows

### ⚡ Quality Assurance
- [**Code Quality Standards**](docs/quality/08-Code-Quality-Standards.md) - SOLID principles, style guides, and best practices
- [**Testing Strategy**](docs/quality/09-Testing-Strategy.md) - Unit, integration, and end-to-end testing approach
- [**Security**](docs/quality/10-Security.md) - OWASP compliance, input validation, secrets management, and data protection
- [**CI/CD Pipeline**](docs/quality/11-CI-CD-Pipeline.md) - Automation, testing, and deployment pipelines

### ⚙️ Operations
- [**Deployment**](docs/operations/12-Deployment.md) - Local setup, environment configuration, and installation
- [**Monitoring & Observability**](docs/operations/13-Monitoring-Observability.md) - Structured logging, error handling, metrics, and alerting
- [**Documentation Requirements**](docs/operations/14-Documentation-Requirements.md) - ADRs, runbooks, and documentation standards
- [**Version Control**](docs/operations/15-Version-Control.md) - Git workflow, branching strategy, and collaboration

### 📅 Planning
- [**Development Phases**](docs/planning/16-Development-Phases.md) - 6-phase implementation roadmap with acceptance criteria
- [**Risks & Mitigations**](docs/planning/17-Risks-And-Mitigations.md) - Risk assessment and mitigation strategies
- [**Future Enhancements**](docs/planning/18-Future-Enhancements.md) - Post-MVP roadmap (v2.0-v5.0)

### 📖 Reference
- [**Appendices**](docs/reference/19-Appendices.md) - Additional resources, links, and references
- [**Glossary & Revision History**](docs/reference/20-Glossary-And-Revision-History.md) - Terminology definitions and document change log

---

## 🛠️ Technology Stack

- **Language**: Python 3.11+
- **Web Framework**: FastAPI (async, high-performance REST API)
- **Database**: PostgreSQL 14+ with TimescaleDB extension
- **Data Processing**: Pandas, NumPy, Pandas-TA
- **Data Providers**: 
  - **India**: Zerodha Kite Connect API
  - **US**: Yahoo Finance (yfinance library)
- **Testing**: Pytest
- **Deployment**: Local installation (MVP)

---

## 📋 Project Documents

- [**MVP_PRD.md**](MVP_PRD.md) - Complete Product Requirements Document with feature specifications and success criteria
- [**Scope.md**](Scope.md) - Detailed scope definition, requirements gathering, and prioritization
- [**Standards/**](Standards/) - Coding standards and development guidelines

---

## 🏁 Getting Started

### Prerequisites
- Python 3.11 or higher
- PostgreSQL 14+ with TimescaleDB extension
- Zerodha API credentials (for Indian market data)
- Internet connectivity for data fetching

### Installation
Refer to the [Development Phases](docs/planning/16-Development-Phases.md) document for the complete 14-week implementation plan.

**Quick Overview:**
1. **Phase 1 (Weeks 1-2)**: Data infrastructure and historical data loading
2. **Phase 2 (Weeks 3-4)**: Indicator calculation and derived metrics
3. **Phase 3 (Weeks 5-7)**: Pattern recognition engine
4. **Phase 4 (Weeks 8-10)**: Backtesting engine with risk management
5. **Phase 5 (Weeks 11-12)**: Web UI and reporting
6. **Phase 6 (Weeks 13-14)**: Integration testing and SEPA validation

---

## 📊 Core Methodologies

### Mark Minervini's Trend Template (8 Criteria)
1. Stock price > 150-day MA AND > 200-day MA
2. 150-day MA > 200-day MA
3. 200-day MA trending upward for ≥1 month
4. 50-day MA > 150-day MA AND > 200-day MA
5. Stock price > 130% of 52-week low
6. Stock price ≥ 75% of 52-week high
7. Relative Strength (RS) rating > 70
8. Price consolidation with volume contraction

### Volatility Contraction Pattern (VCP)
- 2-4 pullback contractions required
- Each pullback shallower than previous (tolerance: 20%)
- Volume contraction during pullbacks
- Tightening price action before breakout

### Weinstein Stage Analysis
- **Stage 1**: Base/Accumulation
- **Stage 2**: Advancing/Mark-up *(Target stage for entry)*
- **Stage 3**: Top/Distribution
- **Stage 4**: Decline/Mark-down

---

## 🎯 Success Criteria

The MVP is considered successful if it:
1. ✅ Loads and processes 20 years of daily data for 10,000 securities
2. ✅ Accurately detects all specified chart patterns with confidence scoring
3. ✅ Executes systematic backtests with proper risk management
4. ✅ Generates actionable `ideas.csv` with clear entry/exit rules
5. ✅ Validates whether SEPA methodology outperforms market benchmarks

---

## 📝 License

*(License information to be added)*

---

## 🤝 Contributing

This is currently a single-user research tool. Multi-user support and collaboration features are planned for future releases.

---

**Built to validate systematic investing through data-driven analysis.**
