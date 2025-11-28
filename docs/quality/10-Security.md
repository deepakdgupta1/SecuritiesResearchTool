# Security
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
