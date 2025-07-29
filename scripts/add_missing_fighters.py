#!/usr/bin/env python3
"""
Add Missing Fighters to Supabase
Add fighters from fights.csv that don't exist in Supabase
"""

import os
import csv
import requests
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MissingFighterAdder:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.service_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        self.headers = {
            'apikey': self.service_key,
            'Authorization': f'Bearer {self.service_key}',
            'Content-Type': 'application/json',
        }
    
    def get_supabase_fighters(self):
        """Get all fighter names from Supabase"""
        try:
            response = requests.get(
                f"{self.supabase_url}/rest/v1/fighters",
                headers=self.headers,
                params={'select': 'id,name'}
            )
            
            if response.status_code == 200:
                fighters = response.json()
                return {fighter['name']: fighter['id'] for fighter in fighters}
            else:
                logger.error(f"❌ Failed to get fighters: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Error getting fighters: {e}")
            return {}
    
    def get_csv_fighter_names(self):
        """Get unique fighter names from fights.csv"""
        fighter_names = set()
        
        try:
            csv_path = "../data/processed/fights.csv"
            
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    fighter_names.add(row['fighter1'])
                    fighter_names.add(row['fighter2'])
            
            return fighter_names
            
        except Exception as e:
            logger.error(f"❌ Error reading CSV: {e}")
            return set()
    
    def create_fighter_record(self, name):
        """Create a basic fighter record"""
        return {
            'name': name,
            'weight_class': None,  # Will be updated later
            'record': {'wins': 0, 'losses': 0, 'draws': 0},
            'reach': None,
            'height': None,
            'stance': None,
            'style': None,
            'stats': {},
            'ufc_ranking': None,
            'is_active': True
        }
    
    def add_missing_fighters(self):
        """Add missing fighters to Supabase"""
        logger.info("🔍 Finding missing fighters...")
        
        # Get fighter names from both sources
        supabase_fighters = self.get_supabase_fighters()
        csv_fighters = self.get_csv_fighter_names()
        
        # Find missing fighters
        missing_fighters = csv_fighters - set(supabase_fighters.keys())
        
        logger.info(f"📊 Found {len(missing_fighters)} missing fighters")
        
        if not missing_fighters:
            logger.info("✅ No missing fighters found!")
            return
        
        # Add missing fighters in batches
        batch_size = 10
        total_added = 0
        
        for i in range(0, len(missing_fighters), batch_size):
            batch_names = list(missing_fighters)[i:i + batch_size]
            batch_records = [self.create_fighter_record(name) for name in batch_names]
            
            try:
                response = requests.post(
                    f"{self.supabase_url}/rest/v1/fighters",
                    headers=self.headers,
                    json=batch_records
                )
                
                if response.status_code == 201:
                    added_count = len(batch_records)
                    total_added += added_count
                    logger.info(f"✅ Added batch {i//batch_size + 1}: {added_count} fighters")
                    
                    # Log the names that were added
                    for name in batch_names:
                        logger.info(f"   - Added: {name}")
                        
                else:
                    logger.error(f"❌ Failed to add batch {i//batch_size + 1}: {response.status_code}")
                    logger.error(f"Response: {response.text}")
                    
            except Exception as e:
                logger.error(f"❌ Error adding batch {i//batch_size + 1}: {e}")
        
        logger.info(f"🎉 Total fighters added: {total_added}")
        return total_added

def main():
    """Main function"""
    adder = MissingFighterAdder()
    total_added = adder.add_missing_fighters()
    
    if total_added:
        print(f"\n🎯 Next steps:")
        print(f"   1. Run the fights migration script again")
        print(f"   2. Check that all fights are now uploaded")
        print(f"   3. Verify the fight cards screen shows real data")

if __name__ == "__main__":
    main() 