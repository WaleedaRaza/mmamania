#!/usr/bin/env python3
"""
Fix Fight Ordering with PUT
Update existing fights with correct fight_order values using PUT
"""

import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv('.env')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

def fix_fight_ordering():
    """Fix fight ordering by updating existing fights with correct fight_order values"""
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("❌ Missing Supabase credentials")
        return False
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        logger.info("🔧 Fixing fight ordering with PUT...")
        
        # Get recent events
        events_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/events",
            headers=headers,
            params={'select': 'id,name,date', 'order': 'date.desc', 'limit': 3}
        )
        
        if events_response.status_code == 200:
            events = events_response.json()
            logger.info(f"📊 Found {len(events)} recent events")
            
            for event in events:
                logger.info(f"\n🎯 Fixing event: {event.get('name', 'Unknown')}")
                logger.info(f"   ID: {event['id']}")
                
                # Get fights for this event
                fights_response = requests.get(
                    f"{SUPABASE_URL}/rest/v1/fights",
                    headers=headers,
                    params={
                        'event_id': f'eq.{event["id"]}',
                        'select': 'id,winner_name,loser_name,fight_order,is_main_event,is_co_main_event',
                        'order': 'fight_order.asc'
                    }
                )
                
                if fights_response.status_code == 200:
                    fights = fights_response.json()
                    logger.info(f"   📊 Found {len(fights)} fights")
                    
                    # Update fight order starting from 1
                    for index, fight in enumerate(fights, start=1):
                        fight_id = fight['id']
                        current_order = fight.get('fight_order', 0)
                        new_order = index
                        
                        # Determine main event and co-main event
                        is_main_event = new_order == 1
                        is_co_main_event = new_order == 2
                        
                        if current_order != new_order:
                            logger.info(f"      Updating fight {fight_id}: order {current_order} -> {new_order}")
                            
                            # Update the fight using PUT
                            update_response = requests.put(
                                f"{SUPABASE_URL}/rest/v1/fights",
                                headers=headers,
                                params={'id': f'eq.{fight_id}'},
                                json={
                                    'fight_order': new_order,
                                    'is_main_event': is_main_event,
                                    'is_co_main_event': is_co_main_event
                                }
                            )
                            
                            if update_response.status_code == 200:
                                logger.info(f"      ✅ Updated fight order to {new_order}")
                            else:
                                logger.warning(f"      ⚠️ Failed to update fight: {update_response.status_code} - {update_response.text}")
                        else:
                            logger.info(f"      Fight {fight_id} already has correct order {current_order}")
                else:
                    logger.warning(f"   ⚠️ Error getting fights: {fights_response.status_code}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error fixing fight ordering: {e}")
        return False

if __name__ == "__main__":
    success = fix_fight_ordering()
    if success:
        print("✅ Fight ordering fix completed!")
    else:
        print("❌ Fight ordering fix failed!")
        exit(1) 