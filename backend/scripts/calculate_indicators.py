"""
Script to calculate technical indicators for all symbols.
"""

import argparse
import logging
import sys
from datetime import datetime

from backend.indicators.manager import IndicatorManager
from backend.core.database import check_database_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("indicator_calculation.log"),
    ],
)

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Calculate technical indicators")
    parser.add_argument(
        "--benchmark",
        type=str,
        default="^NSEI",
        help="Benchmark symbol ticker (default: ^NSEI)",
    )
    args = parser.parse_args()

    logger.info("Starting indicator calculation process...")

    if not check_database_connection():
        logger.error("Database connection failed. Exiting.")
        sys.exit(1)

    manager = IndicatorManager()
    
    start_time = datetime.now()
    try:
        manager.calculate_all(benchmark_symbol=args.benchmark)
    except Exception as e:
        logger.error(f"An error occurred during calculation: {e}")
        sys.exit(1)
    
    duration = datetime.now() - start_time
    logger.info(f"Calculation completed in {duration}")


if __name__ == "__main__":
    main()
