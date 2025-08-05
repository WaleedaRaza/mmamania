#!/usr/bin/env python3
"""
Verify Current Database State
Check what's currently in the database and identify issues
"""

import os
import sys
import requests
import logging
from dotenv import load_dotenv

load_dotenv('scripts/.env')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

def verify_database_state():
    """Verify the current state of the database"""
    logger.info("🔍 Verifying Current Database State")
    logger.info("=" * 50)
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        # Check events
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/events?select=id,name,date&order=date.desc&limit=10",
            headers=headers
        )
        if response.status_code == 200:
            events = response.json()
            logger.info(f"📊 Events in database: {len(events)} (showing latest 10)")
            for event in events:
                logger.info(f"   - {event['name']} ({event['date']})")
        else:
            logger.error(f"❌ Error getting events: {response.status_code}")
        
        # Check fighters
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/fighters?select=id,name&limit=10",
            headers=headers
        )
        if response.status_code == 200:
            fighters = response.json()
            logger.info(f"🥊 Fighters in database: {len(fighters)} (showing first 10)")
            for fighter in fighters[:5]:
                logger.info(f"   - {fighter['name']}")
        else:
            logger.error(f"❌ Error getting fighters: {response.status_code}")
        
        # Check fights
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/fights?select=id,event_id,fighter1_id,fighter2_id&limit=10",
            headers=headers
        )
        if response.status_code == 200:
            fights = response.json()
            logger.info(f"🎯 Fights in database: {len(fights)} (showing first 10)")
            for fight in fights[:5]:
                logger.info(f"   - Fight {fight['id']}: Event {fight['event_id']}")
        else:
            logger.error(f"❌ Error getting fights: {response.status_code}")
        
        # Get total counts
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/events?select=id",
            headers=headers
        )
        if response.status_code == 200:
            total_events = len(response.json())
            logger.info(f"📊 Total events: {total_events}")
        
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/fighters?select=id",
            headers=headers
        )
        if response.status_code == 200:
            total_fighters = len(response.json())
            logger.info(f"🥊 Total fighters: {total_fighters}")
        
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/fights?select=id",
            headers=headers
        )
        if response.status_code == 200:
            total_fights = len(response.json())
            logger.info(f"🎯 Total fights: {total_fights}")
        
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"❌ Error verifying database: {str(e)}")

if __name__ == "__main__":
    verify_database_state() 