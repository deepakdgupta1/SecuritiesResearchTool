from typing import Dict, List, Optional, Type
import pandas as pd
from .base import PatternDetector, PatternResult
from .trend_template import TrendTemplateDetector
from .vcp import VCPDetector
from .cup_with_handle import CupWithHandleDetector
from .double_bottom import DoubleBottomDetector
from .high_tight_flag import HighTightFlagDetector
from .stage_analysis import WeinsteinStageAnalyzer


class PatternScanner:
    """
    Orchestrates pattern scanning across multiple symbols.

    Manages multiple pattern detectors and runs them in batch
    against the provided price data.
    """

    def __init__(self, detectors: Optional[List[PatternDetector]] = None):
        """
        Initialize the scanner with detectors.

        Args:
            detectors: List of pattern detectors to use.
                       If None, uses all available detectors.
        """
        if detectors is None:
            self.detectors = self._get_default_detectors()
        else:
            self.detectors = detectors

    def _get_default_detectors(self) -> List[PatternDetector]:
        """Returns all available pattern detectors."""
        return [
            TrendTemplateDetector(),
            VCPDetector(),
            CupWithHandleDetector(),
            DoubleBottomDetector(),
            HighTightFlagDetector(),
            WeinsteinStageAnalyzer(),
        ]

    def scan_symbol(
        self, symbol: str, data: pd.DataFrame
    ) -> List[PatternResult]:
        """
        Scans a single symbol for all patterns.

        Args:
            symbol: Ticker symbol
            data: OHLCV DataFrame with DatetimeIndex

        Returns:
            List of detected patterns
        """
        results = []
        for detector in self.detectors:
            try:
                result = detector.detect(symbol, data)
                if result is not None:
                    results.append(result)
            except Exception:
                # Log error but continue with other detectors
                pass
        return results

    def scan_universe(
        self, symbol_data: Dict[str, pd.DataFrame]
    ) -> Dict[str, List[PatternResult]]:
        """
        Scans multiple symbols.

        Args:
            symbol_data: Dict mapping symbol -> OHLCV DataFrame

        Returns:
            Dict mapping symbol -> list of detected patterns
        """
        all_results: Dict[str, List[PatternResult]] = {}
        for symbol, data in symbol_data.items():
            patterns = self.scan_symbol(symbol, data)
            if patterns:
                all_results[symbol] = patterns
        return all_results

    def get_actionable_setups(
        self, symbol_data: Dict[str, pd.DataFrame], min_confidence: float = 70.0
    ) -> List[PatternResult]:
        """
        Returns patterns that meet actionable criteria.

        Filters for:
        - Stage 2 stocks (if Weinstein detected)
        - Trend Template confirmed
        - Confidence >= min_confidence

        Args:
            symbol_data: Dict mapping symbol -> OHLCV DataFrame
            min_confidence: Minimum confidence score

        Returns:
            List of actionable PatternResult objects
        """
        all_results = self.scan_universe(symbol_data)
        actionable = []

        for symbol, patterns in all_results.items():
            for pattern in patterns:
                if pattern.confidence_score >= min_confidence:
                    if pattern.confirmed or pattern.meets_trend_template:
                        actionable.append(pattern)

        # Sort by confidence descending
        actionable.sort(key=lambda p: p.confidence_score, reverse=True)
        return actionable
