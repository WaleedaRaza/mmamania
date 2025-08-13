#!/usr/bin/env python3
"""
Check Duplicate Events
Check for duplicate events in the database
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

def check_duplicate_events():
    """Check for duplicate events"""
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("❌ Missing Supabase credentials")
        return False
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        # Get all events
        logger.info("🔍 Checking all events...")
        events_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/events",
            headers=headers,
            params={'select': 'id,name,date', 'order': 'date.desc'}
        )
        
        if events_response.status_code == 200:
            events = events_response.json()
            logger.info(f"📊 Found {len(events)} total events")
            
            # Group by name to find duplicates
            event_groups = {}
            for event in events:
                name = event.get('name', 'Unknown')
                if name not in event_groups:
                    event_groups[name] = []
                event_groups[name].append(event)
            
            # Show duplicates
            logger.info("🔍 Checking for duplicate events:")
            for name, event_list in event_groups.items():
                if len(event_list) > 1:
                    logger.warning(f"⚠️ DUPLICATE: '{name}' has {len(event_list)} instances:")
                    for i, event in enumerate(event_list):
                        logger.warning(f"   {i+1}. ID: {event['id']}, Date: {event.get('date', 'N/A')}")
                    
                    # Check which ones have fights
                    for i, event in enumerate(event_list):
                        fights_response = requests.get(
                            f"{SUPABASE_URL}/rest/v1/fights",
                            headers=headers,
                            params={'event_id': f'eq.{event["id"]}', 'select': 'id'}
                        )
                        if fights_response.status_code == 200:
                            fights = fights_response.json()
                            logger.info(f"   {i+1}. Event {event['id']}: {len(fights)} fights")
                        else:
                            logger.warning(f"   {i+1}. Event {event['id']}: Error checking fights")
                    logger.info("   ---")
            
            # Show events with fights
            logger.info("🔍 Events with fights:")
            for event in events:
                fights_response = requests.get(
                    f"{SUPABASE_URL}/rest/v1/fights",
                    headers=headers,
                    params={'event_id': f'eq.{event["id"]}', 'select': 'id'}
                )
                if fights_response.status_code == 200:
                    fights = fights_response.json()
                    if len(fights) > 0:
                        logger.info(f"✅ '{event.get('name', 'Unknown')}' (ID: {event['id']}): {len(fights)} fights")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking duplicate events: {e}")
        return False

if __name__ == "__main__":
    success = check_duplicate_events()
    if success:
        print("✅ Duplicate events check completed!")
    else:
        print("❌ Duplicate events check failed!")
        exit(1) 