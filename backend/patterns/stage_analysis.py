from typing import Optional

import pandas as pd

from .base import PatternDetector, PatternResult


class WeinsteinStageAnalyzer(PatternDetector):
    """
    Classifies securities into Weinstein's 4 Stages.

    Stage 1: Basing (Accumulation) - Price flat, below declining MA
    Stage 2: Advancing (Markup) - Price rising above rising MA (BUY ZONE)
    Stage 3: Topping (Distribution) - Price flat, MA flattening
    Stage 4: Declining (Markdown) - Price falling below declining MA (AVOID)

    Focus is on identifying Stage 2 for entries.
    Uses 30-week (150-day) moving average as primary indicator.
    """

    def __init__(self, ma_period: int = 150, slope_window: int = 20):
        super().__init__("Weinstein Stage Analysis")
        self.ma_period = ma_period
        self.slope_window = slope_window

    def detect(
            self,
            symbol: str,
            data: pd.DataFrame) -> Optional[PatternResult]:
        if len(data) < self.ma_period + self.slope_window:
            return None

        if "sma_150" not in data.columns:
            # Calculate if not present
            data = data.copy()
            data["sma_150"] = data["close"].rolling(
                window=self.ma_period).mean()

        current = data.iloc[-1]
        close = current["close"]
        sma_150 = current["sma_150"]

        if pd.isna(sma_150):
            return None

        # Calculate MA slope (is it rising or falling?)
        past_ma = data["sma_150"].iloc[-self.slope_window]
        if pd.isna(past_ma):
            return None

        ma_change_pct = ((sma_150 - past_ma) / past_ma) * 100

        # Determine stage
        price_above_ma = close > sma_150
        ma_rising = ma_change_pct > 0.5  # Threshold for "rising"
        ma_falling = ma_change_pct < -0.5  # Threshold for "falling"
        ma_flat = not ma_rising and not ma_falling

        # Stage classification logic
        stage = 0
        stage_name = ""
        confidence = 0.0

        if not price_above_ma and ma_falling:
            stage = 4
            stage_name = "Stage 4 - Declining"
            confidence = 70.0
        elif not price_above_ma and ma_flat:
            stage = 1
            stage_name = "Stage 1 - Basing"
            confidence = 60.0
        elif price_above_ma and ma_rising:
            stage = 2
            stage_name = "Stage 2 - Advancing"
            confidence = 85.0  # High confidence in Stage 2
        elif price_above_ma and ma_flat:
            stage = 3
            stage_name = "Stage 3 - Topping"
            confidence = 65.0
        else:
            # Transitional or unclear
            stage = 0
            stage_name = "Transitional"
            confidence = 40.0

        return PatternResult(
            pattern_type="WEINSTEIN_STAGE",
            symbol=symbol,
            detection_date=data.index[-1].date(),
            confidence_score=confidence,
            confirmed=(stage == 2),
            # Only Stage 2 is "confirmed" as actionable
            weinstein_stage=stage,
            meta_data={
                "stage": stage,
                "stage_name": stage_name,
                "price": float(close),
                "sma_150": float(sma_150),
                "ma_slope_pct": ma_change_pct,
            },
        )
