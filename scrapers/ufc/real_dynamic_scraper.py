#!/usr/bin/env python3
"""
Real Dynamic UFC Scraper
Scrapes actual current UFC rankings from UFC.com with proper champion detection
"""

import requests
from bs4 import BeautifulSoup
import json
import logging
from datetime import datetime
import os
import csv
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealDynamicUFCScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.output_file = "data/real_dynamic_rankings.json"
        
    def scrape_rankings(self):
        """Scrape UFC rankings with proper champion detection from actual HTML structure"""
        logger.info("🔄 Scraping REAL UFC rankings from UFC.com...")
        
        try:
            url = "https://www.ufc.com/rankings"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            rankings = self.parse_rankings_properly(soup)
            
            # Save to file
            self.save_rankings(rankings)
            
            logger.info(f"🎉 Scraped {len(rankings)} REAL rankings!")
            return rankings
            
        except Exception as e:
            logger.error(f"❌ Error scraping rankings: {e}")
            return []
    
    def parse_rankings_properly(self, soup):
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
                division_rankings = self.parse_division_properly(champion_section, contenders_table, division_name)
                rankings.extend(division_rankings)
                
            except Exception as e:
                logger.warning(f"⚠️ Error parsing grouping: {e}")
                continue
        
        return rankings
    
    def parse_division_properly(self, champion_section, contenders_table, division_name):
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
        
        # Add champion as rank 0 if found
        if champion_name:
            champion_data = {
                'rank': 0,  # Champion rank
                'name': champion_name,
                'weight_class': division_name,
                'isChampion': True,
                'rank_position': 0
            }
            rankings.append(champion_data)
        
        # Now parse the contenders from the table
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
    
    def save_rankings(self, rankings):
        """Save rankings to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
            
            data = {
                'timestamp': datetime.now().isoformat(),
                'total_rankings': len(rankings),
                'rankings': rankings
            }
            
            with open(self.output_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"💾 Saved {len(rankings)} rankings to {self.output_file}")
            
        except Exception as e:
            logger.error(f"❌ Error saving rankings: {e}")

def main():
    scraper = RealDynamicUFCScraper()
    rankings = scraper.scrape_rankings()
    
    if rankings:
        print(f"\n🎯 Scraped {len(rankings)} rankings:")
        for ranking in rankings[:10]:  # Show first 10
            champion_status = "👑 CHAMPION" if ranking['isChampion'] else f"#{ranking['rank']}"
            print(f"  {champion_status}: {ranking['name']} ({ranking['weight_class']})")
    else:
        print("❌ No rankings scraped")

if __name__ == "__main__":
    main() 