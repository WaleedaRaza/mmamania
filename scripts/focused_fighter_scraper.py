#!/usr/bin/env python3
"""
Focused Fighter Scraper
Scrapes fighter data from a single UFC event with proper table structure parsing
"""

import os
import requests
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import logging

load_dotenv('scripts/.env')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FocusedFighterScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def scrape_event_fighters(self, url, event_name):
        """Scrape fighter data from a UFC event page"""
        try:
            logger.info(f"🔍 Scraping fighters from: {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            logger.info(f"✅ Successfully loaded page: {event_name}")
            
            # Find all tables
            all_tables = soup.find_all('table')
            logger.info(f"📊 Found {len(all_tables)} total tables on page")
            
            fights_data = []
            
            for table_idx, table in enumerate(all_tables):
                logger.info(f"🔍 Analyzing table {table_idx + 1}")
                
                # Look for tables with "def." patterns
                table_text = table.get_text()
                if 'def.' in table_text:
                    logger.info(f"✅ Found table with 'def.' pattern: Table {table_idx + 1}")
                    
                    # Parse this table for fights
                    table_fights = self._parse_fight_table(table)
                    if table_fights:
                        fights_data.extend(table_fights)
                        logger.info(f"📊 Extracted {len(table_fights)} fights from table {table_idx + 1}")
            
            logger.info(f"🎯 Total fights found: {len(fights_data)}")
            return fights_data
            
        except Exception as e:
            logger.error(f"❌ Error scraping {url}: {str(e)}")
            return []
    
    def _parse_fight_table(self, table):
        """Parse a fight table to extract fight data"""
        fights = []
        
        rows = table.find_all('tr')
        logger.info(f"📋 Analyzing {len(rows)} rows in table")
        
        for row_idx, row in enumerate(rows):
            # Skip header rows
            if row.find('th'):
                logger.info(f"📋 Row {row_idx}: Header row")
                continue
            
            cells = row.find_all('td')
            logger.info(f"📋 Row {row_idx}: {len(cells)} cells")
            
            # Need at least 7 cells for a complete fight row
            if len(cells) >= 7:
                try:
                    # Extract data based on the structure we found
                    weight_class = cells[0].get_text(strip=True)
                    winner = cells[1].get_text(strip=True)
                    def_text = cells[2].get_text(strip=True)
                    loser = cells[3].get_text(strip=True)
                    method = cells[4].get_text(strip=True)
                    round_num = cells[5].get_text(strip=True)
                    time = cells[6].get_text(strip=True)
                    
                    # Verify this is a fight row (has "def.")
                    if def_text.strip() == 'def.':
                        fight_data = {
                            'weight_class': weight_class,
                            'winner': winner,
                            'loser': loser,
                            'method': method,
                            'round': round_num,
                            'time': time
                        }
                        
                        fights.append(fight_data)
                        logger.info(f"✅ Fight {len(fights)}: {winner} def. {loser} ({weight_class})")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error parsing row {row_idx}: {str(e)}")
                    continue
        
        return fights
    
    def run_poc(self):
        """Run the proof of concept"""
        logger.info("🚀 Starting Focused Fighter Scraper")
        logger.info("=" * 50)
        
        # Test with the event we know has results
        test_url = "https://en.wikipedia.org/wiki/UFC_on_ESPN:_Taira_vs._Park"
        test_fighters_data = self.scrape_event_fighters(test_url, "UFC on ESPN: Taira vs. Park")
        
        if test_fighters_data:
            logger.info(f"✅ SUCCESS! Found {len(test_fighters_data)} fights")
            logger.info("📊 Sample fights:")
            for i, fight in enumerate(test_fighters_data[:5], 1):
                logger.info(f"Fight {i}: {fight['winner']} def. {fight['loser']} - {fight['method']} (R{fight['round']}, {fight['time']})")
        else:
            logger.error("❌ No fights found")
        
        return test_fighters_data

if __name__ == "__main__":
    scraper = FocusedFighterScraper()
    scraper.run_poc() 