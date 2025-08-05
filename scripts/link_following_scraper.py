#!/usr/bin/env python3
"""
Link Following Fighter Scraper
Follows actual links from the main UFC events Wikipedia page to scrape fighter data
"""

import os
import requests
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import logging
import time

load_dotenv('scripts/.env')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LinkFollowingScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.base_url = "https://en.wikipedia.org"
    
    def get_past_events_links(self):
        """Get all past events links from the main UFC events page"""
        url = "https://en.wikipedia.org/wiki/List_of_UFC_events"
        
        try:
            logger.info(f"🔍 Loading main UFC events page: {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            logger.info("✅ Successfully loaded main UFC events page")
            
            # Find the "Past events" section
            past_events_heading = None
            for heading in soup.find_all(['h2', 'h3']):
                if 'Past events' in heading.get_text():
                    past_events_heading = heading
                    break
            
            if not past_events_heading:
                logger.error("❌ Could not find 'Past events' section")
                return []
            
            logger.info("✅ Found 'Past events' section")
            
            # Try to find the table by looking for tables with many UFC links
            all_tables = soup.find_all('table')
            logger.info(f"📊 Found {len(all_tables)} total tables on page")
            
            best_table = None
            max_ufc_links = 0
            
            for i, table in enumerate(all_tables):
                # Count UFC links in this table
                links = table.find_all('a')
                ufc_links = [link for link in links if 'UFC' in link.get_text()]
                
                logger.info(f"📋 Table {i+1}: {len(links)} total links, {len(ufc_links)} UFC links")
                
                if len(ufc_links) > max_ufc_links:
                    max_ufc_links = len(ufc_links)
                    best_table = table
            
            if not best_table or max_ufc_links == 0:
                logger.error("❌ Could not find table with UFC links")
                return []
            
            logger.info(f"✅ Found best table with {max_ufc_links} UFC links")
            
            # Extract all UFC event links from the table
            event_links = []
            rows = best_table.find_all('tr')
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:  # Need at least Event column
                    # Look for links in the Event column (usually column 1)
                    event_cell = cells[1] if len(cells) > 1 else cells[0]
                    links = event_cell.find_all('a')
                    
                    for link in links:
                        href = link.get('href')
                        if href and 'UFC' in link.get_text():
                            full_url = self.base_url + href
                            event_name = link.get_text().strip()
                            event_links.append({
                                'name': event_name,
                                'url': full_url
                            })
                            logger.info(f"📎 Found event link: {event_name} -> {full_url}")
            
            logger.info(f"📊 Total event links found: {len(event_links)}")
            return event_links
            
        except Exception as e:
            logger.error(f"Error getting past events links: {e}")
            return []
    
    def scrape_event_fighters(self, event_url, event_name):
        """Scrape fighter data from a single event page"""
        try:
            logger.info(f"🔍 Scraping fighters from: {event_name}")
            response = requests.get(event_url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all tables
            all_tables = soup.find_all('table')
            logger.info(f"📊 Found {len(all_tables)} tables on {event_name}")
            
            fighters_data = []
            
            for i, table in enumerate(all_tables):
                # Check if this table contains fight data
                if self._is_fight_table(table):
                    logger.info(f"✅ Found fight table {i+1} on {event_name}")
                    
                    # Extract fighter data from this table
                    table_fighters = self._extract_fighters_from_table(table)
                    fighters_data.extend(table_fighters)
            
            logger.info(f"📊 Extracted {len(fighters_data)} fights from {event_name}")
            return fighters_data
            
        except Exception as e:
            logger.error(f"Error scraping {event_url}: {e}")
            return []
    
    def _is_fight_table(self, table):
        """Check if table contains fight data"""
        # Look for fight indicators in headers or content
        headers = table.find_all('th')
        if headers:
            header_text = ' '.join([h.get_text(strip=True) for h in headers]).lower()
            if any(keyword in header_text for keyword in ['weight', 'method', 'round', 'time']):
                return True
        
        # Also check for "def." pattern in table content
        table_text = table.get_text().lower()
        if 'def.' in table_text:
            return True
        
        # Check for other fight indicators
        fight_indicators = ['submission', 'decision', 'tko', 'ko', 'dqf', 'nc']
        if any(indicator in table_text for indicator in fight_indicators):
            return True
        
        return False
    
    def _extract_fighters_from_table(self, table):
        """Extract fighter data from a fight table"""
        fighters = []
        
        rows = table.find_all('tr')
        logger.info(f"🔍 Analyzing {len(rows)} rows in table")
        
        for row_idx, row in enumerate(rows):
            # Skip header rows
            if row.find('th'):
                logger.info(f"📋 Row {row_idx}: Header row")
                continue
            
            cells = row.find_all('td')
            logger.info(f"📋 Row {row_idx}: {len(cells)} cells")
            
            if len(cells) >= 3:  # Need at least weight class, fighters, method
                try:
                    # Extract weight class
                    weight_class = cells[0].get_text(strip=True)
                    logger.info(f"  Weight Class: {weight_class}")
                    
                    # Extract fighter names and result
                    fighter_cell = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                    logger.info(f"  Fighter Cell: '{fighter_cell}'")
                    
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
                        
                        logger.info(f"  ✅ Extracted: {winner} def. {loser} ({weight_class})")
                    else:
                        logger.info(f"  ❌ Could not parse fighters from: '{fighter_cell}'")
                
                except Exception as e:
                    logger.warning(f"Error parsing row {row_idx}: {e}")
                    continue
            else:
                logger.info(f"  ⚠️ Row {row_idx}: Not enough cells ({len(cells)})")
        
        logger.info(f"📊 Extracted {len(fighters)} fights from this table")
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
    
    def run_poc(self, max_events=3):
        """Run the proof of concept with link following"""
        logger.info("🚀 Starting Link Following Fighter Scraper")
        logger.info("=" * 50)
        
        # Step 1: Get all past events links
        event_links = self.get_past_events_links()
        
        if not event_links:
            logger.error("❌ No event links found")
            return
        
        logger.info(f"📊 Found {len(event_links)} event links")
        
        # Step 2: Test with a known past event that has results
        logger.info("🔍 Testing with a known past event: UFC 1")
        test_url = "https://en.wikipedia.org/wiki/UFC_1"
        test_fighters_data = self.scrape_event_fighters(test_url, "UFC 1")
        
        if test_fighters_data:
            logger.info(f"✅ SUCCESS! Found {len(test_fighters_data)} fights from UFC 1")
            for i, fight in enumerate(test_fighters_data, 1):
                logger.info(f"Fight {i}: {fight['winner']} def. {fight['loser']} ({fight['weight_class']})")
        else:
            logger.warning("⚠️ No fights found for UFC 1, trying another past event...")
            
            # Try another past event
            test_url2 = "https://en.wikipedia.org/wiki/UFC_5"
            test_fighters_data2 = self.scrape_event_fighters(test_url2, "UFC 5")
            
            if test_fighters_data2:
                logger.info(f"✅ SUCCESS! Found {len(test_fighters_data2)} fights from UFC 5")
                for i, fight in enumerate(test_fighters_data2, 1):
                    logger.info(f"Fight {i}: {fight['winner']} def. {fight['loser']} ({fight['weight_class']})")
            else:
                logger.error("❌ Could not find fights in known past events")
        
        # Step 3: Scrape fighters from first few events from our list (POC)
        all_fighters_data = []
        
        for i, event in enumerate(event_links[:max_events]):
            logger.info(f"🔍 Processing event {i+1}/{min(max_events, len(event_links))}: {event['name']}")
            
            # Add delay to be respectful to Wikipedia
            if i > 0:
                time.sleep(2)
            
            fighters_data = self.scrape_event_fighters(event['url'], event['name'])
            
            if fighters_data:
                # Add event info to each fight
                for fight in fighters_data:
                    fight['event_name'] = event['name']
                    fight['event_url'] = event['url']
                
                all_fighters_data.extend(fighters_data)
                logger.info(f"✅ Added {len(fighters_data)} fights from {event['name']}")
            else:
                logger.warning(f"⚠️ No fights found for {event['name']}")
        
        # Step 4: Display results
        logger.info("📊 FINAL RESULTS:")
        logger.info("=" * 50)
        logger.info(f"Events processed: {min(max_events, len(event_links))}")
        logger.info(f"Total fights found: {len(all_fighters_data)}")
        logger.info("")
        
        for i, fight in enumerate(all_fighters_data, 1):
            logger.info(f"Fight {i}:")
            logger.info(f"  Event: {fight['event_name']}")
            logger.info(f"  Weight Class: {fight['weight_class']}")
            logger.info(f"  Winner: {fight['winner']}")
            logger.info(f"  Loser: {fight['loser']}")
            logger.info(f"  Method: {fight['method']}")
            logger.info(f"  Round: {fight['round']}")
            logger.info(f"  Time: {fight['time']}")
            logger.info("")
        
        logger.info("✅ POC Complete!")

if __name__ == "__main__":
    scraper = LinkFollowingScraper()
    scraper.run_poc(max_events=3)  # Start with 3 events for POC 