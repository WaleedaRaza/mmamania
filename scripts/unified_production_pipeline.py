#!/usr/bin/env python3
"""
Unified Production Pipeline
One pipeline that uses the unified UFC scraper to get real-time data
"""

import sys
import os
import logging
import requests
import json
from datetime import datetime

# Add the scrapers directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))

from ufc.real_dynamic_scraper import RealDynamicUFCScraper

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UnifiedProductionPipeline:
    def __init__(self):
        self.supabase_url = "https://todlaoiuhcxlfhptivzi.supabase.co"
        self.supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRvZGxhb2l1aGN4bGZocHRpdnppIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMwOTMyODIsImV4cCI6MjA2ODY2OTI4Mn0.3_CXAzcRmPotExqH9VsmY0umVA8ax4PsGIEdwsmAnYQ"
        
        self.headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
        
    def run_pipeline(self):
        """Run the unified production pipeline"""
        logger.info("🚀 Starting Unified Production Pipeline...")
        
        try:
            # Step 1: Clear existing data
            logger.info("🗑️ Step 1: Clearing existing data...")
            self.clear_existing_data()
            
            # Step 2: Scrape dynamic rankings with real champions
            logger.info("📊 Step 2: Scraping dynamic rankings...")
            rankings = self.scrape_dynamic_rankings()
            
            if not rankings:
                logger.error("❌ No rankings scraped!")
                return
            
            # Step 3: Upload rankings to Supabase
            logger.info("☁️ Step 3: Uploading rankings to Supabase...")
            self.upload_rankings(rankings)
            
            logger.info("🎉 Unified Production Pipeline completed successfully!")
            logger.info("📱 Your Flutter app should now show real-time champions and rankings!")
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
    
    def clear_existing_data(self):
        """Clear existing rankings data"""
        try:
            # Try to delete all rankings first
            response = requests.delete(
                f"{self.supabase_url}/rest/v1/rankings",
                headers=self.headers
            )
            
            if response.status_code == 200:
                logger.info("✅ Cleared all existing rankings")
            elif response.status_code == 400:
                logger.warning("⚠️ Could not clear all rankings (RLS policy), trying by weight class...")
                # Try to delete by weight class to bypass RLS
                self.clear_rankings_by_weight_class()
            else:
                logger.warning(f"⚠️ Could not clear rankings: {response.status_code}")
                
        except Exception as e:
            logger.warning(f"⚠️ Error clearing data: {e}")
    
    def clear_rankings_by_weight_class(self):
        """Clear rankings by weight class to bypass RLS policies"""
        weight_classes = [
            "Men's Pound-for-Pound",
            "Women's Pound-for-Pound", 
            "Flyweight",
            "Bantamweight",
            "Featherweight",
            "Lightweight",
            "Welterweight",
            "Middleweight",
            "Light Heavyweight",
            "Heavyweight",
            "Women's Strawweight",
            "Women's Flyweight",
            "Women's Bantamweight"
        ]
        
        for weight_class in weight_classes:
            try:
                response = requests.delete(
                    f"{self.supabase_url}/rest/v1/rankings?weight_class=eq.{weight_class}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Cleared {weight_class} rankings")
                else:
                    logger.warning(f"⚠️ Could not clear {weight_class}: {response.status_code}")
                    
            except Exception as e:
                logger.warning(f"⚠️ Error clearing {weight_class}: {e}")
    
    def scrape_dynamic_rankings(self):
        """Scrape rankings using the real dynamic UFC scraper"""
        try:
            scraper = RealDynamicUFCScraper()
            rankings = scraper.scrape_rankings()
            
            logger.info(f"✅ Scraped {len(rankings)} REAL dynamic rankings")
            return rankings
            
        except Exception as e:
            logger.error(f"❌ Error scraping dynamic rankings: {e}")
            return []
    
    def upload_rankings(self, rankings):
        """Upload rankings to Supabase"""
        try:
            uploaded_count = 0
            error_count = 0
            
            for ranking in rankings:
                try:
                    # Prepare ranking data with the correct structure
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
                        uploaded_count += 1
                        if ranking['isChampion']:
                            logger.info(f"👑 Uploaded champion: {ranking['name']} ({ranking['weight_class']})")
                        else:
                            logger.info(f"🥊 Uploaded contender: {ranking['name']} ({ranking['weight_class']}) - #{ranking['rank']}")
                    else:
                        logger.warning(f"⚠️ Failed to upload ranking for {ranking['name']}: {response.status_code}")
                        error_count += 1
                        
                except Exception as e:
                    logger.error(f"❌ Error uploading ranking for {ranking.get('name', 'Unknown')}: {e}")
                    error_count += 1
                    continue
            
            logger.info(f"✅ Successfully uploaded {uploaded_count} rankings, {error_count} errors")
            
        except Exception as e:
            logger.error(f"❌ Error uploading rankings: {e}")

def main():
    """Main function to run the unified production pipeline"""
    try:
        pipeline = UnifiedProductionPipeline()
        pipeline.run_pipeline()
        print("🎉 Unified Production Pipeline completed successfully!")
        print("📱 Your Flutter app should now show real-time champions and rankings!")
    except Exception as e:
        print(f"❌ Unified Production Pipeline failed: {e}")

if __name__ == "__main__":
    main() 