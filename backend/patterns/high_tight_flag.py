from datetime import date
from typing import Optional
import numpy as np
import pandas as pd
from .base import PatternDetector, PatternResult
from .utils import calculate_percentage_change


class HighTightFlagDetector(PatternDetector):
    """
    Detects High-Tight Flag patterns.

    Characteristics:
    - Prior move: 100%+ gain in 4-8 weeks (extremely strong momentum)
    - Consolidation: 10-25% correction (tight)
    - Consolidation length: 3-5 weeks typically
    - One of the rarest and most powerful patterns
    """

    def __init__(
        self,
        min_prior_gain_pct: float = 100.0,
        max_prior_gain_weeks: int = 8,
        min_prior_gain_weeks: int = 4,
        max_consolidation_pct: float = 25.0,
    ):
        super().__init__("High-Tight Flag")
        self.min_prior_gain_pct = min_prior_gain_pct
        self.max_prior_gain_weeks = max_prior_gain_weeks
        self.min_prior_gain_weeks = min_prior_gain_weeks
        self.max_consolidation_pct = max_consolidation_pct

    def detect(self, symbol: str, data: pd.DataFrame) -> Optional[PatternResult]:
        min_days = self.min_prior_gain_weeks * 5  # 5 trading days per week
        max_days = self.max_prior_gain_weeks * 5

        if len(data) < max_days + 25:  # Need enough history
            return None

        closes = data["close"]
        highs = data["high"]
        lows = data["low"]

        # Look for the pattern ending recently
        # Find potential flag pole (100%+ move)
        for lookback in range(min_days, max_days + 1, 5):
            # Check if there was a 100%+ move
            for pole_end_offset in range(10, 35, 5):
                recent_high_idx = len(data) - pole_end_offset
                pole_start_idx = recent_high_idx - lookback

                if pole_start_idx < 0 or recent_high_idx < 0:
                    continue

                pole_start_price = closes.iloc[pole_start_idx]
                pole_end_price = highs.iloc[pole_start_idx:recent_high_idx + 1].max()
                pole_end_idx = highs.iloc[pole_start_idx:recent_high_idx + 1].idxmax()

                gain_pct = calculate_percentage_change(
                    pole_start_price, pole_end_price
                )

                if gain_pct < self.min_prior_gain_pct:
                    continue

                # Check consolidation (flag) after the pole
                pole_end_pos = data.index.get_loc(pole_end_idx)
                flag_data = data.iloc[pole_end_pos:]

                if len(flag_data) < 10:
                    continue

                flag_high = flag_data["high"].max()
                flag_low = flag_data["low"].min()
                consolidation_pct = abs(
                    calculate_percentage_change(flag_high, flag_low)
                )

                if consolidation_pct > self.max_consolidation_pct:
                    continue

                # Valid High-Tight Flag detected
                return PatternResult(
                    pattern_type="HIGH_TIGHT_FLAG",
                    symbol=symbol,
                    detection_date=data.index[-1].date(),
                    confidence_score=90.0,
                    confirmed=True,
                    meta_data={
                        "prior_gain_pct": gain_pct,
                        "consolidation_pct": consolidation_pct,
                        "pole_length_days": lookback,
                        "flag_length_days": len(flag_data),
                    },
                )

        return None
