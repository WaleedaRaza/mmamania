#!/usr/bin/env python3
"""
Complete Wipe and Restore Rankings
Wipe ALL databases including rankings, then restore complete rankings
"""

import os
import sys
import requests
import logging
import subprocess
from dotenv import load_dotenv

load_dotenv('scripts/.env')

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
    
    def wipe_all_databases(self):
        """Wipe ALL data including rankings"""
        logger.info("🗑️ Starting COMPLETE database wipe (INCLUDING RANKINGS)...")
        logger.info("=" * 60)
        
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
            
            # Step 2: Delete all rankings
            logger.info("🗑️ Deleting all rankings...")
            response = requests.delete(
                f"{SUPABASE_URL}/rest/v1/rankings",
                headers=self.supabase_headers,
                params={'fighter_id': 'not.is.null'}  # Delete all rankings
            )
            
            if response.status_code == 200:
                deleted_rankings = response.json()
                logger.info(f"✅ Deleted {len(deleted_rankings)} rankings")
            else:
                logger.warning(f"⚠️ Ranking deletion response: {response.status_code}")
            
            # Step 3: Delete all fighters
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
            
            # Step 4: Delete all events
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
            
            logger.info("✅ COMPLETE database wipe finished successfully!")
            logger.info("=" * 60)
            return True
            
        except Exception as e:
            logger.error(f"❌ Error during complete database wipe: {str(e)}")
            return False
    
    def verify_all_empty(self):
        """Verify that ALL tables are empty"""
        logger.info("🔍 Verifying ALL tables are empty...")
        
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
                else:
                    logger.info("✅ Events table is empty")
            
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
                else:
                    logger.info("✅ Fighters table is empty")
            
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
                else:
                    logger.info("✅ Fights table is empty")
            
            # Check rankings
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/rankings?select=id&limit=1",
                headers=self.supabase_headers
            )
            if response.status_code == 200:
                rankings = response.json()
                if rankings:
                    logger.warning(f"⚠️ Found {len(rankings)} rankings still in database")
                    return False
                else:
                    logger.info("✅ Rankings table is empty")
            
            logger.info("🎉 ALL tables are completely empty!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error verifying database: {str(e)}")
            return False

def run_rankings_scraper():
    """Run the rankings scraper to get complete rankings"""
    logger.info("🔄 Running rankings scraper...")
    try:
        result = subprocess.run(['python3', 'scrapers/ufc/real_dynamic_scraper.py'], 
                              capture_output=True, text=True, check=True)
        logger.info("✅ Rankings scraper completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Rankings scraper failed: {e}")
        return False

def run_rankings_population():
    """Run the rankings population script"""
    logger.info("🔄 Running rankings population...")
    try:
        result = subprocess.run(['python3', 'scripts/populate_rankings_fixed.py'], 
                              capture_output=True, text=True, check=True)
        logger.info("✅ Rankings population completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Rankings population failed: {e}")
        return False

def run_complete_wipe_and_restore():
    """Run the complete process: wipe all, restore rankings"""
    logger.info("🚀 Starting Complete Wipe and Rankings Restore")
    logger.info("=" * 60)
    
    wiper = CompleteDatabaseWiper()
    
    # Step 1: Wipe ALL databases
    logger.info("📋 Step 1: Wiping ALL Databases")
    logger.info("-" * 40)
    if not wiper.wipe_all_databases():
        logger.error("❌ Failed to wipe databases. Aborting.")
        return
    
    # Step 2: Verify all tables are empty
    logger.info("📋 Step 2: Verifying All Tables Empty")
    logger.info("-" * 40)
    if not wiper.verify_all_empty():
        logger.warning("⚠️ Some tables may not be completely empty, but continuing...")
    
    # Step 3: Run rankings scraper
    logger.info("📋 Step 3: Running Rankings Scraper")
    logger.info("-" * 40)
    if not run_rankings_scraper():
        logger.error("❌ Rankings scraper failed. Aborting.")
        return
    
    # Step 4: Populate rankings
    logger.info("📋 Step 4: Populating Rankings")
    logger.info("-" * 40)
    if not run_rankings_population():
        logger.error("❌ Rankings population failed. Aborting.")
        return
    
    logger.info("🎉 Complete wipe and rankings restore finished!")
    logger.info("🏆 Rankings are now complete and ready!")
    logger.info("=" * 60)

if __name__ == "__main__":
    run_complete_wipe_and_restore() 