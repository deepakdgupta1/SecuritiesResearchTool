"""
Utility functions for indicator calculations.
"""

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.database import get_session
from backend.models.db_models import PriceData


def get_price_data(symbol_id: int, session: Session = None) -> pd.DataFrame:
    """
    Fetch historical price data for a symbol and return as a DataFrame.

    Args:
        symbol_id: The ID of the symbol to fetch data for.
        session: Optional SQLAlchemy session. If not provided, a new one will be created.

    Returns:
        pd.DataFrame: DataFrame with columns [open, high, low, close, volume, adjusted_close]
                      indexed by date.
    """
    query = select(PriceData).where(
        PriceData.symbol_id == symbol_id).order_by(
        PriceData.date)

    if session:
        result = session.execute(query).scalars().all()
        data = [
            {
                "date": r.date, "open": float(
                    r.open), "high": float(
                    r.high), "low": float(
                    r.low), "close": float(
                        r.close), "volume": int(
                            r.volume), "adjusted_close": float(
                                r.adjusted_close) if r.adjusted_close else float(
                                    r.close), } for r in result]
    else:
        with get_session() as sess:
            result = sess.execute(query).scalars().all()
            data = [
                {
                    "date": r.date, "open": float(
                        r.open), "high": float(
                        r.high), "low": float(
                        r.low), "close": float(
                        r.close), "volume": int(
                            r.volume), "adjusted_close": float(
                                r.adjusted_close) if r.adjusted_close else float(
                                    r.close), } for r in result]

    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    return df
