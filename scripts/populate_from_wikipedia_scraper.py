#!/usr/bin/env python3
"""
Populate Supabase from Wikipedia Scraper Data
Takes scraped Wikipedia data and populates it into Supabase database
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('scripts/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

class WikipediaDataPopulator:
    def __init__(self):
        self.supabase_url = SUPABASE_URL
        self.headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
        }
    
    def load_scraped_data(self, json_file_path: str) -> list:
        """Load scraped data from JSON file"""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ Loaded {len(data)} events from {json_file_path}")
            return data
        except Exception as e:
            print(f"❌ Error loading data from {json_file_path}: {e}")
            return []
    
    def get_or_create_fighter(self, fighter_name: str) -> str:
        """Get or create fighter in database"""
        try:
            # Check if fighter exists
            response = requests.get(
                f"{self.supabase_url}/rest/v1/fighters?name=eq.{fighter_name}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                fighters = response.json()
                if fighters:
                    return fighters[0]['id']
            
            # Create new fighter
            fighter_to_create = {
                'name': fighter_name,
                'weight_class': 'Unknown',
                'record': {'wins': 0, 'losses': 0, 'draws': 0},
                'is_active': 'Active'
            }
            
            response = requests.post(
                f"{self.supabase_url}/rest/v1/fighters",
                headers=self.headers,
                json=fighter_to_create
            )
            
            if response.status_code == 201:
                # Get the created fighter ID
                response = requests.get(
                    f"{self.supabase_url}/rest/v1/fighters?name=eq.{fighter_name}",
                    headers=self.headers
                )
                if response.status_code == 200:
                    fighters = response.json()
                    if fighters:
                        return fighters[0]['id']
            
            return None
            
        except Exception as e:
            print(f"Error with fighter {fighter_name}: {e}")
            return None
    
    def create_event(self, event_data: dict) -> str:
        """Create event in database"""
        try:
            event_to_create = {
                'name': event_data.get('title', 'Unknown Event'),
                'date': event_data.get('date'),
                'venue': event_data.get('venue'),
                'location': event_data.get('location'),
                'status': 'completed'
            }
            
            response = requests.post(
                f"{self.supabase_url}/rest/v1/events",
                headers=self.headers,
                json=event_to_create
            )
            
            if response.status_code == 201:
                # Get the created event ID
                response = requests.get(
                    f"{self.supabase_url}/rest/v1/events?name=eq.{event_data.get('title', 'Unknown Event')}",
                    headers=self.headers
                )
                if response.status_code == 200:
                    events = response.json()
                    if events:
                        return events[0]['id']
            
            return None
            
        except Exception as e:
            print(f"Error creating event {event_data.get('title', 'Unknown')}: {e}")
            return None
    
    def create_fight(self, fight_data: dict, event_id: str) -> bool:
        """Create fight in database with proper winner/loser data"""
        try:
            fighter1_id = self.get_or_create_fighter(fight_data['fighter1'])
            fighter2_id = self.get_or_create_fighter(fight_data['fighter2'])
            
            if not fighter1_id or not fighter2_id:
                print(f"Could not get/create fighters for {fight_data['fighter1']} vs {fight_data['fighter2']}")
                return False
            
            # Determine winner
            winner_id = None
            if fight_data.get('winner'):
                if fight_data['winner'] == fight_data['fighter1']:
                    winner_id = fighter1_id
                elif fight_data['winner'] == fight_data['fighter2']:
                    winner_id = fighter2_id
                elif fight_data['winner'] == 'Draw':
                    winner_id = None  # Draw - no winner
            
            fight_to_create = {
                'event_id': event_id,
                'fighter1_id': fighter1_id,
                'fighter2_id': fighter2_id,
                'status': 'completed',
                'result': {
                    'method': fight_data.get('method', 'Unknown'),
                    'round': fight_data.get('round'),
                    'time': fight_data.get('time'),
                    'winner_id': winner_id
                },
                'weight_class': fight_data.get('weight_class', 'Unknown')
            }
            
            response = requests.post(
                f"{self.supabase_url}/rest/v1/fights",
                headers=self.headers,
                json=fight_to_create
            )
            
            if response.status_code == 201:
                print(f"   ✅ {fight_data['fighter1']} vs {fight_data['fighter2']} -> {fight_data.get('winner', 'Unknown')} wins")
                return True
            else:
                print(f"   ❌ Failed to create fight: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error creating fight: {e}")
            return False
    
    def populate_from_scraped_data(self, json_file_path: str):
        """Populate database from scraped Wikipedia data"""
        print("🚀 Starting Wikipedia Data Population...")
        
        # Load scraped data
        events_data = self.load_scraped_data(json_file_path)
        if not events_data:
            print("❌ No data to populate")
            return
        
        total_events_created = 0
        total_fights_created = 0
        
        for event_data in events_data:
            event_info = event_data.get('event', {})
            fights = event_data.get('fights', [])
            
            print(f"\n📅 Processing: {event_info.get('title', 'Unknown Event')}")
            
            # Check if event already exists
            response = requests.get(
                f"{self.supabase_url}/rest/v1/events?name=eq.{event_info.get('title', 'Unknown Event')}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                events = response.json()
                if events:
                    event_id = events[0]['id']
                    print(f"   ✅ Event already exists: {event_info.get('title', 'Unknown Event')}")
                else:
                    # Create event
                    event_id = self.create_event(event_info)
                    if not event_id:
                        print(f"❌ Could not create event: {event_info.get('title', 'Unknown Event')}")
                        continue
                    total_events_created += 1
                    print(f"   ✅ Created event: {event_info.get('title', 'Unknown Event')}")
            else:
                # Create event
                event_id = self.create_event(event_info)
                if not event_id:
                    print(f"❌ Could not create event: {event_info.get('title', 'Unknown Event')}")
                    continue
                total_events_created += 1
                print(f"   ✅ Created event: {event_info.get('title', 'Unknown Event')}")
            
            # Check if fights already exist for this event
            fights_response = requests.get(
                f"{self.supabase_url}/rest/v1/fights?event_id=eq.{event_id}&select=id&limit=1",
                headers=self.headers
            )
            
            if fights_response.status_code == 200 and fights_response.json():
                print(f"   ⚠️  Fights already exist for {event_info.get('title', 'Unknown Event')}, skipping...")
                continue
            
            # Create fights for this event
            fights_created = 0
            for fight_data in fights:
                if self.create_fight(fight_data, event_id):
                    fights_created += 1
            
            total_fights_created += fights_created
            print(f"   📊 Created {fights_created} fights for {event_info.get('title', 'Unknown Event')}")
        
        print(f"\n🎉 Population complete!")
        print(f"   📊 Total events: {total_events_created}")
        print(f"   🥊 Total fights: {total_fights_created}")
        
        return total_events_created, total_fights_created
    
    def verify_population(self):
        """Verify the populated data"""
        print("\n🔍 Verifying populated data...")
        
        try:
            # Check events
            events_response = requests.get(
                f"{self.supabase_url}/rest/v1/events?select=id,name,date&order=date.desc&limit=10",
                headers=self.headers
            )
            if events_response.status_code == 200:
                events = events_response.json()
                print(f"   📊 Total events: {len(events)}")
                for event in events:
                    print(f"      ✅ {event['name']} ({event['date']})")
            
            # Check fights
            fights_response = requests.get(
                f"{self.supabase_url}/rest/v1/fights?select=id,event_id&limit=10",
                headers=self.headers
            )
            if fights_response.status_code == 200:
                fights = fights_response.json()
                print(f"   🥊 Total fights: {len(fights)}")
                
                # Group by event
                event_fights = {}
                for fight in fights:
                    event_id = fight['event_id']
                    if event_id not in event_fights:
                        event_fights[event_id] = 0
                    event_fights[event_id] += 1
                
                print(f"   📊 Fights per event:")
                for event_id, count in event_fights.items():
                    print(f"      Event {event_id[:8]}...: {count} fights")
            
        except Exception as e:
            print(f"❌ Error verifying population: {e}")
    
    def run_population(self, json_file_path: str):
        """Run the complete population process"""
        print("🚀 Starting Wikipedia Data Population")
        print("=" * 50)
        
        # Populate from scraped data
        events_created, fights_created = self.populate_from_scraped_data(json_file_path)
        
        # Verify population
        self.verify_population()
        
        print(f"\n✅ Population Complete!")
        print(f"   📊 Events: {events_created}")
        print(f"   🥊 Fights: {fights_created}")
        print(f"   🎯 Ready for Flutter app with comprehensive fight data!")

def main():
    # Use the newly created targeted scraper data file
    json_file_path = "data/exports/targeted_ufc_events_20250804_162210.json"
    
    populator = WikipediaDataPopulator()
    populator.run_population(json_file_path)

if __name__ == "__main__":
    main() 