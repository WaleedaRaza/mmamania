#!/usr/bin/env python3
"""
Wipe Database Except Rankings
Wipe fights, fighters, and events but preserve rankings
"""

import os
import sys
import requests
import logging
from dotenv import load_dotenv

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
    
    def wipe_except_rankings(self):
        """Wipe all data except rankings"""
        logger.info("🗑️ Starting database wipe (PRESERVING RANKINGS)...")
        
        try:
            # Step 1: Delete all fights (due to foreign key constraints)
            logger.info("🗑️ Deleting all fights...")
            response = requests.delete(
                f"{SUPABASE_URL}/rest/v1/fights",
                headers=self.supabase_headers,
                params={'event_id': 'not.is.null'}
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
                params={'name': 'not.is.null'}
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
                params={'name': 'not.is.null'}
            )
            
            if response.status_code == 200:
                deleted_events = response.json()
                logger.info(f"✅ Deleted {len(deleted_events)} events")
            else:
                logger.warning(f"⚠️ Event deletion response: {response.status_code}")
            
            # Step 4: VERIFY RANKINGS ARE STILL THERE
            logger.info("🔍 Verifying rankings are preserved...")
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/rankings?select=id&limit=1",
                headers=self.supabase_headers
            )
            if response.status_code == 200:
                rankings = response.json()
                logger.info(f"✅ RANKINGS PRESERVED: {len(rankings)} rankings still in database")
            else:
                logger.error(f"❌ ERROR: Could not verify rankings!")
            
            logger.info("✅ Database wipe completed successfully!")
            logger.info("🏆 RANKINGS ARE SAFE AND INTACT!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error during database wipe: {str(e)}")
            return False
    
    def verify_database_state(self):
        """Verify the current state of the database"""
        logger.info("🔍 Verifying database state...")
        
        try:
            # Check events
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/events?select=id&limit=1",
                headers=self.supabase_headers
            )
            if response.status_code == 200:
                events = response.json()
                logger.info(f"📊 Events: {len(events)}")
            
            # Check fighters
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/fighters?select=id&limit=1",
                headers=self.supabase_headers
            )
            if response.status_code == 200:
                fighters = response.json()
                logger.info(f"👤 Fighters: {len(fighters)}")
            
            # Check fights
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/fights?select=id&limit=1",
                headers=self.supabase_headers
            )
            if response.status_code == 200:
                fights = response.json()
                logger.info(f"🥊 Fights: {len(fights)}")
            
            # Check rankings
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/rankings?select=id&limit=1",
                headers=self.supabase_headers
            )
            if response.status_code == 200:
                rankings = response.json()
                logger.info(f"🏆 Rankings: {len(rankings)}")
            
        except Exception as e:
            logger.error(f"❌ Error verifying database: {str(e)}")

def run_wipe_except_rankings():
    """Run the wipe process"""
    logger.info("🚀 Starting Database Wipe (Preserving Rankings)")
    logger.info("=" * 60)
    
    wiper = DatabaseWiper()
    
    # Step 1: Wipe database except rankings
    logger.info("📋 Step 1: Wiping Database (Except Rankings)")
    logger.info("-" * 40)
    if not wiper.wipe_except_rankings():
        logger.error("❌ Failed to wipe database. Aborting.")
        return
    
    # Step 2: Verify database state
    logger.info("📋 Step 2: Verifying Database State")
    logger.info("-" * 40)
    wiper.verify_database_state()
    
    logger.info("🎉 Database wipe completed!")
    logger.info("🏆 Rankings are safe and ready for scraper!")
    logger.info("=" * 60)

if __name__ == "__main__":
    run_wipe_except_rankings() 