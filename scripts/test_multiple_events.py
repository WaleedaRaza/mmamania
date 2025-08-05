#!/usr/bin/env python3
"""
Test Multiple Events
Test the focused fighter scraper with multiple UFC events to ensure consistency
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

class MultiEventTester:
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
        
        for row_idx, row in enumerate(rows):
            # Skip header rows
            if row.find('th'):
                continue
            
            cells = row.find_all('td')
            
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
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error parsing row {row_idx}: {str(e)}")
                    continue
        
        return fights
    
    def test_multiple_events(self):
        """Test with multiple UFC events"""
        logger.info("🚀 Testing Multiple UFC Events")
        logger.info("=" * 50)
        
        # Test events with different characteristics
        test_events = [
            {
                'name': 'UFC on ESPN: Taira vs. Park',
                'url': 'https://en.wikipedia.org/wiki/UFC_on_ESPN:_Taira_vs._Park',
                'expected_fights': 12
            },
            {
                'name': 'UFC on ABC: Whittaker vs. de Ridder',
                'url': 'https://en.wikipedia.org/wiki/UFC_on_ABC:_Whittaker_vs._de_Ridder',
                'expected_fights': 12
            },
            {
                'name': 'UFC 318: Holloway vs. Poirier 3',
                'url': 'https://en.wikipedia.org/wiki/UFC_318',
                'expected_fights': 14
            },
            {
                'name': 'UFC 300: Pereira vs. Hill',
                'url': 'https://en.wikipedia.org/wiki/UFC_300',
                'expected_fights': 13
            },
            {
                'name': 'UFC 100: Lesnar vs. Mir 2',
                'url': 'https://en.wikipedia.org/wiki/UFC_100',
                'expected_fights': 11
            }
        ]
        
        results = []
        
        for event in test_events:
            logger.info(f"\n🔍 Testing: {event['name']}")
            logger.info("-" * 30)
            
            fights_data = self.scrape_event_fighters(event['url'], event['name'])
            
            result = {
                'event_name': event['name'],
                'expected_fights': event['expected_fights'],
                'actual_fights': len(fights_data),
                'success': len(fights_data) > 0,
                'fights': fights_data
            }
            
            results.append(result)
            
            if fights_data:
                logger.info(f"✅ SUCCESS: Found {len(fights_data)} fights")
                logger.info("📊 Sample fights:")
                for i, fight in enumerate(fights_data[:3], 1):
                    logger.info(f"  Fight {i}: {fight['winner']} def. {fight['loser']} - {fight['method']} (R{fight['round']}, {fight['time']})")
            else:
                logger.error(f"❌ FAILED: No fights found")
        
        # Summary
        logger.info(f"\n📊 TESTING SUMMARY")
        logger.info("=" * 50)
        
        successful_events = [r for r in results if r['success']]
        failed_events = [r for r in results if not r['success']]
        
        logger.info(f"✅ Successful events: {len(successful_events)}/{len(results)}")
        logger.info(f"❌ Failed events: {len(failed_events)}/{len(results)}")
        
        if successful_events:
            total_fights = sum(r['actual_fights'] for r in successful_events)
            logger.info(f"🎯 Total fights scraped: {total_fights}")
            
            for result in successful_events:
                logger.info(f"  {result['event_name']}: {result['actual_fights']} fights")
        
        if failed_events:
            logger.info(f"\n❌ Failed events:")
            for result in failed_events:
                logger.info(f"  {result['event_name']}")
        
        return results

if __name__ == "__main__":
    tester = MultiEventTester()
    tester.test_multiple_events() 