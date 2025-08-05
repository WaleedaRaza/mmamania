#!/usr/bin/env python3
"""
Check Rankings Count
Simple script to check how many rankings are in the database
"""

import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv('scripts/.env')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

def check_rankings():
    """Check the rankings count"""
    logger.info("🔍 Checking rankings count...")
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/rankings?select=id",
            headers=headers
        )
        
        if response.status_code == 200:
            rankings = response.json()
            logger.info(f"🏆 RANKINGS COUNT: {len(rankings)} rankings in database")
            
            if len(rankings) >= 200:
                logger.info("✅ Rankings look complete!")
            else:
                logger.warning(f"⚠️ Only {len(rankings)} rankings found - may be incomplete")
                
        else:
            logger.error(f"❌ Error getting rankings: {response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ Error checking rankings: {str(e)}")

if __name__ == "__main__":
    check_rankings() 