#!/usr/bin/env python3
"""
Populate Fighter Records
Populate fighter records from existing fighter profile data
"""

import os
import sys
import requests
import logging
import json
from dotenv import load_dotenv

load_dotenv('scripts/.env')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

class FighterRecordPopulator:
    def __init__(self):
        self.supabase_headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
        }
    
    def load_fighter_profiles(self):
        """Load fighter profiles from existing data"""
        try:
            with open('data/live/live_fighter_profiles.json', 'r') as f:
                data = json.load(f)
                profiles = data.get('profiles', [])
                logger.info(f"📊 Loaded {len(profiles)} fighter profiles")
                return profiles
        except Exception as e:
            logger.error(f"❌ Error loading fighter profiles: {str(e)}")
            return []
    
    def get_all_fighters(self):
        """Get all fighters from database"""
        try:
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/fighters?select=id,name",
                headers=self.supabase_headers
            )
            
            if response.status_code == 200:
                fighters = response.json()
                logger.info(f"📊 Found {len(fighters)} fighters in database")
                return fighters
            else:
                logger.error(f"❌ Error getting fighters: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error getting fighters: {str(e)}")
            return []
    
    def find_matching_profile(self, fighter_name, profiles):
        """Find matching fighter profile by name"""
        # Try exact match first
        for profile in profiles:
            if profile['name'].lower() == fighter_name.lower():
                return profile
        
        # Try partial match
        for profile in profiles:
            if fighter_name.lower() in profile['name'].lower() or profile['name'].lower() in fighter_name.lower():
                return profile
        
        return None
    
    def update_fighter_record(self, fighter_id, record):
        """Update fighter record in database"""
        try:
            response = requests.patch(
                f"{SUPABASE_URL}/rest/v1/fighters?id=eq.{fighter_id}",
                headers=self.supabase_headers,
                json={'record': record}
            )
            
            if response.status_code == 204:
                logger.info(f"✅ Updated fighter {fighter_id}: {record}")
                return True
            else:
                logger.error(f"❌ Error updating fighter {fighter_id}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error updating fighter {fighter_id}: {str(e)}")
            return False
    
    def populate_records(self):
        """Populate fighter records from profile data"""
        logger.info("🚀 Starting fighter record population")
        logger.info("=" * 60)
        
        # Load fighter profiles
        profiles = self.load_fighter_profiles()
        if not profiles:
            logger.error("❌ No fighter profiles found")
            return
        
        # Get all fighters from database
        fighters = self.get_all_fighters()
        if not fighters:
            logger.error("❌ No fighters found in database")
            return
        
        updated_count = 0
        matched_count = 0
        error_count = 0
        
        for fighter in fighters:
            fighter_id = fighter['id']
            fighter_name = fighter['name']
            
            # Find matching profile
            profile = self.find_matching_profile(fighter_name, profiles)
            
            if profile:
                matched_count += 1
                record = profile.get('record', '')
                
                if record and record != 'None':
                    logger.info(f"📊 {fighter_name}: {record}")
                    
                    if self.update_fighter_record(fighter_id, record):
                        updated_count += 1
                    else:
                        error_count += 1
                else:
                    logger.info(f"⚠️ {fighter_name}: No record in profile")
            else:
                logger.info(f"❌ {fighter_name}: No matching profile found")
        
        logger.info("=" * 60)
        logger.info(f"🎉 Fighter record population completed!")
        logger.info(f"✅ Updated: {updated_count} fighters")
        logger.info(f"📊 Matched profiles: {matched_count} fighters")
        logger.info(f"❌ Errors: {error_count} fighters")
        logger.info(f"📊 Total processed: {len(fighters)} fighters")

def main():
    populator = FighterRecordPopulator()
    populator.populate_records()

if __name__ == "__main__":
    main() 