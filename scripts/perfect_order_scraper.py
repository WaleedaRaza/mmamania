#!/usr/bin/env python3
"""
Perfect Order Scraper
Scrapes UFC events with perfect fight ordering
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

load_dotenv('.env')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

class PerfectOrderScraper:
    def __init__(self, max_workers=5):
        self.max_workers = max_workers
        self.base_url = "https://en.wikipedia.org"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        self.supabase_headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
        }
        self.lock = Lock()

    def get_all_past_events_with_actual_links(self):
        """Get all past UFC events with their Wikipedia links"""
        try:
            logger.info("🔍 Loading main UFC events page: https://en.wikipedia.org/wiki/List_of_UFC_events")
            response = requests.get("https://en.wikipedia.org/wiki/List_of_UFC_events", headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            logger.info("✅ Successfully loaded main UFC events page")
            
            # Find all tables
            tables = soup.find_all('table')
            logger.info(f"📊 Found {len(tables)} total tables on page")
            
            # Find the Past events table
            past_events_table = None
            for table in tables:
                if 'Past events' in table.get_text():
                    past_events_table = table
                    break
            
            if not past_events_table:
                logger.error("❌ Could not find Past events table")
                return []
            
            logger.info("✅ Found Past events table")
            
            # Extract all UFC event links
            ufc_links = []
            rows = past_events_table.find_all('tr')
            logger.info(f"📊 Found {len(rows)} total rows in Past events table")
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    # Look for UFC references
                    cell_text = row.get_text()
                    if 'UFC' in cell_text:
                        # Find all links in this row
                        links = row.find_all('a')
                        for link in links:
                            href = link.get('href')
                            if href and '/wiki/UFC_' in href:
                                event_name = link.get_text(strip=True)
                                event_url = urljoin(self.base_url, href)
                                ufc_links.append({
                                    'name': event_name,
                                    'url': event_url
                                })
            
            logger.info(f"📊 Found {len(ufc_links)} UFC events with links")
            return ufc_links
            
        except Exception as e:
            logger.error(f"❌ Error getting UFC events: {e}")
            return []

    def parse_date(self, date_str):
        """Parse date string to datetime object"""
        try:
            # Remove extra whitespace and newlines
            date_str = re.sub(r'\s+', ' ', date_str.strip())
            
            # Try different date formats
            date_formats = [
                '%B %d, %Y',
                '%B %d %Y',
                '%d %B %Y',
                '%Y-%m-%d'
            ]
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_str, fmt)
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
            event_name = event_data['name']
            event_url = event_data['url']
            
            logger.info(f"🔍 Processing event: {event_name}")
            
            # Get event info
            event_info = self.get_event_info(event_url)
            if not event_info:
                logger.warning(f"⚠️ Could not get event info for {event_name}")
                return False
            
            # Create event in database
            event_id = self.create_event(event_data, event_info)
            if not event_id:
                logger.error(f"❌ Failed to create event: {event_name}")
                return False
            
            # Scrape fights with perfect ordering
            fights = self.scrape_event_fights_perfect_order(event_url, event_name)
            if not fights:
                logger.warning(f"⚠️ No fights found for {event_name}")
                return True  # Event created but no fights
            
            # Create fights in database
            created_fights = 0
            for fight_data in fights:
                if self.create_fight_with_winner_loser(fight_data, event_id):
                    created_fights += 1
            
            logger.info(f"✅ Event {event_name}: {created_fights}/{len(fights)} fights created")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error processing event {event_data.get('name', 'Unknown')}: {e}")
            return False

    def get_event_info(self, url):
        """Extract event information from Wikipedia page"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract event details
            event_info = {
                'name': '',
                'date': None,
                'location': '',
                'venue': ''
            }
            
            # Look for event name in page title
            title = soup.find('title')
            if title:
                title_text = title.get_text()
                if 'UFC' in title_text:
                    event_info['name'] = title_text.replace(' - Wikipedia', '').strip()
            
            # Look for date and location in infobox
            infobox = soup.find('table', class_='infobox')
            if infobox:
                rows = infobox.find_all('tr')
                for row in rows:
                    cells = row.find_all(['th', 'td'])
                    if len(cells) >= 2:
                        label = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)
                        
                        if 'date' in label:
                            event_info['date'] = self.parse_date(value)
                        elif 'venue' in label or 'location' in label:
                            event_info['venue'] = value
                        elif 'city' in label:
                            event_info['location'] = value
            
            return event_info
            
        except Exception as e:
            logger.error(f"❌ Error getting event info from {url}: {e}")
            return None

    def scrape_event_fights_perfect_order(self, url, event_name):
        """Extract ALL fights from a UFC event page with PERFECT ordering"""
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
                if self._is_fight_table(table):
                    logger.info(f"✅ Found fight table #{table_idx + 1}")
                    
                    # Parse fights with global fight order
                    table_fights = self._parse_fight_table_perfect_order(table, global_fight_order)
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

    def _is_fight_table(self, table):
        """Check if table contains fight data"""
        try:
            # Look for weight class column header
            headers = table.find_all('th')
            for header in headers:
                if 'weight' in header.get_text().lower() or 'class' in header.get_text().lower():
                    return True
            
            # Look for "def." pattern in table content
            table_text = table.get_text()
            if 'def.' in table_text:
                return True
                
            return False
        except:
            return False

    def _parse_fight_table_perfect_order(self, table, global_fight_order):
        """Parse fight table with perfect global fight order"""
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
                    fight_data = self._parse_fight_row_perfect_order(cells, fight_order)
                    if fight_data:
                        fights.append(fight_data)
                        fight_order += 1  # Only increment if a valid fight was created
                except Exception as e:
                    logger.warning(f"⚠️ Error parsing fight row {row_idx}: {e}")
                    continue
        
        return fights

    def _parse_fight_row_perfect_order(self, cells, fight_order):
        """Parse a single fight row with perfect fight order"""
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
            
            # Perfect logic: first fight = main event, second fight = co-main
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
        except:
            return name.strip()

    def _clean_method_text(self, method):
        """Clean method text"""
        try:
            # Remove extra whitespace
            method = re.sub(r'\s+', ' ', method.strip())
            
            # Remove HTML entities
            method = method.replace('&nbsp;', ' ')
            
            return method.strip()
        except:
            return method.strip()

    def create_event(self, event_data, event_info):
        """Create event in Supabase"""
        try:
            event_payload = {
                'name': event_data['name'],
                'location': event_info.get('venue', 'Unknown'),
                'date': event_info.get('date').isoformat() if event_info.get('date') else None
            }
            
            logger.info(f"📝 Creating event: {event_data['name']}")
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/events",
                headers=self.supabase_headers,
                json=event_payload
            )
            
            if response.status_code == 201:
                # Supabase returns empty response, so we need to get the created event ID
                logger.info(f"✅ Created event: {event_data['name']}")
                
                # Get the created event by name
                get_response = requests.get(
                    f"{SUPABASE_URL}/rest/v1/events?name=eq.{event_data['name']}",
                    headers=self.supabase_headers
                )
                
                if get_response.status_code == 200:
                    events = get_response.json()
                    if events:
                        event_id = events[0]['id']
                        logger.info(f"✅ Event ID: {event_id}")
                        return event_id
                
                logger.error(f"❌ Could not get event ID for: {event_data['name']}")
                return None
            else:
                logger.error(f"❌ Error creating event: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error creating event: {e}")
            return None

    def create_fight_with_winner_loser(self, fight_data, event_id):
        """Create fight with winner/loser names in Supabase"""
        try:
            fight_payload = {
                'event_id': event_id,
                'weight_class': fight_data['weight_class'],
                'winner_name': fight_data['winner_name'],
                'loser_name': fight_data['loser_name'],
                'method': fight_data['method'],
                'round': fight_data['round'],
                'time': fight_data['time'],
                'fight_order': fight_data['fight_order'],
                'is_main_event': fight_data['is_main_event'],
                'is_co_main_event': fight_data['is_co_main_event'],
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
                logger.error(f"❌ Error creating fight: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating fight: {e}")
            return False

    def run_perfect_order_scraper(self, max_events=None, start_from=0):
        """Run the perfect order scraper"""
        logger.info("🚀 Starting PERFECT ORDER Wikipedia UFC Scraper")
        
        # Get all UFC events
        events = self.get_all_past_events_with_actual_links()
        if not events:
            logger.error("❌ No events found")
            return
        
        # Limit events if specified
        if max_events:
            events = events[start_from:start_from + max_events]
        
        logger.info(f"📊 Processing {len(events)} events (starting from {start_from})")
        
        successful_events = 0
        failed_events = 0
        total_fights = 0
        
        # Process events
        for event_data in events:
            logger.info(f"🔍 Processing event: {event_data['name']}")
            if self.process_single_event(event_data):
                successful_events += 1
            else:
                failed_events += 1
        
        logger.info("🎉 PERFECT ORDER SCRAPER COMPLETED!")
        logger.info(f"📊 Successful events: {successful_events}")
        logger.info(f"📊 Failed events: {failed_events}")
        logger.info(f"📊 Total fights: {total_fights}")

def main():
    scraper = PerfectOrderScraper()
    scraper.run_perfect_order_scraper(max_events=5, start_from=0)

if __name__ == "__main__":
    main() 