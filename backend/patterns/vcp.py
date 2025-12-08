from datetime import date
from typing import Optional, List, Dict, Any
import numpy as np
import pandas as pd
from .base import PatternDetector, PatternResult
from .utils import find_local_extrema, is_volume_drying_up, calculate_percentage_change

class VCPDetector(PatternDetector):
    """
    Detects Volatility Contraction Patterns (VCP).
    
    Characteristics:
    - 2 to 6 contractions (usually 2-4).
    - Successive contractions result in smaller price corrections (depth decreases).
    - Volume dries up during the consolidation, especially on the right side.
    - Timeframe: Usually 3 weeks to 65 weeks.
    """
    
    def __init__(self, min_contractions: int = 2, max_contractions: int = 5):
        super().__init__("VCP")
        self.min_contractions = min_contractions
        self.max_contractions = max_contractions

    def detect(self, symbol: str, data: pd.DataFrame) -> Optional[PatternResult]:
        if len(data) < 50:
            return None
            
        # Analysis window: Last 250 days (approx 1 year) max, 
        # but pattern is usually shorter. 
        # Let's focus on identifying the pattern leading up to the MOST RECENT data point.
        # The breakout might have just happened or is setting up.
        # SEPA usually scans for setups *before* breakout or *at* breakout.
        
        # 1. Start with high/low analysis on highs
        # We need local maxima to identify the "tops" of the contractions.
        highs = data['high']
        lows = data['low']
        
        # Get local extrema
        max_indices, min_indices = find_local_extrema(highs, order=5)
        
        # We need to parse these extrema to find a VCP structure ending near the current date.
        # Heuristic:
        # Find the highest high in the last 6 months (base start).
        # Check if we have a series of lower highs and higher lows? 
        # No, VCP is about *depth of correction*, not necessarily triangle convergence (slope), 
        # though often they look like triangles.
        # Key is: High1 -> Low1 (Depth1), High2 -> Low2 (Depth2), ...
        # where High2 < High1 (usually), and Depth2 < Depth1.
        
        if not max_indices:
            return None
            
        # Filter for recent relevant extrema (last 250 days or all data)
        recent_cutoff = max(0, len(data) - 250)
        max_indices = [i for i in max_indices if i >= recent_cutoff]
        min_indices = [i for i in min_indices if i >= recent_cutoff]
        
        if len(max_indices) < 2:
            return None
            
        # Try to find a valid VCP sequence ending recently
        # We iterate backwards from the latest potential top
        
        # Find the global high in this window - identifying the "Left Side" of the base
        # This naive approach assumes the base started at the highest point in the window.
        window_highs = highs.iloc[max_indices]
        if window_highs.empty:
            return None
        base_start_idx = window_highs.idxmax() # Index in data (datetime or integer?)
        # data index is datetime usually, but max_indices are integer positions
        # Let's map back to integer index
        try:
             # window_highs index is the integer position from iloc? No.
             # highs.iloc[max_indices] keeps the original index (datetime).
             # We want the integer location.
             # improved:
             base_start_pos = -1
             base_high_val = -1.0
             
             for idx in max_indices:
                 val = highs.iloc[idx]
                 if val > base_high_val:
                     base_high_val = val
                     base_start_pos = idx
        except Exception:
             return None

        if base_start_pos == -1:
            return None
            
        # Now look for contractions after base_start_pos
        # A contraction is defined by a High -> Low -> High (next pivot)
        # We collect (High_pos, Low_pos) pairs
        
        relevant_max = [i for i in max_indices if i >= base_start_pos]
        relevant_min = [i for i in min_indices if i > base_start_pos]
        
        if len(relevant_max) < 2 or not relevant_min:
             return None
             
        contractions = []
        
        # Greedy matching: for each High, find the deepest Low before the next High
        for i in range(len(relevant_max) - 1):
            h1_pos = relevant_max[i]
            h2_pos = relevant_max[i+1]
            
            # Find lowest low between h1 and h2
            interval_mins = [m for m in relevant_min if h1_pos < m < h2_pos]
            if not interval_mins:
                continue
                
            # Find the minimum value in this interval
            # interval_mins contains indices.
            min_pos = -1
            min_val = float('inf')
            for m in interval_mins:
                val = lows.iloc[m]
                if val < min_val:
                    min_val = val
                    min_pos = m
            
            if min_pos != -1:
                # Calculate depth
                high_val = highs.iloc[h1_pos]
                depth_pct = abs(calculate_percentage_change(high_val, min_val))
                contractions.append({
                    'start_high_idx': h1_pos, 
                    'low_idx': min_pos, 
                    'end_high_idx': h2_pos,
                    'depth': depth_pct
                })
        
        # Check if last contraction is ongoing (current price is near potential pivot or breakout)
        # For now, we only look at completed contractions or "setting up"
        # If we found at least 2 contractions
        if len(contractions) < self.min_contractions:
            return None
            
        # Check VCP criteria: Depth should decrease
        # e.g. -20%, -10%, -5%
        valid_structure = True
        for i in range(1, len(contractions)):
            prev_depth = contractions[i-1]['depth']
            curr_depth = contractions[i]['depth']
            
            # Allow some tolerance, but generally current should be smaller
            if curr_depth > prev_depth * 1.2: # allow slightly larger but generally should be smaller
                valid_structure = False
                break
                
        if not valid_structure:
            return None
            
        # Check Volume Dry Up
        # Volume should be lower on the right side of the base
        vol_dry = is_volume_drying_up(data['volume'], window=20)
        
        # Final confirmation
        # Check if the last contraction is "tight" (e.g. < 10-15%)
        last_depth = contractions[-1]['depth']
        is_tight = last_depth < 15.0
        
        if valid_structure and is_tight:
             return PatternResult(
                pattern_type="VCP",
                symbol=symbol,
                detection_date=data.index[-1].date(),
                confidence_score=85.0 if vol_dry else 70.0,
                confirmed=False, # pattern detected but maybe not triggered entry yet
                meta_data={
                    "contractions": len(contractions),
                    "depths": [c['depth'] for c in contractions],
                    "volume_dry_up": vol_dry
                }
            )
            
        return None
