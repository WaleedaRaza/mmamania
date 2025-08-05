#!/usr/bin/env python3
"""
Populate Events Only
Focus on getting ALL past UFC events from Wikipedia into the events table
"""

import os
import re
import json
import time
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv('scripts/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EventsOnlyScraper:
    def __init__(self):
        self.base_url = "https://en.wikipedia.org"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.supabase_url = SUPABASE_URL
        self.headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
        }
    
    def get_all_past_events(self) -> List[Dict]:
        """Get ALL past UFC events from Wikipedia"""
        logger.info("Getting ALL past UFC events from Wikipedia...")
        
        list_url = f"{self.base_url}/wiki/List_of_UFC_events"
        
        try:
            response = self.session.get(list_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            events = []
            
            # Find all tables and look for the one with the most UFC links
            tables = soup.find_all('table')
            logger.info(f"Found {len(tables)} tables")
            
            # Find the table with the most UFC event links
            best_table = None
            max_ufc_links = 0
            
            for table in tables:
                links = table.find_all('a', href=True)
                ufc_links = [link for link in links if 'UFC' in link.get_text()]
                if len(ufc_links) > max_ufc_links:
                    max_ufc_links = len(ufc_links)
                    best_table = table
            
            if best_table:
                logger.info(f"Found table with {max_ufc_links} UFC event links")
                
                # Extract all UFC event links
                links = best_table.find_all('a', href=True)
                ufc_links = []
                
                for link in links:
                    text = link.get_text(strip=True)
                    href = link.get('href', '')
                    
                    # Check if this is a UFC event link
                    if 'UFC' in text and href.startswith('/wiki/'):
                        event_name = text
                        event_url = f"{self.base_url}{href}"
                        
                        # Try to extract date from the same row
                        row = link.find_parent('tr')
                        if row:
                            cells = row.find_all(['td', 'th'])
                            date_text = ""
                            location_text = ""
                            venue_text = ""
                            
                            for cell in cells:
                                cell_text = cell.get_text(strip=True)
                                # Look for date patterns
                                if re.match(r'\d{4}-\d{2}-\d{2}', cell_text) or re.match(r'\w+ \d{1,2}, \d{4}', cell_text):
                                    date_text = cell_text
                                # Look for location patterns
                                elif ',' in cell_text and len(cell_text) > 10:
                                    location_text = cell_text
                                # Look for venue patterns
                                elif any(word in cell_text.lower() for word in ['arena', 'center', 'stadium', 'garden', 'theatre']):
                                    venue_text = cell_text
                            
                            events.append({
                                'name': event_name,
                                'url': event_url,
                                'date': date_text,
                                'location': location_text,
                                'venue': venue_text
                            })
                
                logger.info(f"Extracted {len(events)} UFC events")
                return events
            else:
                logger.error("Could not find table with UFC events")
                return []
                
        except Exception as e:
            logger.error(f"Error getting past events: {e}")
            return []
    
    def create_event(self, event_data: Dict) -> Optional[str]:
        """Create an event in Supabase"""
        try:
            # Parse date if available
            date_str = event_data.get('date', '')
            parsed_date = None
            
            if date_str:
                # Try different date formats
                date_formats = ['%Y-%m-%d', '%B %d, %Y', '%B %d %Y']
                for fmt in date_formats:
                    try:
                        parsed_date = datetime.strptime(date_str, fmt).isoformat()
                        break
                    except ValueError:
                        continue
            
            event_to_create = {
                'name': event_data['name'],
                'date': parsed_date,
                'location': event_data.get('location'),
                'venue': event_data.get('venue'),
                'status': 'completed'
            }
            
            response = requests.post(
                f"{self.supabase_url}/rest/v1/events",
                headers=self.headers,
                json=event_to_create
            )
            
            if response.status_code == 201:
                # Supabase returns empty response body on successful creation
                # We can't get the ID from response, but the event was created
                logger.info(f"✅ Created event: {event_data['name']}")
                return "created"  # Return a placeholder since we can't get the ID
            else:
                logger.warning(f"⚠️ Failed to create event {event_data['name']}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error creating event {event_data['name']}: {e}")
            return None
    
    def populate_all_events(self):
        """Populate ALL past UFC events"""
        logger.info("Starting to populate ALL past UFC events...")
        
        # Get all past events
        events = self.get_all_past_events()
        
        if not events:
            logger.error("No events found!")
            return
        
        logger.info(f"Found {len(events)} events to populate")
        
        # Create events in batches
        created_count = 0
        failed_count = 0
        
        for i, event in enumerate(events):
            logger.info(f"Processing event {i+1}/{len(events)}: {event['name']}")
            
            event_id = self.create_event(event)
            if event_id:
                created_count += 1
            else:
                failed_count += 1
            
            # Small delay to avoid overwhelming the API
            time.sleep(0.1)
        
        logger.info(f"✅ COMPLETED: Created {created_count} events, Failed {failed_count} events")
        
        # Save events to JSON for reference
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/exports/all_ufc_events_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(events, f, indent=2)
        
        logger.info(f"📁 Saved events to: {filename}")

def main():
    scraper = EventsOnlyScraper()
    scraper.populate_all_events()

if __name__ == "__main__":
    main() 