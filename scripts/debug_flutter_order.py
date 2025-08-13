#!/usr/bin/env python3
"""
Debug Flutter Order
Check what data the Flutter app is actually getting from Supabase
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

def debug_flutter_order():
    """Debug the exact data being returned to Flutter"""
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        # Get the UFC 317 event ID
        logger.info("🔍 Getting UFC 317 event ID...")
        events_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/events?name=eq.UFC 317: Topuria vs. Oliveira",
            headers=headers
        )
        
        if events_response.status_code != 200:
            logger.error(f"❌ Error getting events: {events_response.status_code}")
            return
        
        events = events_response.json()
        if not events:
            logger.error("❌ No UFC 317 event found")
            return
        
        event_id = events[0]['id']
        logger.info(f"✅ Found event ID: {event_id}")
        
        # Get fights for this event - EXACTLY like Flutter does
        logger.info("🔍 Getting fights for event (like Flutter does)...")
        fights_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/fights?event_id=eq.{event_id}&order=fight_order.asc",
            headers=headers
        )
        
        if fights_response.status_code != 200:
            logger.error(f"❌ Error getting fights: {fights_response.status_code}")
            return
        
        fights = fights_response.json()
        logger.info(f"📊 Found {len(fights)} fights")
        
        # Show the EXACT data being returned
        logger.info("🎯 EXACT DATA BEING RETURNED TO FLUTTER:")
        for i, fight in enumerate(fights):
            logger.info(f"   {i+1}. fight_order={fight.get('fight_order')} | winner={fight.get('winner_name')} | loser={fight.get('loser_name')} | weight_class={fight.get('weight_class')} | is_main_event={fight.get('is_main_event')}")
        
        # Check if there are any fights with wrong fight_order
        logger.info("🔍 Checking for ordering issues...")
        fight_orders = [fight.get('fight_order') for fight in fights]
        logger.info(f"   Fight orders: {fight_orders}")
        
        # Check if fights are in the expected order
        expected_order = [
            "Ilia Topuria",
            "Alexandre Pantoja", 
            "Joshua Van",
            "Beneil Dariush",
            "Payton Talbott",
            "Gregory Rodrigues",
            "Jose Miguel Delgado",
            "Tracy Cortez",
            "Terrance McKinney",
            "Jacobe Smith",
            "Jhonata Diniz"
        ]
        
        actual_winners = [fight.get('winner_name') for fight in fights]
        logger.info(f"   Expected winners: {expected_order}")
        logger.info(f"   Actual winners: {actual_winners}")
        
        # Find mismatches
        for i, (expected, actual) in enumerate(zip(expected_order, actual_winners)):
            if expected != actual:
                logger.error(f"❌ MISMATCH at position {i+1}: expected '{expected}', got '{actual}'")
        
        return fights
        
    except Exception as e:
        logger.error(f"❌ Error debugging: {e}")
        return None

if __name__ == "__main__":
    debug_flutter_order() 