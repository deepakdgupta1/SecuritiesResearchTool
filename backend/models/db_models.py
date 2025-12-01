"""SQLAlchemy ORM models for the Securities Research Tool database.

This module defines all database tables as SQLAlchemy ORM models:
- Symbol: Securities master list
- PriceData: Historical OHLCV data (TimescaleDB hypertable)
- DerivedMetrics: Cached technical indicator calculations
- PatternDetection: Pattern recognition results
- TradeRecommendation: Trading signals and recommendations
- BacktestResult: Backtest summary statistics
- BacktestTrade: Individual trade records from backtests

Models follow the schema defined in docs/architecture/03-Data-Model.md
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, relationship

# Base class for all ORM models
class Base(DeclarativeBase):
    pass


class Symbol(Base):
    """Securities master table containing all symbols across markets.
    
    Attributes:
        id: Primary key (auto-incrementing)
        symbol: Ticker symbol (e.g., 'AAPL', 'RELIANCE') - unique
        name: Company/security name
        exchange: Exchange code (NSE, BSE, NYSE, NASDAQ)
        market: Market region (IN, US)
        sector: Industry sector
        active: Whether symbol is currently active for trading
        created_at: Timestamp when record was created
        
    Relationships:
        price_data: Historical price records
        derived_metrics: Calculated technical indicators
        pattern_detections: Detected chart patterns
        trade_recommendations: Trading signals
        backtest_trades: Trades in backtests
    """
    
    __tablename__ = "symbols"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Symbol identification
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(200))
    
    # Market classification
    exchange = Column(String(20), index=True)  # NSE, BSE, NYSE, NASDAQ
    market = Column(String(10), index=True)  # IN, US
    sector = Column(String(100))
    
    # Status
    active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    price_data = relationship("PriceData", back_populates="symbol", cascade="all, delete-orphan")
    derived_metrics = relationship("DerivedMetrics", back_populates="symbol", cascade="all, delete-orphan")
    pattern_detections = relationship("PatternDetection", back_populates="symbol", cascade="all, delete-orphan")
    trade_recommendations = relationship("TradeRecommendation", back_populates="symbol", cascade="all, delete-orphan")
    backtest_trades = relationship("BacktestTrade", back_populates="symbol", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Symbol(id={self.id}, symbol='{self.symbol}', exchange='{self.exchange}')>"


class PriceData(Base):
    """Historical daily OHLCV price data (TimescaleDB hypertable).
    
    This table stores raw price data for all symbols. Converted to a
    TimescaleDB hypertable for efficient time-series queries.
    
    Attributes:
        symbol_id: Foreign key to symbols table
        date: Trading date
        open: Opening price
        high: High price for the day
        low: Low price for the day
        close: Closing price
        volume: Trading volume (shares)
        adjusted_close: Adjusted close price (after splits/dividends)
        
    Relationships:
        symbol: Reference to Symbol model
    """
    
    __tablename__ = "price_data"
    
    # Composite primary key (symbol_id, date)
    symbol_id = Column(Integer, ForeignKey("symbols.id"), primary_key=True)
    date = Column(Date, primary_key=True, index=True)
    
    # OHLCV data
    open = Column(Numeric(12, 2))
    high = Column(Numeric(12, 2))
    low = Column(Numeric(12, 2))
    close = Column(Numeric(12, 2))
    volume = Column(BigInteger)
    adjusted_close = Column(Numeric(12, 2))
    
    # Relationships
    symbol = relationship("Symbol", back_populates="price_data")
    
    # Additional indexes for common queries
    __table_args__ = (
        Index("ix_price_data_date_symbol", "date", "symbol_id"),
    )
    
    def __repr__(self) -> str:
        return f"<PriceData(symbol_id={self.symbol_id}, date={self.date}, close={self.close})>"


class DerivedMetrics(Base):
    """Cached technical indicators and derived metrics.
    
    Pre-calculated technical indicators to avoid recalculation during
    pattern scanning and backtesting.
    
    Attributes:
        symbol_id: Foreign key to symbols table
        date: Date for which metrics are calculated
        ema_50: 50-day exponential moving average
        ema_150: 150-day exponential moving average
        ema_200: 200-day exponential moving average
        sma_50: 50-day simple moving average
        sma_150: 150-day simple moving average
        sma_200: 200-day simple moving average
        rsi_14: 14-day Relative Strength Index
        macd: MACD line
        macd_signal: MACD signal line
        macd_histogram: MACD histogram
        mansfield_rs: Mansfield Relative Strength score
        week_52_high: 52-week high price
        week_52_low: 52-week low price
        volume_avg_50: 50-day average volume
        
    Relationships:
        symbol: Reference to Symbol model
    """
    
    __tablename__ = "derived_metrics"
    
    # Composite primary key (symbol_id, date)
    symbol_id = Column(Integer, ForeignKey("symbols.id"), primary_key=True)
    date = Column(Date, primary_key=True, index=True)
    
    # Moving averages
    ema_50 = Column(Numeric(12, 4))
    ema_150 = Column(Numeric(12, 4))
    ema_200 = Column(Numeric(12, 4))
    sma_50 = Column(Numeric(12, 4))
    sma_150 = Column(Numeric(12, 4))
    sma_200 = Column(Numeric(12, 4))
    
    # Momentum indicators
    rsi_14 = Column(Numeric(6, 2))
    macd = Column(Numeric(12, 4))
    macd_signal = Column(Numeric(12, 4))
    macd_histogram = Column(Numeric(12, 4))
    
    # Relative strength
    mansfield_rs = Column(Numeric(12, 4))
    
    # 52-week high/low
    week_52_high = Column(Numeric(12, 2))
    week_52_low = Column(Numeric(12, 2))
    
    # Volume
    volume_avg_50 = Column(BigInteger)
    
    # Relationships
    symbol = relationship("Symbol", back_populates="derived_metrics")
    
    # Additional indexes
    __table_args__ = (
        Index("ix_derived_metrics_date_symbol", "date", "symbol_id"),
    )
    
    def __repr__(self) -> str:
        return f"<DerivedMetrics(symbol_id={self.symbol_id}, date={self.date})>"


class PatternDetection(Base):
    """Chart pattern detection results.
    
    Records all detected chart patterns with confidence scores and
    metadata about the pattern characteristics.
    
    Attributes:
        id: Primary key
        symbol_id: Foreign key to symbols table
        detection_date: Date when pattern was detected
        pattern_type: Type of pattern (VCP, CUP_HANDLE, etc.)
        confidence_score: Pattern match quality (0-100)
        weinstein_stage: Weinstein stage (1-4)
        meets_trend_template: Boolean flag for Trend Template criteria
        metadata: JSONB field with pattern-specific details
        created_at: Timestamp when record was created
        
    Relationships:
        symbol: Reference to Symbol model
        trade_recommendations: Associated trade recommendations
    """
    
    __tablename__ = "pattern_detections"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Pattern identification
    symbol_id = Column(Integer, ForeignKey("symbols.id"), nullable=False, index=True)
    detection_date = Column(Date, nullable=False, index=True)
    pattern_type = Column(String(50), index=True)  # VCP, CUP_HANDLE, TREND_TEMPLATE, etc.
    confidence_score = Column(Numeric(5, 2))
    
    # Stage analysis
    weinstein_stage = Column(Integer)  # 1, 2, 3, 4
    meets_trend_template = Column(Boolean, default=False)
    
    # Pattern-specific details stored as JSON
    pattern_metadata = Column(JSONB)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    symbol = relationship("Symbol", back_populates="pattern_detections")
    trade_recommendations = relationship("TradeRecommendation", back_populates="pattern_detection", cascade="all, delete-orphan")
    
    # Additional indexes
    __table_args__ = (
        Index("ix_pattern_detections_date_symbol", "detection_date", "symbol_id"),
        Index("ix_pattern_detections_type_stage", "pattern_type", "weinstein_stage"),
    )
    
    def __repr__(self) -> str:
        return f"<PatternDetection(id={self.id}, symbol_id={self.symbol_id}, pattern='{self.pattern_type}')>"


class TradeRecommendation(Base):
    """Trading signals and recommendations based on pattern detections.
    
    Generated recommendations for entering/exiting positions with
    specific entry, stop-loss, and take-profit levels.
    
    Attributes:
        id: Primary key
        pattern_detection_id: Foreign key to pattern_detections table (optional)
        symbol_id: Foreign key to symbols table
        recommendation_date: Date of recommendation
        trade_type: BUY or SELL
        entry_price: Recommended entry price
        stop_loss: Stop-loss price
        take_profit: Take-profit target price
        position_size_pct: Recommended position size (% of portfolio)
        rationale: Text explanation for the recommendation
        status: OPEN, CLOSED, or CANCELLED
        created_at: Timestamp when record was created
        
    Relationships:
        pattern_detection: Reference to PatternDetection model
        symbol: Reference to Symbol model
    """
    
    __tablename__ = "trade_recommendations"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # References
    pattern_detection_id = Column(Integer, ForeignKey("pattern_detections.id"), index=True)
    symbol_id = Column(Integer, ForeignKey("symbols.id"), nullable=False, index=True)
    
    # Recommendation details
    recommendation_date = Column(Date, nullable=False, index=True)
    trade_type = Column(String(10))  # BUY, SELL
    entry_price = Column(Numeric(12, 2))
    stop_loss = Column(Numeric(12, 2))
    take_profit = Column(Numeric(12, 2))
    position_size_pct = Column(Numeric(5, 2))
    rationale = Column(Text)
    
    # Status tracking
    status = Column(String(20), default="OPEN", index=True)  # OPEN, CLOSED, CANCELLED
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    pattern_detection = relationship("PatternDetection", back_populates="trade_recommendations")
    symbol = relationship("Symbol", back_populates="trade_recommendations")
    
    # Additional indexes
    __table_args__ = (
        Index("ix_trade_recommendations_date_status", "recommendation_date", "status"),
    )
    
    def __repr__(self) -> str:
        return f"<TradeRecommendation(id={self.id}, symbol_id={self.symbol_id}, type='{self.trade_type}')>"


class BacktestResult(Base):
    """Summary statistics for backtest runs.
    
    Stores aggregate performance metrics for each backtest execution.
    
    Attributes:
        id: Primary key
        backtest_name: Descriptive name for the backtest
        start_date: Backtest start date
        end_date: Backtest end date
        strategy_config: JSONB field with strategy parameters
        total_return: Total return percentage
        annualized_return: Annualized return percentage
        cagr: Compound Annual Growth Rate
        sharpe_ratio: Risk-adjusted return metric
        sortino_ratio: Downside risk-adjusted return metric
        max_drawdown: Maximum peak-to-trough decline
        win_rate: Percentage of winning trades
        profit_factor: Gross profit / gross loss
        total_trades: Total number of trades
        winning_trades: Number of profitable trades
        losing_trades: Number of losing trades
        created_at: Timestamp when backtest was run
        
    Relationships:
        backtest_trades: Individual trades in this backtest
    """
    
    __tablename__ = "backtest_results"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Backtest identification
    backtest_name = Column(String(200), index=True)
    start_date = Column(Date)
    end_date = Column(Date)
    strategy_config = Column(JSONB)
    
    # Performance metrics
    total_return = Column(Numeric(10, 4))
    annualized_return = Column(Numeric(10, 4))
    cagr = Column(Numeric(10, 4))
    sharpe_ratio = Column(Numeric(10, 4))
    sortino_ratio = Column(Numeric(10, 4))
    max_drawdown = Column(Numeric(10, 4))
    win_rate = Column(Numeric(5, 2))
    profit_factor = Column(Numeric(10, 4))
    
    # Trade statistics
    total_trades = Column(Integer)
    winning_trades = Column(Integer)
    losing_trades = Column(Integer)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    backtest_trades = relationship("BacktestTrade", back_populates="backtest_result", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<BacktestResult(id={self.id}, name='{self.backtest_name}', return={self.total_return})>"


class BacktestTrade(Base):
    """Individual trade records from backtests.
    
    Detailed record of each trade executed during a backtest,
    including entry/exit prices and performance.
    
    Attributes:
        id: Primary key
        backtest_id: Foreign key to backtest_results table
        symbol_id: Foreign key to symbols table
        entry_date: Trade entry date
        entry_price: Entry price
        exit_date: Trade exit date
        exit_price: Exit price
        position_type: LONG or SHORT
        quantity: Number of shares/units
        profit_loss: Absolute profit/loss in currency
        profit_loss_pct: Percentage profit/loss
        exit_reason: Reason for exit (STOP_LOSS, TAKE_PROFIT, etc.)
        
    Relationships:
        backtest_result: Reference to BacktestResult model
        symbol: Reference to Symbol model
    """
    
    __tablename__ = "backtest_trades"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # References
    backtest_id = Column(Integer, ForeignKey("backtest_results.id"), nullable=False, index=True)
    symbol_id = Column(Integer, ForeignKey("symbols.id"), nullable=False, index=True)
    
    # Trade details
    entry_date = Column(Date, index=True)
    entry_price = Column(Numeric(12, 2))
    exit_date = Column(Date, index=True)
    exit_price = Column(Numeric(12, 2))
    position_type = Column(String(10))  # LONG, SHORT
    quantity = Column(Integer)
    
    # Performance
    profit_loss = Column(Numeric(12, 2))
    profit_loss_pct = Column(Numeric(10, 4))
    exit_reason = Column(String(50))  # STOP_LOSS, TAKE_PROFIT, TRAILING_STOP, SIGNAL
    
    # Relationships
    backtest_result = relationship("BacktestResult", back_populates="backtest_trades")
    symbol = relationship("Symbol", back_populates="backtest_trades")
    
    # Additional indexes
    __table_args__ = (
        Index("ix_backtest_trades_dates", "entry_date", "exit_date"),
    )
    
    def __repr__(self) -> str:
        return f"<BacktestTrade(id={self.id}, symbol_id={self.symbol_id}, pnl={self.profit_loss})>"
