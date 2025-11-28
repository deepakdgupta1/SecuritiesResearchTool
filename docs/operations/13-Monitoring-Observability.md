# Monitoring & Observability
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
