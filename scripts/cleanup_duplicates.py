#!/usr/bin/env python3
"""
Cleanup Duplicates
Delete duplicate events that have no fights
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

def cleanup_duplicates():
    """Delete duplicate events that have no fights"""
    
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
        logger.info("🔍 Getting all events...")
        events_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/events",
            headers=headers,
            params={'select': 'id,name,date', 'order': 'date.desc'}
        )
        
        if events_response.status_code != 200:
            logger.error(f"❌ Could not get events: {events_response.status_code}")
            return False
        
        all_events = events_response.json()
        logger.info(f"📊 Found {len(all_events)} total events")
        
        # Group events by name
        event_groups = {}
        for event in all_events:
            name = event.get('name', 'Unknown')
            if name not in event_groups:
                event_groups[name] = []
            event_groups[name].append(event)
        
        # Find events to delete (duplicates with no fights)
        events_to_delete = []
        
        for name, event_list in event_groups.items():
            if len(event_list) > 1:
                logger.info(f"🔍 Processing duplicates for '{name}' ({len(event_list)} instances)")
                
                # Check which ones have fights
                events_with_fights = []
                events_without_fights = []
                
                for event in event_list:
                    fights_response = requests.get(
                        f"{SUPABASE_URL}/rest/v1/fights",
                        headers=headers,
                        params={'event_id': f'eq.{event["id"]}', 'select': 'id'}
                    )
                    
                    if fights_response.status_code == 200:
                        fights = fights_response.json()
                        if len(fights) > 0:
                            events_with_fights.append(event)
                            logger.info(f"   ✅ Event {event['id']}: {len(fights)} fights (KEEP)")
                        else:
                            events_without_fights.append(event)
                            logger.info(f"   ❌ Event {event['id']}: 0 fights (DELETE)")
                    else:
                        events_without_fights.append(event)
                        logger.info(f"   ❌ Event {event['id']}: Error checking fights (DELETE)")
                
                # Keep the first event with fights, delete the rest
                if events_with_fights:
                    # Keep only the first event with fights
                    keep_event = events_with_fights[0]
                    logger.info(f"   🎯 Keeping event {keep_event['id']} with fights")
                    
                    # Delete all other events (including other events with fights)
                    for event in event_list:
                        if event['id'] != keep_event['id']:
                            events_to_delete.append(event)
                            logger.info(f"   🗑️ Marking for deletion: {event['id']}")
                else:
                    # If no events have fights, keep the first one
                    keep_event = event_list[0]
                    logger.info(f"   🎯 No events have fights, keeping first: {keep_event['id']}")
                    
                    # Delete all other events
                    for event in event_list[1:]:
                        events_to_delete.append(event)
                        logger.info(f"   🗑️ Marking for deletion: {event['id']}")
        
        # Delete the marked events
        logger.info(f"\n🗑️ Deleting {len(events_to_delete)} duplicate events...")
        deleted_count = 0
        
        for event in events_to_delete:
            try:
                delete_response = requests.delete(
                    f"{SUPABASE_URL}/rest/v1/events",
                    headers=headers,
                    params={'id': f'eq.{event["id"]}'}
                )
                
                if delete_response.status_code == 200:
                    deleted_count += 1
                    logger.info(f"   ✅ Deleted event {event['id']} ({event.get('name', 'Unknown')})")
                else:
                    logger.warning(f"   ⚠️ Failed to delete event {event['id']}: {delete_response.status_code}")
                    
            except Exception as e:
                logger.error(f"   ❌ Error deleting event {event['id']}: {e}")
        
        logger.info(f"\n📊 Cleanup completed!")
        logger.info(f"   ✅ Deleted {deleted_count} duplicate events")
        
        # Verify the cleanup
        logger.info("\n🔍 Verifying cleanup...")
        verify_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/events",
            headers=headers,
            params={'select': 'id,name', 'order': 'date.desc'}
        )
        
        if verify_response.status_code == 200:
            remaining_events = verify_response.json()
            logger.info(f"📊 Remaining events: {len(remaining_events)}")
            
            for event in remaining_events:
                fights_response = requests.get(
                    f"{SUPABASE_URL}/rest/v1/fights",
                    headers=headers,
                    params={'event_id': f'eq.{event["id"]}', 'select': 'id'}
                )
                if fights_response.status_code == 200:
                    fights = fights_response.json()
                    logger.info(f"   {event.get('name', 'Unknown')}: {len(fights)} fights")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in cleanup: {e}")
        return False

if __name__ == "__main__":
    success = cleanup_duplicates()
    if success:
        print("✅ Duplicate cleanup completed!")
    else:
        print("❌ Duplicate cleanup failed!")
        exit(1) 