#!/usr/bin/env python3
import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from threading import Lock
import logging

# Load environment variables
load_dotenv('.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkingWikipediaScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.supabase_headers = {
            'apikey': SUPABASE_SERVICE_KEY,
            'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
            'Content-Type': 'application/json',
        }
        self.lock = Lock()
        
    def scrape_event_fighters(self, url, event_name):
        """Scrape fighter data from a UFC event page"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            all_tables = soup.find_all('table')
            fights_data = []
            
            print(f"🔍 DEBUG: Scraping {url}")
            print(f"   Found {len(all_tables)} tables")
            
            for table_idx, table in enumerate(all_tables):
                table_text = table.get_text()
                print(f"   Table {table_idx}: {len(table_text)} chars")
                
                if any(indicator in table_text.lower() for indicator in ['def.', 'def', 'decision', 'ko', 'submission', 'tko']):
                    print(f"   Table {table_idx} contains fight data")
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
            if row.find('th'):
                continue
            
            cells = row.find_all('td')
            
            if len(cells) >= 7:
                try:
                    weight_class = cells[0].get_text(strip=True)
                    winner = cells[1].get_text(strip=True)
                    def_text = cells[2].get_text(strip=True)
                    loser = cells[3].get_text(strip=True)
                    method = cells[4].get_text(strip=True)
                    round_num = cells[5].get_text(strip=True)
                    time = cells[6].get_text(strip=True)
                    
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
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/events",
                headers=self.supabase_headers,
                json=event_to_create
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 201:
                try:
                    return response.json()['id']
                except (ValueError, KeyError):
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
            fight_to_create = {
                'event_id': event_id,
                'weight_class': fight_data['weight_class'],
                'status': 'completed',
                'result': {
                    'method': fight_data['method'],
                    'round': fight_data['round'],
                    'time': fight_data['time']
                },
                'fighter1_name': fight_data['winner'],
                'fighter2_name': fight_data['loser']
            }
            
            print(f"   Creating fight: {fight_data['winner']} vs {fight_data['loser']}")
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/fights",
                headers=self.supabase_headers,
                json=fight_to_create
            )
            
            print(f"   Fight creation response: {response.status_code}")
            print(f"   Response text: {response.text}")
            
            if response.status_code == 201:
                print(f"   ✅ Fight created successfully")
                try:
                    return response.json()['id']
                except (ValueError, KeyError):
                    return None
            else:
                print(f"   ❌ Failed to create fight: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Exception creating fight: {e}")
            return None
    
    def process_single_event(self, event_data):
        """Process a single event"""
        event_name = event_data['name']
        wikipedia_url = event_data['wikipedia_url']
        
        try:
            fights_data = self.scrape_event_fighters(wikipedia_url, event_name)
            
            if not fights_data:
                return f"❌ No fights found for: {event_name}"
            
            event_id = self.create_event(event_data)
            
            if not event_id:
                return f"❌ Failed to create event: {event_name}"
            
            created_fights = 0
            for fight_data in fights_data:
                fight_id = self.create_fight_with_names(fight_data, event_id, event_name)
                if fight_id:
                    created_fights += 1
            
            return f"✅ {event_name}: {created_fights}/{len(fights_data)} fights created"
            
        except Exception as e:
            return f"❌ Error processing {event_name}: {str(e)}"

def main():
    scraper = WorkingWikipediaScraper()
    
    # Test with a single event
    test_event = {
        'name': 'UFC on ESPN: Taira vs. Park',
        'date': 'August 2, 2025',
        'venue': 'UFC Apex',
        'location': 'Enterprise, Nevada, United States',
        'wikipedia_url': 'https://en.wikipedia.org/wiki/UFC_on_ESPN:_Taira_vs._Park'
    }
    
    result = scraper.process_single_event(test_event)
    print(result)

if __name__ == "__main__":
    main()
