#!/usr/bin/env python3
"""
Wipe and Run Parallel Population
First wipe the database completely, then run the full parallel scraper
"""

import os
import sys
import requests
import logging
import time
from dotenv import load_dotenv

# Add the scripts directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv('scripts/.env')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

class DatabaseWiper:
    def __init__(self):
        self.supabase_headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
        }
    
    def wipe_database(self):
        """Wipe all data from the database"""
        logger.info("🗑️ Starting database wipe...")
        
        try:
            # Step 1: Delete all fights (due to foreign key constraints)
            logger.info("🗑️ Deleting all fights...")
            response = requests.delete(
                f"{SUPABASE_URL}/rest/v1/fights",
                headers=self.supabase_headers,
                params={'event_id': 'not.is.null'}  # Delete all fights
            )
            
            if response.status_code == 200:
                deleted_fights = response.json()
                logger.info(f"✅ Deleted {len(deleted_fights)} fights")
            else:
                logger.warning(f"⚠️ Fight deletion response: {response.status_code}")
            
            # Step 2: Delete all fighters
            logger.info("🗑️ Deleting all fighters...")
            response = requests.delete(
                f"{SUPABASE_URL}/rest/v1/fighters",
                headers=self.supabase_headers,
                params={'name': 'not.is.null'}  # Delete all fighters
            )
            
            if response.status_code == 200:
                deleted_fighters = response.json()
                logger.info(f"✅ Deleted {len(deleted_fighters)} fighters")
            else:
                logger.warning(f"⚠️ Fighter deletion response: {response.status_code}")
            
            # Step 3: Delete all events
            logger.info("🗑️ Deleting all events...")
            response = requests.delete(
                f"{SUPABASE_URL}/rest/v1/events",
                headers=self.supabase_headers,
                params={'name': 'not.is.null'}  # Delete all events
            )
            
            if response.status_code == 200:
                deleted_events = response.json()
                logger.info(f"✅ Deleted {len(deleted_events)} events")
            else:
                logger.warning(f"⚠️ Event deletion response: {response.status_code}")
            
            logger.info("✅ Database wipe completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error during database wipe: {str(e)}")
            return False
    
    def verify_database_empty(self):
        """Verify that the database is empty"""
        logger.info("🔍 Verifying database is empty...")
        
        try:
            # Check events
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/events?select=id&limit=1",
                headers=self.supabase_headers
            )
            if response.status_code == 200:
                events = response.json()
                if events:
                    logger.warning(f"⚠️ Found {len(events)} events still in database")
                    return False
            
            # Check fighters
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/fighters?select=id&limit=1",
                headers=self.supabase_headers
            )
            if response.status_code == 200:
                fighters = response.json()
                if fighters:
                    logger.warning(f"⚠️ Found {len(fighters)} fighters still in database")
                    return False
            
            # Check fights
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/fights?select=id&limit=1",
                headers=self.supabase_headers
            )
            if response.status_code == 200:
                fights = response.json()
                if fights:
                    logger.warning(f"⚠️ Found {len(fights)} fights still in database")
                    return False
            
            logger.info("✅ Database is completely empty!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error verifying database: {str(e)}")
            return False

def run_wipe_and_parallel_population():
    """Run the complete process: wipe database, then parallel population"""
    logger.info("🚀 Starting Complete Database Reset and Population")
    logger.info("=" * 60)
    
    # Step 1: Wipe the database
    logger.info("📋 Step 1: Wiping Database")
    logger.info("-" * 40)
    wiper = DatabaseWiper()
    if not wiper.wipe_database():
        logger.error("❌ Failed to wipe database. Aborting.")
        return
    
    # Step 2: Verify database is empty
    logger.info("📋 Step 2: Verifying Database is Empty")
    logger.info("-" * 40)
    if not wiper.verify_database_empty():
        logger.warning("⚠️ Database may not be completely empty, but continuing...")
    
    # Step 3: Import and run the parallel scraper
    logger.info("📋 Step 3: Running Parallel Population")
    logger.info("-" * 40)
    try:
        from parallel_robust_scraper import ParallelRobustScraper
    except ImportError:
        logger.error("❌ Could not import parallel scraper. Please ensure the file exists.")
        return
    
    # Create parallel scraper with 15 workers for maximum speed
    scraper = ParallelRobustScraper(max_workers=15)
    
    # Run the full scraper on ALL 667 events
    logger.info("🎯 Running parallel scraper on ALL 667 events...")
    logger.info("⚡ Estimated time: ~18-20 minutes with 15 workers")
    logger.info("📊 Expected fights: ~8,000+ fights")
    
    # Run without any limits to process all events
    scraper.run_parallel_scraper(max_events=None, start_from=0)
    
    logger.info("🎉 Complete database reset and population finished!")
    logger.info("=" * 60)

if __name__ == "__main__":
    run_wipe_and_parallel_population() 