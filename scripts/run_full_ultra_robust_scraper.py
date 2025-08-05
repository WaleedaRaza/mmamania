#!/usr/bin/env python3
"""
Run Full Ultra Robust Scraper
Run the ultra robust scraper on all 647 events
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

def run_full_ultra_robust_scraper():
    """Run the full ultra robust scraper on all 647 events"""
    logger.info("🚀 Starting Full Ultra Robust Scraper")
    logger.info("=" * 60)
    
    try:
        from ultra_robust_scraper import UltraRobustScraper
    except ImportError:
        logger.error("❌ Could not import ultra robust scraper. Please ensure the file exists.")
        return
    
    # Create ultra robust scraper with 8 workers for stability
    scraper = UltraRobustScraper(max_workers=8)
    
    # Run the full scraper on ALL 647 events
    logger.info("🎯 Running ultra robust scraper on ALL 647 events...")
    logger.info("⚡ Estimated time: ~20-25 minutes with 8 workers")
    logger.info("📊 Expected fights: ~7,000+ fights")
    logger.info("🎯 Expected success rate: ~85-90% (filtering out future events)")
    
    # Run without any limits to process all events
    scraper.run_ultra_robust_scraper(max_events=None, start_from=0)
    
    logger.info("🎉 Full ultra robust scraper completed!")
    logger.info("=" * 60)

if __name__ == "__main__":
    run_full_ultra_robust_scraper() 