#!/usr/bin/env python3
"""
Simple Database Wipe
Just wipes events and fights tables using Supabase REST API
"""

import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv('.env')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

def wipe_tables():
    """Just wipe the events and fights tables"""
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("❌ Missing Supabase credentials")
        return False
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        logger.info("🗑️ Wiping fights table...")
        
        # Delete all fights
        fights_response = requests.delete(
            f"{SUPABASE_URL}/rest/v1/fights",
            headers=headers
        )
        
        if fights_response.status_code == 200:
            logger.info("✅ Fights table wiped successfully")
        else:
            logger.warning(f"⚠️ Fights deletion response: {fights_response.status_code}")
            logger.warning(f"⚠️ Response: {fights_response.text}")
        
        logger.info("🗑️ Wiping events table...")
        
        # Delete all events
        events_response = requests.delete(
            f"{SUPABASE_URL}/rest/v1/events",
            headers=headers
        )
        
        if events_response.status_code == 200:
            logger.info("✅ Events table wiped successfully")
        else:
            logger.warning(f"⚠️ Events deletion response: {events_response.status_code}")
            logger.warning(f"⚠️ Response: {events_response.text}")
        
        # Verify tables are empty
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
        
        logger.info("🎉 Database wipe completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error wiping database: {e}")
        return False

if __name__ == "__main__":
    success = wipe_tables()
    if success:
        print("✅ Database wipe completed successfully!")
    else:
        print("❌ Database wipe failed!")
        exit(1) 