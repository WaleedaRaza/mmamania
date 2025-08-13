#!/usr/bin/env python3
"""
Check Events Table
See what's in the events table
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

def check_events():
    """Check what's in the events table"""
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("❌ Missing Supabase credentials")
        return False
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        # Get first few events
        logger.info("🔍 Checking events table...")
        events_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/events",
            headers=headers,
            params={'select': 'id,title,date', 'limit': 5}
        )
        
        if events_response.status_code == 200:
            events = events_response.json()
            logger.info(f"📊 Found {len(events)} events (showing first 5):")
            for event in events:
                logger.info(f"   ID: {event['id']}, Title: {event.get('title', 'N/A')}, Date: {event.get('date', 'N/A')}")
        else:
            logger.warning(f"⚠️ Could not get events: {events_response.status_code}")
            logger.warning(f"⚠️ Response: {events_response.text}")
        
        # Get total count
        count_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/events",
            headers=headers,
            params={'select': 'id'}
        )
        
        if count_response.status_code == 200:
            total_events = len(count_response.json())
            logger.info(f"📊 Total events in table: {total_events}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking events: {e}")
        return False

if __name__ == "__main__":
    success = check_events()
    if success:
        print("✅ Events check completed!")
    else:
        print("❌ Events check failed!")
        exit(1) 