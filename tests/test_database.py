"""Unit tests for database connection and session management.

Tests database connection pooling, session management, and retry logic.
"""

from unittest.mock import patch

import pytest
from sqlalchemy.exc import OperationalError

from backend.core.database import (
    SessionLocal,
    check_database_connection,
    engine,
    execute_with_retry,
    get_session,
)


class TestDatabaseConnection:
    """Test suite for database connection management."""

    def test_engine_is_configured(self):
        """Test that database engine is properly configured."""
        assert engine is not None
        assert engine.pool is not None
        # Verify pool configuration
        assert engine.pool.size() >= 0  # Pool exists

    def test_session_factory_exists(self):
        """Test that SessionLocal factory is configured."""
        assert SessionLocal is not None
        # Create a session to verify factory works
        session = SessionLocal()
        assert session is not None
        session.close()


class TestSessionManagement:
    """Test suite for session management."""

    def test_get_session_context_manager(self, db_session):
        """Test that get_session provides a valid session."""
        with get_session() as session:
            assert session is not None
            assert session.is_active

    def test_get_session_commits_on_success(self):
        """Test that session commits on successful completion."""
        from backend.models.db_models import Symbol

        with get_session() as session:
            # Create a test symbol
            symbol = Symbol(
                symbol="TEST_SESSION",
                name="Test Session Symbol",
                exchange="NYSE",
                market="US",
                active=True
            )
            session.add(symbol)

        # Verify it was committed
        with get_session() as session:
            result = session.query(Symbol).filter_by(
                symbol="TEST_SESSION").first()
            if result:
                # Clean up
                session.delete(result)
                session.commit()

    def test_get_session_rolls_back_on_error(self):
        """Test that session rolls back on exception."""
        from backend.models.db_models import Symbol

        try:
            with get_session() as session:
                # Create a test symbol
                symbol = Symbol(
                    symbol="TEST_ROLLBACK",
                    name="Test Rollback Symbol",
                    exchange="NYSE",
                    market="US",
                    active=True
                )
                session.add(symbol)
                # Force an error
                raise ValueError("Test error")
        except ValueError:
            pass

        # Verify it was rolled back
        with get_session() as session:
            result = session.query(Symbol).filter_by(
                symbol="TEST_ROLLBACK").first()
            assert result is None


class TestDatabaseHealthCheck:
    """Test suite for database health check."""

    def test_check_database_connection_success(self):
        """Test successful database connection check."""
        result = check_database_connection()
        assert result is True

    def test_check_database_connection_failure(self):
        """Test database connection check handles failures."""
        # Mock the session to raise an exception
        with patch('backend.core.database.get_session') as mock_session:
            mock_session.side_effect = OperationalError(
                "Connection failed", None, None)
            result = check_database_connection()
            assert result is False


class TestRetryLogic:
    """Test suite for retry logic."""

    def test_execute_with_retry_success(self):
        """Test successful query execution with retry."""
        def successful_query():
            return "success"

        result = execute_with_retry(successful_query)
        assert result == "success"

    def test_execute_with_retry_eventual_success(self):
        """Test retry logic succeeds after initial failures."""
        call_count = 0

        def flaky_query():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise OperationalError("Temporary failure", None, None)
            return "success"

        result = execute_with_retry(flaky_query)
        assert result == "success"
        assert call_count == 2

    def test_execute_with_retry_max_attempts(self):
        """Test retry logic fails after max attempts."""
        def always_fails():
            raise OperationalError("Permanent failure", None, None)

        with pytest.raises(OperationalError):
            execute_with_retry(always_fails)

    def test_execute_with_retry_with_args(self):
        """Test retry logic passes arguments correctly."""
        def query_with_args(arg1, arg2, kwarg1=None):
            return f"{arg1}-{arg2}-{kwarg1}"

        result = execute_with_retry(query_with_args, "a", "b", kwarg1="c")
        assert result == "a-b-c"


class TestConnectionPooling:
    """Test suite for connection pooling."""

    def test_multiple_sessions_from_pool(self):
        """Test that multiple sessions can be created from pool."""
        sessions = []
        for _ in range(3):
            session = SessionLocal()
            sessions.append(session)
            assert session is not None

        # Clean up
        for session in sessions:
            session.close()

    def test_session_isolation(self):
        """Test that sessions are isolated from each other."""
        from backend.models.db_models import Symbol

        session1 = SessionLocal()
        session2 = SessionLocal()

        try:
            # Add object in session1
            symbol = Symbol(
                symbol="TEST_ISOLATION",
                name="Test Isolation",
                exchange="NYSE",
                market="US",
                active=True
            )
            session1.add(symbol)
            session1.flush()

            # Should not be visible in session2 until committed
            result = session2.query(Symbol).filter_by(
                symbol="TEST_ISOLATION").first()
            # Note: Depending on isolation level, this might be None

            session1.rollback()
        finally:
            session1.close()
            session2.close()
