from datetime import date
from typing import Optional
import pandas as pd
from .base import PatternDetector, PatternResult

class TrendTemplateDetector(PatternDetector):
    """
    Detects Mark Minervini's Trend Template criteria.
    
    Criteria:
    1. Stock price is above both the 150-day (30-week) and the 200-day (40-week) moving average price line.
    2. The 150-day moving average is above the 200-day moving average.
    3. The 200-day moving average price line is trending up for at least 1 month (approx 20 trading days).
    4. The 50-day (10-week) moving average is above both the 150-day and 200-day moving averages.
    5. The current stock price is trading above the 50-day moving average.
    6. The current stock price is at least 30 percent above its 52-week low.
    7. The current stock price is within at least 25 percent of its 52-week high.
    8. The Relative Strength (RS) rating is not below 70 (optional strictness).
    """
    
    def __init__(self) -> None:
        super().__init__("Trend Template")

    def detect(self, symbol: str, data: pd.DataFrame) -> Optional[PatternResult]:
        """
        Checks if the latest data point meets the Trend Template criteria.
        Expects data to contain pre-calculated metrics keys:
        - close
        - sma_50
        - sma_150
        - sma_200
        - week_52_high
        - week_52_low
        - mansfield_rs (optional, but recommended)
        """
        if data.empty:
            return None
            
        current = data.iloc[-1]
        
        # Ensure required columns exist
        required_cols = ['close', 'sma_50', 'sma_150', 'sma_200', 'week_52_high', 'week_52_low']
        for col in required_cols:
            if col not in current.index or pd.isna(current[col]):
                # If crucial data is missing, cannot evaluate
                return None
                
        close = current['close']
        sma_50 = current['sma_50']
        sma_150 = current['sma_150']
        sma_200 = current['sma_200']
        week_52_high = current['week_52_high']
        week_52_low = current['week_52_low']
        
        # 1. Price > 150-day and 200-day MA
        c1 = (close > sma_150) and (close > sma_200)
        
        # 2. 150-day MA > 200-day MA
        c2 = (sma_150 > sma_200)
        
        # 3. 200-day MA trending up for at least 1 month (20 days)
        # We need historical data for this. Check if data length supports it.
        c3 = False
        if len(data) >= 20:
            past_sma_200 = data['sma_200'].iloc[-20]
            if not pd.isna(past_sma_200):
                c3 = (sma_200 > past_sma_200)
        
        # 4. 50-day MA > 150-day and 200-day MA
        c4 = (sma_50 > sma_150) and (sma_50 > sma_200)
        
        # 5. Price > 50-day MA
        c5 = (close > sma_50)
        
        # 6. Price >= 1.30 * 52-week low (30% above low)
        c6 = (close >= (1.30 * week_52_low))
        
        # 7. Price >= 0.75 * 52-week high (Within 25% of high)
        # "Within 25% of high" usually means price is >= 75% of the high.
        c7 = (close >= (0.75 * week_52_high))
        
        # 8. RS Rating > 70
        # If mansfield_rs is not present to proxy RS Rating, we might skip or fail.
        # Assuming simple check if column exists.
        c8 = True
        if 'mansfield_rs' in current.index and not pd.isna(current['mansfield_rs']):
             # Mansfield RS is centered around 0. RS Rating (IBD style 1-99) is different.
             # Standardizing: If using Mansfield, positive is good. 
             # Let's assume for this strict template we want strong positive momentum.
             # Phase 2 defined Mansfield RS. 
             # For now, let's require Mansfield RS > 0 as a loose proxy for "better than market"
             # or create a mapping. The requirement says "RS Rating not below 70".
             # Since we only have Mansfield RS (relative strength vs SPY/Nifty), 
             # let's assume > 0.5 (or some threshold) implies strength.
             # Or just check if it's positive. Let's stick to positive for now.
             c8 = (current['mansfield_rs'] > 0)
        
        all_criteria_met = c1 and c2 and c3 and c4 and c5 and c6 and c7 and c8
        
        if all_criteria_met:
            return PatternResult(
                pattern_type="TREND_TEMPLATE",
                symbol=symbol,
                detection_date=current.name.date() if hasattr(current.name, 'date') else date.today(),
                confidence_score=90.0 if c8 else 70.0, # Higher confidence if RS checked
                confirmed=True,
                meets_trend_template=True,
                meta_data={
                    "sma_50": float(sma_50),
                    "sma_200": float(sma_200),
                    "distance_from_high_pct": float((week_52_high - close) / week_52_high * 100),
                    "distance_from_low_pct": float((close - week_52_low) / week_52_low * 100)
                }
            )
            
        return None
