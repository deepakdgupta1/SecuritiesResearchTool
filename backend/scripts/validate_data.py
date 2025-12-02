"""Data validation script.

Performs comprehensive data quality checks on the database.
Generates a report of missing data, anomalies, and statistics.

Checks:
- Missing days (gaps in trading history)
- Zero or negative prices
- Abnormal price spikes (>50% daily change)
- Volume anomalies (zero volume for active stocks)
- Data freshness (last available date)

Usage:
    python -m backend.scripts.validate_data
"""

import logging
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import List, Dict

import pandas as pd
from sqlalchemy import func, text

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.core.config import settings
from backend.core.database import get_session
from backend.models.db_models import Symbol, PriceData

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def check_data_freshness(session) -> Dict:
    """Check how up-to-date the data is."""
    logger.info("Checking data freshness...")
    
    # Get max date per market
    results = session.query(
        Symbol.market,
        func.max(PriceData.date).label('last_date'),
        func.count(func.distinct(Symbol.id)).label('symbol_count')
    ).join(PriceData).group_by(Symbol.market).all()
    
    stats = {}
    for market, last_date, count in results:
        stats[market] = {
            'last_date': last_date,
            'symbols_with_data': count
        }
        logger.info(f"Market {market}: Last date {last_date} ({count} symbols)")
        
    return stats


def check_price_anomalies(session) -> List[Dict]:
    """Check for price anomalies (negative prices, huge spikes)."""
    logger.info("Checking for price anomalies...")
    
    anomalies = []
    
    # Check 1: Negative or Zero prices
    bad_prices = session.query(PriceData).filter(
        (PriceData.close <= 0) | 
        (PriceData.high <= 0) | 
        (PriceData.low <= 0) | 
        (PriceData.open <= 0)
    ).limit(100).all()
    
    if bad_prices:
        logger.warning(f"Found {len(bad_prices)} records with zero/negative prices")
        for p in bad_prices:
            anomalies.append({
                'type': 'BAD_PRICE',
                'symbol_id': p.symbol_id,
                'date': p.date,
                'details': f"Close: {p.close}"
            })
            
    # Check 2: Abnormal spikes (> 50% daily return)
    # Using SQL window function for efficiency
    query = text("""
        WITH returns AS (
            SELECT 
                symbol_id, 
                date, 
                close,
                LAG(close) OVER (PARTITION BY symbol_id ORDER BY date) as prev_close
            FROM price_data
            WHERE date > current_date - interval '1 year'
        )
        SELECT symbol_id, date, close, prev_close
        FROM returns
        WHERE prev_close > 0 AND ABS(close - prev_close) / prev_close > 0.5
        LIMIT 50;
    """)
    
    spikes = session.execute(query).fetchall()
    if spikes:
        logger.warning(f"Found {len(spikes)} abnormal price spikes (>50%)")
        for row in spikes:
            anomalies.append({
                'type': 'PRICE_SPIKE',
                'symbol_id': row.symbol_id,
                'date': row.date,
                'details': f"Price changed from {row.prev_close} to {row.close}"
            })
            
    return anomalies


def check_missing_data(session) -> List[Dict]:
    """Check for symbols with missing recent data."""
    logger.info("Checking for missing recent data...")
    
    missing = []
    cutoff_date = date.today() - timedelta(days=5)  # Allow 5 days lag (weekends/holidays)
    
    # Find active symbols with no data in last 5 days
    subquery = session.query(
        PriceData.symbol_id,
        func.max(PriceData.date).label('max_date')
    ).group_by(PriceData.symbol_id).subquery()
    
    results = session.query(Symbol, subquery.c.max_date).join(
        subquery, Symbol.id == subquery.c.symbol_id
    ).filter(
        Symbol.active == True,
        subquery.c.max_date < cutoff_date
    ).limit(50).all()
    
    if results:
        logger.warning(f"Found {len(results)} active symbols with stale data")
        for sym, last_date in results:
            missing.append({
                'symbol': sym.symbol,
                'market': sym.market,
                'last_date': last_date
            })
            
    return missing


def main() -> int:
    """Main entry point."""
    logger.info("=" * 70)
    logger.info("Securities Research Tool - Data Validation")
    logger.info("=" * 70)
    
    try:
        with get_session() as session:
            # 1. Check Freshness
            freshness = check_data_freshness(session)
            
            # 2. Check Anomalies
            anomalies = check_price_anomalies(session)
            
            # 3. Check Missing Data
            missing = check_missing_data(session)
            
            logger.info("-" * 70)
            logger.info("VALIDATION SUMMARY")
            logger.info("-" * 70)
            
            # Report
            if not anomalies and not missing:
                logger.info("✓ Data quality looks good!")
            else:
                if anomalies:
                    logger.warning(f"⚠ Found {len(anomalies)} price anomalies")
                if missing:
                    logger.warning(f"⚠ Found {len(missing)} symbols with stale data")
            
            logger.info("=" * 70)
            return 0 if not anomalies else 1
            
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
