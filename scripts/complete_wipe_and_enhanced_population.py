#!/usr/bin/env python3
"""
Complete Wipe and Enhanced Population
First wipe the database completely, then run the enhanced parallel scraper for ALL 742 events
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

class CompleteDatabaseWiper:
    def __init__(self):
        self.supabase_headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
        }
    
    def wipe_database_completely(self):
        """Wipe ALL data from the database - completely clean slate"""
        logger.info("🗑️ Starting COMPLETE database wipe...")
        
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
            
            logger.info("✅ COMPLETE database wipe finished!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error during database wipe: {str(e)}")
            return False
    
    def verify_database_completely_empty(self):
        """Verify that the database is completely empty"""
        logger.info("🔍 Verifying database is completely empty...")
        
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
            
            logger.info("✅ Database is COMPLETELY empty!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error verifying database: {str(e)}")
            return False

def run_complete_wipe_and_enhanced_population():
    """Run the complete process: wipe database completely, then enhanced parallel population"""
    logger.info("🚀 Starting COMPLETE Database Reset and Enhanced Population")
    logger.info("=" * 70)
    
    # Step 1: Wipe the database completely
    logger.info("📋 Step 1: COMPLETE Database Wipe")
    logger.info("-" * 50)
    wiper = CompleteDatabaseWiper()
    if not wiper.wipe_database_completely():
        logger.error("❌ Failed to wipe database completely. Aborting.")
        return
    
    # Step 2: Verify database is completely empty
    logger.info("📋 Step 2: Verifying Database is Completely Empty")
    logger.info("-" * 50)
    if not wiper.verify_database_completely_empty():
        logger.error("❌ Database is not completely empty. Aborting.")
        return
    
    # Step 3: Import and run the enhanced parallel scraper
    logger.info("📋 Step 3: Running Enhanced Parallel Population")
    logger.info("-" * 50)
    try:
        from enhanced_parallel_scraper import EnhancedParallelScraper
    except ImportError:
        logger.error("❌ Could not import enhanced parallel scraper. Please ensure the file exists.")
        return
    
    # Create enhanced parallel scraper with 15 workers for maximum speed
    scraper = EnhancedParallelScraper(max_workers=15)
    
    # Run the enhanced scraper on ALL events (should be ~742)
    logger.info("🎯 Running enhanced parallel scraper on ALL events...")
    logger.info("⚡ Estimated time: ~20-25 minutes with 15 workers")
    logger.info("📊 Expected events: ~742 events")
    logger.info("📊 Expected fights: ~9,000+ fights")
    
    # Run without any limits to process all events
    scraper.run_enhanced_parallel_scraper(max_events=None, start_from=0)
    
    logger.info("🎉 COMPLETE database reset and enhanced population finished!")
    logger.info("=" * 70)

if __name__ == "__main__":
    run_complete_wipe_and_enhanced_population() 