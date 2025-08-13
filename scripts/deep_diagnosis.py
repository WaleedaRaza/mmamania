#!/usr/bin/env python3
"""
Deep Diagnosis
Comprehensive analysis of why Flutter can't find fights
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

def deep_diagnosis():
    """Deep diagnosis of the fight mapping issue"""
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("❌ Missing Supabase credentials")
        return False
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        logger.info("🔍 STEP 1: Check all events in database")
        events_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/events",
            headers=headers,
            params={'select': 'id,name,date', 'order': 'date.desc'}
        )
        
        if events_response.status_code == 200:
            all_events = events_response.json()
            logger.info(f"📊 Total events in database: {len(all_events)}")
            
            # Show first 10 events
            for i, event in enumerate(all_events[:10]):
                logger.info(f"   {i+1}. {event.get('name', 'Unknown')} (ID: {event['id']}) - Date: {event.get('date', 'N/A')}")
        
        logger.info("\n🔍 STEP 2: Check which events have fights")
        events_with_fights = []
        for event in all_events:
            fights_response = requests.get(
                f"{SUPABASE_URL}/rest/v1/fights",
                headers=headers,
                params={'event_id': f'eq.{event["id"]}', 'select': 'id'}
            )
            if fights_response.status_code == 200:
                fights = fights_response.json()
                if len(fights) > 0:
                    events_with_fights.append({
                        'event': event,
                        'fight_count': len(fights)
                    })
                    logger.info(f"✅ Event '{event.get('name', 'Unknown')}' (ID: {event['id']}): {len(fights)} fights")
        
        logger.info(f"\n📊 Events with fights: {len(events_with_fights)}")
        
        logger.info("\n🔍 STEP 3: Check Flutter's event loading logic")
        # Simulate what Flutter is doing - get events ordered by date
        flutter_events_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/events",
            headers=headers,
            params={'select': 'id,name,date', 'order': 'date.desc', 'limit': 10}
        )
        
        if flutter_events_response.status_code == 200:
            flutter_events = flutter_events_response.json()
            logger.info(f"📊 Flutter would load these events (first 10):")
            for i, event in enumerate(flutter_events):
                logger.info(f"   {i+1}. {event.get('name', 'Unknown')} (ID: {event['id']})")
                
                # Check if this event has fights
                fights_response = requests.get(
                    f"{SUPABASE_URL}/rest/v1/fights",
                    headers=headers,
                    params={'event_id': f'eq.{event["id"]}', 'select': 'id'}
                )
                if fights_response.status_code == 200:
                    fights = fights_response.json()
                    logger.info(f"      -> Has {len(fights)} fights")
                else:
                    logger.warning(f"      -> Error checking fights: {fights_response.status_code}")
        
        logger.info("\n🔍 STEP 4: Check if there are any fights at all")
        all_fights_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/fights",
            headers=headers,
            params={'select': 'id,event_id,winner_name,loser_name', 'limit': 5}
        )
        
        if all_fights_response.status_code == 200:
            all_fights = all_fights_response.json()
            logger.info(f"📊 Sample fights in database:")
            for fight in all_fights:
                logger.info(f"   Fight ID: {fight['id']}")
                logger.info(f"   Event ID: {fight['event_id']}")
                logger.info(f"   Winner: {fight.get('winner_name', 'N/A')}")
                logger.info(f"   Loser: {fight.get('loser_name', 'N/A')}")
                logger.info("   ---")
        
        logger.info("\n🔍 STEP 5: Check if events have correct dates")
        for event in all_events[:5]:
            logger.info(f"Event: {event.get('name', 'Unknown')}")
            logger.info(f"  ID: {event['id']}")
            logger.info(f"  Date: {event.get('date', 'N/A')}")
            
            # Check fights for this event
            fights_response = requests.get(
                f"{SUPABASE_URL}/rest/v1/fights",
                headers=headers,
                params={'event_id': f'eq.{event["id"]}', 'select': 'id,winner_name,loser_name'}
            )
            if fights_response.status_code == 200:
                fights = fights_response.json()
                logger.info(f"  Fights: {len(fights)}")
                if fights:
                    logger.info(f"  Sample fight: {fights[0].get('winner_name', 'N/A')} vs {fights[0].get('loser_name', 'N/A')}")
            logger.info("  ---")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in deep diagnosis: {e}")
        return False

if __name__ == "__main__":
    success = deep_diagnosis()
    if success:
        print("✅ Deep diagnosis completed!")
    else:
        print("❌ Deep diagnosis failed!")
        exit(1) 