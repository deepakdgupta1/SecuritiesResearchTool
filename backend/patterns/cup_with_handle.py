from typing import Optional

import pandas as pd

from .base import PatternDetector, PatternResult
from .utils import calculate_percentage_change, find_local_extrema


class CupWithHandleDetector(PatternDetector):
    """
    Detects Cup & Handle patterns.

    Characteristics:
    - Cup depth: 12% to 35% (shallow cup is better)
    - Cup length: 7 weeks to 65 weeks
    - Handle: Downward drift, typically 1-4 weeks
    - Handle should not drop below the midpoint of the cup
    - Volume: Dry up at the low of the cup, increases on breakout
    """

    def __init__(
        self,
        min_cup_depth_pct: float = 12.0,
        max_cup_depth_pct: float = 35.0,
        min_cup_length_days: int = 35,
        max_cup_length_days: int = 325,
    ):
        super().__init__("Cup & Handle")
        self.min_cup_depth_pct = min_cup_depth_pct
        self.max_cup_depth_pct = max_cup_depth_pct
        self.min_cup_length_days = min_cup_length_days
        self.max_cup_length_days = max_cup_length_days

    def detect(
            self,
            symbol: str,
            data: pd.DataFrame) -> Optional[PatternResult]:
        if len(data) < self.min_cup_length_days:
            return None

        highs = data["high"]
        lows = data["low"]

        max_indices, min_indices = find_local_extrema(highs, order=5)

        if len(max_indices) < 2 or not min_indices:
            return None

        # Look for cup structure: High -> Low -> High (approximately same level)
        # Find the two highest peaks in the window
        recent_cutoff = max(0, len(data) - self.max_cup_length_days)
        max_indices = [i for i in max_indices if i >= recent_cutoff]
        min_indices = [i for i in min_indices if i >= recent_cutoff]

        if len(max_indices) < 2:
            return None

        # Sort by value to find the two highest peaks
        peak_values = [(i, highs.iloc[i]) for i in max_indices]
        peak_values.sort(key=lambda x: x[1], reverse=True)

        # Try pairs of peaks to find a cup
        for i in range(len(peak_values) - 1):
            left_peak_idx, left_peak_val = peak_values[i]
            for j in range(i + 1, len(peak_values)):
                right_peak_idx, right_peak_val = peak_values[j]

                # Ensure left is before right
                if left_peak_idx > right_peak_idx:
                    left_peak_idx, right_peak_idx = right_peak_idx, left_peak_idx
                    left_peak_val, right_peak_val = right_peak_val, left_peak_val

                # Check cup length
                cup_length = right_peak_idx - left_peak_idx
                if cup_length < self.min_cup_length_days:
                    continue

                # Find lowest point between peaks (cup bottom)
                interval_mins = [
                    m for m in min_indices if left_peak_idx < m < right_peak_idx]
                if not interval_mins:
                    continue

                cup_bottom_idx = min(interval_mins, key=lambda x: lows.iloc[x])
                cup_bottom_val = lows.iloc[cup_bottom_idx]

                # Calculate cup depth
                cup_depth_pct = abs(
                    calculate_percentage_change(left_peak_val, cup_bottom_val)
                )

                if not (self.min_cup_depth_pct <=
                        cup_depth_pct <= self.max_cup_depth_pct):
                    continue

                # Check if right peak is within 5% of left peak (symmetry)
                peak_diff_pct = abs(
                    calculate_percentage_change(left_peak_val, right_peak_val)
                )
                if peak_diff_pct > 10.0:
                    continue

                # Look for handle after right peak
                handle_data = data.iloc[right_peak_idx:]
                if len(handle_data) < 5:
                    # No handle yet, but cup is forming
                    return PatternResult(
                        pattern_type="CUP_FORMING",
                        symbol=symbol,
                        detection_date=data.index[-1].date(),
                        confidence_score=60.0,
                        confirmed=False,
                        meta_data={
                            "cup_depth_pct": cup_depth_pct,
                            "cup_length_days": cup_length,
                            "left_peak": float(left_peak_val),
                            "right_peak": float(right_peak_val),
                        },
                    )

                # Check handle characteristics
                handle_low = handle_data["low"].min()
                cup_midpoint = (left_peak_val + cup_bottom_val) / 2

                if handle_low < cup_midpoint:
                    continue  # Handle too deep

                return PatternResult(
                    pattern_type="CUP_AND_HANDLE",
                    symbol=symbol,
                    detection_date=data.index[-1].date(),
                    confidence_score=80.0,
                    confirmed=True,
                    meta_data={
                        "cup_depth_pct": cup_depth_pct,
                        "cup_length_days": cup_length,
                        "handle_depth": float(
                            abs(calculate_percentage_change(right_peak_val, handle_low))
                        ),
                    },
                )

        return None
