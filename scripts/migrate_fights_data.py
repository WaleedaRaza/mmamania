#!/usr/bin/env python3
"""
Migrate Fights Data to Supabase
Uploads processed fights data from CSV to Supabase database
"""

import os
import sys
import csv
import json
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FightsDataMigrator:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.service_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        self.headers = {
            'apikey': self.service_key,
            'Authorization': f'Bearer {self.service_key}',
            'Content-Type': 'application/json',
        }
        
        # Cache for fighter name to ID mapping
        self.fighter_cache = {}
        
    def run_migration(self):
        """Run the complete fights data migration"""
        logger.info("🚀 Starting Fights Data Migration...")
        
        try:
            # Step 1: Load fighter name to ID mapping
            logger.info("📊 Step 1: Loading fighter name to ID mapping...")
            self.load_fighter_mapping()
            
            # Step 2: Load and process fights data
            logger.info("🥊 Step 2: Loading fights data from CSV...")
            fights_data = self.load_fights_data()
            
            if not fights_data:
                logger.error("❌ No fights data found!")
                return False
            
            # Step 3: Upload fights to Supabase
            logger.info("📤 Step 3: Uploading fights to Supabase...")
            self.upload_fights(fights_data)
            
            logger.info("🎉 Fights Data Migration completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return False
    
    def load_fighter_mapping(self):
        """Load fighter name to ID mapping from Supabase"""
        try:
            response = requests.get(
                f"{self.supabase_url}/rest/v1/fighters",
                headers=self.headers,
                params={'select': 'id,name'}
            )
            
            if response.status_code == 200:
                fighters = response.json()
                for fighter in fighters:
                    self.fighter_cache[fighter['name']] = fighter['id']
                logger.info(f"✅ Loaded {len(self.fighter_cache)} fighter mappings")
            else:
                logger.error(f"❌ Failed to load fighters: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Error loading fighter mapping: {e}")
    
    def load_fights_data(self):
        """Load fights data from CSV and process it"""
        fights_data = []
        
        try:
            csv_path = "../data/processed/fights.csv"
            
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    # Get fighter IDs
                    fighter1_id = self.fighter_cache.get(row['fighter1'])
                    fighter2_id = self.fighter_cache.get(row['fighter2'])
                    
                    if not fighter1_id or not fighter2_id:
                        logger.warning(f"⚠️ Skipping fight: {row['fighter1']} vs {row['fighter2']} (fighters not found)")
                        continue
                    
                    # Determine winner ID
                    winner_id = None
                    if row['winner'] == row['fighter1']:
                        winner_id = fighter1_id
                    elif row['winner'] == row['fighter2']:
                        winner_id = fighter2_id
                    
                    # Create result JSON
                    result = {
                        'winner_id': winner_id,
                        'method': row['method'],
                        'round': row['round'] if row['round'] else None,
                        'time': row['time'] if row['time'] else None
                    }
                    
                    # Create fight data
                    fight_data = {
                        'fighter1_id': fighter1_id,
                        'fighter2_id': fighter2_id,
                        'status': 'completed',
                        'result': result
                    }
                    
                    fights_data.append(fight_data)
                
                logger.info(f"✅ Processed {len(fights_data)} fights from CSV")
                return fights_data
                
        except Exception as e:
            logger.error(f"❌ Error loading fights data: {e}")
            return []
    
    def upload_fights(self, fights_data):
        """Upload fights data to Supabase"""
        try:
            # Upload in batches to avoid timeout
            batch_size = 50
            total_uploaded = 0
            
            for i in range(0, len(fights_data), batch_size):
                batch = fights_data[i:i + batch_size]
                
                response = requests.post(
                    f"{self.supabase_url}/rest/v1/fights",
                    headers=self.headers,
                    json=batch
                )
                
                if response.status_code == 201:
                    uploaded_count = len(batch)
                    total_uploaded += uploaded_count
                    logger.info(f"✅ Uploaded batch {i//batch_size + 1}: {uploaded_count} fights")
                else:
                    logger.error(f"❌ Failed to upload batch {i//batch_size + 1}: {response.status_code}")
                    logger.error(f"Response: {response.text}")
            
            logger.info(f"🎉 Total fights uploaded: {total_uploaded}")
            
        except Exception as e:
            logger.error(f"❌ Error uploading fights: {e}")

def main():
    migrator = FightsDataMigrator()
    migrator.run_migration()

if __name__ == "__main__":
    main() 