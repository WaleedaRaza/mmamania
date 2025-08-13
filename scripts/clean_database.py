#!/usr/bin/env python3
"""
Clean Database
Remove duplicates and empty fights from the database
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

def clean_database():
    """Clean up the database by removing duplicates and empty fights"""
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("❌ Missing Supabase credentials")
        return False
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        logger.info("🧹 Cleaning database...")
        
        # Get all fights
        fights_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/fights",
            headers=headers,
            params={'select': 'id,winner_name,loser_name,event_id'}
        )
        
        if fights_response.status_code == 200:
            all_fights = fights_response.json()
            logger.info(f"📊 Found {len(all_fights)} total fights")
            
            # Find fights to delete (empty names or duplicates)
            fights_to_delete = []
            seen_fights = set()
            
            for fight in all_fights:
                winner = fight.get('winner_name', '').strip()
                loser = fight.get('loser_name', '').strip()
                event_id = fight.get('event_id')
                
                # Check for empty names
                if not winner or not loser:
                    fights_to_delete.append(fight['id'])
                    logger.info(f"🗑️ Will delete fight with empty names: '{winner}' vs '{loser}'")
                    continue
                
                # Check for duplicates
                fight_key = f"{event_id}:{winner}:{loser}"
                if fight_key in seen_fights:
                    fights_to_delete.append(fight['id'])
                    logger.info(f"🗑️ Will delete duplicate fight: {winner} vs {loser}")
                else:
                    seen_fights.add(fight_key)
            
            logger.info(f"📊 Found {len(fights_to_delete)} fights to delete")
            
            # Delete the fights
            deleted_count = 0
            for fight_id in fights_to_delete:
                delete_response = requests.delete(
                    f"{SUPABASE_URL}/rest/v1/fights",
                    headers=headers,
                    params={'id': f'eq.{fight_id}'}
                )
                
                if delete_response.status_code == 200:
                    deleted_count += 1
                else:
                    logger.warning(f"⚠️ Failed to delete fight {fight_id}: {delete_response.status_code}")
            
            logger.info(f"✅ Deleted {deleted_count} fights")
            
            # Verify cleanup
            remaining_response = requests.get(
                f"{SUPABASE_URL}/rest/v1/fights",
                headers=headers,
                params={'select': 'id'}
            )
            
            if remaining_response.status_code == 200:
                remaining_fights = remaining_response.json()
                logger.info(f"📊 Remaining fights: {len(remaining_fights)}")
                
                # Show sample of remaining fights
                sample_response = requests.get(
                    f"{SUPABASE_URL}/rest/v1/fights",
                    headers=headers,
                    params={'select': 'winner_name,loser_name,method,fight_order', 'limit': 5}
                )
                
                if sample_response.status_code == 200:
                    sample_fights = sample_response.json()
                    logger.info("📊 Sample of remaining fights:")
                    for fight in sample_fights:
                        winner = fight.get('winner_name', 'N/A')
                        loser = fight.get('loser_name', 'N/A')
                        method = fight.get('method', 'N/A')
                        order = fight.get('fight_order', 'N/A')
                        logger.info(f"   {order}. {winner} def. {loser} - {method}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error cleaning database: {e}")
        return False

if __name__ == "__main__":
    success = clean_database()
    if success:
        print("✅ Database cleanup completed!")
    else:
        print("❌ Database cleanup failed!")
        exit(1) 