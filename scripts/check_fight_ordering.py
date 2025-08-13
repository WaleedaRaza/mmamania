#!/usr/bin/env python3
"""
Check Fight Ordering
Check the fight_order values and main event identification
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

def check_fight_ordering():
    """Check fight ordering and main event identification"""
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("❌ Missing Supabase credentials")
        return False
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        logger.info("🔍 Checking fight ordering and main event identification...")
        
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
                logger.info(f"\n🎯 Event: {event.get('name', 'Unknown')}")
                logger.info(f"   ID: {event['id']}")
                
                # Get fights for this event ordered by fight_order
                fights_response = requests.get(
                    f"{SUPABASE_URL}/rest/v1/fights",
                    headers=headers,
                    params={
                        'event_id': f'eq.{event["id"]}',
                        'select': 'winner_name,loser_name,method,fight_order,is_main_event,is_co_main_event,weight_class',
                        'order': 'fight_order.asc'
                    }
                )
                
                if fights_response.status_code == 200:
                    fights = fights_response.json()
                    logger.info(f"   📊 {len(fights)} fights (ordered by fight_order):")
                    
                    for fight in fights:
                        winner = fight.get('winner_name', 'N/A')
                        loser = fight.get('loser_name', 'N/A')
                        method = fight.get('method', 'N/A')
                        order = fight.get('fight_order', 'N/A')
                        is_main = fight.get('is_main_event', False)
                        is_co_main = fight.get('is_co_main_event', False)
                        weight = fight.get('weight_class', 'N/A')
                        
                        main_text = " (MAIN EVENT)" if is_main else ""
                        co_main_text = " (CO-MAIN)" if is_co_main else ""
                        event_text = main_text + co_main_text
                        
                        logger.info(f"      {order}. {winner} def. {loser} - {method} - {weight}{event_text}")
                        
                        # Check if fight_order matches is_main_event
                        if order == 1 and not is_main:
                            logger.warning(f"      ⚠️ Fight order {order} but is_main_event is {is_main}")
                        elif order == 2 and not is_co_main:
                            logger.warning(f"      ⚠️ Fight order {order} but is_co_main_event is {is_co_main}")
                else:
                    logger.warning(f"   ⚠️ Error getting fights: {fights_response.status_code}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking fight ordering: {e}")
        return False

if __name__ == "__main__":
    success = check_fight_ordering()
    if success:
        print("✅ Fight ordering check completed!")
    else:
        print("❌ Fight ordering check failed!")
        exit(1) 