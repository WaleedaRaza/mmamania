#!/usr/bin/env python3
"""
Simple Schema Check
Check the schema by trying individual columns
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
    """Check the schema by trying individual columns"""
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("❌ Missing Supabase credentials")
        return False
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        # Check events table columns
        logger.info("🔍 Checking events table columns...")
        
        events_columns = ['id', 'name', 'date', 'venue', 'location']
        events_existing_columns = []
        
        for column in events_columns:
            try:
                response = requests.get(
                    f"{SUPABASE_URL}/rest/v1/events",
                    headers=headers,
                    params={'select': column, 'limit': 1}
                )
                if response.status_code == 200:
                    events_existing_columns.append(column)
                    logger.info(f"✅ Events column '{column}' exists")
                else:
                    logger.info(f"❌ Events column '{column}' does not exist")
            except Exception as e:
                logger.info(f"❌ Events column '{column}' error: {e}")
        
        logger.info(f"📊 Events table existing columns: {events_existing_columns}")
        
        # Check fights table columns
        logger.info("🔍 Checking fights table columns...")
        
        fights_columns = ['id', 'event_id', 'date', 'weight_class', 'rounds', 'result', 'winner_id', 'method', 'round', 'time', 'is_main_event', 'is_title_fight', 'status', 'winner_name', 'loser_name', 'fight_order', 'is_co_main_event', 'notes']
        fights_existing_columns = []
        
        for column in fights_columns:
            try:
                response = requests.get(
                    f"{SUPABASE_URL}/rest/v1/fights",
                    headers=headers,
                    params={'select': column, 'limit': 1}
                )
                if response.status_code == 200:
                    fights_existing_columns.append(column)
                    logger.info(f"✅ Fights column '{column}' exists")
                else:
                    logger.info(f"❌ Fights column '{column}' does not exist")
            except Exception as e:
                logger.info(f"❌ Fights column '{column}' error: {e}")
        
        logger.info(f"📊 Fights table existing columns: {fights_existing_columns}")
        
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