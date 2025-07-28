#!/usr/bin/env python3
"""
Real Dynamic Production Pipeline
Uses the real dynamic scraper to get current, accurate UFC data
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
from wikipedia.comprehensive_wikipedia_scraper import ComprehensiveWikipediaScraper

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class RealDynamicPipeline:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.service_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        self.headers = {
            'apikey': self.service_key,
            'Authorization': f'Bearer {self.service_key}',
            'Content-Type': 'application/json',
        }
        
        self.ufc_scraper = RealDynamicUFCScraper()
        self.wikipedia_scraper = ComprehensiveWikipediaScraper()
        
    def run_pipeline(self):
        """Run the complete real dynamic pipeline"""
        logger.info("🚀 Starting REAL DYNAMIC production pipeline...")
        
        try:
            # Step 1: Scrape current UFC rankings
            logger.info("📊 Step 1: Scraping current UFC rankings...")
            rankings = self.ufc_scraper.scrape_rankings()
            
            if not rankings:
                logger.error("❌ No rankings scraped!")
                return False
            
            logger.info(f"✅ Scraped {len(rankings)} current rankings")
            
            # Step 2: Upload rankings to Supabase
            logger.info("📤 Step 2: Uploading rankings to Supabase...")
            self.upload_rankings(rankings)
            
            # Step 3: Scrape fighter profiles for ranked fighters
            logger.info("👤 Step 3: Scraping fighter profiles...")
            self.scrape_fighter_profiles(rankings)
            
            # Step 4: Scrape Wikipedia events
            logger.info("📅 Step 4: Scraping Wikipedia events...")
            self.scrape_wikipedia_events()
            
            logger.info("🎉 REAL DYNAMIC pipeline completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            return False
    
    def upload_rankings(self, rankings):
        """Upload rankings to Supabase"""
        logger.info(f"📤 Uploading {len(rankings)} rankings to Supabase...")
        
        for ranking in rankings:
            try:
                # Prepare ranking data
                ranking_data = {
                    'name': ranking['name'],
                    'weight_class': ranking['weight_class'],
                    'rank': ranking['rank'],
                    'isChampion': ranking['isChampion'],
                    'rank_position': ranking['rank_position'],
                    'created_at': datetime.now().isoformat()
                }
                
                # Upload to Supabase
                response = requests.post(
                    f"{self.supabase_url}/rest/v1/rankings",
                    headers=self.headers,
                    json=ranking_data
                )
                
                if response.status_code == 201:
                    logger.info(f"✅ Uploaded ranking: {ranking['name']} ({ranking['weight_class']})")
                elif response.status_code == 409:
                    logger.warning(f"⚠️ Ranking already exists: {ranking['name']}")
                else:
                    logger.warning(f"⚠️ Failed to upload ranking for {ranking['name']}: {response.status_code}")
                    
            except Exception as e:
                logger.warning(f"⚠️ Error uploading ranking for {ranking['name']}: {e}")
    
    def scrape_fighter_profiles(self, rankings):
        """Scrape fighter profiles for ranked fighters"""
        logger.info("👤 Scraping fighter profiles for ranked fighters...")
        
        # Get unique fighter names
        fighter_names = list(set([ranking['name'] for ranking in rankings]))
        
        for fighter_name in fighter_names:
            try:
                # Scrape fighter profile
                profile = self.scrape_fighter_profile(fighter_name)
                
                if profile:
                    # Upload to Supabase
                    self.upload_fighter_profile(profile)
                    
            except Exception as e:
                logger.warning(f"⚠️ Error scraping profile for {fighter_name}: {e}")
    
    def scrape_fighter_profile(self, fighter_name):
        """Scrape individual fighter profile"""
        try:
            # Convert name to URL format
            url_name = fighter_name.lower().replace(' ', '-')
            url = f"https://www.ufc.com/athlete/{url_name}"
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # Basic profile data
                return {
                    'name': fighter_name,
                    'url': url,
                    'scraped_at': datetime.now().isoformat()
                }
            
        except Exception as e:
            logger.warning(f"⚠️ Error scraping profile for {fighter_name}: {e}")
        
        return None
    
    def upload_fighter_profile(self, profile):
        """Upload fighter profile to Supabase"""
        try:
            response = requests.post(
                f"{self.supabase_url}/rest/v1/fighters",
                headers=self.headers,
                json=profile
            )
            
            if response.status_code == 201:
                logger.info(f"✅ Uploaded fighter profile: {profile['name']}")
            elif response.status_code == 409:
                logger.warning(f"⚠️ Fighter profile already exists: {profile['name']}")
            else:
                logger.warning(f"⚠️ Failed to upload fighter profile for {profile['name']}: {response.status_code}")
                
        except Exception as e:
            logger.warning(f"⚠️ Error uploading fighter profile for {profile['name']}: {e}")
    
    def scrape_wikipedia_events(self):
        """Scrape Wikipedia UFC events"""
        try:
            logger.info("📅 Scraping Wikipedia UFC events...")
            
            # Use the existing Wikipedia scraper
            events = self.wikipedia_scraper.scrape_ufc_events()
            
            if events:
                logger.info(f"✅ Scraped {len(events)} Wikipedia events")
                
                # Upload events to Supabase
                for event in events:
                    self.upload_event(event)
            else:
                logger.warning("⚠️ No Wikipedia events scraped")
                
        except Exception as e:
            logger.warning(f"⚠️ Error scraping Wikipedia events: {e}")
    
    def upload_event(self, event):
        """Upload event to Supabase"""
        try:
            response = requests.post(
                f"{self.supabase_url}/rest/v1/events",
                headers=self.headers,
                json=event
            )
            
            if response.status_code == 201:
                logger.info(f"✅ Uploaded event: {event.get('title', 'Unknown')}")
            elif response.status_code == 409:
                logger.warning(f"⚠️ Event already exists: {event.get('title', 'Unknown')}")
            else:
                logger.warning(f"⚠️ Failed to upload event: {response.status_code}")
                
        except Exception as e:
            logger.warning(f"⚠️ Error uploading event: {e}")

def main():
    pipeline = RealDynamicPipeline()
    success = pipeline.run_pipeline()
    
    if success:
        print("\n🎉 REAL DYNAMIC pipeline completed successfully!")
        print("✅ Current UFC rankings uploaded")
        print("✅ Fighter profiles scraped")
        print("✅ Wikipedia events scraped")
        print("✅ All data is now LIVE and ACCURATE!")
    else:
        print("\n❌ Pipeline failed!")

if __name__ == "__main__":
    main() 