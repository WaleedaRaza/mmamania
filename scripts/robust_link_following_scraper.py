#!/usr/bin/env python3
"""
Robust Link Following Scraper
Extracts actual Wikipedia links from the table and uses them for scraping
"""

import os
import requests
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import logging
import time
import json

load_dotenv('scripts/.env')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

class RobustLinkFollowingScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.supabase_headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
        }
        self.base_url = "https://en.wikipedia.org"
    
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
                            
                            if actual_wikipedia_url:
                                logger.info(f"🔗 Found event with link: {event_name} -> {actual_wikipedia_url}")
                            else:
                                logger.warning(f"⚠️ No Wikipedia link found for: {event_name}")
                            
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
                from datetime import datetime
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.isoformat()
            except ValueError:
                continue
        
        return None
    
    def scrape_event_fighters(self, url, event_name):
        """Scrape fighter data from a UFC event page"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all tables
            all_tables = soup.find_all('table')
            
            fights_data = []
            
            for table_idx, table in enumerate(all_tables):
                # Look for tables with "def." patterns
                table_text = table.get_text()
                if 'def.' in table_text:
                    # Parse this table for fights
                    table_fights = self._parse_fight_table(table)
                    if table_fights:
                        fights_data.extend(table_fights)
            
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
    
    def get_or_create_fighter(self, fighter_name):
        """Get or create a fighter in the database"""
        try:
            # First, try to get existing fighter
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/fighters?name=eq.{fighter_name}",
                headers=self.supabase_headers
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
                json=fighter_data
            )
            
            if response.status_code == 201:
                # Handle empty response body
                try:
                    return response.json()['id']
                except (ValueError, KeyError):
                    # If response is empty, try to get the fighter by name
                    fetch_response = requests.get(
                        f"{SUPABASE_URL}/rest/v1/fighters?name=eq.{fighter_name}",
                        headers=self.supabase_headers
                    )
                    if fetch_response.status_code == 200:
                        fighters = fetch_response.json()
                        if fighters:
                            return fighters[0]['id']
                    return None
            else:
                logger.error(f"❌ Failed to create fighter {fighter_name}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error with fighter {fighter_name}: {str(e)}")
            return None
    
    def create_event(self, event_data):
        """Create an event in the database"""
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
                json=event_to_create
            )
            
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
                logger.error(f"❌ Failed to create event {event_data['name']}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error creating event {event_data['name']}: {str(e)}")
            return None
    
    def create_fight(self, fight_data, event_id):
        """Create a fight in the database"""
        try:
            # Get or create fighters
            winner_id = self.get_or_create_fighter(fight_data['winner'])
            loser_id = self.get_or_create_fighter(fight_data['loser'])
            
            if not winner_id or not loser_id:
                logger.error(f"❌ Failed to get/create fighters for fight")
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
                json=fight_to_create
            )
            
            if response.status_code == 201:
                # Handle empty response body
                try:
                    return response.json()['id']
                except (ValueError, KeyError):
                    # If response is empty, try to get the fight by event and fighters
                    fetch_response = requests.get(
                        f"{SUPABASE_URL}/rest/v1/fights?event_id=eq.{event_id}&fighter1_id=eq.{winner_id}&fighter2_id=eq.{loser_id}",
                        headers=self.supabase_headers
                    )
                    if fetch_response.status_code == 200:
                        fights = fetch_response.json()
                        if fights:
                            return fights[0]['id']
                    return None
            else:
                logger.error(f"❌ Failed to create fight: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error creating fight: {str(e)}")
            return None
    
    def run_robust_scraper(self, max_events=None, start_from=0):
        """Run the robust scraper using actual Wikipedia links"""
        logger.info("🚀 Starting Robust Link Following Scraper")
        logger.info("=" * 50)
        
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
        
        logger.info(f"📊 Processing {len(events)} events (starting from event {start_from})")
        
        total_fights = 0
        successful_events = 0
        failed_events = 0
        
        for i, event in enumerate(events, 1):
            logger.info(f"\n🔍 Processing event {i}/{len(events)}: {event['name']}")
            
            # Check if we have a Wikipedia URL
            if not event['wikipedia_url']:
                logger.warning(f"⚠️ No Wikipedia URL for: {event['name']}")
                failed_events += 1
                continue
            
            # Step 2: Scrape fighter data using the actual Wikipedia URL
            fights_data = self.scrape_event_fighters(event['wikipedia_url'], event['name'])
            
            if fights_data:
                logger.info(f"✅ Found {len(fights_data)} fights")
                
                # Step 3: Create event in database
                event_id = self.create_event(event)
                
                if event_id:
                    logger.info(f"✅ Created event in database: {event_id}")
                    
                    # Step 4: Create fights in database
                    created_fights = 0
                    for fight_data in fights_data:
                        fight_id = self.create_fight(fight_data, event_id)
                        if fight_id:
                            created_fights += 1
                    
                    logger.info(f"✅ Created {created_fights}/{len(fights_data)} fights in database")
                    total_fights += created_fights
                    successful_events += 1
                else:
                    logger.error(f"❌ Failed to create event: {event['name']}")
                    failed_events += 1
            else:
                logger.warning(f"⚠️ No fights found for: {event['name']}")
                failed_events += 1
            
            # Add delay to be respectful to Wikipedia
            time.sleep(1)
            
            # Progress update every 10 events
            if i % 10 == 0:
                logger.info(f"📊 Progress: {i}/{len(events)} events processed")
                logger.info(f"✅ Successful: {successful_events}, ❌ Failed: {failed_events}")
                logger.info(f"🎯 Total fights: {total_fights}")
        
        # Final Summary
        logger.info(f"\n📊 ROBUST SCRAPING SUMMARY")
        logger.info("=" * 50)
        logger.info(f"✅ Successful events: {successful_events}/{len(events)}")
        logger.info(f"❌ Failed events: {failed_events}/{len(events)}")
        logger.info(f"🎯 Total fights created: {total_fights}")
        logger.info(f"📊 Average fights per successful event: {total_fights/successful_events if successful_events > 0 else 0:.1f}")

if __name__ == "__main__":
    scraper = RobustLinkFollowingScraper()
    # Test with a small number first
    scraper.run_robust_scraper(max_events=10, start_from=0) 