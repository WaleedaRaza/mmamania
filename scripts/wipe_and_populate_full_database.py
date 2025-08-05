#!/usr/bin/env python3
"""
Wipe and Populate Full Database
Wipe the current database and populate with all 667 UFC events
"""

import os
import sys
import requests
import logging
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
                logger.info(f"📊 Events in database: {len(events)}")
            
            # Check fighters
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/fighters?select=id&limit=1",
                headers=self.supabase_headers
            )
            if response.status_code == 200:
                fighters = response.json()
                logger.info(f"📊 Fighters in database: {len(fighters)}")
            
            # Check fights
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/fights?select=id&limit=1",
                headers=self.supabase_headers
            )
            if response.status_code == 200:
                fights = response.json()
                logger.info(f"📊 Fights in database: {len(fights)}")
            
            total_records = len(events) + len(fighters) + len(fights)
            if total_records == 0:
                logger.info("✅ Database is completely empty!")
                return True
            else:
                logger.warning(f"⚠️ Database still has {total_records} records")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error verifying database: {str(e)}")
            return False

def run_full_population():
    """Run the complete database population process"""
    logger.info("🚀 Starting Full Database Population")
    logger.info("=" * 60)
    
    # Step 1: Wipe the database
    wiper = DatabaseWiper()
    if not wiper.wipe_database():
        logger.error("❌ Failed to wipe database. Aborting.")
        return
    
    # Step 2: Verify database is empty
    if not wiper.verify_database_empty():
        logger.warning("⚠️ Database may not be completely empty, but continuing...")
    
    # Step 3: Import and run the robust scraper
    logger.info("🔄 Importing robust scraper...")
    try:
        from robust_link_following_scraper import RobustLinkFollowingScraper
    except ImportError:
        logger.error("❌ Could not import robust scraper. Please ensure the file exists.")
        return
    
    # Step 4: Run the full scraper on all 667 events
    logger.info("🎯 Running robust scraper on ALL 667 events...")
    scraper = RobustLinkFollowingScraper()
    
    # Run without any limits to process all events
    scraper.run_robust_scraper(max_events=None, start_from=0)
    
    logger.info("🎉 Full database population completed!")
    logger.info("=" * 60)

if __name__ == "__main__":
    run_full_population() 