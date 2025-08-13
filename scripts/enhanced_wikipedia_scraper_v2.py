#!/usr/bin/env python3
"""
Enhanced Wikipedia Scraper V2
Scrapes UFC events from Wikipedia with proper winner/loser detection and fight order
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

# Add the scripts directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv('.env')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

class EnhancedWikipediaScraperV2:
    def __init__(self, max_workers=5):
        self.max_workers = max_workers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.supabase_headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
        }
        self.base_url = "https://en.wikipedia.org"
        
        # Thread-safe counters
        self.lock = Lock()
        self.successful_events = 0
        self.failed_events = 0
        self.total_fights = 0
        self.processed_events = 0
        
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
                        
                        # Look for the event link in the second cell
                        event_link = cells[1].find('a')
                        if event_link and event_link.get('href'):
                            event_url = urljoin(self.base_url, event_link.get('href'))
                            
                            # Parse date
                            event_date = self.parse_date(date_text)
                            
                            events.append({
                                'number': event_number,
                                'name': event_name,
                                'date': event_date,
                                'venue': venue_text,
                                'url': event_url
                            })
                    except Exception as e:
                        logger.warning(f"⚠️ Error parsing row: {e}")
                        continue
            
            logger.info(f"✅ Extracted {len(events)} events from Wikipedia")
            return events
            
        except Exception as e:
            logger.error(f"❌ Error extracting events from Wikipedia: {e}")
            return []
    
    def parse_date(self, date_str):
        """Parse date from various formats"""
        try:
            # Remove extra whitespace and normalize
            date_str = re.sub(r'\s+', ' ', date_str.strip())
            
            # Common date patterns
            patterns = [
                r'(\w+\s+\d{1,2},\s+\d{4})',  # "June 28, 2025"
                r'(\d{1,2}\s+\w+\s+\d{4})',   # "28 June 2025"
                r'(\w+\s+\d{4})',              # "June 2025"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, date_str)
                if match:
                    return match.group(1)
            
            return date_str
        except Exception as e:
            logger.error(f"Error parsing date '{date_str}': {e}")
            return date_str
    
    def process_single_event(self, event_data):
        """Process a single UFC event and extract all fights"""
        try:
            logger.info(f"🔍 Processing event: {event_data['name']}")
            
            # Get event info
            event_info = self.get_event_info(event_data['url'])
            if not event_info:
                return None
            
            # Create event in database
            event_id = self.create_event(event_data, event_info)
            if not event_id:
                logger.error(f"❌ Failed to create event: {event_data['name']}")
                return None
            
            # Extract fights from the event page
            fights = self.scrape_event_fights(event_data['url'], event_data['name'])
            
            # Create fights in database
            created_fights = 0
            for fight_data in fights:
                fight_id = self.create_fight_with_winner_loser(fight_data, event_id)
                if fight_id:
                    created_fights += 1
            
            with self.lock:
                self.successful_events += 1
                self.total_fights += created_fights
            
            logger.info(f"✅ Event processed: {event_data['name']} - {created_fights} fights created")
            return {
                'event_id': event_id,
                'fights_created': created_fights
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing event {event_data['name']}: {e}")
            with self.lock:
                self.failed_events += 1
            return None
    
    def get_event_info(self, url):
        """Extract event information from Wikipedia page"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract event title
            title = soup.find('h1', {'id': 'firstHeading'})
            event_title = title.get_text().strip() if title else "Unknown Event"
            
            # Extract event date from infobox
            event_date = None
            infobox = soup.find('table', {'class': 'infobox'})
            if infobox:
                date_row = infobox.find('th', string=lambda text: text and 'Date' in text)
                if date_row and date_row.find_next_sibling('td'):
                    date_text = date_row.find_next_sibling('td').get_text().strip()
                    event_date = self.parse_date(date_text)
            
            # Extract venue from infobox
            venue = None
            if infobox:
                venue_row = infobox.find('th', string=lambda text: text and 'Venue' in text)
                if venue_row and venue_row.find_next_sibling('td'):
                    venue = venue_row.find_next_sibling('td').get_text().strip()
            
            return {
                'title': event_title,
                'date': event_date,
                'venue': venue,
                'url': url
            }
            
        except Exception as e:
            logger.error(f"Error getting event info from {url}: {e}")
            return None
    
    def scrape_event_fights(self, url, event_name):
        """Extract all fights from a UFC event page with proper winner/loser detection"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all tables
            tables = soup.find_all('table')
            fights = []
            
            for table in tables:
                # Check if this table contains fight data
                if self._is_fight_table(table):
                    table_fights = self._parse_fight_table_v2(table)
                    fights.extend(table_fights)
            
            logger.info(f"📊 Found {len(fights)} fights in {event_name}")
            return fights
            
        except Exception as e:
            logger.error(f"❌ Error scraping fights from {url}: {e}")
            return []
    
    def _is_fight_table(self, table):
        """Check if a table contains fight data"""
        try:
            # Look for headers that indicate fight data
            headers = table.find_all('th')
            header_text = ' '.join([h.get_text(strip=True) for h in headers]).lower()
            
            # Check for fight indicators
            fight_indicators = ['weight class', 'fighter', 'def.', 'method', 'round', 'time']
            has_indicators = any(indicator in header_text for indicator in fight_indicators)
            
            # Also check if the table has fight data in the rows
            rows = table.find_all('tr')
            has_def_pattern = False
            if len(rows) > 2:  # Need at least header + data rows
                # Check if any row contains "def." pattern
                for row in rows[1:]:  # Skip header row
                    cells = row.find_all(['td', 'th'])
                    cell_texts = [cell.get_text(strip=True) for cell in cells]
                    if any('def.' in text.lower() for text in cell_texts):
                        has_def_pattern = True
                        break
            
            return has_indicators or has_def_pattern
            
        except Exception as e:
            logger.warning(f"⚠️ Error checking if table is fight table: {e}")
            return False
    
    def _parse_fight_table_v2(self, table):
        """Parse fight table with enhanced winner/loser detection"""
        fights = []
        rows = table.find_all('tr')
        
        if len(rows) < 2:  # Need at least header + data
            return fights
        
        # Skip header row
        for row_idx, row in enumerate(rows[1:], start=1):
            cells = row.find_all(['td', 'th'])
            
            if len(cells) >= 6:  # Need at least weight class, fighter1, result, fighter2, method, round, time
                try:
                    fight_data = self._parse_fight_row_v2(cells, row_idx)
                    if fight_data:
                        fights.append(fight_data)
                except Exception as e:
                    logger.warning(f"⚠️ Error parsing fight row {row_idx}: {e}")
                    continue
        
        return fights
    
    def _parse_fight_row_v2(self, cells, fight_order):
        """Parse a single fight row with enhanced winner/loser detection"""
        try:
            # Extract basic fight data
            weight_class = cells[0].get_text(strip=True) if len(cells) > 0 else ""
            
            # Find the "def." cell to determine winner/loser
            winner_name = None
            loser_name = None
            method = ""
            round_num = None
            time = ""
            
            # Look for the "def." pattern
            for i, cell in enumerate(cells):
                cell_text = cell.get_text(strip=True).lower()
                if 'def.' in cell_text:
                    # The fighter before "def." is the winner
                    if i > 0:
                        winner_name = self._clean_fighter_name(cells[i-1].get_text(strip=True))
                    
                    # The fighter after "def." is the loser
                    if i + 1 < len(cells):
                        loser_name = self._clean_fighter_name(cells[i+1].get_text(strip=True))
                    break
            
            # Extract method, round, time from remaining cells
            for i, cell in enumerate(cells):
                cell_text = cell.get_text(strip=True)
                
                # Look for method (usually contains parentheses or specific terms)
                if any(term in cell_text.lower() for term in ['ko', 'submission', 'decision', 'tko', 'dqf', 'nc']):
                    method = cell_text
                
                # Look for round number
                if re.match(r'^\d+$', cell_text.strip()):
                    round_num = int(cell_text.strip())
                
                # Look for time (format: MM:SS)
                if re.match(r'^\d+:\d+$', cell_text.strip()):
                    time = cell_text.strip()
            
            # If we couldn't determine winner/loser from "def.", try alternative patterns
            if not winner_name or not loser_name:
                winner_name, loser_name = self._determine_winner_loser_alternative(cells)
            
            if winner_name and loser_name:
                return {
                    'weight_class': weight_class,
                    'winner_name': winner_name,
                    'loser_name': loser_name,
                    'method': method,
                    'round': round_num,
                    'time': time,
                    'fight_order': fight_order,
                    'is_main_event': fight_order == 1,
                    'is_co_main_event': fight_order == 2
                }
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Error parsing fight row: {e}")
            return None
    
    def _determine_winner_loser_alternative(self, cells):
        """Alternative method to determine winner/loser if "def." pattern not found"""
        try:
            # Look for other patterns that might indicate winner
            for i, cell in enumerate(cells):
                cell_text = cell.get_text(strip=True).lower()
                
                # Look for victory indicators
                victory_indicators = ['win', 'victory', 'defeated', 'beat']
                if any(indicator in cell_text for indicator in victory_indicators):
                    if i > 0:
                        winner_name = self._clean_fighter_name(cells[i-1].get_text(strip=True))
                    if i + 1 < len(cells):
                        loser_name = self._clean_fighter_name(cells[i+1].get_text(strip=True))
                    return winner_name, loser_name
            
            # If no clear pattern, assume first fighter is winner, second is loser
            if len(cells) >= 2:
                winner_name = self._clean_fighter_name(cells[0].get_text(strip=True))
                loser_name = self._clean_fighter_name(cells[1].get_text(strip=True))
                return winner_name, loser_name
            
            return None, None
            
        except Exception as e:
            logger.warning(f"⚠️ Error in alternative winner/loser detection: {e}")
            return None, None
    
    def _clean_fighter_name(self, name):
        """Clean fighter name by removing extra whitespace and special characters"""
        try:
            # Remove extra whitespace
            name = re.sub(r'\s+', ' ', name.strip())
            
            # Remove common prefixes/suffixes
            name = re.sub(r'^\[.*?\]\s*', '', name)  # Remove [brackets]
            name = re.sub(r'\s*\[.*?\]$', '', name)  # Remove [brackets] at end
            
            # Remove common titles
            name = re.sub(r'\b(def\.|defeated|beat|win|victory)\b', '', name, flags=re.IGNORECASE)
            
            return name.strip()
        except Exception as e:
            logger.warning(f"⚠️ Error cleaning fighter name '{name}': {e}")
            return name.strip()
    
    def create_event(self, event_data, event_info):
        """Create event in database or return existing one"""
        try:
            # First check if event already exists
            check_response = requests.get(
                f"{SUPABASE_URL}/rest/v1/events",
                headers=self.supabase_headers,
                params={'name': f'eq.{event_data["name"]}', 'select': 'id', 'limit': 1}
            )
            
            if check_response.status_code == 200:
                existing_events = check_response.json()
                if existing_events:
                    event_id = existing_events[0]['id']
                    logger.info(f"✅ Found existing event: {event_data['name']} (ID: {event_id})")
                    return event_id
            
            # Create new event if it doesn't exist
            event_payload = {
                'name': event_data['name'],
                'date': event_data['date'],
                'venue': event_data.get('venue', ''),
                'location': event_data.get('venue', '')  # Use venue as location for now
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/events",
                headers=self.supabase_headers,
                json=event_payload
            )
            
            if response.status_code == 201:
                # Supabase POST requests return empty response on success
                # We need to get the created event ID by querying for it
                try:
                    # Query for the event we just created
                    query_response = requests.get(
                        f"{SUPABASE_URL}/rest/v1/events",
                        headers=self.supabase_headers,
                        params={'name': f'eq.{event_data["name"]}', 'select': 'id', 'limit': 1}
                    )
                    
                    if query_response.status_code == 200:
                        events = query_response.json()
                        if events:
                            event_id = events[0]['id']
                            logger.info(f"✅ Created event: {event_data['name']} (ID: {event_id})")
                            return event_id
                        else:
                            logger.warning(f"⚠️ Event created but could not retrieve ID for: {event_data['name']}")
                            return None
                    else:
                        logger.warning(f"⚠️ Could not query for created event: {query_response.status_code}")
                        return None
                except Exception as e:
                    logger.error(f"❌ Error getting event ID: {e}")
                    return None
            else:
                logger.error(f"❌ Failed to create event: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error creating event: {e}")
            return None
    
    def create_fight_with_winner_loser(self, fight_data, event_id):
        """Create fight in database with winner/loser information"""
        try:
            fight_payload = {
                'event_id': event_id,
                'winner_name': fight_data['winner_name'],
                'loser_name': fight_data['loser_name'],
                'fight_order': fight_data['fight_order'],
                'is_main_event': fight_data['is_main_event'],
                'is_co_main_event': fight_data['is_co_main_event'],
                'weight_class': fight_data['weight_class'],
                'method': fight_data['method'],
                'round': fight_data['round'],
                'time': fight_data['time'],
                'notes': fight_data.get('notes', '')
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/fights",
                headers=self.supabase_headers,
                json=fight_payload
            )
            
            if response.status_code == 201:
                # Supabase POST requests return empty response on success
                # We need to get the created fight ID by querying for it
                try:
                    # Query for the fight we just created
                    query_response = requests.get(
                        f"{SUPABASE_URL}/rest/v1/fights",
                        headers=self.supabase_headers,
                        params={'event_id': f'eq.{event_id}', 'winner_name': f'eq.{fight_data.get("winner_name", "")}', 'select': 'id', 'limit': 1}
                    )
                    
                    if query_response.status_code == 200:
                        fights = query_response.json()
                        if fights:
                            fight_id = fights[0]['id']
                            logger.info(f"✅ Created fight: {fight_data['winner_name']} def. {fight_data['loser_name']} (ID: {fight_id})")
                            return fight_id
                        else:
                            logger.warning(f"⚠️ Fight created but could not retrieve ID")
                            return None
                    else:
                        logger.warning(f"⚠️ Could not query for created fight: {query_response.status_code}")
                        return None
                except Exception as e:
                    logger.error(f"❌ Error getting fight ID: {e}")
                    return None
            else:
                logger.error(f"❌ Failed to create fight: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error creating fight: {e}")
            return None
    
    def run_enhanced_scraper(self, max_events=None, start_from=0):
        """Run the enhanced scraper"""
        try:
            logger.info("🚀 Starting Enhanced Wikipedia Scraper V2")
            
            # Get all events
            events = self.get_all_past_events_with_actual_links()
            
            if not events:
                logger.error("❌ No events found")
                return False
            
            # Limit events if specified
            if max_events:
                events = events[start_from:start_from + max_events]
                logger.info(f"📊 Processing {len(events)} events (starting from {start_from})")
            else:
                events = events[start_from:]
                logger.info(f"📊 Processing {len(events)} events (starting from {start_from})")
            
            # Process events in parallel
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all tasks
                future_to_event = {
                    executor.submit(self.process_single_event, event): event 
                    for event in events
                }
                
                # Process completed tasks
                for future in as_completed(future_to_event):
                    event = future_to_event[future]
                    try:
                        result = future.result()
                        if result:
                            with self.lock:
                                self.processed_events += 1
                    except Exception as e:
                        logger.error(f"❌ Error processing event {event['name']}: {e}")
                        with self.lock:
                            self.failed_events += 1
            
            # Print summary
            logger.info("🎉 Scraping completed!")
            logger.info(f"📊 Summary:")
            logger.info(f"   ✅ Successful events: {self.successful_events}")
            logger.info(f"   ❌ Failed events: {self.failed_events}")
            logger.info(f"   👊 Total fights created: {self.total_fights}")
            logger.info(f"   📈 Processed events: {self.processed_events}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error in enhanced scraper: {e}")
            return False

def main():
    """Main function"""
    scraper = EnhancedWikipediaScraperV2(max_workers=3)
    
    # Run scraper with limited events for testing
    success = scraper.run_enhanced_scraper(max_events=5, start_from=0)
    
    if success:
        print("✅ Enhanced Wikipedia scraper completed successfully!")
    else:
        print("❌ Enhanced Wikipedia scraper failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 