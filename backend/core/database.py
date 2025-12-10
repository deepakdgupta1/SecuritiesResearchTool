"""Database connection and session management.

This module handles all database operations including:
- Connection pooling
- Session management
- Transaction handling
- Retry logic with exponential backoff

Usage:
    from backend.core.database import get_session

    with get_session() as session:
        result = session.execute(query)
"""

import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from backend.core.config import settings
from backend.core.constants import (
    API_RETRY_BACKOFF_SECONDS,
    API_RETRY_MAX_ATTEMPTS,
    DB_CONNECTION_POOL_SIZE,
    DB_CONNECTION_TIMEOUT_SECONDS,
)

logger = logging.getLogger(__name__)


# ==============================================================================
# Database Engine Configuration
# ==============================================================================

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=DB_CONNECTION_POOL_SIZE,
    pool_timeout=DB_CONNECTION_TIMEOUT_SECONDS,
    pool_pre_ping=True,  # Verify connections before using
    echo=settings.ENVIRONMENT == "development",  # SQL logging in dev mode
)
"""Global database engine with connection pooling."""


# Configure connection pool events for logging
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Log database connections."""
    logger.debug("Database connection established")


@event.listens_for(engine, "close")
def receive_close(dbapi_conn, connection_record):
    """Log database disconnections."""
    logger.debug("Database connection closed")


# ==============================================================================
# Session Factory
# ==============================================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
"""Session factory for creating database sessions."""


# ==============================================================================
# Session Management
# ==============================================================================

@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Provide a transactional scope for database operations.

    This context manager automatically:
    - Creates a new session
    - Commits on successful completion
    - Rolls back on exception
    - Closes the session

    Yields:
        Session: SQLAlchemy session for database operations

    Example:
        >>> with get_session() as session:
        ...     result = session.query(Symbol).filter_by(symbol="AAPL").first()
        ...     print(result.name)
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
        logger.debug("Database transaction committed")
    except Exception as e:
        session.rollback()
        logger.error(f"Database transaction rolled back: {e}")
        raise
    finally:
        session.close()


@retry(
    stop=stop_after_attempt(API_RETRY_MAX_ATTEMPTS),
    wait=wait_exponential(
        multiplier=API_RETRY_BACKOFF_SECONDS,
        min=API_RETRY_BACKOFF_SECONDS,
        max=60,
    ),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def execute_with_retry(query_func, *args, **kwargs):
    """Execute a database query with automatic retry on failure.

    Uses exponential backoff retry strategy for transient failures
    (network issues, connection timeouts, deadlocks).

    Args:
        query_func: Function that executes the database query
        *args: Positional arguments to pass to query_func
        **kwargs: Keyword arguments to pass to query_func

    Returns:
        Result of query_func execution

    Raises:
        Exception: If all retry attempts fail

    Example:
        >>> def fetch_symbols():
        ...     with get_session() as session:
        ...         return session.query(Symbol).all()
        >>>
        >>> symbols = execute_with_retry(fetch_symbols)
    """
    logger.debug(f"Executing query with retry: {query_func.__name__}")
    try:
        return query_func(*args, **kwargs)
    except Exception as e:
        logger.warning(f"Query failed, will retry: {e}")
        raise


# ==============================================================================
# Health Check
# ==============================================================================

def check_database_connection() -> bool:
    """Verify database connection is healthy.

    Returns:
        bool: True if connection successful, False otherwise

    Example:
        >>> if check_database_connection():
        ...     print("Database is ready")
        ... else:
        ...     print("Database connection failed")
    """
    try:
        with get_session() as session:
            session.execute(text("SELECT 1"))
        logger.info("Database connection check: SUCCESS")
        return True
    except Exception as e:
        logger.error(f"Database connection check: FAILED - {e}")
        return False
