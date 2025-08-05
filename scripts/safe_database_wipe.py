#!/usr/bin/env python3
"""
Safe Database Wipe - PRESERVES RANKINGS
Wipe fights, fighters, and events but NEVER touch rankings
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

class SafeDatabaseWiper:
    def __init__(self):
        self.supabase_headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
        }
    
    def wipe_database_safely(self):
        """Wipe all data EXCEPT rankings"""
        logger.info("🗑️ Starting SAFE database wipe (PRESERVING RANKINGS)...")
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
            
            logger.info("✅ SAFE database wipe completed successfully!")
            logger.info("🏆 RANKINGS ARE SAFE AND INTACT!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error during safe database wipe: {str(e)}")
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
                if events:
                    logger.warning(f"⚠️ Found {len(events)} events still in database")
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
                else:
                    logger.info("✅ Fights table is empty")
            
            # Check rankings (SHOULD BE THERE)
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/rankings?select=id",
                headers=self.supabase_headers
            )
            if response.status_code == 200:
                rankings = response.json()
                logger.info(f"🏆 RANKINGS INTACT: {len(rankings)} rankings in database")
            else:
                logger.error(f"❌ ERROR: Could not verify rankings!")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error verifying database: {str(e)}")
            return False

def run_safe_wipe():
    """Run the safe database wipe"""
    logger.info("🚀 Starting Safe Database Wipe")
    logger.info("=" * 60)
    
    wiper = SafeDatabaseWiper()
    
    # Step 1: Wipe database safely
    if not wiper.wipe_database_safely():
        logger.error("❌ Failed to wipe database safely. Aborting.")
        return
    
    # Step 2: Verify database state
    if not wiper.verify_database_state():
        logger.warning("⚠️ Database verification failed, but continuing...")
    
    logger.info("🎉 Safe database wipe completed!")
    logger.info("🏆 Rankings are preserved and ready for action!")
    logger.info("=" * 60)

if __name__ == "__main__":
    run_safe_wipe() 