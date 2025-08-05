#!/usr/bin/env python3
"""
Calculate Fighter Records
Calculate fighter records from fight data and update the fighters table
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

class FighterRecordCalculator:
    def __init__(self):
        self.supabase_headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
        }
    
    def get_all_fighters(self):
        """Get all fighters from the database"""
        try:
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/fighters?select=id,name",
                headers=self.supabase_headers
            )
            
            if response.status_code == 200:
                fighters = response.json()
                logger.info(f"📊 Found {len(fighters)} fighters")
                return fighters
            else:
                logger.error(f"❌ Error getting fighters: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error getting fighters: {str(e)}")
            return []
    
    def get_fighter_fights(self, fighter_id):
        """Get all fights for a specific fighter"""
        try:
            # Get fights where fighter is fighter1 or fighter2
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/fights?select=*&or=(fighter1_id.eq.{fighter_id},fighter2_id.eq.{fighter_id})",
                headers=self.supabase_headers
            )
            
            if response.status_code == 200:
                fights = response.json()
                return fights
            else:
                logger.error(f"❌ Error getting fights for fighter {fighter_id}: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error getting fights for fighter {fighter_id}: {str(e)}")
            return []
    
    def calculate_fighter_record(self, fighter_id, fights):
        """Calculate fighter record from fights"""
        wins = 0
        losses = 0
        draws = 0
        
        for fight in fights:
            result = fight.get('result')
            if not result:
                continue
                
            winner_id = result.get('winner_id')
            
            if winner_id == fighter_id:
                wins += 1
            elif winner_id is not None:  # There's a winner but it's not this fighter
                losses += 1
            else:
                # No winner means draw or no contest
                draws += 1
        
        return {
            'wins': wins,
            'losses': losses,
            'draws': draws,
            'total': wins + losses + draws
        }
    
    def update_fighter_record(self, fighter_id, record):
        """Update fighter record in database"""
        try:
            record_string = f"{record['wins']}-{record['losses']}-{record['draws']}"
            
            response = requests.patch(
                f"{SUPABASE_URL}/rest/v1/fighters?id=eq.{fighter_id}",
                headers=self.supabase_headers,
                json={'record': record_string}
            )
            
            if response.status_code == 204:
                logger.info(f"✅ Updated fighter {fighter_id}: {record_string}")
                return True
            else:
                logger.error(f"❌ Error updating fighter {fighter_id}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error updating fighter {fighter_id}: {str(e)}")
            return False
    
    def calculate_all_records(self):
        """Calculate records for all fighters"""
        logger.info("🚀 Starting fighter record calculation")
        logger.info("=" * 60)
        
        # Get all fighters
        fighters = self.get_all_fighters()
        if not fighters:
            logger.error("❌ No fighters found")
            return
        
        total_fighters = len(fighters)
        updated_count = 0
        error_count = 0
        
        for i, fighter in enumerate(fighters, 1):
            fighter_id = fighter['id']
            fighter_name = fighter['name']
            
            logger.info(f"📊 Processing {i}/{total_fighters}: {fighter_name}")
            
            # Get fighter's fights
            fights = self.get_fighter_fights(fighter_id)
            
            if not fights:
                logger.info(f"  ⚠️ No fights found for {fighter_name}")
                continue
            
            # Calculate record
            record = self.calculate_fighter_record(fighter_id, fights)
            
            logger.info(f"  📈 {fighter_name}: {record['wins']}-{record['losses']}-{record['draws']} ({record['total']} fights)")
            
            # Update fighter record
            if self.update_fighter_record(fighter_id, record):
                updated_count += 1
            else:
                error_count += 1
        
        logger.info("=" * 60)
        logger.info(f"🎉 Record calculation completed!")
        logger.info(f"✅ Updated: {updated_count} fighters")
        logger.info(f"❌ Errors: {error_count} fighters")
        logger.info(f"📊 Total processed: {total_fighters} fighters")

def main():
    calculator = FighterRecordCalculator()
    calculator.calculate_all_records()

if __name__ == "__main__":
    main() 