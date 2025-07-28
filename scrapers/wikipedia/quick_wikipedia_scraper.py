#!/usr/bin/env python3
"""
Quick Wikipedia UFC Scraper
Pulls live UFC events and results immediately
"""

import requests
from bs4 import BeautifulSoup
import json
import logging
from datetime import datetime
import os
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QuickWikipediaScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.output_file = "data/live_wikipedia_data.json"
        
    def scrape_recent_events(self):
        """Scrape recent UFC events from Wikipedia"""
        logger.info("🔄 Scraping live Wikipedia UFC events...")
        
        try:
            # Wikipedia UFC Events URL
            url = "https://en.wikipedia.org/wiki/List_of_UFC_events"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            events = []
            
            # Find the main events table
            tables = soup.find_all('table', class_='wikitable')
            
            for table in tables:
                # Look for UFC event tables
                if 'UFC' in str(table):
                    event_data = self.extract_events_from_table(table)
                    events.extend(event_data)
            
            # Save to file
            self.save_data(events, 'events')
            
            logger.info(f"🎉 Scraped {len(events)} live events!")
            return events
            
        except Exception as e:
            logger.error(f"❌ Error scraping Wikipedia data: {e}")
            return []
    
    def extract_events_from_table(self, table):
        """Extract events from a table"""
        events = []
        
        try:
            rows = table.find_all('tr')
            
            for row in rows[1:]:  # Skip header
                cells = row.find_all(['td', 'th'])
                
                if len(cells) >= 3:
                    event_data = self.extract_event_from_row(cells)
                    if event_data:
                        events.append(event_data)
                        logger.info(f"✅ Event: {event_data.get('name', 'Unknown')}")
        
        except Exception as e:
            logger.warning(f"Could not extract events from table: {e}")
        
        return events
    
    def extract_event_from_row(self, cells):
        """Extract event data from table row"""
        try:
            # Extract event name
            name_cell = cells[0] if cells else None
            name = name_cell.get_text(strip=True) if name_cell else "Unknown"
            
            # Extract date
            date_cell = cells[1] if len(cells) > 1 else None
            date = date_cell.get_text(strip=True) if date_cell else ""
            
            # Extract venue
            venue_cell = cells[2] if len(cells) > 2 else None
            venue = venue_cell.get_text(strip=True) if venue_cell else ""
            
            # Extract location
            location_cell = cells[3] if len(cells) > 3 else None
            location = location_cell.get_text(strip=True) if location_cell else ""
            
            # Check if this is a recent event (2024-2025)
            if self.is_recent_event(date):
                return {
                    'name': name,
                    'date': date,
                    'venue': venue,
                    'location': location,
                    'scraped_at': datetime.now().isoformat()
                }
            
            return None
            
        except Exception as e:
            logger.warning(f"Could not extract event from row: {e}")
            return None
    
    def is_recent_event(self, date_str):
        """Check if event is recent (2024-2025)"""
        try:
            # Look for year patterns
            year_match = re.search(r'202[45]', date_str)
            return bool(year_match)
        except:
            return False
    
    def save_data(self, data, data_type):
        """Save data to JSON file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
            
            output_data = {
                data_type: data,
                'total_items': len(data),
                'scraped_at': datetime.now().isoformat(),
                'source': 'Wikipedia'
            }
            
            with open(self.output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            logger.info(f"💾 {data_type.capitalize()} saved to: {self.output_file}")
            
        except Exception as e:
            logger.error(f"❌ Error saving data: {e}")

def main():
    """Main function"""
    scraper = QuickWikipediaScraper()
    events = scraper.scrape_recent_events()
    
    print(f"\n📊 Results:")
    print(f"   Total events: {len(events)}")
    print(f"   Output file: {scraper.output_file}")
    print(f"   Check the file for live data!")

if __name__ == "__main__":
    main() 