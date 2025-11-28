# Technology Stack Recommendations \with Pricing Analysis\
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

## Performance Targets

All performance targets are defined in `backend/core/constants.py` and monitored in production.

**Target Metrics:**

| Metric | Target Value | Rationale | Constant Name |
|--------|--------------|-----------|---------------|
| **Full Universe Scan** | <30 min (ideal: <15 min) | Enable overnight batch processing without blocking user | `TARGET_FULL_SCAN_MINUTES` |
| **20-Year Backtest** | <30 minutes | Allow rapid strategy iteration and parameter tuning | `TARGET_BACKTEST_MINUTES` |
| **Data Ingestion Success Rate** | ≥99% | Occasional API failures acceptable, but data must be reliable | `DATA_INGESTION_SUCCESS_RATE_TARGET` |
| **Database Query P95 Latency** | <500ms | Adequate for batch processing, acceptable UX for web queries | `DATABASE_QUERY_P95_LATENCY_MS` |
| **API Response P95** | <2 seconds | Acceptable UX for web interface interactions | `API_RESPONSE_P95_LATENCY_MS` |
| **Pattern Detection Accuracy** | Manual validation | No false positives on known historical examples | N/A (qualitative) |

---

## Performance Philosophy

**MVP Priorities:**
1. **Correctness First:** Accurate pattern detection and backtest results over raw speed
2. **Maintainability:** Clean, readable code over premature optimization
3. **Developer Experience:** Fast iteration cycles, easy debugging
4. **Acceptable Speed:** Batch processing (overnight) is fine for MVP

**Not Optimizing For (Yet):**
- Real-time pattern detection (deferred to Phase 2+)
- Sub-second API responses (2s is acceptable for MVP)
- Horizontal scaling (single machine sufficient for 10K securities)
- GPU acceleration (CPU-only is fine)

---

## Why These Targets

### Full Universe Scan: <30 minutes

**Reasoning:**
- **10,000 securities** × **20+ indicators each** × **pattern matching**
- Run overnight (11pm - 7am = 8 hours available)
- 30 minutes leaves plenty of buffer for failures/retries
- 15 minutes is ideal - allows multiple scans if needed

**Acceptable on:**
- Modern laptop (8GB RAM, 4-core CPU)
- No cloud costs required

**Implementation:**
```python
from backend.core.constants import TARGET_FULL_SCAN_MINUTES

def scan_universe(symbols: List[str]) -> pd.DataFrame:
    """Scan all symbols for patterns."""
    start_time = time.time()
    
    results = pattern_detector.scan_all(symbols)
    
    elapsed_minutes = (time.time() - start_time) / 60
    
    if elapsed_minutes > TARGET_FULL_SCAN_MINUTES:
        logger.warning(
            f"Scan took {elapsed_minutes:.1f} min (target: {TARGET_FULL_SCAN_MINUTES} min)"
        )
    
    return results
```

---

### 20-Year Backtest: <30 minutes

**Reasoning:**
- **20 years** × **252 trading days** = **~5,000 trading days**
- User wants to test multiple parameter combinations
- 30 min/backtest = 10-20 backtests per day (good iteration speed)

**Acceptable on:**
- Same laptop as above
- PostgreSQL with proper indexes

**Trade-offs:**
- Could be faster with caching, but adds complexity
- MVP priority: correctness over speed

---

### Data Ingestion Success Rate: ≥99%

**Reasoning:**
- External APIs (Zerodha, Yahoo Finance) occasionally fail
- 1% failure rate = ~1 failed fetch per 100 symbols
- Retry logic handles transient failures
- Manual intervention acceptable for persistent issues

**Monitoring:**
```python
from backend.core.constants import DATA_INGESTION_SUCCESS_RATE_TARGET

def monitor_ingestion_success():
    """Track data ingestion success rate."""
    total_fetches = 10000
    successful_fetches = 9950  # Example
    
    success_rate = successful_fetches / total_fetches
    
    if success_rate < DATA_INGESTION_SUCCESS_RATE_TARGET:
        alert_admin(f"Success rate {success_rate:.2%} below target {DATA_INGESTION_SUCCESS_RATE_TARGET:.2%}")
```

---

### Database Query P95: <500ms

**Reasoning:**
- Most queries for batch processing (not user-facing)
- 500ms is imperceptible to users for background jobs
- Allows complex joins and aggregations
- P95 metric: 95% of queries faster than 500ms

**Optimization Strategy:**
- Proper indexes on `symbol_id` and `date` columns
- TimescaleDB compression for older data
- No premature optimization - measure first

---

### API Response P95: <2 seconds

**Reasoning:**
- Web UI interactions feel responsive under 2 seconds
- Covers pattern scan, backtest trigger, report generation
- Most endpoints much faster (<500ms)
- P95 allows for occasional complex queries

**User Experience:**
- Instant feedback (<200ms): Button clicks, navigation
- Fast (<1s): Simple queries, list views
- Acceptable (<2s): Complex reports, backtest results
- Show spinner for anything >500ms

---

## Performance Monitoring

**Implementation:**
```python
from backend.core.constants import (
    TARGET_FULL_SCAN_MINUTES,
    TARGET_BACKTEST_MINUTES,
    DATABASE_QUERY_P95_LATENCY_MS,
    API_RESPONSE_P95_LATENCY_MS
)
import time
from functools import wraps

def monitor_performance(target_ms: int, operation_name: str):
    """Decorator to monitor operation performance."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            elapsed_ms = (time.time() - start) * 1000
            
            if elapsed_ms > target_ms:
                logger.warning(
                    f"{operation_name} took {elapsed_ms:.0f}ms (target: {target_ms}ms)"
                )
            
            # Track metric for P95 calculation
            metrics.record(operation_name, elapsed_ms)
            
            return result
        return wrapper
    return decorator

# Usage
@monitor_performance(DATABASE_QUERY_P95_LATENCY_MS, "fetch_price_data")
def fetch_price_data(symbol: str) -> pd.DataFrame:
    """Fetch price data with performance monitoring."""
    return db.query(...)
```

---

## Optimization Roadmap (Post-MVP)

**If targets not met, optimize in this order:**

1. **Database Indexes** (biggest impact, low effort)
   - Add indexes on frequently queried columns
   - Use TimescaleDB continuous aggregates

2. **Query Optimization** (high impact, medium effort)
   - Reduce data fetched (only required columns/dates)
   - Batch operations instead of row-by-row

3. **Parallel Processing** (medium impact, medium effort)
   - Process symbols in parallel (multiprocessing)
   - Parallelize independent calculations

4. **Caching** (medium impact, high complexity)
   - Cache calculated indicators
   - Redis for frequently accessed data

5. **Code Profiling** (variable impact, low effort)
   - Identify bottlenecks with cProfile
   - Optimize hot paths only

**Do NOT optimize:**
- Until targets are consistently missed
- Without measuring first (no guessing)
- At the expense of code readability

---

## Hardware Requirements

**Minimum (MVP):**
- CPU: 4 cores (Intel i5 or equivalent)
- RAM: 8GB
- Storage: 50GB SSD
- OS: Windows/Linux/Mac

**Recommended:**
- CPU: 8 cores (for parallel processing)
- RAM: 16GB
- Storage: 100GB NVMe SSD (faster database)

**Cloud Alternative (Post-MVP):**
- AWS EC2 t3.medium ($30/month)
- DigitalOcean Droplet ($ 12/month for 2GB RAM, upgrade as needed)
