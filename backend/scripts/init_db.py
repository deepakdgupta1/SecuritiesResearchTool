"""Database initialization script for Securities Research Tool.

This script creates all database tables from the SQLAlchemy ORM models.
It also handles TimescaleDB hypertable conversion for price_data table.

Usage:
    python -m backend.scripts.init_db

Prerequisites:
    - PostgreSQL 14+ installed and running
    - TimescaleDB extension installed
    - Database 'securities_research' created
    - .env file configured with DATABASE_URL
"""

import logging
import sys
from pathlib import Path

from sqlalchemy import text

from backend.core.config import settings
from backend.core.database import check_database_connection, engine
from backend.models.db_models import Base

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_timescaledb_extension() -> bool:
    """Create TimescaleDB extension if not already exists.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with engine.connect() as conn:
            # Check if TimescaleDB is already installed
            result = conn.execute(
                text("SELECT * FROM pg_extension WHERE extname = 'timescaledb'"))
            if result.fetchone():
                logger.info("TimescaleDB extension already exists")
                return True

            # Create extension
            conn.execute(
                text("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE"))
            conn.commit()
            logger.info("✓ TimescaleDB extension created successfully")
            return True

    except Exception as e:
        logger.error(f"Failed to create TimescaleDB extension: {e}")
        logger.warning(
            "Continuing without TimescaleDB - performance may be degraded")
        return False


def create_tables() -> bool:
    """Create all database tables from ORM models.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✓ All tables created successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        return False


def convert_to_hypertable() -> bool:
    """Convert price_data table to TimescaleDB hypertable.

    This enables time-series optimization for efficient queries on large datasets.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with engine.connect() as conn:
            # Check if already a hypertable
            result = conn.execute(
                text(
                    "SELECT * FROM timescaledb_information.hypertables "
                    "WHERE hypertable_name = 'price_data'"
                )
            )

            if result.fetchone():
                logger.info("price_data is already a hypertable")
                return True

            # Convert to hypertable
            # Note: Using symbol_id as partitioning column as well for better
            # performance
            conn.execute(
                text(
                    "SELECT create_hypertable('price_data', 'date', "
                    "partitioning_column => 'symbol_id', "
                    "number_partitions => 4, "
                    "if_not_exists => TRUE)"
                )
            )
            conn.commit()
            logger.info("✓ price_data converted to TimescaleDB hypertable")
            return True

    except Exception as e:
        logger.error(f"Failed to convert to hypertable: {e}")
        logger.warning(
            "Table created as regular table - consider manual conversion")
        return False


def create_indexes() -> bool:
    """Create additional indexes for optimal query performance.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with engine.connect() as conn:
            # Composite index on symbols for common lookups
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS ix_symbols_market_exchange "
                    "ON symbols(market, exchange)"
                )
            )

            # Index on pattern_detections for confidence filtering
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS ix_pattern_detections_confidence "
                    "ON pattern_detections(confidence_score) "
                    "WHERE confidence_score >= 70"))

            conn.commit()
            logger.info("✓ Additional indexes created successfully")
            return True

    except Exception as e:
        logger.error(f"Failed to create additional indexes: {e}")
        return False


def verify_schema() -> bool:
    """Verify that all expected tables exist.

    Returns:
        bool: True if all tables exist, False otherwise
    """
    expected_tables = [
        "symbols",
        "price_data",
        "derived_metrics",
        "pattern_detections",
        "trade_recommendations",
        "backtest_results",
        "backtest_trades",
    ]

    try:
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT tablename FROM pg_tables "
                    "WHERE schemaname = 'public'"
                )
            )
            existing_tables = {row[0] for row in result}

            missing_tables = set(expected_tables) - existing_tables

            if missing_tables:
                logger.error(f"Missing tables: {missing_tables}")
                return False

            logger.info(f"✓ All {len(expected_tables)} tables verified")
            return True

    except Exception as e:
        logger.error(f"Failed to verify schema: {e}")
        return False


def main() -> int:
    """Main entry point for database initialization.

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    logger.info("=" * 70)
    logger.info("Securities Research Tool - Database Initialization")
    logger.info("=" * 70)
    logger.info(
        f"Database URL: {
            settings.DATABASE_URL.split('@')[1]}")  # Hide credentials
    logger.info("")

    # Step 1: Check database connection
    logger.info("Step 1: Checking database connection...")
    if not check_database_connection():
        logger.error("✗ Database connection failed")
        logger.error("\nPlease ensure:")
        logger.error("  1. PostgreSQL is running")
        logger.error("  2. Database 'securities_research' exists")
        logger.error("  3. DATABASE_URL in .env is correct")
        return 1
    logger.info("✓ Database connection successful")
    logger.info("")

    # Step 2: Create TimescaleDB extension
    logger.info("Step 2: Creating TimescaleDB extension...")
    timescaledb_available = create_timescaledb_extension()
    logger.info("")

    # Step 3: Create tables
    logger.info("Step 3: Creating database tables...")
    if not create_tables():
        logger.error("✗ Table creation failed")
        return 1
    logger.info("")

    # Step 4: Convert to hypertable (if TimescaleDB available)
    if timescaledb_available:
        logger.info("Step 4: Converting price_data to hypertable...")
        if not convert_to_hypertable():
            logger.warning(
                "⚠ Hypertable conversion failed - continuing anyway")
        logger.info("")
    else:
        logger.info(
            "Step 4: Skipping hypertable conversion (TimescaleDB not available)")
        logger.info("")

    # Step 5: Create additional indexes
    logger.info("Step 5: Creating additional indexes...")
    if not create_indexes():
        logger.warning(
            "⚠ Additional index creation failed - continuing anyway")
    logger.info("")

    # Step 6: Verify schema
    logger.info("Step 6: Verifying database schema...")
    if not verify_schema():
        logger.error("✗ Schema verification failed")
        return 1
    logger.info("")

    # Success!
    logger.info("=" * 70)
    logger.info("✓ Database initialization completed successfully!")
    logger.info("=" * 70)
    logger.info("\nNext steps:")
    logger.info("  1. Run: python -m backend.scripts.load_symbols")
    logger.info("  2. Run: python -m backend.scripts.load_history")
    logger.info("")

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
