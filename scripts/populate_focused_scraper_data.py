#!/usr/bin/env python3
"""
Populate Supabase from Focused Scraper Data
Takes the focused scraper data and populates it into Supabase database
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('scripts/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

class FocusedDataPopulator:
    def __init__(self):
        self.supabase_url = SUPABASE_URL
        self.headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
        }
    
    def get_or_create_fighter(self, name: str) -> str:
        """Get or create a fighter and return their ID"""
        if not name:
            return None
            
        # First try to find existing fighter
        response = requests.get(
            f"{self.supabase_url}/rest/v1/fighters?name=eq.{name}&select=id",
            headers=self.headers
        )
        
        if response.status_code == 200 and response.json():
            return response.json()[0]['id']
        
        # Create new fighter
        fighter_data = {
            'name': name,
            'weight_class': None,  # Will be updated from fight data
            'record': None,
            'ufc_ranking': None
        }
        
        response = requests.post(
            f"{self.supabase_url}/rest/v1/fighters",
            headers=self.headers,
            json=fighter_data
        )
        
        if response.status_code == 201:
            return response.json()['id']
        else:
            print(f"❌ Error creating fighter {name}: {response.status_code} - {response.text}")
            return None
    
    def create_event(self, event_name: str, event_url: str, date: str = None) -> str:
        """Create an event and return its ID"""
        event_data = {
            'name': event_name,
            'date': date,
            'venue': None,
            'location': None
        }
        
        response = requests.post(
            f"{self.supabase_url}/rest/v1/events",
            headers=self.headers,
            json=event_data
        )
        
        if response.status_code == 201:
            return response.json()['id']
        else:
            print(f"❌ Error creating event {event_name}: {response.status_code} - {response.text}")
            return None
    
    def create_fight(self, event_id: str, fighter1_id: str, fighter2_id: str, 
                    weight_class: str, winner_id: str = None, method: str = None, 
                    round_num: str = None, time: str = None) -> bool:
        """Create a fight record"""
        fight_data = {
            'event_id': event_id,
            'fighter_a_id': fighter1_id,
            'fighter_b_id': fighter2_id,
            'weight_class': weight_class,
            'winner_id': winner_id,
            'result': {
                'method': method,
                'round': round_num,
                'time': time,
                'winner_id': winner_id
            }
        }
        
        response = requests.post(
            f"{self.supabase_url}/rest/v1/fights",
            headers=self.headers,
            json=fight_data
        )
        
        if response.status_code == 201:
            return True
        else:
            print(f"❌ Error creating fight: {response.status_code} - {response.text}")
            return False
    
    def populate_from_focused_scraper(self, json_file_path: str):
        """Populate database from focused scraper data"""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                events_data = json.load(f)
            
            print(f"📊 Found {len(events_data)} events to populate")
            
            total_fights = 0
            successful_events = 0
            
            for event in events_data:
                event_name = event.get('event_name')
                event_url = event.get('event_url')
                fights = event.get('fights', [])
                
                if not fights:
                    continue
                
                print(f"\n📅 Processing {event_name} with {len(fights)} fights")
                
                # Create event
                event_id = self.create_event(event_name, event_url)
                if not event_id:
                    continue
                
                event_fights = 0
                
                for fight in fights:
                    fighter1_name = fight.get('fighter1')
                    fighter2_name = fight.get('fighter2')
                    weight_class = fight.get('weight_class')
                    winner_name = fight.get('winner')
                    method = fight.get('method')
                    round_num = fight.get('round')
                    time = fight.get('time')
                    
                    if not fighter1_name or not fighter2_name:
                        continue
                    
                    # Get or create fighters
                    fighter1_id = self.get_or_create_fighter(fighter1_name)
                    fighter2_id = self.get_or_create_fighter(fighter2_name)
                    
                    if not fighter1_id or not fighter2_id:
                        continue
                    
                    # Determine winner ID
                    winner_id = None
                    if winner_name:
                        if winner_name == fighter1_name:
                            winner_id = fighter1_id
                        elif winner_name == fighter2_name:
                            winner_id = fighter2_id
                    
                    # Create fight
                    if self.create_fight(event_id, fighter1_id, fighter2_id, 
                                       weight_class, winner_id, method, round_num, time):
                        event_fights += 1
                        total_fights += 1
                
                if event_fights > 0:
                    successful_events += 1
                    print(f"✅ Successfully created {event_fights} fights for {event_name}")
            
            print(f"\n🎉 Population complete!")
            print(f"📊 Events processed: {successful_events}")
            print(f"🥊 Total fights created: {total_fights}")
            
        except Exception as e:
            print(f"❌ Error populating data: {e}")

def main():
    """Main function to populate data"""
    # Use the latest focused scraper data file
    json_file_path = "data/exports/focused_ufc_events_20250804_163847.json"
    
    populator = FocusedDataPopulator()
    populator.populate_from_focused_scraper(json_file_path)

if __name__ == "__main__":
    main() 