#!/usr/bin/env python3
"""
Ultra Robust UFC Scraper
Enhanced scraper with better error handling, retry logic, and comprehensive fight detection
"""

import os
import sys
import requests
import logging
import time
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Add the scripts directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv('scripts/.env')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

class UltraRobustScraper:
    def __init__(self, max_workers=8):
        self.max_workers = max_workers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
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
        self.retry_count = 0
        
    def get_all_past_events_with_actual_links(self):
        """Get all past events with their actual Wikipedia links - ultra robust"""
        url = "https://en.wikipedia.org/wiki/List_of_UFC_events"
        
        try:
            logger.info(f"🔍 Loading main UFC events page: {url}")
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            logger.info("✅ Successfully loaded main UFC events page")
            
            # Find all tables
            all_tables = soup.find_all('table')
            logger.info(f"📊 Found {len(all_tables)} total tables on page")
            
            events = []
            
            # Process ALL tables that might contain UFC events
            for table_idx, table in enumerate(all_tables):
                table_text = table.get_text()
                ufc_count = table_text.count('UFC')
                
                # Only process tables with UFC references
                if ufc_count > 0:
                    logger.info(f"📋 Processing Table {table_idx + 1} with {ufc_count} UFC references")
                    table_events = self._extract_events_from_table_robust(table, table_idx)
                    events.extend(table_events)
            
            # Remove duplicates based on event name
            unique_events = []
            seen_names = set()
            for event in events:
                if event['name'] not in seen_names:
                    seen_names.add(event['name'])
                    unique_events.append(event)
            
            logger.info(f"📊 Found {len(events)} total events, {len(unique_events)} unique events")
            events_with_links = len([e for e in unique_events if e['wikipedia_url']])
            logger.info(f"🔗 Events with Wikipedia links: {events_with_links}/{len(unique_events)}")
            
            return unique_events
            
        except Exception as e:
            logger.error(f"❌ Error getting past events: {str(e)}")
            return []
    
    def _extract_events_from_table_robust(self, table, table_idx):
        """Extract events from a specific table with robust error handling"""
        events = []
        rows = table.find_all('tr')
        
        for row_idx, row in enumerate(rows):
            try:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 3:  # Need at least some basic data
                    # Try different column configurations
                    event_data = self._parse_event_row_robust(cells, table_idx, row_idx)
                    if event_data:
                        events.append(event_data)
                        
            except Exception as e:
                logger.debug(f"⚠️ Error parsing row {row_idx} in table {table_idx}: {str(e)}")
                continue
        
        return events
    
    def _parse_event_row_robust(self, cells, table_idx, row_idx):
        """Parse a single event row with ultra robust error handling"""
        try:
            # Try different column configurations based on table structure
            if len(cells) >= 6:
                # Standard format: #, Event, Date, Venue, Location
                event_number = cells[0].get_text(strip=True)
                event_name = cells[1].get_text(strip=True)
                date_text = cells[2].get_text(strip=True)
                venue_text = cells[3].get_text(strip=True) if len(cells) > 3 else ""
                location_text = cells[4].get_text(strip=True) if len(cells) > 4 else ""
            elif len(cells) >= 4:
                # Alternative format: Event, Date, Venue, Location
                event_name = cells[0].get_text(strip=True)
                date_text = cells[1].get_text(strip=True)
                venue_text = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                location_text = cells[3].get_text(strip=True) if len(cells) > 3 else ""
                event_number = ""
            else:
                return None
            
            # Skip header rows and empty rows
            if (event_name in ['Event', 'Event Name', ''] or 
                event_number == '#' or 
                not event_name or 
                not 'UFC' in event_name):
                return None
            
            # Find actual Wikipedia link in the event cell
            event_cell = cells[1] if len(cells) >= 6 else cells[0]
            links = event_cell.find_all('a')
            actual_wikipedia_url = None
            
            if links:
                for link in links:
                    href = link.get('href')
                    if href and 'wiki' in href:
                        actual_wikipedia_url = f"https://en.wikipedia.org{href}"
                        break
            
            # Parse date with multiple attempts
            parsed_date = self.parse_date_robust(date_text)
            
            if event_name and 'UFC' in event_name:
                event_data = {
                    'name': event_name,
                    'date': parsed_date,
                    'venue': venue_text,
                    'location': location_text,
                    'event_number': event_number,
                    'wikipedia_url': actual_wikipedia_url,
                    'table_source': table_idx
                }
                
                if actual_wikipedia_url:
                    logger.debug(f"🔗 Found event with link: {event_name} -> {actual_wikipedia_url}")
                else:
                    logger.debug(f"⚠️ No Wikipedia link found for: {event_name}")
                
                return event_data
            
        except Exception as e:
            logger.debug(f"⚠️ Error parsing event row {row_idx}: {str(e)}")
            return None
    
    def parse_date_robust(self, date_str):
        """Parse date string with multiple format attempts"""
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
            '%m-%d-%Y',
            '%d %B %Y',
            '%d %b %Y'
        ]
        
        for fmt in date_formats:
            try:
                from datetime import datetime
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.isoformat()
            except ValueError:
                continue
        
        return None
    
    def process_single_event_robust(self, event_data):
        """Process a single event with ultra robust error handling and retries"""
        event_name = event_data['name']
        wikipedia_url = event_data['wikipedia_url']
        
        # Retry logic for failed events
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Step 1: Scrape fighter data using the actual Wikipedia URL
                fights_data = self.scrape_event_fighters_robust(wikipedia_url, event_name)
                
                if not fights_data:
                    if attempt < max_retries - 1:
                        logger.warning(f"⚠️ No fights found for {event_name}, retrying... (attempt {attempt + 1})")
                        time.sleep(2)  # Wait before retry
                        continue
                    else:
                        with self.lock:
                            self.failed_events += 1
                            self.processed_events += 1
                        return f"❌ No fights found for: {event_name}"
                
                # Step 2: Create event in database
                event_id = self.create_event_robust(event_data)
                
                if not event_id:
                    if attempt < max_retries - 1:
                        logger.warning(f"⚠️ Failed to create event {event_name}, retrying... (attempt {attempt + 1})")
                        time.sleep(2)
                        continue
                    else:
                        with self.lock:
                            self.failed_events += 1
                            self.processed_events += 1
                        return f"❌ Failed to create event: {event_name}"
                
                # Step 3: Create fights in database
                created_fights = 0
                for fight_data in fights_data:
                    fight_id = self.create_fight_robust(fight_data, event_id)
                    if fight_id:
                        created_fights += 1
                
                # Update counters thread-safely
                with self.lock:
                    self.successful_events += 1
                    self.total_fights += created_fights
                    self.processed_events += 1
                
                return f"✅ {event_name}: {created_fights}/{len(fights_data)} fights created"
                
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"⚠️ Error processing {event_name}, retrying... (attempt {attempt + 1}): {str(e)}")
                    time.sleep(2)
                    continue
                else:
                    with self.lock:
                        self.failed_events += 1
                        self.processed_events += 1
                    return f"❌ Error processing {event_name}: {str(e)}"
    
    def scrape_event_fighters_robust(self, url, event_name):
        """Scrape fighter data from a UFC event page with enhanced detection"""
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            all_tables = soup.find_all('table')
            
            fights_data = []
            
            for table_idx, table in enumerate(all_tables):
                # Enhanced fight detection
                table_text = table.get_text()
                fight_indicators = ['def.', 'defeated', 'winner', 'loser', 'ko', 'submission', 'decision']
                
                if any(indicator in table_text.lower() for indicator in fight_indicators):
                    # Parse this table for fights
                    table_fights = self._parse_fight_table_ultra_robust(table)
                    if table_fights:
                        fights_data.extend(table_fights)
            
            return fights_data
            
        except Exception as e:
            logger.error(f"❌ Error scraping {url}: {str(e)}")
            return []
    
    def _parse_fight_table_ultra_robust(self, table):
        """Parse a fight table with ultra robust detection"""
        fights = []
        
        rows = table.find_all('tr')
        
        for row_idx, row in enumerate(rows):
            try:
                # Skip header rows
                if row.find('th'):
                    continue
                
                cells = row.find_all('td')
                
                # Need at least 4 cells for a basic fight row
                if len(cells) >= 4:
                    # Try multiple parsing strategies
                    fight_data = self._parse_fight_row_robust(cells)
                    if fight_data:
                        fights.append(fight_data)
                
            except Exception as e:
                logger.debug(f"⚠️ Error parsing fight row {row_idx}: {str(e)}")
                continue
        
        return fights
    
    def _parse_fight_row_robust(self, cells):
        """Parse a single fight row with multiple strategies"""
        try:
            # Strategy 1: Standard format (Weight Class, Winner, def., Loser, Method, Round, Time)
            if len(cells) >= 7:
                weight_class = cells[0].get_text(strip=True)
                winner = cells[1].get_text(strip=True)
                def_text = cells[2].get_text(strip=True)
                loser = cells[3].get_text(strip=True)
                method = cells[4].get_text(strip=True)
                round_num = cells[5].get_text(strip=True)
                time = cells[6].get_text(strip=True)
                
                # Verify this is a fight row (has "def.")
                if def_text.strip() == 'def.':
                    return {
                        'weight_class': weight_class,
                        'winner': winner,
                        'loser': loser,
                        'method': method,
                        'round': round_num,
                        'time': time
                    }
            
            # Strategy 2: Alternative format (Winner vs Loser in single cell)
            if len(cells) >= 3:
                for cell in cells:
                    cell_text = cell.get_text(strip=True)
                    if ' vs ' in cell_text or ' def. ' in cell_text:
                        # Parse winner vs loser
                        if ' def. ' in cell_text:
                            parts = cell_text.split(' def. ')
                            if len(parts) == 2:
                                winner = parts[0].strip()
                                loser = parts[1].strip()
                                return {
                                    'weight_class': 'Unknown',
                                    'winner': winner,
                                    'loser': loser,
                                    'method': 'Unknown',
                                    'round': 'Unknown',
                                    'time': 'Unknown'
                                }
                        elif ' vs ' in cell_text:
                            parts = cell_text.split(' vs ')
                            if len(parts) == 2:
                                winner = parts[0].strip()
                                loser = parts[1].strip()
                                return {
                                    'weight_class': 'Unknown',
                                    'winner': winner,
                                    'loser': loser,
                                    'method': 'Unknown',
                                    'round': 'Unknown',
                                    'time': 'Unknown'
                                }
            
            return None
            
        except Exception as e:
            logger.debug(f"⚠️ Error parsing fight row: {str(e)}")
            return None
    
    def get_or_create_fighter_robust(self, fighter_name):
        """Get or create a fighter with robust error handling"""
        try:
            # Clean fighter name
            fighter_name = self.clean_fighter_name_robust(fighter_name)
            if not fighter_name:
                return None
            
            # First, try to get existing fighter
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/fighters?name=eq.{fighter_name}",
                headers=self.supabase_headers,
                timeout=10
            )
            
            if response.status_code == 200:
                existing_fighters = response.json()
                if existing_fighters:
                    return existing_fighters[0]['id']
            
            # Create new fighter
            fighter_data = {
                'name': fighter_name,
                'weight_class': None,
                'record': None,
                'ufc_ranking': None
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/fighters",
                headers=self.supabase_headers,
                json=fighter_data,
                timeout=10
            )
            
            if response.status_code == 201:
                # Handle empty response body
                try:
                    return response.json()['id']
                except (ValueError, KeyError):
                    # If response is empty, try to get the fighter by name
                    fetch_response = requests.get(
                        f"{SUPABASE_URL}/rest/v1/fighters?name=eq.{fighter_name}",
                        headers=self.supabase_headers,
                        timeout=10
                    )
                    if fetch_response.status_code == 200:
                        fighters = fetch_response.json()
                        if fighters:
                            return fighters[0]['id']
                    return None
            else:
                return None
                
        except Exception as e:
            logger.debug(f"⚠️ Error getting/creating fighter {fighter_name}: {str(e)}")
            return None
    
    def clean_fighter_name_robust(self, fighter_name):
        """Clean fighter name with comprehensive patterns"""
        if not fighter_name:
            return None
        
        # Remove common artifacts
        patterns_to_remove = [
            r'\s*\([^)]*\)',  # Remove parentheses and content
            r'\s*\[[^\]]*\]',  # Remove brackets and content
            r'\s*def\.\s*',    # Remove "def."
            r'\s*vs\.\s*',     # Remove "vs."
            r'\s*winner\s*',   # Remove "winner"
            r'\s*loser\s*',    # Remove "loser"
            r'\s*ko\s*',       # Remove "ko"
            r'\s*submission\s*', # Remove "submission"
            r'\s*decision\s*', # Remove "decision"
            r'\s*round\s*\d+', # Remove "round X"
            r'\s*\d+:\d+',     # Remove time stamps
            r'\s*\(\d+\)',     # Remove numbers in parentheses
            r'\s*#\d+',        # Remove ranking numbers
            r'\s*champion\s*', # Remove "champion"
            r'\s*contender\s*', # Remove "contender"
        ]
        
        cleaned_name = fighter_name.strip()
        for pattern in patterns_to_remove:
            cleaned_name = re.sub(pattern, '', cleaned_name, flags=re.IGNORECASE)
        
        # Final cleanup
        cleaned_name = re.sub(r'\s+', ' ', cleaned_name).strip()
        
        return cleaned_name if cleaned_name else None
    
    def create_event_robust(self, event_data):
        """Create an event with robust error handling"""
        try:
            event_to_create = {
                'name': event_data['name'],
                'date': event_data['date'],
                'venue': event_data['venue'],
                'location': event_data['location']
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/events",
                headers=self.supabase_headers,
                json=event_to_create,
                timeout=10
            )
            
            if response.status_code == 201:
                # Handle empty response body
                try:
                    return response.json()['id']
                except (ValueError, KeyError):
                    # If response is empty, try to get the event by name
                    fetch_response = requests.get(
                        f"{SUPABASE_URL}/rest/v1/events?name=eq.{event_data['name']}",
                        headers=self.supabase_headers,
                        timeout=10
                    )
                    if fetch_response.status_code == 200:
                        events = fetch_response.json()
                        if events:
                            return events[0]['id']
                    return None
            else:
                return None
                
        except Exception as e:
            logger.debug(f"⚠️ Error creating event {event_data['name']}: {str(e)}")
            return None
    
    def create_fight_robust(self, fight_data, event_id):
        """Create a fight with robust error handling"""
        try:
            # Get or create fighters
            winner_id = self.get_or_create_fighter_robust(fight_data['winner'])
            loser_id = self.get_or_create_fighter_robust(fight_data['loser'])
            
            if not winner_id or not loser_id:
                return None
            
            # Create fight
            fight_to_create = {
                'event_id': event_id,
                'fighter1_id': winner_id,
                'fighter2_id': loser_id,
                'weight_class': fight_data['weight_class'],
                'status': 'completed',
                'result': {
                    'winner_id': winner_id,
                    'method': fight_data['method'],
                    'round': fight_data['round'],
                    'time': fight_data['time']
                }
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/fights",
                headers=self.supabase_headers,
                json=fight_to_create,
                timeout=10
            )
            
            if response.status_code == 201:
                # Handle empty response body
                try:
                    return response.json()['id']
                except (ValueError, KeyError):
                    # If response is empty, try to get the fight by event and fighters
                    fetch_response = requests.get(
                        f"{SUPABASE_URL}/rest/v1/fights?event_id=eq.{event_id}&fighter1_id=eq.{winner_id}&fighter2_id=eq.{loser_id}",
                        headers=self.supabase_headers,
                        timeout=10
                    )
                    if fetch_response.status_code == 200:
                        fights = fetch_response.json()
                        if fights:
                            return fights[0]['id']
                    return None
            else:
                return None
                
        except Exception as e:
            logger.debug(f"⚠️ Error creating fight: {str(e)}")
            return None
    
    def run_ultra_robust_scraper(self, max_events=None, start_from=0):
        """Run the ultra robust scraper"""
        logger.info("🚀 Starting Ultra Robust Scraper")
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
                executor.submit(self.process_single_event_robust, event): event 
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
                        logger.info(f"   🎯 Total fights: {self.total_fights}")
                        logger.info(f"   ⚡ Events/sec: {events_per_second:.2f}")
                        logger.info(f"   ⏱️ Estimated remaining time: {remaining_time/60:.1f} minutes")
                        
                except Exception as e:
                    logger.error(f"❌ Exception processing {event['name']}: {str(e)}")
                    with self.lock:
                        self.failed_events += 1
                        self.processed_events += 1
        
        # Final Summary
        total_time = time.time() - start_time
        events_per_second = len(events) / total_time if total_time > 0 else 0
        
        logger.info(f"\n📊 ULTRA ROBUST SCRAPING SUMMARY")
        logger.info("=" * 60)
        logger.info(f"✅ Successful events: {self.successful_events}/{len(events)}")
        logger.info(f"❌ Failed events: {self.failed_events}/{len(events)}")
        logger.info(f"🎯 Total fights created: {self.total_fights}")
        logger.info(f"📊 Average fights per successful event: {self.total_fights/self.successful_events if self.successful_events > 0 else 0:.1f}")
        logger.info(f"⚡ Processing speed: {events_per_second:.2f} events/second")
        logger.info(f"⏱️ Total time: {total_time/60:.1f} minutes")

if __name__ == "__main__":
    # Create ultra robust scraper with 8 workers for stability
    scraper = UltraRobustScraper(max_workers=8)
    
    # Test with a small number first, then run full scale
    scraper.run_ultra_robust_scraper(max_events=50, start_from=0) 