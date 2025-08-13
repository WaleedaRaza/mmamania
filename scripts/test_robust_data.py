#!/usr/bin/env python3
"""
Test Robust Data
Verify the quality of data from the robust scraper
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

def test_robust_data():
    """Test the quality of data from the robust scraper"""
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("❌ Missing Supabase credentials")
        return False
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        logger.info("🔍 Testing robust scraper data quality...")
        
        # Get recent events
        events_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/events",
            headers=headers,
            params={'select': 'id,name,date', 'order': 'date.desc', 'limit': 5}
        )
        
        if events_response.status_code == 200:
            events = events_response.json()
            logger.info(f"📊 Found {len(events)} recent events")
            
            for event in events:
                logger.info(f"\n🎯 Event: {event.get('name', 'Unknown')}")
                logger.info(f"   ID: {event['id']}")
                logger.info(f"   Date: {event.get('date', 'N/A')}")
                
                # Get fights for this event
                fights_response = requests.get(
                    f"{SUPABASE_URL}/rest/v1/fights",
                    headers=headers,
                    params={
                        'event_id': f'eq.{event["id"]}',
                        'select': 'winner_name,loser_name,method,fight_order,is_main_event,weight_class',
                        'order': 'fight_order.asc'
                    }
                )
                
                if fights_response.status_code == 200:
                    fights = fights_response.json()
                    logger.info(f"   📊 {len(fights)} fights:")
                    
                    for fight in fights[:5]:  # Show first 5 fights
                        winner = fight.get('winner_name', 'N/A')
                        loser = fight.get('loser_name', 'N/A')
                        method = fight.get('method', 'N/A')
                        order = fight.get('fight_order', 'N/A')
                        is_main = fight.get('is_main_event', False)
                        weight = fight.get('weight_class', 'N/A')
                        
                        main_text = " (MAIN EVENT)" if is_main else ""
                        logger.info(f"      {order}. {winner} def. {loser} - {method} - {weight}{main_text}")
                    
                    if len(fights) > 5:
                        logger.info(f"      ... and {len(fights) - 5} more fights")
                else:
                    logger.warning(f"   ⚠️ Error getting fights: {fights_response.status_code}")
        
        # Test Flutter loading simulation
        logger.info("\n🔍 Testing Flutter loading simulation...")
        flutter_events_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/events",
            headers=headers,
            params={'select': 'id,name,date', 'order': 'date.desc', 'limit': 3}
        )
        
        if flutter_events_response.status_code == 200:
            flutter_events = flutter_events_response.json()
            logger.info(f"📊 Flutter would load these events:")
            
            total_fights = 0
            for event in flutter_events:
                fights_response = requests.get(
                    f"{SUPABASE_URL}/rest/v1/fights",
                    headers=headers,
                    params={'event_id': f'eq.{event["id"]}', 'select': 'id'}
                )
                
                if fights_response.status_code == 200:
                    fights = fights_response.json()
                    total_fights += len(fights)
                    logger.info(f"   ✅ {event.get('name', 'Unknown')}: {len(fights)} fights")
                else:
                    logger.warning(f"   ⚠️ {event.get('name', 'Unknown')}: Error loading fights")
            
            logger.info(f"🎯 TOTAL: Flutter would find {total_fights} fights across {len(flutter_events)} events")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing robust data: {e}")
        return False

if __name__ == "__main__":
    success = test_robust_data()
    if success:
        print("✅ Robust data test completed!")
    else:
        print("❌ Robust data test failed!")
        exit(1) 