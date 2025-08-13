#!/usr/bin/env python3
"""
Check Fights
Check what fights are in the database
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

def check_fights():
    """Check what fights are in the database"""
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("❌ Missing Supabase credentials")
        return False
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        # Get all fights
        logger.info("🔍 Checking fights table...")
        fights_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/fights",
            headers=headers,
            params={'select': 'id,event_id,winner_name,loser_name,fight_order,is_main_event,weight_class,method', 'limit': 10}
        )
        
        if fights_response.status_code == 200:
            fights = fights_response.json()
            logger.info(f"📊 Found {len(fights)} fights (showing first 10):")
            for fight in fights:
                logger.info(f"   ID: {fight['id']}")
                logger.info(f"   Event ID: {fight['event_id']}")
                logger.info(f"   Winner: {fight.get('winner_name', 'N/A')}")
                logger.info(f"   Loser: {fight.get('loser_name', 'N/A')}")
                logger.info(f"   Order: {fight.get('fight_order', 'N/A')}")
                logger.info(f"   Main Event: {fight.get('is_main_event', 'N/A')}")
                logger.info(f"   Weight Class: {fight.get('weight_class', 'N/A')}")
                logger.info(f"   Method: {fight.get('method', 'N/A')}")
                logger.info("   ---")
        else:
            logger.warning(f"⚠️ Could not get fights: {fights_response.status_code}")
            logger.warning(f"⚠️ Response: {fights_response.text}")
        
        # Get total count
        count_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/fights",
            headers=headers,
            params={'select': 'id'}
        )
        
        if count_response.status_code == 200:
            total_fights = len(count_response.json())
            logger.info(f"📊 Total fights in table: {total_fights}")
        
        # Check events
        logger.info("🔍 Checking events table...")
        events_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/events",
            headers=headers,
            params={'select': 'id,name', 'limit': 5}
        )
        
        if events_response.status_code == 200:
            events = events_response.json()
            logger.info(f"📊 Found {len(events)} events (showing first 5):")
            for event in events:
                logger.info(f"   ID: {event['id']}")
                logger.info(f"   Name: {event.get('name', 'N/A')}")
                logger.info("   ---")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking fights: {e}")
        return False

if __name__ == "__main__":
    success = check_fights()
    if success:
        print("✅ Fights check completed!")
    else:
        print("❌ Fights check failed!")
        exit(1) 