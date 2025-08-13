#!/usr/bin/env python3
"""
Check Current Fights
Check the current fight data to understand the update issue
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

def check_current_fights():
    """Check current fight data to understand the update issue"""
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("❌ Missing Supabase credentials")
        return False
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        logger.info("🔍 Checking current fight data...")
        
        # Get a sample fight to understand the structure
        fights_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/fights",
            headers=headers,
            params={'select': '*', 'limit': 1}
        )
        
        if fights_response.status_code == 200:
            fights = fights_response.json()
            if fights:
                sample_fight = fights[0]
                logger.info(f"📊 Sample fight structure:")
                for key, value in sample_fight.items():
                    logger.info(f"   {key}: {value}")
                
                # Try a simple update to test
                fight_id = sample_fight['id']
                logger.info(f"\n🧪 Testing update for fight {fight_id}")
                
                # Try PATCH
                patch_response = requests.patch(
                    f"{SUPABASE_URL}/rest/v1/fights",
                    headers=headers,
                    params={'id': f'eq.{fight_id}'},
                    json={'is_main_event': True}
                )
                
                logger.info(f"   PATCH response: {patch_response.status_code}")
                if patch_response.status_code != 200:
                    logger.info(f"   PATCH error: {patch_response.text}")
                
                # Try PUT
                put_response = requests.put(
                    f"{SUPABASE_URL}/rest/v1/fights",
                    headers=headers,
                    params={'id': f'eq.{fight_id}'},
                    json={'is_main_event': True}
                )
                
                logger.info(f"   PUT response: {put_response.status_code}")
                if put_response.status_code != 200:
                    logger.info(f"   PUT error: {put_response.text}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking fights: {e}")
        return False

if __name__ == "__main__":
    success = check_current_fights()
    if success:
        print("✅ Fight data check completed!")
    else:
        print("❌ Fight data check failed!")
        exit(1) 