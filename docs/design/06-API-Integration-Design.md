# API & Integration Design
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
