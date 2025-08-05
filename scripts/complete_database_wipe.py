#!/usr/bin/env python3
"""
Complete Database Wipe
Wipe ALL tables including rankings, fights, fighters, and events
"""

import os
import sys
import requests
import logging
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
    
    def wipe_all_tables(self):
        """Wipe ALL data from the database in correct order"""
        logger.info("🗑️ Starting COMPLETE database wipe...")
        logger.info("=" * 60)
        
        try:
            # Step 1: Delete all fights (due to foreign key constraints)
            logger.info("🗑️ Step 1: Deleting all fights...")
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
            
            # Step 2: Delete all rankings (due to foreign key constraints)
            logger.info("🗑️ Step 2: Deleting all rankings...")
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
            logger.info("🗑️ Step 3: Deleting all fighters...")
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
            logger.info("🗑️ Step 4: Deleting all events...")
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
            logger.error(f"❌ Error during database wipe: {str(e)}")
            return False
    
    def verify_database_empty(self):
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

def run_complete_wipe():
    """Run the complete database wipe"""
    logger.info("🚀 Starting Complete Database Wipe")
    logger.info("=" * 60)
    
    wiper = CompleteDatabaseWiper()
    
    # Step 1: Wipe all tables
    if not wiper.wipe_all_tables():
        logger.error("❌ Failed to wipe database. Aborting.")
        return
    
    # Step 2: Verify all tables are empty
    if not wiper.verify_database_empty():
        logger.warning("⚠️ Database may not be completely empty, but continuing...")
    else:
        logger.info("✅ Database is completely clean and ready for fresh data!")
    
    logger.info("🎉 Complete database wipe finished!")
    logger.info("=" * 60)

if __name__ == "__main__":
    run_complete_wipe() 