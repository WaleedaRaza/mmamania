#!/usr/bin/env python3
"""
UUID Database Wipe
Wipes events and fights tables with proper UUID handling
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
    """Wipe the events and fights tables by getting all IDs first"""
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("❌ Missing Supabase credentials")
        return False
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        # Step 1: Get all fight IDs
        logger.info("🔍 Getting all fight IDs...")
        fights_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/fights",
            headers=headers,
            params={'select': 'id'}
        )
        
        if fights_response.status_code == 200:
            fights = fights_response.json()
            logger.info(f"📊 Found {len(fights)} fights to delete")
            
            # Delete each fight individually
            deleted_fights = 0
            for fight in fights:
                fight_id = fight['id']
                delete_response = requests.delete(
                    f"{SUPABASE_URL}/rest/v1/fights",
                    headers=headers,
                    params={'id': f'eq.{fight_id}'}
                )
                if delete_response.status_code == 200:
                    deleted_fights += 1
            
            logger.info(f"✅ Deleted {deleted_fights} fights")
        else:
            logger.warning(f"⚠️ Could not get fights: {fights_response.status_code}")
        
        # Step 2: Get all event IDs
        logger.info("🔍 Getting all event IDs...")
        events_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/events",
            headers=headers,
            params={'select': 'id'}
        )
        
        if events_response.status_code == 200:
            events = events_response.json()
            logger.info(f"📊 Found {len(events)} events to delete")
            
            # Delete each event individually
            deleted_events = 0
            for event in events:
                event_id = event['id']
                delete_response = requests.delete(
                    f"{SUPABASE_URL}/rest/v1/events",
                    headers=headers,
                    params={'id': f'eq.{event_id}'}
                )
                if delete_response.status_code == 200:
                    deleted_events += 1
            
            logger.info(f"✅ Deleted {deleted_events} events")
        else:
            logger.warning(f"⚠️ Could not get events: {events_response.status_code}")
        
        # Step 3: Verify tables are empty
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