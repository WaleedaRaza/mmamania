#!/usr/bin/env python3
"""
Test Create Event
Test creating a single event
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

def test_create_event():
    """Test creating a single event"""
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("❌ Missing Supabase credentials")
        return False
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        # Test event data
        event_payload = {
            'name': 'Test UFC Event',
            'date': '2025-08-08',
            'venue': 'Test Arena',
            'location': 'Test City'
        }
        
        logger.info(f"🧪 Testing event creation with payload: {event_payload}")
        
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/events",
            headers=headers,
            json=event_payload
        )
        
        logger.info(f"📊 Response status: {response.status_code}")
        logger.info(f"📊 Response headers: {dict(response.headers)}")
        logger.info(f"📊 Response text: '{response.text}'")
        
        if response.status_code == 201:
            try:
                response_data = response.json()
                logger.info(f"✅ Event created successfully: {response_data}")
                return True
            except Exception as e:
                logger.error(f"❌ Error parsing response: {e}")
                return False
        else:
            logger.error(f"❌ Failed to create event: {response.status_code}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Error creating event: {e}")
        return False

if __name__ == "__main__":
    success = test_create_event()
    if success:
        print("✅ Event creation test completed successfully!")
    else:
        print("❌ Event creation test failed!")
        exit(1) 