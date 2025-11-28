# Deployment Architecture
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
