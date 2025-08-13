#!/usr/bin/env python3
"""
Wipe Remaining Events
Wipe the remaining events in the events table
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

def wipe_remaining_events():
    """Wipe the remaining events in the events table"""
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("❌ Missing Supabase credentials")
        return False
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        # Get all event IDs
        logger.info("🔍 Getting all event IDs...")
        events_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/events",
            headers=headers,
            params={'select': 'id'}
        )
        
        if events_response.status_code == 200:
            events = events_response.json()
            logger.info(f"📊 Found {len(events)} events to delete")
            
            # Delete events in batches of 50
            batch_size = 50
            deleted_events = 0
            
            for i in range(0, len(events), batch_size):
                batch = events[i:i + batch_size]
                logger.info(f"🗑️ Deleting batch {i//batch_size + 1} ({len(batch)} events)...")
                
                for event in batch:
                    event_id = event['id']
                    delete_response = requests.delete(
                        f"{SUPABASE_URL}/rest/v1/events",
                        headers=headers,
                        params={'id': f'eq.{event_id}'}
                    )
                    if delete_response.status_code == 200:
                        deleted_events += 1
                
                logger.info(f"✅ Deleted {deleted_events} events so far...")
            
            logger.info(f"✅ Total deleted events: {deleted_events}")
        else:
            logger.warning(f"⚠️ Could not get events: {events_response.status_code}")
            logger.warning(f"⚠️ Response: {events_response.text}")
        
        # Verify table is empty
        logger.info("🔍 Verifying events table is empty...")
        
        events_check = requests.get(
            f"{SUPABASE_URL}/rest/v1/events",
            headers=headers,
            params={'select': 'id', 'limit': 1}
        )
        
        if events_check.status_code == 200 and len(events_check.json()) == 0:
            logger.info("✅ Events table is empty")
        else:
            logger.warning("⚠️ Events table may not be empty")
        
        logger.info("🎉 Events wipe completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error wiping events: {e}")
        return False

if __name__ == "__main__":
    success = wipe_remaining_events()
    if success:
        print("✅ Events wipe completed successfully!")
    else:
        print("❌ Events wipe failed!")
        exit(1) 