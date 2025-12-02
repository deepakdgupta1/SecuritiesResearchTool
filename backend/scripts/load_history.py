"""Historical data loader script.

Fetches historical OHLCV data from data providers and stores it in the
TimescaleDB hypertable (price_data).

Features:
- Supports both Indian (Zerodha) and US (Yahoo Finance) markets
- Incremental loading (fetches only missing data)
- Batch processing for performance
- Error handling and logging
- Sample mode for verification

Usage:
    # Load history for all symbols (default 20 years)
    python -m backend.scripts.load_history
    
    # Load sample (10 symbols, 1 year)
    python -m backend.scripts.load_history --sample
    
    # Load specific market
    python -m backend.scripts.load_history --market US
    
    # Force full reload
    python -m backend.scripts.load_history --force
"""

import argparse
import logging
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List, Optional, Type

import pandas as pd
from sqlalchemy import func, text
from sqlalchemy.dialects.postgresql import insert

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.core.config import settings
from backend.core.constants import (
    MARKET_IN,
    MARKET_US,
    COL_OPEN,
    COL_HIGH,
    COL_LOW,
    COL_CLOSE,
    COL_VOLUME,
    COL_ADJ_CLOSE,
    COL_DATE,
)
from backend.core.database import get_session
from backend.models.db_models import Symbol, PriceData
from backend.data_providers.base import BaseDataProvider, DataNotFoundError
from backend.data_providers.yahoo_client import YahooFinanceProvider
from backend.data_providers.zerodha_client import ZerodhaProvider

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_provider_for_market(market: str) -> Optional[BaseDataProvider]:
    """Get appropriate data provider for the market."""
    if market == MARKET_US:
        return YahooFinanceProvider()
    elif market == MARKET_IN:
        try:
            return ZerodhaProvider()
        except Exception as e:
            logger.warning(f"Zerodha provider not available: {e}")
            return None
    return None


def get_last_date(session, symbol_id: int) -> Optional[date]:
    """Get the last available date for a symbol in the database."""
    result = session.query(func.max(PriceData.date)).filter_by(symbol_id=symbol_id).scalar()
    return result


def load_symbol_history(
    session,
    provider: BaseDataProvider,
    symbol: Symbol,
    start_date: date,
    end_date: date,
    force: bool = False
) -> int:
    """Load historical data for a single symbol.
    
    Args:
        session: Database session
        provider: Data provider instance
        symbol: Symbol object
        start_date: Target start date
        end_date: Target end date
        force: If True, reload even if data exists
        
    Returns:
        Number of records inserted
    """
    try:
        # Determine actual start date
        actual_start = start_date
        if not force:
            last_date = get_last_date(session, symbol.id)
            if last_date:
                # Start from next day
                actual_start = last_date + timedelta(days=1)
                
                # If up to date, skip
                if actual_start > end_date:
                    logger.debug(f"Skipping {symbol.symbol}: Up to date")
                    return 0
        
        logger.info(f"Fetching {symbol.symbol} ({symbol.market}) from {actual_start} to {end_date}")
        
        # Fetch data
        df = provider.get_historical_data(
            symbol=symbol.symbol,
            start_date=actual_start,
            end_date=end_date,
            exchange=symbol.exchange if symbol.market == MARKET_IN else None
        )
        
        if df.empty:
            logger.warning(f"No data found for {symbol.symbol}")
            return 0
            
        # Prepare records for insertion
        records = []
        for _, row in df.iterrows():
            records.append({
                'symbol_id': symbol.id,
                'date': row[COL_DATE],
                'open': row[COL_OPEN],
                'high': row[COL_HIGH],
                'low': row[COL_LOW],
                'close': row[COL_CLOSE],
                'volume': int(row[COL_VOLUME]),
                'adjusted_close': row[COL_ADJ_CLOSE],
            })
            
        # Bulk insert with upsert (on conflict do update)
        stmt = insert(PriceData).values(records)
        stmt = stmt.on_conflict_do_update(
            index_elements=['symbol_id', 'date'],
            set_={
                'open': stmt.excluded.open,
                'high': stmt.excluded.high,
                'low': stmt.excluded.low,
                'close': stmt.excluded.close,
                'volume': stmt.excluded.volume,
                'adjusted_close': stmt.excluded.adjusted_close,
            }
        )
        
        session.execute(stmt)
        session.commit()
        
        return len(records)
        
    except DataNotFoundError:
        logger.warning(f"Symbol {symbol.symbol} not found in provider")
        return 0
    except Exception as e:
        logger.error(f"Error loading {symbol.symbol}: {e}")
        session.rollback()
        return 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Load historical price data")
    parser.add_argument("--market", choices=[MARKET_IN, MARKET_US, "ALL"], default="ALL", help="Market to load")
    parser.add_argument("--sample", action="store_true", help="Load sample data (10 symbols, 1 year)")
    parser.add_argument("--force", action="store_true", help="Force reload existing data")
    parser.add_argument("--days", type=int, default=None, help="Number of days to load (default: 20 years)")
    
    args = parser.parse_args()
    
    logger.info("=" * 70)
    logger.info("Securities Research Tool - Historical Data Loader")
    logger.info("=" * 70)
    
    # Configuration
    end_date = date.today()
    if args.sample:
        start_date = end_date - timedelta(days=365)  # 1 year for sample
        limit = 10
        logger.info("Mode: SAMPLE (10 symbols, 1 year)")
    else:
        # Default to 20 years if not specified
        days = args.days if args.days else (365 * 20)
        start_date = end_date - timedelta(days=days)
        limit = None
        logger.info(f"Mode: FULL ({days/365:.1f} years)")
    
    total_records = 0
    start_time = time.time()
    
    with get_session() as session:
        # Get symbols to process
        query = session.query(Symbol).filter(Symbol.active == True)
        
        if args.market != "ALL":
            query = query.filter(Symbol.market == args.market)
            
        if limit:
            # For sample, take 5 from each market if ALL
            if args.market == "ALL":
                us_symbols = session.query(Symbol).filter_by(market=MARKET_US, active=True).limit(5).all()
                in_symbols = session.query(Symbol).filter_by(market=MARKET_IN, active=True).limit(5).all()
                symbols = us_symbols + in_symbols
            else:
                symbols = query.limit(limit).all()
        else:
            symbols = query.all()
            
        logger.info(f"Found {len(symbols)} symbols to process")
        
        # Group by market to reuse providers
        symbols_by_market = {}
        for sym in symbols:
            if sym.market not in symbols_by_market:
                symbols_by_market[sym.market] = []
            symbols_by_market[sym.market].append(sym)
            
        # Process each market
        for market, market_symbols in symbols_by_market.items():
            provider = get_provider_for_market(market)
            if not provider:
                logger.warning(f"Skipping {market} market: Provider not available")
                continue
                
            logger.info(f"Processing {len(market_symbols)} symbols for {market}...")
            
            for i, symbol in enumerate(market_symbols):
                records = load_symbol_history(
                    session, provider, symbol, start_date, end_date, args.force
                )
                total_records += records
                
                # Progress logging
                if (i + 1) % 10 == 0:
                    logger.info(f"Progress {market}: {i + 1}/{len(market_symbols)}")
                    
    duration = time.time() - start_time
    logger.info("=" * 70)
    logger.info(f"✓ Data load completed in {duration:.2f}s")
    logger.info(f"Total records inserted: {total_records}")
    logger.info("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
