from datetime import date
from typing import Optional
import numpy as np
import pandas as pd
from .base import PatternDetector, PatternResult
from .utils import find_local_extrema, calculate_percentage_change


class DoubleBottomDetector(PatternDetector):
    """
    Detects Double Bottom patterns ("W" shape).

    Characteristics:
    - Two distinct lows at approximately the same price level
    - Separation of 2-7 weeks between lows
    - Second low may undercut first low slightly (shakeout)
    - Volume typically higher on first low, dry on second
    """

    def __init__(
        self,
        max_low_diff_pct: float = 5.0,
        min_separation_days: int = 10,
        max_separation_days: int = 50,
    ):
        super().__init__("Double Bottom")
        self.max_low_diff_pct = max_low_diff_pct
        self.min_separation_days = min_separation_days
        self.max_separation_days = max_separation_days

    def detect(self, symbol: str, data: pd.DataFrame) -> Optional[PatternResult]:
        if len(data) < self.min_separation_days * 2:
            return None

        lows = data["low"]
        highs = data["high"]

        _, min_indices = find_local_extrema(lows, order=5)

        if len(min_indices) < 2:
            return None

        # Look for two lows at similar levels
        recent_cutoff = max(0, len(data) - 100)
        min_indices = [i for i in min_indices if i >= recent_cutoff]

        if len(min_indices) < 2:
            return None

        # Check pairs of lows
        for i in range(len(min_indices) - 1):
            first_low_idx = min_indices[i]
            for j in range(i + 1, len(min_indices)):
                second_low_idx = min_indices[j]

                separation = second_low_idx - first_low_idx
                if not (self.min_separation_days <= separation <= self.max_separation_days):
                    continue

                first_low_val = lows.iloc[first_low_idx]
                second_low_val = lows.iloc[second_low_idx]

                # Check if lows are at similar levels
                low_diff_pct = abs(
                    calculate_percentage_change(first_low_val, second_low_val)
                )
                if low_diff_pct > self.max_low_diff_pct:
                    continue

                # Find the peak between the two lows (the "middle" of the W)
                interval_highs = highs.iloc[first_low_idx:second_low_idx]
                if interval_highs.empty:
                    continue

                middle_peak_val = interval_highs.max()
                middle_peak_idx = interval_highs.idxmax()

                # Calculate pattern depth
                depth_pct = calculate_percentage_change(middle_peak_val, first_low_val)

                # Undercut check (second low slightly below first is bullish)
                is_undercut = bool(second_low_val < first_low_val)

                return PatternResult(
                    pattern_type="DOUBLE_BOTTOM",
                    symbol=symbol,
                    detection_date=data.index[-1].date(),
                    confidence_score=85.0 if is_undercut else 75.0,
                    confirmed=True,
                    meta_data={
                        "first_low": float(first_low_val),
                        "second_low": float(second_low_val),
                        "middle_peak": float(middle_peak_val),
                        "depth_pct": abs(depth_pct),
                        "separation_days": separation,
                        "is_undercut": is_undercut,
                    },
                )

        return None
