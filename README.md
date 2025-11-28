# Securities Research Tool

A comprehensive, automated securities analysis platform designed to support data-driven trading decisions. This tool integrates data ingestion, technical analysis, pattern recognition (VCP, Trend Template), and systematic backtesting into a unified workflow.

---

## 📚 Documentation

The technical documentation is organized into a modular 20-file structure within the `docs/` directory.

### 🏗️ Architecture
- [**TDD Overview**](docs/architecture/00-TDD-Overview.md): Master index and document control.
- [**System Architecture**](docs/architecture/01-System-Architecture.md): High-level design and component interaction.
- [**Technology Stack**](docs/architecture/02-Technology-Stack.md): Tech choices, pricing analysis, and performance targets.
- [**Data Architecture**](docs/architecture/03-Data-Architecture.md): Schema design and data flow.

### 🎨 Design
- [**Component Design**](docs/design/04-Component-Design.md): Detailed class and module design (Data Providers, Backtesting, etc.).
- [**Algorithms & Logic**](docs/design/05-Algorithms-And-Logic.md): Core algorithms (Mansfield RS, VCP Detection, Metrics).
- [**User Interface**](docs/design/06-User-Interface.md): UI/UX design and wireframes.
- [**Security Design**](docs/design/07-Security-Design.md): Authentication and data protection.

### ⚙️ Operations
- [**API Specification**](docs/operations/12-API-Specification.md): REST API endpoints and contracts.
- [**Monitoring & Observability**](docs/operations/13-Monitoring-Observability.md): Logging, error handling, and metrics.
- [**Documentation Requirements**](docs/operations/14-Documentation-Requirements.md): Standards and ADRs.

### 📅 Planning & Quality
- [**Project Roadmap**](docs/planning/08-Project-Roadmap.md): Phased implementation plan.
- [**Implementation Plan**](docs/planning/09-Implementation-Plan.md): Detailed step-by-step tasks.
- [**Testing Strategy**](docs/quality/10-Testing-Strategy.md): Unit, integration, and backtesting strategies.
- [**Quality Assurance**](docs/quality/11-Quality-Assurance.md): Code quality standards and CI/CD.

---

## 🚀 Key Features

- **Automated Data Ingestion**: Fetches historical and daily data from Zerodha (India) and Yahoo Finance (US).
- **Advanced Pattern Recognition**:
  - **Volatility Contraction Pattern (VCP)**: Detects price consolidations with decreasing volatility.
  - **Trend Template**: Filters for Stage 2 uptrends based on Mark Minervini's criteria.
  - **Mansfield Relative Strength**: Identifies market leaders outperforming the index.
- **Systematic Backtesting**:
  - **Positions-First Engine**: accurately simulates trading by managing existing positions before new entries.
  - **Risk Management**: Enforces stop-losses, position sizing, and portfolio heat limits.
- **Performance Metrics**: Calculates Sharpe Ratio, Max Drawdown, CAGR, and Profit Factor.

---

## 🛠️ Technology Stack

- **Language**: Python 3.11+
- **Web Framework**: FastAPI
- **Database**: PostgreSQL with TimescaleDB (Time-series optimization)
- **Data Processing**: Pandas, NumPy, Pandas-TA
- **Testing**: Pytest

---

## 🏁 Getting Started

### Prerequisites
- Python 3.11 or higher
- PostgreSQL 14+

### Installation
*(Coming soon - see [Implementation Plan](docs/planning/09-Implementation-Plan.md))*
