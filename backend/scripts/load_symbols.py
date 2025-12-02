"""Symbol loader script for Indian and US markets.

Loads symbols from data providers into the symbols table.
Supports both full load and incremental updates.

Usage:
    # Load all symbols
    python -m backend.scripts.load_symbols --market ALL
    
    # Load only Indian symbols
    python -m backend.scripts.load_symbols --market IN
    
    # Load only US symbols (S&P 500)
    python -m backend.scripts.load_symbols --market US
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Dict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.exc import IntegrityError

from backend.core.config import settings
from backend.core.constants import (
    MARKET_IN,
    MARKET_US,
    EXCHANGE_NSE,
    BATCH_SIZE_INSERT,
)
from backend.core.database import get_session
from backend.models.db_models import Symbol
from backend.data_providers.yahoo_client import YahooFinanceProvider
from backend.data_providers.zerodha_client import ZerodhaProvider

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def load_indian_symbols() -> int:
    """Load Indian market symbols from Zerodha.
    
    Returns:
        Number of symbols loaded
    """
    logger.info("=" * 70)
    logger.info("Loading Indian Market Symbols (NSE)")
    logger.info("=" * 70)
    
    try:
        # Initialize Zerodha provider
        provider = ZerodhaProvider()
        
        # Fetch NSE symbols
        logger.info("Fetching NSE instrument list...")
        symbols_data = provider.get_symbols_list(exchange=EXCHANGE_NSE)
        
        logger.info(f"Found {len(symbols_data)} NSE symbols")
        
        # Load into database
        loaded_count = 0
        skipped_count = 0
        
        with get_session() as session:
            for symbol_info in symbols_data:
                try:
                    # Check if symbol already exists
                    existing = session.query(Symbol).filter_by(
                        symbol=symbol_info['symbol'],
                        exchange=EXCHANGE_NSE
                    ).first()
                    
                    if existing:
                        # Update existing symbol
                        existing.name = symbol_info['name']
                        existing.sector = symbol_info['sector']
                        existing.active = True
                        skipped_count += 1
                    else:
                        # Create new symbol
                        symbol = Symbol(
                            symbol=symbol_info['symbol'],
                            name=symbol_info['name'],
                            exchange=EXCHANGE_NSE,
                            market=MARKET_IN,
                            sector=symbol_info['sector'],
                            active=True,
                        )
                        session.add(symbol)
                        loaded_count += 1
                    
                    # Commit every 100 symbols
                    if (loaded_count + skipped_count) % BATCH_SIZE_INSERT == 0:
                        session.commit()
                        logger.info(f"Progress: {loaded_count + skipped_count} symbols processed")
                
                except IntegrityError as e:
                    logger.warning(f"Duplicate symbol {symbol_info['symbol']}: {e}")
                    session.rollback()
                    skipped_count += 1
                    continue
            
            # Final commit
            session.commit()
        
        logger.info(f"✓ Loaded {loaded_count} new symbols, updated {skipped_count} existing symbols")
        return loaded_count
        
    except Exception as e:
        logger.error(f"Error loading Indian symbols: {e}")
        raise


def load_us_symbols() -> int:
    """Load US market symbols from Yahoo Finance (S&P 500).
    
    Returns:
        Number of symbols loaded
    """
    logger.info("=" * 70)
    logger.info("Loading US Market Symbols (S&P 500)")
    logger.info("=" * 70)
    
    try:
        # Initialize Yahoo Finance provider
        provider = YahooFinanceProvider()
        
        # Fetch S&P 500 symbols
        logger.info("Fetching S&P 500 constituent list...")
        symbols_data = provider.get_sp500_symbols()
        
        logger.info(f"Found {len(symbols_data)} S&P 500 symbols")
        
        # Load into database
        loaded_count = 0
        skipped_count = 0
        
        with get_session() as session:
            for symbol_info in symbols_data:
                try:
                    # Check if symbol already exists
                    existing = session.query(Symbol).filter_by(
                        symbol=symbol_info['symbol']
                    ).first()
                    
                    if existing:
                        # Update existing symbol
                        existing.name = symbol_info['name']
                        existing.exchange = symbol_info['exchange']
                        existing.sector = symbol_info['sector']
                        existing.active = True
                        skipped_count += 1
                    else:
                        # Create new symbol
                        symbol = Symbol(
                            symbol=symbol_info['symbol'],
                            name=symbol_info['name'],
                            exchange=symbol_info['exchange'],
                            market=MARKET_US,
                            sector=symbol_info['sector'],
                            active=True,
                        )
                        session.add(symbol)
                        loaded_count += 1
                    
                    # Commit every 100 symbols
                    if (loaded_count + skipped_count) % BATCH_SIZE_INSERT == 0:
                        session.commit()
                        logger.info(f"Progress: {loaded_count + skipped_count} symbols processed")
                
                except IntegrityError as e:
                    logger.warning(f"Duplicate symbol {symbol_info['symbol']}: {e}")
                    session.rollback()
                    skipped_count += 1
                    continue
            
            # Final commit
            session.commit()
        
        logger.info(f"✓ Loaded {loaded_count} new symbols, updated {skipped_count} existing symbols")
        return loaded_count
        
    except Exception as e:
        logger.error(f"Error loading US symbols: {e}")
        raise


def verify_symbols() -> None:
    """Verify symbols were loaded correctly."""
    logger.info("=" * 70)
    logger.info("Verifying Symbol Load")
    logger.info("=" * 70)
    
    with get_session() as session:
        # Count by market
        indian_count = session.query(Symbol).filter_by(market=MARKET_IN, active=True).count()
        us_count = session.query(Symbol).filter_by(market=MARKET_US, active=True).count()
        total_count = session.query(Symbol).filter_by(active=True).count()
        
        logger.info(f"Indian Market (NSE): {indian_count} symbols")
        logger.info(f"US Market (S&P 500): {us_count} symbols")
        logger.info(f"Total Active Symbols: {total_count}")
        
        # Sample some symbols
        logger.info("\nSample Indian Symbols:")
        indian_samples = session.query(Symbol).filter_by(market=MARKET_IN).limit(5).all()
        for sym in indian_samples:
            logger.info(f"  {sym.symbol} - {sym.name} ({sym.exchange})")
        
        logger.info("\nSample US Symbols:")
        us_samples = session.query(Symbol).filter_by(market=MARKET_US).limit(5).all()
        for sym in us_samples:
            logger.info(f"  {sym.symbol} - {sym.name} ({sym.exchange})")


def main() -> int:
    """Main entry point for symbol loader.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(description="Load symbols into database")
    parser.add_argument(
        "--market",
        choices=[MARKET_IN, MARKET_US, "ALL"],
        default="ALL",
        help="Market to load symbols for (IN=India, US=United States, ALL=Both)",
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 70)
    logger.info("Securities Research Tool - Symbol Loader")
    logger.info("=" * 70)
    logger.info(f"Market: {args.market}")
    logger.info("")
    
    try:
        total_loaded = 0
        
        if args.market in [MARKET_IN, "ALL"]:
            total_loaded += load_indian_symbols()
            logger.info("")
        
        if args.market in [MARKET_US, "ALL"]:
            total_loaded += load_us_symbols()
            logger.info("")
        
        # Verify load
        verify_symbols()
        
        logger.info("")
        logger.info("=" * 70)
        logger.info(f"✓ Symbol load completed successfully!")
        logger.info(f"Total new symbols loaded: {total_loaded}")
        logger.info("=" * 70)
        logger.info("")
        logger.info("Next step: Run historical data ingestion")
        logger.info("  python -m backend.scripts.load_history --sample")
        logger.info("")
        
        return 0
        
    except Exception as e:
        logger.error("=" * 70)
        logger.error(f"✗ Symbol load failed: {e}")
        logger.error("=" * 70)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
