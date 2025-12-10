from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, Optional

import pandas as pd


@dataclass
class PatternResult:
    """Standardized result from a pattern detection algorithm."""
    pattern_type: str
    symbol: str
    detection_date: date
    confidence_score: float  # 0.0 to 100.0
    confirmed: bool = False
    meta_data: Dict[str, Any] = field(default_factory=dict)

    # Specific fields matching DB model optimized for SEPA
    weinstein_stage: Optional[int] = None
    meets_trend_template: bool = False


class PatternDetector(ABC):
    """Abstract base class for all chart pattern detectors."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def detect(
            self,
            symbol: str,
            data: pd.DataFrame) -> Optional[PatternResult]:
        """
        Detects the pattern in the provided historical data.

        Args:
            symbol: Ticker symbol being analyzed
            data: DataFrame containing OHLCV data.
                  Expected columns: 'open', 'high', 'low', 'close', 'volume'.
                  Index should be DatetimeIndex.

        Returns:
            PatternResult if pattern is detected and meets minimum criteria,
            None otherwise.
        """
