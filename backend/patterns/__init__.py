# Export all pattern detectors and scanner
from .base import PatternDetector, PatternResult
from .cup_with_handle import CupWithHandleDetector
from .double_bottom import DoubleBottomDetector
from .high_tight_flag import HighTightFlagDetector
from .orchestrator import PatternScanner
from .stage_analysis import WeinsteinStageAnalyzer
from .trend_template import TrendTemplateDetector
from .vcp import VCPDetector

__all__ = [
    "PatternDetector",
    "PatternResult",
    "TrendTemplateDetector",
    "VCPDetector",
    "CupWithHandleDetector",
    "DoubleBottomDetector",
    "HighTightFlagDetector",
    "WeinsteinStageAnalyzer",
    "PatternScanner",
]
