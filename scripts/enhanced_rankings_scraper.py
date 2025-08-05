#!/usr/bin/env python3
"""
Enhanced Rankings Scraper
Blends rankings scraping with fighter profile scraping to get both rankings and fighter records
"""

import os
import sys
import requests
import json
import logging
import time
from datetime import datetime
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Add the scrapers directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv('scripts/.env')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

class EnhancedRankingsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.supabase_headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
        }
        self.base_url = "https://www.ufc.com"
        
    def scrape_rankings_with_profiles(self):
        """Scrape rankings AND fighter profiles together"""
        logger.info("🚀 Starting Enhanced Rankings Scraper")
        logger.info("📊 Scraping rankings + fighter records from UFC.com")
        logger.info("=" * 60)
        
        try:
            # Step 1: Scrape rankings
            rankings = self.scrape_rankings()
            if not rankings:
                logger.error("❌ No rankings scraped")
                return
            
            logger.info(f"📊 Scraped {len(rankings)} rankings")
            
            # Step 2: For each ranked fighter, get their profile/record
            fighters_with_records = []
            for ranking in rankings:
                fighter_name = ranking['name']
                logger.info(f"🔍 Getting profile for: {fighter_name}")
                
                # Get fighter record from UFC.com
                fighter_record = self.get_fighter_record_from_ufc(fighter_name)
                
                fighter_data = {
                    'name': fighter_name,
                    'record': fighter_record,
                    'weight_class': ranking['weight_class']
                }
                fighters_with_records.append(fighter_data)
                
                # Small delay to be respectful
                time.sleep(0.5)
            
            # Step 3: Populate database
            self.populate_rankings_and_fighters(rankings, fighters_with_records)
            
            logger.info("🎉 Enhanced rankings scraping completed!")
            
        except Exception as e:
            logger.error(f"❌ Error in enhanced scraping: {str(e)}")
    
    def scrape_rankings(self):
        """Scrape UFC rankings from UFC.com"""
        try:
            url = f"{self.base_url}/rankings"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            rankings = self.parse_rankings(soup)
            
            return rankings
            
        except Exception as e:
            logger.error(f"❌ Error scraping rankings: {e}")
            return []
    
    def parse_rankings(self, soup):
        """Parse rankings using the actual UFC.com HTML structure"""
        rankings = []
        
        # Find all division groupings
        groupings = soup.select('div.view-grouping')
        
        for grouping in groupings:
            try:
                # Get division name
                header = grouping.select_one('div.view-grouping-header')
                division_name = header.get_text(strip=True) if header else 'Unknown'
                
                # Clean division name
                division_name = self.clean_division_name(division_name)
                
                # Get the champion section
                champion_section = grouping.select_one('div.rankings--athlete--champion')
                
                # Get the contenders table
                content = grouping.select_one('div.view-grouping-content')
                contenders_table = None
                if content:
                    table = content.find('table')
                    if table:
                        tbody = table.find('tbody')
                        if tbody:
                            contenders_table = tbody
                
                # Parse division with proper champion detection
                division_rankings = self.parse_division(champion_section, contenders_table, division_name)
                rankings.extend(division_rankings)
                
            except Exception as e:
                logger.warning(f"⚠️ Error parsing grouping: {e}")
                continue
        
        return rankings
    
    def parse_division(self, champion_section, contenders_table, division_name):
        """Parse division rankings using the actual HTML structure"""
        rankings = []
        
        # First, get the champion from the champion section
        champion_name = None
        if champion_section:
            # Look for the champion name in h5 tag
            champion_h5 = champion_section.select_one('h5 a')
            if champion_h5:
                champion_name = champion_h5.get_text(strip=True)
                logger.info(f"👑 Found champion for {division_name}: {champion_name}")
                
                # Add champion as rank 0
                champion_data = {
                    'rank': 0,
                    'name': champion_name,
                    'weight_class': division_name,
                    'isChampion': True,
                    'rank_position': 0
                }
                rankings.append(champion_data)
        
        # Then get contenders from the table
        if contenders_table:
            rows = contenders_table.find_all('tr')
            for row in rows:
                try:
                    # Get the rank number
                    rank_cell = row.find('td', class_='views-field-weight-class-rank')
                    if not rank_cell:
                        continue
                    
                    rank_text = rank_cell.get_text(strip=True)
                    if not rank_text or not rank_text.isdigit():
                        continue
                    
                    rank = int(rank_text)
                    
                    # Get the fighter name
                    name_cell = row.find('td', class_='views-field-title')
                    if not name_cell:
                        continue
                    
                    name_link = name_cell.find('a')
                    if not name_link:
                        continue
                    
                    fighter_name = name_link.get_text(strip=True)
                    
                    # Create contender data
                    contender_data = {
                        'rank': rank,
                        'name': fighter_name,
                        'weight_class': division_name,
                        'isChampion': False,
                        'rank_position': rank
                    }
                    rankings.append(contender_data)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error parsing contender row: {e}")
                    continue
        
        return rankings
    
    def clean_division_name(self, division_name):
        """Clean and standardize division names"""
        # Remove extra text and standardize
        if 'Top Rank' in division_name:
            division_name = division_name.replace('Top Rank', '').strip()
        
        # Map to standard names
        division_mapping = {
            "Men's Pound-for-Pound": "Men's Pound-for-Pound",
            "Women's Pound-for-Pound": "Women's Pound-for-Pound",
            "Flyweight": "Flyweight",
            "Bantamweight": "Bantamweight", 
            "Featherweight": "Featherweight",
            "Lightweight": "Lightweight",
            "Welterweight": "Welterweight",
            "Middleweight": "Middleweight",
            "Light Heavyweight": "Light Heavyweight",
            "Heavyweight": "Heavyweight",
            "Women's Strawweight": "Women's Strawweight",
            "Women's Flyweight": "Women's Flyweight",
            "Women's Bantamweight": "Women's Bantamweight"
        }
        
        return division_mapping.get(division_name, division_name)
    
    def get_fighter_record_from_ufc(self, fighter_name):
        """Get fighter record from UFC.com fighter profile"""
        try:
            # First try to get from existing fighter profiles data
            record = self.get_record_from_existing_profiles(fighter_name)
            if record:
                return record
            
            # If not found, try to scrape from UFC.com
            record = self.scrape_fighter_record_from_ufc(fighter_name)
            return record
            
        except Exception as e:
            logger.warning(f"⚠️ Error getting record for {fighter_name}: {e}")
            return None
    
    def get_record_from_existing_profiles(self, fighter_name):
        """Get fighter record from existing fighter profiles data"""
        try:
            # Load existing fighter profiles
            profiles_file = 'data/live/live_fighter_profiles.json'
            if os.path.exists(profiles_file):
                with open(profiles_file, 'r') as f:
                    data = json.load(f)
                
                profiles = data.get('profiles', [])
                
                # Find matching fighter
                for profile in profiles:
                    if profile.get('name', '').lower() == fighter_name.lower():
                        return profile.get('record')
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Error reading fighter profiles: {e}")
            return None
    
    def scrape_fighter_record_from_ufc(self, fighter_name):
        """Scrape fighter record directly from UFC.com"""
        try:
            # Convert fighter name to URL slug
            slug = self.name_to_slug(fighter_name)
            url = f"{self.base_url}/athlete/{slug}"
            
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for record in hero section
                record_element = soup.select_one('.hero-athlete__record')
                if record_element:
                    record_text = record_element.get_text(strip=True)
                    # Extract just the record part (e.g., "17-0-0" from "17-0-0 (W-L-D)")
                    import re
                    match = re.search(r'(\d+-\d+-\d+)', record_text)
                    if match:
                        return match.group(1)
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Error scraping record for {fighter_name}: {e}")
            return None
    
    def name_to_slug(self, fighter_name):
        """Convert fighter name to URL slug"""
        # Convert to lowercase and replace spaces with hyphens
        slug = fighter_name.lower().replace(' ', '-')
        # Remove special characters
        import re
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        return slug
    
    def populate_rankings_and_fighters(self, rankings, fighters_with_records):
        """Populate both rankings and fighters tables"""
        logger.info("🗄️ Populating database with rankings and fighter records")
        
        # Step 1: Create fighters first
        fighter_id_map = {}
        for fighter_data in fighters_with_records:
            fighter_id = self.create_fighter(fighter_data)
            if fighter_id:
                fighter_id_map[fighter_data['name']] = fighter_id
                logger.info(f"✅ Created fighter: {fighter_data['name']} ({fighter_data['record']})")
        
        # Step 2: Create rankings
        rankings_created = 0
        for ranking in rankings:
            fighter_name = ranking['name']
            fighter_id = fighter_id_map.get(fighter_name)
            
            if fighter_id:
                ranking_id = self.create_ranking(ranking, fighter_id)
                if ranking_id:
                    rankings_created += 1
                    rank_type = 'champion' if ranking['isChampion'] else 'contender'
                    logger.info(f"✅ Created ranking: {fighter_name} - {ranking['weight_class']} #{ranking['rank']} ({rank_type})")
        
        logger.info(f"🎉 Database population completed!")
        logger.info(f"✅ Created {len(fighter_id_map)} fighters")
        logger.info(f"✅ Created {rankings_created} rankings")
    
    def create_fighter(self, fighter_data):
        """Create a fighter in the database"""
        try:
            fighter_to_create = {
                'name': fighter_data['name'],
                'record': fighter_data['record'],
                'weight_class': fighter_data['weight_class']
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/fighters",
                headers=self.supabase_headers,
                json=fighter_to_create
            )
            
            if response.status_code == 201:
                try:
                    return response.json()['id']
                except (ValueError, KeyError):
                    # If response is empty, try to get the fighter by name
                    fetch_response = requests.get(
                        f"{SUPABASE_URL}/rest/v1/fighters?name=eq.{fighter_data['name']}",
                        headers=self.supabase_headers
                    )
                    if fetch_response.status_code == 200:
                        fighters = fetch_response.json()
                        if fighters:
                            return fighters[0]['id']
                    return None
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ Error creating fighter {fighter_data['name']}: {str(e)}")
            return None
    
    def create_ranking(self, ranking_data, fighter_id):
        """Create a ranking in the database"""
        try:
            ranking_to_create = {
                'fighter_id': fighter_id,
                'weight_class': ranking_data['weight_class'],
                'rank_position': ranking_data['rank'],
                'rank_type': 'champion' if ranking_data['isChampion'] else 'contender'
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/rankings",
                headers=self.supabase_headers,
                json=ranking_to_create
            )
            
            if response.status_code == 201:
                try:
                    return response.json()['id']
                except (ValueError, KeyError):
                    # If response is empty, try to get the ranking by fighter and division
                    fetch_response = requests.get(
                        f"{SUPABASE_URL}/rest/v1/rankings?fighter_id=eq.{fighter_id}&weight_class=eq.{ranking_data['weight_class']}",
                        headers=self.supabase_headers
                    )
                    if fetch_response.status_code == 200:
                        rankings = fetch_response.json()
                        if rankings:
                            return rankings[0]['id']
                    return None
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ Error creating ranking for {ranking_data['name']}: {str(e)}")
            return None

def main():
    scraper = EnhancedRankingsScraper()
    scraper.scrape_rankings_with_profiles()

if __name__ == "__main__":
    main() 