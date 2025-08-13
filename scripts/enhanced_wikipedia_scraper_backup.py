#!/usr/bin/env python3
"""
Enhanced Wikipedia Scraper
Scrapes events and fights with fighter names as fields (no separate fighter records)
"""

import os
import sys
import requests
import logging
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Add the scripts directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv('.env')

# Debug: Check if environment variables are loaded
print(f"🔍 DEBUG: SUPABASE_URL = {os.getenv('SUPABASE_URL')}")
print(f"🔍 DEBUG: SUPABASE_SERVICE_KEY = {os.getenv('SUPABASE_SERVICE_KEY')[:20] + '...' if os.getenv('SUPABASE_SERVICE_KEY') else 'None'}")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

class EnhancedWikipediaScraper:
    def __init__(self, max_workers=10):
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
                        location_text = cells[4].get_text(strip=True)
                        
                        # Skip header row
                        if event_number == '#' or event_name == 'Event':
                            continue
                        
                        # Find actual Wikipedia link in the event cell
                        event_cell = cells[1]
                        links = event_cell.find_all('a')
                        actual_wikipedia_url = None
                        
                        if links:
                            for link in links:
                                href = link.get('href')
                                if href and 'wiki' in href:
                                    actual_wikipedia_url = f"https://en.wikipedia.org{href}"
                                    break
                        
                        # Parse date
                        parsed_date = self.parse_date(date_text)
                        
                        if parsed_date and event_name:
                            event_data = {
                                'name': event_name,
                                'date': parsed_date,
                                'venue': venue_text,
                                'location': location_text,
                                'event_number': event_number,
                                'wikipedia_url': actual_wikipedia_url
                            }
                            events.append(event_data)
                            
                    except Exception as e:
                        logger.warning(f"⚠️ Error parsing event row: {str(e)}")
                        continue
            
            logger.info(f"📊 Found {len(events)} past events")
            events_with_links = len([e for e in events if e['wikipedia_url']])
            logger.info(f"🔗 Events with Wikipedia links: {events_with_links}/{len(events)}")
            
            return events
            
        except Exception as e:
            logger.error(f"❌ Error getting past events: {str(e)}")
            return []
    
    def parse_date(self, date_str):
        """Parse date from various formats"""
        try:
            # Remove extra whitespace and normalize
            import re
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
        """Process a single event (thread-safe)"""
        event_name = event_data['name']
        wikipedia_url = event_data['wikipedia_url']
        
        try:
            # Step 1: Scrape fighter data using the actual Wikipedia URL
            fights_data = self.scrape_event_fighters(wikipedia_url, event_name)
            
            if not fights_data:
                with self.lock:
                    self.failed_events += 1
                    self.processed_events += 1
                return f"❌ No fights found for: {event_name}"
            
            # Step 2: Create event in database
            event_id = self.create_event(event_data)
            
            if not event_id:
                with self.lock:
                    self.failed_events += 1
                    self.processed_events += 1
                return f"❌ Failed to create event: {event_name}"
            
            # Step 3: Create fights in database with fighter names as fields
            created_fights = 0
            for fight_data in fights_data:
                fight_id = self.create_fight_with_names(fight_data, event_id, event_name)
                if fight_id:
                    created_fights += 1
            
            # Update counters thread-safely
            with self.lock:
                self.successful_events += 1
                self.total_fights += created_fights
                self.processed_events += 1
            
            return f"✅ {event_name}: {created_fights}/{len(fights_data)} fights created"
            
        except Exception as e:
            with self.lock:
                self.failed_events += 1
                self.processed_events += 1
            return f"❌ Error processing {event_name}: {str(e)}"
    
    def scrape_event_fighters(self, url, event_name):
        """Scrape fighter data from a UFC event page"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all tables
            all_tables = soup.find_all('table')
            
            fights_data = []
            
            print(f"🔍 DEBUG: Scraping {url}")
            print(f"   Found {len(all_tables)} tables")
            
            for table_idx, table in enumerate(all_tables):
                # Look for tables with fight patterns
                table_text = table.get_text()
                print(f"   Table {table_idx}: {len(table_text)} chars")
                
                # Look for various fight indicators
                if any(indicator in table_text.lower() for indicator in ['def.', 'def', 'decision', 'ko', 'submission', 'tko']):
                    print(f"   Table {table_idx} contains fight data")
                    # Parse this table for fights
                    table_fights = self._parse_fight_table(table)
                    if table_fights:
                        print(f"   Found {len(table_fights)} fights in table {table_idx}")
                        fights_data.extend(table_fights)
            
            print(f"   Total fights found: {len(fights_data)}")
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
                    continue
        
        return fights
    
    def create_event(self, event_data):
        """Create an event in the database"""
        try:
            event_to_create = {
                'name': event_data['name'],
                'date': event_data['date'],
                'venue': event_data['venue'],
                'location': event_data['location']
            }
            
            print(f"🔍 DEBUG: Creating event: {event_data['name']}")
            print(f"   Data: {event_to_create}")
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/events",
                headers=self.supabase_headers,
                json=event_to_create
            )
            
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
            if response.status_code == 201:
                # Handle empty response body
                try:
                    return response.json()['id']
                except (ValueError, KeyError):
                    # If response is empty, try to get the event by name
                    fetch_response = requests.get(
                        f"{SUPABASE_URL}/rest/v1/events?name=eq.{event_data['name']}",
                        headers=self.supabase_headers
                    )
                    if fetch_response.status_code == 200:
                        events = fetch_response.json()
                        if events:
                            return events[0]['id']
                    return None
            else:
                print(f"   ❌ Failed to create event: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Exception creating event: {e}")
            return None
    
    def create_fight_with_names(self, fight_data, event_id, event_name):
        """Create a fight in the database with fighter names as fields"""
        try:
            # Create fight with embedded fighter names (no separate fighter records)
            fight_to_create = {
                'event_id': event_id,
                'weight_class': fight_data['weight_class'],
                'status': 'completed',
                'result': {
                    'method': fight_data['method'],
                    'round': fight_data['round'],
                    'time': fight_data['time']
                },
                # NEW: Fighter names as fields (no records)
                'fighter1_name': fight_data['winner'],
                'fighter2_name': fight_data['loser'],
                # Set winner ID correctly (fighter1 is the winner, so winner_id = 1)
                '# winner_id: 1,  # TODO: Add schema property  # fighter1_id = 1 (winner is fighter1)
                # Mark as main event if it's the main event
                '# is_main_event: self._is_main_event_fight(fight_data, event_name)  # TODO: Add schema property
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/fights",
                headers=self.supabase_headers,
                json=fight_to_create
            )
            
            if response.status_code == 201:
                # Handle empty response body
                try:
                    return response.json()['id']
                except (ValueError, KeyError):
                    # If response is empty, try to get the fight by event and fighter names
                    fetch_response = requests.get(
                        f"{SUPABASE_URL}/rest/v1/fights?event_id=eq.{event_id}&fighter1_name=eq.{fight_data['winner']}&fighter2_name=eq.{fight_data['loser']}",
                        headers=self.supabase_headers
                    )
                    if fetch_response.status_code == 200:
                        fights = fetch_response.json()
                        if fights:
                            return fights[0]['id']
                    return None
            else:
                return None
                
        except Exception as e:
            return None
    
    def _# is_main_event: self._is_main_event_fight(fight_data, event_name)  # TODO: Add schema property:
        """Determine if a fight is the main event based on event name and fighter names"""
        # Extract fighter names from the event name
        # Event format: "UFC on ESPN: Taira vs. Park" or "UFC 300: Pereira vs. Hill"
        event_lower = event_name.lower()
        
        # Look for "vs" pattern in event name
        if ' vs ' in event_name:
            # Extract the main event fighters from the event name
            # Handle different formats: "UFC on ESPN: Taira vs. Park" or "UFC 300: Pereira vs. Hill"
            if ': ' in event_name:
                main_event_part = event_name.split(': ')[-1]
            else:
                main_event_part = event_name
            
            # Split by " vs " to get both fighters
            if ' vs ' in main_event_part:
                fighter1_name = main_event_part.split(' vs ')[0].strip()
                fighter2_name = main_event_part.split(' vs ')[1].strip()
                
                # Check if this fight involves the main event fighters
                current_winner = fight_data['winner'].lower()
                current_loser = fight_data['loser'].lower()
                
                # Check if either fighter in this fight matches the main event fighters
                if (fighter1_name.lower() in current_winner or fighter1_name.lower() in current_loser or
                    fighter2_name.lower() in current_winner or fighter2_name.lower() in current_loser):
                    return True
        
        # Fallback: check if it's a championship weight class
        championship_classes = ['Heavyweight', 'Light Heavyweight', 'Middleweight', 
                              'Welterweight', 'Lightweight', 'Featherweight', 'Bantamweight',
                              'Flyweight', 'Women\'s Bantamweight', 'Women\'s Flyweight',
                              'Women\'s Strawweight', 'Women\'s Featherweight']
        
        weight_class = fight_data['weight_class'].lower()
        for champ_class in championship_classes:
            if champ_class.lower() in weight_class:
                return True
                
        return False
    
    def run_enhanced_scraper(self, max_events=None, start_from=0):
        """Run the enhanced Wikipedia scraper"""
        logger.info("🚀 Starting Enhanced Wikipedia Scraper")
        logger.info("📊 Scraping events and fights with fighter names as fields")
        logger.info("⚡ No separate fighter records - clean data structure")
        logger.info(f"⚡ Using {self.max_workers} parallel workers")
        logger.info("=" * 60)
        
        # Step 1: Get all past events with their actual Wikipedia links
        events = self.get_all_past_events_with_actual_links()
        
        if not events:
            logger.error("❌ No events found")
            return
        
        # Apply limits
        if start_from > 0:
            events = events[start_from:]
        
        if max_events:
            events = events[:max_events]
        
        logger.info(f"📊 Processing {len(events)} events in parallel (starting from event {start_from})")
        
        # Step 2: Process events in parallel
        start_time = time.time()
        
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
                    logger.info(f"📊 Progress: {self.processed_events}/{len(events)} - {result}")
                    
                    # Progress update every 20 events
                    if self.processed_events % 20 == 0:
                        elapsed_time = time.time() - start_time
                        events_per_second = self.processed_events / elapsed_time if elapsed_time > 0 else 0
                        estimated_total_time = len(events) / events_per_second if events_per_second > 0 else 0
                        remaining_time = estimated_total_time - elapsed_time
                        
                        logger.info(f"📈 Progress Update:")
                        logger.info(f"   ✅ Successful: {self.successful_events}, ❌ Failed: {self.failed_events}")
                        logger.info(f"   🥊 Total fights: {self.total_fights}")
                        logger.info(f"   ⏱️ Elapsed: {elapsed_time:.1f}s, Remaining: {remaining_time:.1f}s")
                        logger.info(f"   🚀 Speed: {events_per_second:.2f} events/sec")
                
                except Exception as e:
                    logger.error(f"❌ Error processing event {event['name']}: {str(e)}")
        
        # Final summary
        total_time = time.time() - start_time
        logger.info("=" * 60)
        logger.info("🎉 Enhanced Wikipedia Scraper Completed!")
        logger.info(f"📊 Events processed: {self.processed_events}")
        logger.info(f"✅ Successful events: {self.successful_events}")
        logger.info(f"❌ Failed events: {self.failed_events}")
        logger.info(f"🥊 Total fights created: {self.total_fights}")
        logger.info(f"⏱️ Total time: {total_time:.1f} seconds")
        logger.info(f"🚀 Average speed: {self.processed_events/total_time:.2f} events/sec")
        logger.info("=" * 60)

def main():
    scraper = EnhancedWikipediaScraper(max_workers=10)
    scraper.run_enhanced_scraper(max_events=None, start_from=0)

if __name__ == "__main__":
    main() 