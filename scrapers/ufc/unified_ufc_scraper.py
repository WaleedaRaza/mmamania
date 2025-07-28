#!/usr/bin/env python3
"""
Unified UFC Scraper
One dynamic scraper that reads real current champions and rankings from UFC.com
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

class UnifiedUFCScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.output_file = "data/unified_ufc_rankings.json"
        
    def scrape_rankings(self):
        """Scrape UFC rankings with dynamic champion detection"""
        logger.info("🔄 Scraping UFC rankings with dynamic champion detection...")
        
        try:
            url = "https://www.ufc.com/rankings"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            rankings = self.parse_rankings_dynamically(soup)
            
            # Save to file
            self.save_rankings(rankings)
            
            logger.info(f"🎉 Scraped {len(rankings)} dynamic rankings!")
            return rankings
            
        except Exception as e:
            logger.error(f"❌ Error scraping rankings: {e}")
            return []
    
    def parse_rankings_dynamically(self, soup):
        """Parse rankings by dynamically detecting champions from the HTML"""
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
                
                # Get rankings table
                content = grouping.select_one('div.view-grouping-content')
                if not content:
                    continue
                    
                table = content.find('table')
                if not table:
                    continue
                    
                tbody = table.find('tbody')
                if not tbody:
                    continue
                
                # Parse division with dynamic champion detection
                division_rankings = self.parse_division_dynamically(tbody, division_name, grouping)
                rankings.extend(division_rankings)
                
            except Exception as e:
                logger.warning(f"⚠️ Error parsing grouping: {e}")
                continue
        
        return rankings
    
    def parse_division_dynamically(self, tbody, division_name, grouping):
        """Parse division rankings with dynamic champion detection"""
        rankings = []
        
        # First, try to find the champion dynamically
        champion_name = self.find_champion_dynamically(grouping, division_name)
        
        # Add champion as rank 0 if found
        if champion_name:
            champion_data = {
                'rank': 0,  # Champion rank
                'name': champion_name,
                'division': division_name,
                'url': f"https://www.ufc.com/athlete/{champion_name.lower().replace(' ', '-')}",
                'scraped_at': datetime.now().isoformat(),
                'is_champion': True
            }
            rankings.append(champion_data)
            logger.info(f"👑 {champion_name} ({division_name}) - CHAMPION (dynamically detected)")
        
        # Parse the numbered list (these are contenders, starting from #1)
        contender_rank = 1
        
        rows = tbody.find_all('tr')
        for row in rows:
            try:
                tds = row.find_all('td')
                if len(tds) < 2:
                    continue
                
                # Get fighter name from the list
                name_link = tds[1].find('a', href=True)
                if not name_link:
                    continue
                
                fighter_name = name_link.get_text(strip=True)
                fighter_url = f"https://www.ufc.com{name_link['href']}"
                
                # Skip if this is the champion (they're already added)
                if champion_name and fighter_name == champion_name:
                    continue
                
                # Check if this is actually a valid ranking row
                if not fighter_name or fighter_name.strip() == '':
                    continue
                
                # This is a contender, rank them accordingly
                contender_data = {
                    'rank': contender_rank,  # #1 contender, #2 contender, etc.
                    'name': fighter_name,
                    'division': division_name,
                    'url': fighter_url,
                    'scraped_at': datetime.now().isoformat(),
                    'is_champion': False
                }
                rankings.append(contender_data)
                
                logger.info(f"🥊 {fighter_name} ({division_name}) - #{contender_rank} Contender")
                contender_rank += 1
                    
            except Exception as e:
                logger.warning(f"⚠️ Error parsing row: {e}")
                continue
        
        return rankings
    
    def find_champion_dynamically(self, grouping, division_name):
        """Find champion by analyzing the actual HTML structure dynamically"""
        try:
            # Method 1: Look for "Champion" text and extract the name near it
            division_text = grouping.get_text()
            champion_match = re.search(r'Champion[:\s]*([A-Za-z\s]+)', division_text, re.IGNORECASE)
            if champion_match:
                champion_name = champion_match.group(1).strip()
                if len(champion_name.split()) <= 3:  # Reasonable name length
                    return champion_name
            
            # Method 2: Look for special champion styling or classes
            champion_elements = grouping.select('.champion, [class*="champion"], [class*="title"], .title-holder, [class*="title-holder"]')
            for element in champion_elements:
                # Look for fighter names in champion elements
                links = element.find_all('a')
                for link in links:
                    name = link.get_text(strip=True)
                    if name and len(name.split()) <= 3:
                        return name
                
                # Look for text that might be a champion name
                text = element.get_text(strip=True)
                if text and len(text.split()) <= 3 and not text.isdigit():
                    return text
            
            # Method 3: Look for prominent athlete images and extract names
            athlete_images = grouping.select('img[src*="athlete"], .athlete-image, .fighter-image')
            for img in athlete_images:
                # Look for the name associated with this image
                parent = img.parent
                if parent:
                    links = parent.find_all('a')
                    for link in links:
                        name = link.get_text(strip=True)
                        if name and len(name.split()) <= 3:
                            return name
            
            # Method 4: Look for the first prominent fighter mentioned before the numbered list
            # Champions are often displayed prominently before the numbered contenders
            division_content = grouping.get_text()
            lines = division_content.split('\n')
            
            for line in lines:
                line = line.strip()
                if line and not line.isdigit() and not line.startswith('#') and not line.startswith('Rank'):
                    # This might be a champion name
                    if len(line.split()) <= 3 and not any(word in line.lower() for word in ['division', 'weight', 'rank']):
                        return line
            
            # Method 5: Look for special formatting that indicates champion status
            # Champions often have different styling or appear in special sections
            special_sections = grouping.select('.champion-section, .title-holder, [class*="champion"], [class*="title"]')
            for section in special_sections:
                links = section.find_all('a')
                for link in links:
                    name = link.get_text(strip=True)
                    if name and len(name.split()) <= 3:
                        return name
            
            # Method 6: Look for the first fighter in the division (before any numbered list)
            # This is a fallback method - sometimes the first fighter mentioned is the champion
            all_links = grouping.find_all('a')
            fighter_names = []
            for link in all_links:
                name = link.get_text(strip=True)
                if name and len(name.split()) <= 3 and not name.isdigit():
                    fighter_names.append(name)
            
            if fighter_names:
                # Return the first fighter name found (potential champion)
                return fighter_names[0]
            
            logger.warning(f"⚠️ Could not find champion for {division_name}")
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Error finding champion dynamically: {e}")
            return None
    
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
        
        for key, value in division_mapping.items():
            if key in division_name:
                return value
        
        return division_name
    
    def save_rankings(self, rankings):
        """Save rankings to JSON and CSV files"""
        try:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
            
            # Save as JSON
            with open(self.output_file, 'w') as f:
                json.dump(rankings, f, indent=2)
            logger.info(f"💾 Rankings saved to: {self.output_file}")
            
            # Save as CSV
            csv_file = self.output_file.replace('.json', '.csv')
            with open(csv_file, 'w', newline='') as f:
                if rankings:
                    writer = csv.DictWriter(f, fieldnames=rankings[0].keys())
                    writer.writeheader()
                    writer.writerows(rankings)
            logger.info(f"💾 Rankings also saved to: {csv_file}")
            
        except Exception as e:
            logger.error(f"❌ Error saving rankings: {e}")

def main():
    """Main function to test the unified UFC scraper"""
    scraper = UnifiedUFCScraper()
    rankings = scraper.scrape_rankings()
    
    # Print some examples to verify
    print(f"\n🎉 Scraped {len(rankings)} dynamic rankings!")
    print("\n📊 Sample rankings:")
    
    # Group by division and show top 5
    divisions = {}
    for ranking in rankings:
        div = ranking['division']
        if div not in divisions:
            divisions[div] = []
        divisions[div].append(ranking)
    
    for division, div_rankings in divisions.items():
        print(f"\n{division}:")
        for ranking in div_rankings[:5]:  # Show top 5
            if ranking.get('is_champion', False):
                print(f"  👑 {ranking['name']} (Champion)")
            else:
                print(f"  #{ranking['rank']} {ranking['name']}")

if __name__ == "__main__":
    main() 