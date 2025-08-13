#!/usr/bin/env python3
"""
Wipe Events and Fights Database
Clears all events and fights data from the database
"""

import os
import sys
import logging
from dotenv import load_dotenv
import requests

# Add the scripts directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv('.env')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

def wipe_events_fights_db():
    """Wipe all events and fights from the database"""
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("❌ Missing Supabase credentials")
        return False
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        logger.info("🗑️ Starting database wipe...")
        
        # Delete all fights first (due to foreign key constraints)
        logger.info("🗑️ Deleting all fights...")
        fights_response = requests.delete(
            f"{SUPABASE_URL}/rest/v1/fights",
            headers=headers,
            params={'select': 'id'}
        )
        
        if fights_response.status_code == 200:
            deleted_fights = len(fights_response.json())
            logger.info(f"✅ Deleted {deleted_fights} fights")
        else:
            logger.warning(f"⚠️ Fights deletion response: {fights_response.status_code}")
        
        # Delete all events
        logger.info("🗑️ Deleting all events...")
        events_response = requests.delete(
            f"{SUPABASE_URL}/rest/v1/events",
            headers=headers,
            params={'select': 'id'}
        )
        
        if events_response.status_code == 200:
            deleted_events = len(events_response.json())
            logger.info(f"✅ Deleted {deleted_events} events")
        else:
            logger.warning(f"⚠️ Events deletion response: {events_response.status_code}")
        
        # Verify the tables are empty
        logger.info("🔍 Verifying tables are empty...")
        
        fights_check = requests.get(
            f"{SUPABASE_URL}/rest/v1/fights",
            headers=headers,
            params={'select': 'id', 'limit': 1}
        )
        
        events_check = requests.get(
            f"{SUPABASE_URL}/rest/v1/events",
            headers=headers,
            params={'select': 'id', 'limit': 1}
        )
        
        if fights_check.status_code == 200 and len(fights_check.json()) == 0:
            logger.info("✅ Fights table is empty")
        else:
            logger.warning("⚠️ Fights table may not be empty")
        
        if events_check.status_code == 200 and len(events_check.json()) == 0:
            logger.info("✅ Events table is empty")
        else:
            logger.warning("⚠️ Events table may not be empty")
        
        logger.info("🎉 Database wipe completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error wiping database: {e}")
        return False

if __name__ == "__main__":
    success = wipe_events_fights_db()
    if success:
        print("✅ Database wipe completed successfully!")
    else:
        print("❌ Database wipe failed!")
        sys.exit(1) 