#!/usr/bin/env python3
"""
Run Full Parallel Population
Run the parallel scraper on all 667 events to populate the complete database
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add the scripts directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv('scripts/.env')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_full_parallel_population():
    """Run the full parallel population of all 667 events"""
    logger.info("🚀 Starting Full Parallel Population")
    logger.info("=" * 60)
    
    try:
        from parallel_robust_scraper import ParallelRobustScraper
    except ImportError:
        logger.error("❌ Could not import parallel scraper. Please ensure the file exists.")
        return
    
    # Create parallel scraper with 15 workers for maximum speed
    # You can adjust this based on your system capabilities
    scraper = ParallelRobustScraper(max_workers=15)
    
    # Run the full scraper on ALL 667 events
    logger.info("🎯 Running parallel scraper on ALL 667 events...")
    logger.info("⚡ Estimated time: ~18-20 minutes with 15 workers")
    logger.info("📊 Expected fights: ~8,000+ fights")
    
    # Run without any limits to process all events
    scraper.run_parallel_scraper(max_events=None, start_from=0)
    
    logger.info("🎉 Full parallel population completed!")
    logger.info("=" * 60)

if __name__ == "__main__":
    run_full_parallel_population() 