"""
Indicator Manager module.
Orchestrates the calculation of all technical indicators for symbols.
"""

import logging
from datetime import datetime
from typing import List, Optional

import pandas as pd
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from backend.core.database import get_session, execute_with_retry
from backend.models.db_models import Symbol, DerivedMetrics, PriceData
from backend.indicators.utils import get_price_data
from backend.indicators.moving_averages import calculate_all_moving_averages
from backend.indicators.momentum import calculate_all_momentum_indicators
from backend.indicators.price_action import calculate_52_week_high_low
from backend.indicators.volume import calculate_all_volume_indicators
from backend.indicators.relative_strength import calculate_mansfield_rs

logger = logging.getLogger(__name__)


class IndicatorManager:
    """
    Manager class to handle technical indicator calculations.
    """

    def __init__(self, session: Session = None):
        """
        Initialize the manager.
        
        Args:
            session: Optional SQLAlchemy session. If not provided, methods will create their own.
        """
        self.session = session

    def calculate_for_symbol(self, symbol_id: int, benchmark_df: Optional[pd.DataFrame] = None) -> bool:
        """
        Calculate all indicators for a specific symbol and save to DB.

        Args:
            symbol_id: ID of the symbol.
            benchmark_df: DataFrame of the benchmark symbol (for RS calculation).

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Use provided session or create a new one
            if self.session:
                return self._calculate_with_session(self.session, symbol_id, benchmark_df)
            else:
                with get_session() as session:
                    return self._calculate_with_session(session, symbol_id, benchmark_df)
        except Exception as e:
            logger.error(f"Error calculating indicators for symbol {symbol_id}: {e}")
            return False

    def _calculate_with_session(self, session: Session, symbol_id: int, benchmark_df: Optional[pd.DataFrame]) -> bool:
        """Internal method to calculate using a specific session."""
        # 1. Fetch price data
        df = get_price_data(symbol_id, session)
        
        if df.empty:
            logger.warning(f"No price data found for symbol {symbol_id}")
            return False
            
        if len(df) < 50:  # Minimum data requirement
            logger.warning(f"Insufficient data for symbol {symbol_id}: {len(df)} rows")
            return False

        # 2. Calculate Indicators
        # Moving Averages
        df = calculate_all_moving_averages(df)
        
        # Momentum
        df = calculate_all_momentum_indicators(df)
        
        # Price Action
        df = calculate_52_week_high_low(df)
        
        # Volume
        df = calculate_all_volume_indicators(df)
        
        # Relative Strength
        if benchmark_df is not None and not benchmark_df.empty:
            df["mansfield_rs"] = calculate_mansfield_rs(df, benchmark_df)
        else:
            df["mansfield_rs"] = None

        # 3. Prepare data for insertion
        # We want to save the calculated metrics to DerivedMetrics table.
        # We should probably clear existing metrics for this symbol to avoid duplicates or use upsert.
        # For simplicity/performance in batch, we might delete and re-insert or use merge.
        # Given the volume of data, upsert is better.
        
        metrics_objects = []
        for date, row in df.iterrows():
            # Skip rows where critical indicators might be NaN if we want to save space,
            # but usually we want to save what we have.
            # However, DerivedMetrics table has nullable columns for indicators.
            
            # Check if we have at least some data calculated (e.g. SMA_50)
            # if pd.isna(row["sma_50"]): continue
            
            metrics = DerivedMetrics(
                symbol_id=symbol_id,
                date=date.date(),
                ema_50=row.get("ema_50") if not pd.isna(row.get("ema_50")) else None,
                ema_150=row.get("ema_150") if not pd.isna(row.get("ema_150")) else None,
                ema_200=row.get("ema_200") if not pd.isna(row.get("ema_200")) else None,
                sma_50=row.get("sma_50") if not pd.isna(row.get("sma_50")) else None,
                sma_150=row.get("sma_150") if not pd.isna(row.get("sma_150")) else None,
                sma_200=row.get("sma_200") if not pd.isna(row.get("sma_200")) else None,
                rsi_14=row.get("rsi_14") if not pd.isna(row.get("rsi_14")) else None,
                macd=row.get("macd") if not pd.isna(row.get("macd")) else None,
                macd_signal=row.get("macd_signal") if not pd.isna(row.get("macd_signal")) else None,
                macd_histogram=row.get("macd_histogram") if not pd.isna(row.get("macd_histogram")) else None,
                mansfield_rs=row.get("mansfield_rs") if not pd.isna(row.get("mansfield_rs")) else None,
                week_52_high=row.get("week_52_high") if not pd.isna(row.get("week_52_high")) else None,
                week_52_low=row.get("week_52_low") if not pd.isna(row.get("week_52_low")) else None,
                volume_avg_50=int(row.get("volume_avg_50")) if not pd.isna(row.get("volume_avg_50")) else None,
            )
            metrics_objects.append(metrics)

        # 4. Save to DB
        # Delete existing for this symbol to avoid conflicts (simplest approach for full recalc)
        # In production with incremental updates, we would only calculate new days.
        # For MVP full recalc, delete-insert is fine.
        session.execute(delete(DerivedMetrics).where(DerivedMetrics.symbol_id == symbol_id))
        
        # Bulk save
        session.add_all(metrics_objects)
        # Commit is handled by the context manager in the caller if not provided
        if not self.session:
            session.commit()
            
        return True

    def calculate_all(self, benchmark_symbol: str = "^NSEI") -> None:
        """
        Calculate indicators for all active symbols.
        
        Args:
            benchmark_symbol: Ticker of the benchmark symbol.
        """
        with get_session() as session:
            # 1. Get benchmark data
            benchmark = session.execute(select(Symbol).where(Symbol.symbol == benchmark_symbol)).scalar_one_or_none()
            benchmark_df = None
            if benchmark:
                benchmark_df = get_price_data(benchmark.id, session)
                logger.info(f"Loaded benchmark data for {benchmark_symbol}: {len(benchmark_df)} rows")
            else:
                logger.warning(f"Benchmark symbol {benchmark_symbol} not found. RS will be skipped.")

            # 2. Get all active symbols
            symbols = session.execute(select(Symbol).where(Symbol.active == True)).scalars().all()
            logger.info(f"Found {len(symbols)} active symbols")
            
            # 3. Process each symbol
            count = 0
            for symbol in symbols:
                if symbol.symbol == benchmark_symbol:
                    continue
                    
                logger.info(f"Processing {symbol.symbol}...")
                success = self._calculate_with_session(session, symbol.id, benchmark_df)
                if success:
                    count += 1
                
                # Commit every 10 symbols to avoid huge transaction
                if count % 10 == 0:
                    session.commit()
            
            session.commit()
            logger.info(f"Completed indicator calculation for {count} symbols")
