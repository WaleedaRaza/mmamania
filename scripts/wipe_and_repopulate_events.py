#!/usr/bin/env python3
"""
Wipe and Repopulate Events
Wipe the database and repopulate with events organized by date
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

class WipeAndRepopulateEvents:
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
    
    def wipe_database(self):
        """Wipe all events from the database"""
        logger.info("🗑️ Wiping all events from database...")
        
        try:
            # Delete all events
            response = requests.delete(f"{self.supabase_url}/rest/v1/events", headers=self.headers)
            if response.status_code == 200:
                logger.info("✅ Successfully wiped all events")
            else:
                logger.warning(f"⚠️ Warning: Could not wipe events: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Error wiping database: {e}")
    
    def get_all_past_events_with_dates(self) -> List[Dict]:
        """Get ALL past UFC events from Wikipedia with proper date parsing"""
        logger.info("Getting ALL past UFC events from Wikipedia with dates...")
        
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
                
                # Extract all UFC event links with dates
                links = best_table.find_all('a', href=True)
                
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
                            
                            # Based on the table structure: #, Event, Date, Venue, Location, Attendance, Ref.
                            for i, cell in enumerate(cells):
                                cell_text = cell.get_text(strip=True)
                                # Column 3 is the Date column
                                if i == 2:  # Date column
                                    date_text = cell_text
                                # Column 5 is the Location column
                                elif i == 4:  # Location column
                                    location_text = cell_text
                                # Column 4 is the Venue column
                                elif i == 3:  # Venue column
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
    
    def parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string into ISO format"""
        if not date_str:
            return None
        
        # Try different date formats
        date_formats = [
            '%Y-%m-%d',
            '%B %d, %Y',
            '%B %d %Y',
            '%b %d, %Y',  # Aug 2, 2025
            '%b %d %Y',
            '%m/%d/%Y',
            '%m-%d-%Y'
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.isoformat()
            except ValueError:
                continue
        
        return None
    
    def sort_events_by_date(self, events: List[Dict]) -> List[Dict]:
        """Sort events by date, putting most recent first"""
        logger.info("📅 Sorting events by date...")
        
        # Parse dates and filter out events without valid dates
        events_with_dates = []
        events_without_dates = []
        
        for event in events:
            parsed_date = self.parse_date(event.get('date', ''))
            if parsed_date:
                event['parsed_date'] = parsed_date
                events_with_dates.append(event)
            else:
                events_without_dates.append(event)
        
        # Sort by date (most recent first)
        events_with_dates.sort(key=lambda x: x['parsed_date'], reverse=True)
        
        logger.info(f"✅ Sorted {len(events_with_dates)} events with dates")
        logger.info(f"⚠️ {len(events_without_dates)} events without dates")
        
        return events_with_dates
    
    def create_event(self, event_data: Dict) -> Optional[str]:
        """Create an event in Supabase"""
        try:
            event_to_create = {
                'name': event_data['name'],
                'date': event_data.get('parsed_date'),
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
                logger.info(f"✅ Created event: {event_data['name']} ({event_data.get('parsed_date', 'No date')})")
                return "created"
            else:
                logger.warning(f"⚠️ Failed to create event {event_data['name']}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error creating event {event_data['name']}: {e}")
            return None
    
    def repopulate_events_by_date(self):
        """Wipe database and repopulate with events organized by date"""
        logger.info("🔄 Starting wipe and repopulate process...")
        
        # Step 1: Wipe database
        self.wipe_database()
        
        # Step 2: Get all events
        events = self.get_all_past_events_with_dates()
        
        if not events:
            logger.error("No events found!")
            return
        
        logger.info(f"Found {len(events)} events to process")
        
        # Step 3: Sort events by date
        sorted_events = self.sort_events_by_date(events)
        
        # Step 4: Create events in date order
        created_count = 0
        failed_count = 0
        
        for i, event in enumerate(sorted_events):
            logger.info(f"Processing event {i+1}/{len(sorted_events)}: {event['name']}")
            
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
        filename = f"data/exports/sorted_ufc_events_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(sorted_events, f, indent=2)
        
        logger.info(f"📁 Saved sorted events to: {filename}")

def main():
    scraper = WipeAndRepopulateEvents()
    scraper.repopulate_events_by_date()

if __name__ == "__main__":
    main() 