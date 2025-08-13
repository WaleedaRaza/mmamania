#!/usr/bin/env python3
"""
Check Schema
Check the actual schema of the events and fights tables
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

def check_schema():
    """Check the schema of events and fights tables"""
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("❌ Missing Supabase credentials")
        return False
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        # Check events table schema by trying different columns
        logger.info("🔍 Checking events table schema...")
        
        # Try to get a single event with all possible columns
        events_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/events",
            headers=headers,
            params={'select': 'id,name,date,venue,location,type', 'limit': 1}
        )
        
        if events_response.status_code == 200:
            events = events_response.json()
            if events:
                event = events[0]
                logger.info("✅ Events table columns found:")
                for key, value in event.items():
                    logger.info(f"   {key}: {value}")
            else:
                logger.info("📊 Events table is empty")
        else:
            logger.warning(f"⚠️ Could not get events: {events_response.status_code}")
            logger.warning(f"⚠️ Response: {events_response.text}")
        
        # Check fights table schema
        logger.info("🔍 Checking fights table schema...")
        
        fights_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/fights",
            headers=headers,
            params={'select': 'id,event_id,fighter1_id,fighter2_id,date,weight_class,rounds,result,winner_id,method,round,time,is_main_event,is_title_fight,status,winner_name,loser_name,fight_order,is_co_main_event,notes', 'limit': 1}
        )
        
        if fights_response.status_code == 200:
            fights = fights_response.json()
            if fights:
                fight = fights[0]
                logger.info("✅ Fights table columns found:")
                for key, value in fight.items():
                    logger.info(f"   {key}: {value}")
            else:
                logger.info("📊 Fights table is empty")
        else:
            logger.warning(f"⚠️ Could not get fights: {fights_response.status_code}")
            logger.warning(f"⚠️ Response: {fights_response.text}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking schema: {e}")
        return False

if __name__ == "__main__":
    success = check_schema()
    if success:
        print("✅ Schema check completed!")
    else:
        print("❌ Schema check failed!")
        exit(1) 