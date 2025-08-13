#!/usr/bin/env python3
"""
Test Flutter Loading
Test what Flutter would load after cleanup
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

def test_flutter_loading():
    """Test what Flutter would load after cleanup"""
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("❌ Missing Supabase credentials")
        return False
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        logger.info("🔍 Testing Flutter's event loading logic...")
        
        # Simulate what Flutter does - get events ordered by date
        events_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/events",
            headers=headers,
            params={'select': 'id,name,date', 'order': 'date.desc', 'limit': 10}
        )
        
        if events_response.status_code == 200:
            events = events_response.json()
            logger.info(f"📊 Flutter would load these events:")
            
            total_fights = 0
            for i, event in enumerate(events):
                logger.info(f"   {i+1}. {event.get('name', 'Unknown')} (ID: {event['id']})")
                
                # Check if this event has fights
                fights_response = requests.get(
                    f"{SUPABASE_URL}/rest/v1/fights",
                    headers=headers,
                    params={'event_id': f'eq.{event["id"]}', 'select': 'id,winner_name,loser_name,fight_order,is_main_event'}
                )
                
                if fights_response.status_code == 200:
                    fights = fights_response.json()
                    logger.info(f"      -> Has {len(fights)} fights")
                    total_fights += len(fights)
                    
                    # Show sample fights
                    if fights:
                        logger.info(f"      -> Sample fights:")
                        for fight in fights[:3]:  # Show first 3 fights
                            winner = fight.get('winner_name', 'Unknown')
                            loser = fight.get('loser_name', 'Unknown')
                            order = fight.get('fight_order', 'N/A')
                            is_main = fight.get('is_main_event', False)
                            main_text = " (Main Event)" if is_main else ""
                            logger.info(f"         {order}. {winner} def. {loser}{main_text}")
                else:
                    logger.warning(f"      -> Error checking fights: {fights_response.status_code}")
            
            logger.info(f"\n📊 SUMMARY:")
            logger.info(f"   Events loaded: {len(events)}")
            logger.info(f"   Total fights: {total_fights}")
            
            if total_fights > 0:
                logger.info("   ✅ SUCCESS: Flutter should now find fights!")
            else:
                logger.warning("   ❌ PROBLEM: Flutter still won't find fights")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing Flutter loading: {e}")
        return False

if __name__ == "__main__":
    success = test_flutter_loading()
    if success:
        print("✅ Flutter loading test completed!")
    else:
        print("❌ Flutter loading test failed!")
        exit(1) 