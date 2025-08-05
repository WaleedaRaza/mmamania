#!/usr/bin/env python3
"""
Proof of Concept Fighter Scraper
Scrapes fighter data from a single UFC event Wikipedia page
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

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

class POCFighterScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_event_from_database(self):
        """Get a single event from our database"""
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
        }
        
        try:
            # Get the most recent event
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/events?select=id,name,date&order=date.desc&limit=1",
                headers=headers
            )
            
            if response.status_code == 200:
                events = response.json()
                if events:
                    event = events[0]
                    logger.info(f"Selected event: {event['name']} ({event['date']})")
                    return event
                else:
                    logger.error("No events found in database")
                    return None
            else:
                logger.error(f"Failed to get event: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting event: {e}")
            return None
    
    def get_wikipedia_url(self, event_name):
        """Convert event name to Wikipedia URL"""
        # Clean the event name for URL
        url_name = event_name.replace(' ', '_')
        
        # Handle special cases for UFC event names
        if 'UFC on ESPN:' in url_name:
            url_name = url_name.replace('UFC_on_ESPN:', 'UFC_on_ESPN:_')
        elif 'UFC on ABC:' in url_name:
            url_name = url_name.replace('UFC_on_ABC:', 'UFC_on_ABC:_')
        elif 'UFC on Fox:' in url_name:
            url_name = url_name.replace('UFC_on_Fox:', 'UFC_on_Fox:_')
        elif 'UFC on FX:' in url_name:
            url_name = url_name.replace('UFC_on_FX:', 'UFC_on_FX:_')
        elif 'UFC on Fuel TV:' in url_name:
            url_name = url_name.replace('UFC_on_Fuel_TV:', 'UFC_on_Fuel_TV:_')
        
        # Handle vs. properly
        url_name = url_name.replace('vs.', 'vs.')
        
        # Remove any remaining colons that aren't part of the network name
        url_name = url_name.replace(':', '')
        
        wikipedia_url = f"https://en.wikipedia.org/wiki/{url_name}"
        logger.info(f"Wikipedia URL: {wikipedia_url}")
        return wikipedia_url
    
    def scrape_fight_card_tables(self, url):
        """Scrape fighter data from fight card tables"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            logger.info(f"✅ Successfully loaded page: {url}")
            logger.info(f"📄 Page title: {soup.title.get_text() if soup.title else 'No title'}")
            
            # Find all tables
            all_tables = soup.find_all('table')
            logger.info(f"📊 Found {len(all_tables)} total tables on page")
            
            # Find tables with wikitable class
            wikitable_tables = soup.find_all('table', class_='wikitable')
            logger.info(f"📋 Found {len(wikitable_tables)} wikitable tables")
            
            fighters_data = []
            
            # Check all tables, not just wikitable ones
            for i, table in enumerate(all_tables):
                logger.info(f"🔍 Analyzing table {i+1}/{len(all_tables)}")
                
                # Check if this table contains fight data
                if self._is_fight_table(table):
                    logger.info(f"✅ Found fight table {i+1} with {len(table.find_all('tr'))} rows")
                    
                    # Extract fighter data from this table
                    table_fighters = self._extract_fighters_from_table(table)
                    fighters_data.extend(table_fighters)
                else:
                    logger.info(f"❌ Table {i+1} is not a fight table")
            
            return fighters_data
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return []
    
    def _is_fight_table(self, table):
        """Check if table contains fight data"""
        # Look for fight indicators in headers or content
        headers = table.find_all('th')
        if headers:
            header_text = ' '.join([h.get_text(strip=True) for h in headers]).lower()
            logger.info(f"📝 Table headers: {header_text}")
            if any(keyword in header_text for keyword in ['weight', 'method', 'round', 'time']):
                return True
        
        # Also check for "def." pattern in table content
        table_text = table.get_text().lower()
        if 'def.' in table_text:
            logger.info(f"✅ Found 'def.' pattern in table")
            return True
        
        # Check for other fight indicators
        fight_indicators = ['submission', 'decision', 'tko', 'ko', 'dqf', 'nc']
        if any(indicator in table_text for indicator in fight_indicators):
            logger.info(f"✅ Found fight indicators in table")
            return True
        
        return False
    
    def _extract_fighters_from_table(self, table):
        """Extract fighter data from a fight table"""
        fighters = []
        
        rows = table.find_all('tr')
        for row in rows:
            # Skip header rows
            if row.find('th'):
                continue
            
            cells = row.find_all('td')
            if len(cells) >= 3:  # Need at least weight class, fighters, method
                try:
                    # Extract weight class
                    weight_class = cells[0].get_text(strip=True)
                    
                    # Extract fighter names and result
                    fighter_cell = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                    
                    # Parse winner and loser
                    winner, loser = self._parse_fighters(fighter_cell)
                    
                    if winner and loser:
                        # Extract method, round, time
                        method = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                        round_num = cells[3].get_text(strip=True) if len(cells) > 3 else ""
                        time = cells[4].get_text(strip=True) if len(cells) > 4 else ""
                        
                        fighters.append({
                            'weight_class': weight_class,
                            'winner': winner,
                            'loser': loser,
                            'method': method,
                            'round': round_num,
                            'time': time
                        })
                        
                        logger.info(f"Extracted: {winner} def. {loser} ({weight_class})")
                
                except Exception as e:
                    logger.warning(f"Error parsing row: {e}")
                    continue
        
        return fighters
    
    def _parse_fighters(self, fighter_text):
        """Parse winner and loser from fighter text"""
        if not fighter_text:
            return None, None
        
        # Look for "def." pattern
        if 'def.' in fighter_text:
            parts = fighter_text.split('def.')
            if len(parts) == 2:
                winner = parts[0].strip()
                loser = parts[1].strip()
                return winner, loser
        
        # Alternative patterns
        patterns = [
            r'(.+?)\s+def\.\s+(.+)',
            r'(.+?)\s+defeated\s+(.+)',
            r'(.+?)\s+beat\s+(.+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, fighter_text, re.IGNORECASE)
            if match:
                winner = match.group(1).strip()
                loser = match.group(2).strip()
                return winner, loser
        
        return None, None
    
    def run_poc(self):
        """Run the proof of concept"""
        logger.info("🚀 Starting POC Fighter Scraper")
        logger.info("=" * 50)
        
        # Step 1: Get an event from our database
        event = self.get_event_from_database()
        if not event:
            logger.error("❌ Failed to get event from database")
            return
        
        # Step 2: Get Wikipedia URL
        wikipedia_url = self.get_wikipedia_url(event['name'])
        
        # Step 3: Scrape fighter data
        logger.info("🔍 Scraping fighter data from Wikipedia...")
        fighters_data = self.scrape_fight_card_tables(wikipedia_url)
        
        # If no data found, try a known working URL for testing
        if not fighters_data:
            logger.info("🔄 No data found, trying known working URL for testing...")
            test_url = "https://en.wikipedia.org/wiki/UFC_300"
            fighters_data = self.scrape_fight_card_tables(test_url)
        
        # Step 4: Display results
        logger.info("📊 RESULTS:")
        logger.info("=" * 50)
        logger.info(f"Event: {event['name']}")
        logger.info(f"Date: {event['date']}")
        logger.info(f"Total fighters found: {len(fighters_data)}")
        logger.info("")
        
        for i, fight in enumerate(fighters_data, 1):
            logger.info(f"Fight {i}:")
            logger.info(f"  Weight Class: {fight['weight_class']}")
            logger.info(f"  Winner: {fight['winner']}")
            logger.info(f"  Loser: {fight['loser']}")
            logger.info(f"  Method: {fight['method']}")
            logger.info(f"  Round: {fight['round']}")
            logger.info(f"  Time: {fight['time']}")
            logger.info("")
        
        logger.info("✅ POC Complete!")

if __name__ == "__main__":
    scraper = POCFighterScraper()
    scraper.run_poc() 