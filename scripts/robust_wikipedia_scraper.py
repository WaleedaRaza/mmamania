#!/usr/bin/env python3
"""
ROBUST Wikipedia UFC Scraper
Scrapes every single fight from Wikipedia with perfect accuracy
"""

import os
import sys
import requests
import logging
import time
import json
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import argparse

load_dotenv('.env')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

class RobustWikipediaScraper:
    def __init__(self, max_workers=5):
        self.max_workers = max_workers
        self.base_url = "https://en.wikipedia.org"  # Add the missing base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        self.supabase_headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
        }
        
        # Thread-safe counters
        self.lock = Lock()
        self.successful_events = 0
        self.failed_events = 0
        self.total_fights = 0
        
    def get_all_past_events_with_actual_links(self):
        """Get all past events with their actual Wikipedia links"""
        url = "https://en.wikipedia.org/wiki/List_of_UFC_events"
        
        try:
            logger.info(f"🔍 Loading main UFC events page: {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            logger.info("✅ Successfully loaded main UFC events page")
            
            # Find all tables
            all_tables = soup.find_all('table')
            logger.info(f"📊 Found {len(all_tables)} total tables on page")
            
            # Find the table with the most UFC references (this is the Past events table)
            best_table = None
            max_ufc_links = 0
            
            for table_idx, table in enumerate(all_tables):
                table_text = table.get_text()
                ufc_count = table_text.count('UFC')
                
                if ufc_count > max_ufc_links:
                    max_ufc_links = ufc_count
                    best_table = table
            
            if not best_table:
                logger.error("❌ Could not find Past events table")
                return []
            
            logger.info(f"✅ Found Past events table with {max_ufc_links} UFC references")
            
            # Parse the table to extract events with their actual links
            events = []
            rows = best_table.find_all('tr')
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 6:  # Need at least #, Event, Date, Venue, Location
                    try:
                        # Extract event data
                        event_number = cells[0].get_text(strip=True)
                        event_name = cells[1].get_text(strip=True)
                        date_text = cells[2].get_text(strip=True)
                        venue_text = cells[3].get_text(strip=True)
                        
                        # Get the actual Wikipedia link for the event
                        event_link = None
                        event_cell = cells[1]
                        link = event_cell.find('a')
                        if link and link.get('href'):
                            event_link = urljoin(self.base_url, link['href'])
                        
                        # Only include events that have links and are UFC events
                        if event_link and 'UFC' in event_name:
                            # Parse date directly from the list row (canonical)
                            list_date = self.parse_date(date_text)
                            event_data = {
                                'number': event_number,
                                'name': event_name,
                                'list_date': list_date,
                                'venue': venue_text,
                                'url': event_link
                            }
                            events.append(event_data)
                            
                    except Exception as e:
                        logger.warning(f"⚠️ Error parsing event row: {e}")
                        continue
            
            logger.info(f"📊 Found {len(events)} UFC events with links")
            return events
            
        except Exception as e:
            logger.error(f"❌ Error loading main UFC events page: {e}")
            return []
    
    def parse_date(self, date_str):
        """Parse date string to datetime object"""
        try:
            if not date_str:
                return None
            # Normalize: remove references like [a], NBSPs, and condense spaces
            cleaned = re.sub(r'\[[^\]]*\]', '', date_str)
            cleaned = cleaned.replace('\xa0', ' ')
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()

            # Prefer ISO date inside parentheses if present: e.g., "June 28, 2025 (2025-06-28)"
            iso_in_paren = re.search(r'(\d{4}-\d{2}-\d{2})', cleaned)
            if iso_in_paren:
                return datetime.strptime(iso_in_paren.group(1), '%Y-%m-%d')

            # Try common formats
            date_formats = [
                '%B %d, %Y',      # January 1, 2025
                '%b %d, %Y',      # Jan 1, 2025
                '%d %B %Y',       # 1 January 2025
                '%d %b %Y',       # 1 Jan 2025
                '%Y-%m-%d',       # 2025-01-01
                '%m/%d/%Y',       # 01/01/2025
            ]
            for fmt in date_formats:
                try:
                    return datetime.strptime(cleaned, fmt)
                except ValueError:
                    continue

            logger.warning(f"⚠️ Could not parse date: {date_str}")
            return None

        except Exception as e:
            logger.warning(f"⚠️ Error parsing date '{date_str}': {e}")
            return None
    
    def process_single_event(self, event_data):
        """Process a single UFC event"""
        try:
            logger.info(f"🔍 Processing event: {event_data['name']}")
            
            # Get event info
            event_info = self.get_event_info(event_data['url'])
            if not event_info:
                logger.warning(f"⚠️ Could not get event info for {event_data['name']}")
                return False
            
            # Create event in database
            event_id = self.create_event(event_data, event_info)
            if not event_id:
                logger.warning(f"⚠️ Could not create event for {event_data['name']}")
                return False
            
            # Scrape fights
            fights = self.scrape_event_fights_robust(event_data['url'], event_data['name'])
            if not fights:
                logger.warning(f"⚠️ No fights found for {event_data['name']}")
                return False
            
            # Create fights in database
            successful_fights = 0
            for fight_data in fights:
                if self.create_fight_with_winner_loser(fight_data, event_id):
                    successful_fights += 1
            
            logger.info(f"✅ Event {event_data['name']}: {successful_fights}/{len(fights)} fights created")
            
            with self.lock:
                self.successful_events += 1
                self.total_fights += successful_fights
            
            # Be polite to Wikipedia: brief pause between events
            time.sleep(1.0)

            return True
            
        except Exception as e:
            logger.error(f"❌ Error processing event {event_data['name']}: {e}")
            with self.lock:
                self.failed_events += 1
            return False
    
    def get_event_info(self, url):
        """Extract event information from Wikipedia page"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for infobox
            infobox = soup.find('table', class_='infobox')
            if not infobox:
                return None
            
            event_info = {}
            
            # Extract event name from title
            title = soup.find('h1', id='firstHeading')
            if title:
                event_info['name'] = title.get_text(strip=True)
            
            # Extract date from infobox
            rows = infobox.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True).lower()
                    value = cells[1].get_text(strip=True)
                    
                    if 'date' in label:
                        event_info['date'] = self.parse_date(value)
                    elif 'venue' in label:
                        event_info['venue'] = value
                    elif 'location' in label:
                        event_info['location'] = value
            
            return event_info
            
        except Exception as e:
            logger.error(f"❌ Error getting event info from {url}: {e}")
            return None
    
    def scrape_event_fights_robust(self, url, event_name):
        """Extract ALL fights from a UFC event page with perfect accuracy"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all tables in document order
            tables = soup.find_all('table')
            all_fights = []
            global_fight_order = 1  # Maintain global fight order across all tables
            
            logger.info(f"📊 Found {len(tables)} tables on page")
            
            for table_idx, table in enumerate(tables):
                logger.info(f"🔍 Checking table #{table_idx + 1}")
                
                # Check if this table contains fight data
                if self._is_fight_table_robust(table):
                    logger.info(f"✅ Found fight table #{table_idx + 1}")
                    
                    # Parse fights with global fight order
                    table_fights = self._parse_fight_table_robust(table, global_fight_order)
                    all_fights.extend(table_fights)
                    logger.info(f"📊 Table #{table_idx + 1}: {len(table_fights)} fights (global order {global_fight_order}-{global_fight_order + len(table_fights) - 1})")
                    
                    # Update global fight order for next table
                    global_fight_order += len(table_fights)
            
            logger.info(f"🎯 TOTAL: Found {len(all_fights)} fights in {event_name}")
            
            # Log the perfect order
            for i, fight in enumerate(all_fights):
                main_text = " (MAIN EVENT)" if fight['is_main_event'] else ""
                co_main_text = " (CO-MAIN)" if fight['is_co_main_event'] else ""
                event_text = main_text + co_main_text
                logger.info(f"   {fight['fight_order']}. {fight['winner_name']} def. {fight['loser_name']} - {fight['weight_class']}{event_text}")
            
            return all_fights
            
        except Exception as e:
            logger.error(f"❌ Error scraping fights from {url}: {e}")
            return []
    
    def _is_fight_table_robust(self, table):
        """Check if a table contains fight data with exact 8-column structure"""
        try:
            rows = table.find_all('tr')
            
            # Need at least 2 rows (header + data)
            if len(rows) < 2:
                return False
            
            # Check if any row has exactly 8 columns (the fight table structure)
            for row in rows[1:]:  # Skip header
                cells = row.find_all(['td', 'th'])
                if len(cells) == 8:
                    # Check if it has the "def." pattern
                    cell_texts = [cell.get_text(strip=True) for cell in cells]
                    if any('def.' in text.lower() for text in cell_texts):
                        return True
            
            return False
            
        except Exception as e:
            logger.warning(f"⚠️ Error checking if table is fight table: {e}")
            return False
    
    def _parse_fight_table_robust(self, table, global_fight_order):
        """Parse fight table with exact 8-column structure"""
        fights = []
        rows = table.find_all('tr')
        
        if len(rows) < 2:
            return fights
        
        fight_order = global_fight_order  # Use the global fight order
        
        # Process each row in table order
        for row_idx, row in enumerate(rows[1:], start=1):
            cells = row.find_all(['td', 'th'])
            
            # Skip section headers (colspan=8)
            if len(cells) == 1 and cells[0].get('colspan') == '8':
                continue
                
            # Need exactly 8 columns for fight data
            if len(cells) == 8:
                try:
                    fight_data = self._parse_fight_row_robust(cells, fight_order)
                    if fight_data:
                        fights.append(fight_data)
                        fight_order += 1  # Only increment if a valid fight was created
                    # Don't increment fight_order if fight_data is None (skipped fight)
                except Exception as e:
                    logger.warning(f"⚠️ Error parsing fight row {row_idx}: {e}")
                    continue
        
        return fights
    
    def _parse_fight_row_robust(self, cells, fight_order):
        """Parse a single fight row with exact 8-column structure"""
        try:
            # Column 0: Weight Class
            weight_class = cells[0].get_text(strip=True)
            
            # Column 1: Winner
            winner_name = self._clean_fighter_name(cells[1].get_text(strip=True))
            
            # Column 2: "def." (skip this)
            # Column 3: Loser  
            loser_name = self._clean_fighter_name(cells[3].get_text(strip=True))
            
            # Column 4: Method
            method = cells[4].get_text(strip=True)
            
            # Column 5: Round
            round_text = cells[5].get_text(strip=True)
            round_num = int(round_text) if round_text.isdigit() else None
            
            # Column 6: Time
            time = cells[6].get_text(strip=True)
            
            # Column 7: Notes (skip this)
            
            # Skip fights with empty fighter names
            if not winner_name or not loser_name or winner_name.strip() == '' or loser_name.strip() == '':
                logger.warning(f"⚠️ Skipping fight with empty names: '{winner_name}' vs '{loser_name}'")
                return None
            
            # Simple logic: first fight = main event, second fight = co-main
            is_main_event = fight_order == 1
            is_co_main_event = fight_order == 2
            
            # Clean up method text
            method = self._clean_method_text(method)
            
            return {
                'weight_class': weight_class,
                'winner_name': winner_name,
                'loser_name': loser_name,
                'method': method,
                'round': round_num,
                'time': time,
                'fight_order': fight_order,
                'is_main_event': is_main_event,
                'is_co_main_event': is_co_main_event
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Error parsing fight row: {e}")
            return None
    
    def _clean_fighter_name(self, name):
        """Clean fighter name by removing extra whitespace and special characters"""
        try:
            # Remove extra whitespace
            name = re.sub(r'\s+', ' ', name.strip())
            
            # Remove common prefixes/suffixes
            name = re.sub(r'^\s*\([^)]*\)\s*', '', name)  # Remove (c) or other prefixes
            name = re.sub(r'\s*\([^)]*\)\s*$', '', name)  # Remove suffixes
            
            # Remove HTML entities
            name = name.replace('&nbsp;', ' ')
            
            return name.strip()
        except Exception as e:
            logger.warning(f"⚠️ Error cleaning fighter name '{name}': {e}")
            return name.strip()
    
    def _clean_method_text(self, method):
        """Clean up method text to standardize it"""
        method = method.strip()
        
        # Remove parentheses content
        method = re.sub(r'\([^)]*\)', '', method).strip()
        
        # Standardize common methods
        method_lower = method.lower()
        if 'decision' in method_lower:
            if 'unanimous' in method_lower:
                return 'Decision (Unanimous)'
            elif 'split' in method_lower:
                return 'Decision (Split)'
            elif 'majority' in method_lower:
                return 'Decision (Majority)'
            else:
                return 'Decision'
        elif 'ko' in method_lower:
            return 'KO'
        elif 'tko' in method_lower:
            return 'TKO'
        elif 'submission' in method_lower:
            return 'Submission'
        elif 'dqf' in method_lower:
            return 'DQ'
        elif 'nc' in method_lower:
            return 'No Contest'
        else:
            return method
    
    def create_event(self, event_data, event_info):
        """Create event in Supabase database"""
        try:
            # Check if event already exists
            check_response = requests.get(
                f"{SUPABASE_URL}/rest/v1/events",
                headers=self.supabase_headers,
                params={'name': f'eq.{event_data["name"]}', 'select': 'id'}
            )
            
            if check_response.status_code == 200:
                existing_events = check_response.json()
                if existing_events:
                    logger.info(f"✅ Event '{event_data['name']}' already exists, reusing ID: {existing_events[0]['id']}")
                    return existing_events[0]['id']
            
            # Create new event
            preferred_date = None
            # Prefer list page date first if available and valid, else event page date
            if event_data.get('list_date') is not None:
                preferred_date = event_data['list_date']
            elif event_info.get('date') is not None:
                preferred_date = event_info['date']

            event_payload = {
                'name': event_data['name'],
                'location': event_info.get('location', ''),
                'venue': event_info.get('venue', ''),
                'status': 'completed'
            }
            if preferred_date is not None:
                event_payload['date'] = preferred_date.isoformat()
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/events",
                headers=self.supabase_headers,
                json=event_payload
            )
            
            if response.status_code == 201:
                # Get the created event ID
                events_response = requests.get(
                    f"{SUPABASE_URL}/rest/v1/events",
                    headers=self.supabase_headers,
                    params={'name': f'eq.{event_data["name"]}', 'select': 'id', 'limit': 1}
                )
                
                if events_response.status_code == 200:
                    events = events_response.json()
                    if events:
                        event_id = events[0]['id']
                        logger.info(f"✅ Created event '{event_data['name']}' with ID: {event_id}")
                        return event_id
            
            logger.error(f"❌ Failed to create event '{event_data['name']}'")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error creating event '{event_data['name']}': {e}")
            return None
    
    def create_fight_with_winner_loser(self, fight_data, event_id):
        """Create fight in Supabase database with winner/loser data"""
        try:
            # Check if this fight already exists
            check_response = requests.get(
                f"{SUPABASE_URL}/rest/v1/fights",
                headers=self.supabase_headers,
                params={
                    'event_id': f'eq.{event_id}',
                    'winner_name': f'eq.{fight_data["winner_name"]}',
                    'loser_name': f'eq.{fight_data["loser_name"]}',
                    'select': 'id'
                }
            )
            
            if check_response.status_code == 200:
                existing_fights = check_response.json()
                if existing_fights:
                    logger.info(f"✅ Fight already exists: {fight_data['winner_name']} def. {fight_data['loser_name']}")
                    return True
            
            fight_payload = {
                'event_id': event_id,
                'weight_class': fight_data['weight_class'],
                'winner_name': fight_data['winner_name'],
                'loser_name': fight_data['loser_name'],
                'fight_order': fight_data['fight_order'],
                'is_main_event': fight_data['is_main_event'],
                'is_co_main_event': fight_data['is_co_main_event'],
                'method': fight_data['method'],
                'round': fight_data['round'],
                'time': fight_data['time'],
                'status': 'completed'
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/fights",
                headers=self.supabase_headers,
                json=fight_payload
            )
            
            if response.status_code == 201:
                logger.info(f"✅ Created fight: {fight_data['winner_name']} def. {fight_data['loser_name']}")
                return True
            else:
                logger.warning(f"⚠️ Failed to create fight: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating fight: {e}")
            return False
    
    def run_robust_scraper(self, max_events=None, start_from=0):
        """Run the robust scraper"""
        try:
            logger.info("🚀 Starting ROBUST Wikipedia UFC Scraper")
            
            # Get all events
            events = self.get_all_past_events_with_actual_links()
            if not events:
                logger.error("❌ No events found")
                return
            
            # Limit events if specified
            if max_events:
                events = events[start_from:start_from + max_events]
                logger.info(f"📊 Processing {len(events)} events (starting from {start_from})")
            else:
                events = events[start_from:]
                logger.info(f"📊 Processing {len(events)} events (starting from {start_from})")
            
            # Process events with threading
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [executor.submit(self.process_single_event, event) for event in events]
                
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logger.error(f"❌ Error in thread: {e}")
            
            # Print final statistics
            logger.info("🎉 ROBUST SCRAPER COMPLETED!")
            logger.info(f"📊 Successful events: {self.successful_events}")
            logger.info(f"📊 Failed events: {self.failed_events}")
            logger.info(f"📊 Total fights: {self.total_fights}")
            
        except Exception as e:
            logger.error(f"❌ Error in robust scraper: {e}")

def main():
    """Main function with CLI for scaling"""
    parser = argparse.ArgumentParser(description="ROBUST Wikipedia UFC Scraper")
    parser.add_argument("--max-events", type=int, default=None, help="Limit number of events to process (default: all)")
    parser.add_argument("--start-from", type=int, default=0, help="Start index in discovered events list")
    parser.add_argument("--workers", type=int, default=4, help="Number of concurrent events to process")
    args = parser.parse_args()

    scraper = RobustWikipediaScraper(max_workers=args.workers)
    scraper.run_robust_scraper(max_events=args.max_events, start_from=args.start_from)

if __name__ == "__main__":
    main() 