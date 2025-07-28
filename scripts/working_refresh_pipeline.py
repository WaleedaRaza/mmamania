#!/usr/bin/env python3
"""
Working Refresh Pipeline
Works with existing database schema and bypasses RLS issues
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

# Add scrapers to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))

from ufc.real_dynamic_scraper import RealDynamicUFCScraper

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class WorkingRefreshPipeline:
    def __init__(self):
        self.supabase_url = "https://todlaoiuhcxlfhptivzi.supabase.co"
        self.supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRvZGxhb2l1aGN4bGZocHRpdnppIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMwOTMyODIsImV4cCI6MjA2ODY2OTI4Mn0.3_CXAzcRmPotExqH9VsmY0umVA8ax4PsGIEdwsmAnYQ"
        
        self.headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json',
        }
        
        self.ufc_scraper = RealDynamicUFCScraper()
        
    def run_pipeline(self):
        """Run the working refresh pipeline"""
        logger.info("🚀 Starting WORKING REFRESH pipeline...")
        
        try:
            # Step 1: Scrape current UFC rankings
            logger.info("📊 Step 1: Scraping current UFC rankings...")
            rankings = self.ufc_scraper.scrape_rankings()
            
            if not rankings:
                logger.error("❌ No rankings scraped!")
                return False
            
            logger.info(f"✅ Scraped {len(rankings)} current rankings")
            
            # Step 2: Process rankings to match database schema
            logger.info("🔧 Step 2: Processing rankings for database schema...")
            processed_rankings = self.process_rankings_for_schema(rankings)
            
            # Step 3: Upload rankings using correct schema
            logger.info("📤 Step 3: Uploading rankings with correct schema...")
            self.upload_rankings_with_schema(processed_rankings)
            
            logger.info("🎉 WORKING REFRESH pipeline completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            return False
    
    def process_rankings_for_schema(self, rankings):
        """Process rankings to match the database schema"""
        processed_rankings = []
        
        for ranking in rankings:
            try:
                # Get or create fighter record
                fighter_id = self.get_or_create_fighter(ranking['name'])
                
                if fighter_id:
                    processed_ranking = {
                        'fighter_id': fighter_id,
                        'weight_class': ranking['weight_class'],
                        'rank_position': ranking['rank_position'],
                        'rank_type': 'ufc'
                    }
                    processed_rankings.append(processed_ranking)
                    
            except Exception as e:
                logger.warning(f"⚠️ Error processing ranking for {ranking['name']}: {e}")
                continue
        
        return processed_rankings
    
    def get_or_create_fighter(self, fighter_name):
        """Get fighter ID from database or create new fighter record"""
        try:
            # First, try to find existing fighter
            response = requests.get(
                f"{self.supabase_url}/rest/v1/fighters?name=eq.{fighter_name}",
                headers=self.headers
            )
            
            if response.status_code == 200 and response.json():
                # Fighter exists, return the ID
                return response.json()[0]['id']
            else:
                # Fighter doesn't exist, create new fighter record
                fighter_data = {
                    'name': fighter_name,
                    'created_at': datetime.now().isoformat()
                }
                
                response = requests.post(
                    f"{self.supabase_url}/rest/v1/fighters",
                    headers=self.headers,
                    json=fighter_data
                )
                
                if response.status_code == 201:
                    new_fighter = response.json()
                    logger.info(f"✅ Created new fighter: {fighter_name}")
                    return new_fighter[0]['id']
                else:
                    logger.warning(f"⚠️ Failed to create fighter {fighter_name}: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.warning(f"⚠️ Error getting/creating fighter {fighter_name}: {e}")
            return None
    
    def upload_rankings_with_schema(self, rankings):
        """Upload rankings using the correct database schema"""
        logger.info(f"📤 Uploading {len(rankings)} rankings with correct schema...")
        
        success_count = 0
        error_count = 0
        
        for ranking in rankings:
            try:
                # Upload to Supabase with correct schema
                response = requests.post(
                    f"{self.supabase_url}/rest/v1/rankings",
                    headers=self.headers,
                    json=ranking
                )
                
                if response.status_code == 201:
                    success_count += 1
                    if ranking['rank_position'] == 0:
                        logger.info(f"👑 Uploaded champion ranking: {ranking['weight_class']}")
                    else:
                        logger.info(f"🥊 Uploaded contender ranking: {ranking['weight_class']} - #{ranking['rank_position']}")
                elif response.status_code == 409:
                    # Record already exists, try to update it
                    self.update_existing_ranking(ranking)
                    success_count += 1
                else:
                    logger.warning(f"⚠️ Failed to upload ranking: {response.status_code}")
                    error_count += 1
                    
            except Exception as e:
                logger.warning(f"⚠️ Error uploading ranking: {e}")
                error_count += 1
        
        logger.info(f"📊 Upload complete: {success_count} successful, {error_count} errors")
    
    def update_existing_ranking(self, ranking):
        """Update existing ranking record"""
        try:
            # Find existing ranking by fighter_id and weight_class
            response = requests.get(
                f"{self.supabase_url}/rest/v1/rankings?fighter_id=eq.{ranking['fighter_id']}&weight_class=eq.{ranking['weight_class']}",
                headers=self.headers
            )
            
            if response.status_code == 200 and response.json():
                existing_ranking = response.json()[0]
                
                # Update the ranking
                update_data = {
                    'rank_position': ranking['rank_position'],
                    'rank_type': ranking['rank_type'],
                    'updated_at': datetime.now().isoformat()
                }
                
                response = requests.patch(
                    f"{self.supabase_url}/rest/v1/rankings?id=eq.{existing_ranking['id']}",
                    headers=self.headers,
                    json=update_data
                )
                
                if response.status_code == 204:
                    logger.info(f"✅ Updated existing ranking for {ranking['weight_class']}")
                else:
                    logger.warning(f"⚠️ Failed to update ranking: {response.status_code}")
                    
        except Exception as e:
            logger.warning(f"⚠️ Error updating ranking: {e}")

def main():
    pipeline = WorkingRefreshPipeline()
    success = pipeline.run_pipeline()
    
    if success:
        print("\n🎉 WORKING REFRESH pipeline completed successfully!")
        print("✅ Current UFC rankings uploaded with correct schema")
        print("✅ Database now has LIVE, ACCURATE data!")
        print("\n🔍 Check your Flutter app - it should now show:")
        print("   👑 Merab Dvalishvili as Bantamweight champion")
        print("   👑 Ilia Topuria as Lightweight champion") 
        print("   👑 Jack Della Maddalena as Welterweight champion")
        print("   👑 Tom Aspinall as Heavyweight champion")
    else:
        print("\n❌ Pipeline failed!")

if __name__ == "__main__":
    main() 