#!/usr/bin/env python3
"""
Verify Past Events Data Script
Comprehensive verification of past events, fights, and winner/loser data in Supabase
"""

import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

class PastEventsVerifier:
    def __init__(self):
        self.supabase_url = SUPABASE_URL
        self.headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
        }
    
    def verify_events(self):
        """Verify events are properly created"""
        print("📊 Verifying Events...")
        print("=" * 50)
        
        try:
            response = requests.get(
                f"{self.supabase_url}/rest/v1/events?select=id,name,date,venue,location,status&order=date.desc",
                headers=self.headers
            )
            
            if response.status_code == 200:
                events = response.json()
                print(f"✅ Found {len(events)} events in database")
                print()
                
                for event in events:
                    print(f"📅 {event['name']}")
                    print(f"   📍 {event['venue']}, {event['location']}")
                    print(f"   📅 {event['date']}")
                    print(f"   📊 Status: {event['status']}")
                    print()
            else:
                print(f"❌ Error getting events: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error verifying events: {e}")
    
    def verify_fighters(self):
        """Verify fighters are properly created"""
        print("👊 Verifying Fighters...")
        print("=" * 50)
        
        try:
            response = requests.get(
                f"{self.supabase_url}/rest/v1/fighters?select=id,name,weight_class,is_active&order=name.asc",
                headers=self.headers
            )
            
            if response.status_code == 200:
                fighters = response.json()
                print(f"✅ Found {len(fighters)} fighters in database")
                print()
                
                # Group fighters by weight class
                weight_classes = {}
                for fighter in fighters:
                    weight_class = fighter.get('weight_class', 'Unknown')
                    if weight_class not in weight_classes:
                        weight_classes[weight_class] = []
                    weight_classes[weight_class].append(fighter['name'])
                
                for weight_class, names in weight_classes.items():
                    print(f"🏆 {weight_class}: {len(names)} fighters")
                    for name in names[:5]:  # Show first 5
                        print(f"   👊 {name}")
                    if len(names) > 5:
                        print(f"   ... and {len(names) - 5} more")
                    print()
            else:
                print(f"❌ Error getting fighters: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error verifying fighters: {e}")
    
    def verify_fights(self):
        """Verify fights are properly created with winner/loser data"""
        print("🥊 Verifying Fights...")
        print("=" * 50)
        
        try:
            # Get all fights with event and fighter details
            response = requests.get(
                f"{self.supabase_url}/rest/v1/fights?select=id,event_id,weight_class,result&order=created_at.desc",
                headers=self.headers
            )
            
            if response.status_code == 200:
                fights = response.json()
                print(f"✅ Found {len(fights)} fights in database")
                print()
                
                # Group fights by event
                event_fights = {}
                for fight in fights:
                    event_id = fight['event_id']
                    if event_id not in event_fights:
                        event_fights[event_id] = []
                    event_fights[event_id].append(fight)
                
                # Get event names
                events_response = requests.get(
                    f"{self.supabase_url}/rest/v1/events?select=id,name",
                    headers=self.headers
                )
                events_map = {}
                if events_response.status_code == 200:
                    events = events_response.json()
                    events_map = {event['id']: event['name'] for event in events}
                
                for event_id, event_fights_list in event_fights.items():
                    event_name = events_map.get(event_id, f"Event {event_id[:8]}")
                    print(f"📅 {event_name}: {len(event_fights_list)} fights")
                    
                    # Count fights with winners
                    fights_with_winners = [f for f in event_fights_list if f.get('winner_id')]
                    print(f"   ✅ {len(fights_with_winners)} fights with winners")
                    
                    # Show sample fights
                    for fight in event_fights_list[:3]:  # Show first 3
                        print(f"   🥊 {fight['weight_class']}: {fight['method']} (Round {fight['round']})")
                        if fight.get('winner_id'):
                            print(f"      🏆 Winner ID: {fight['winner_id']}")
                    print()
            else:
                print(f"❌ Error getting fights: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error verifying fights: {e}")
    
    def verify_winner_loser_data(self):
        """Verify winner/loser data is properly structured"""
        print("🏆 Verifying Winner/Loser Data...")
        print("=" * 50)
        
        try:
            # Get fights with fighter details
            response = requests.get(
                f"{self.supabase_url}/rest/v1/fights?select=id,fighter1_id,fighter2_id,result&limit=10",
                headers=self.headers
            )
            
            if response.status_code == 200:
                fights = response.json()
                print(f"✅ Checking {len(fights)} fights for winner/loser data")
                print()
                
                for fight in fights:
                    print(f"🥊 Fight {fight['id'][:8]}...")
                    
                    # Check winner_id from result object
                    result = fight.get('result', {})
                    winner_id = result.get('winner_id') if isinstance(result, dict) else None
                    if winner_id:
                        print(f"   ✅ Has winner_id: {winner_id}")
                    else:
                        print(f"   ❌ No winner_id")
                    
                    # Check result object
                    result = fight.get('result')
                    if result and isinstance(result, dict):
                        print(f"   ✅ Has result object with {len(result)} fields")
                        if 'winner_id' in result:
                            print(f"      🏆 Result winner_id: {result['winner_id']}")
                        if 'method' in result:
                            print(f"      📋 Method: {result['method']}")
                    else:
                        print(f"   ❌ No result object or invalid format")
                    
                    print()
            else:
                print(f"❌ Error getting fights: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error verifying winner/loser data: {e}")
    
    def verify_event_fight_distribution(self):
        """Verify fights are properly distributed across events"""
        print("📊 Verifying Event-Fight Distribution...")
        print("=" * 50)
        
        try:
            # Get events with fight counts
            response = requests.get(
                f"{self.supabase_url}/rest/v1/events?select=id,name,date",
                headers=self.headers
            )
            
            if response.status_code == 200:
                events = response.json()
                print(f"✅ Found {len(events)} events")
                print()
                
                for event in events:
                    # Get fights for this event
                    fights_response = requests.get(
                        f"{self.supabase_url}/rest/v1/fights?event_id=eq.{event['id']}&select=id,weight_class,winner_id",
                        headers=self.headers
                    )
                    
                    if fights_response.status_code == 200:
                        fights = fights_response.json()
                        fights_with_winners = [f for f in fights if f.get('result', {}).get('winner_id')]
                        
                        print(f"📅 {event['name']}")
                        print(f"   📊 Total fights: {len(fights)}")
                        print(f"   🏆 Fights with winners: {len(fights_with_winners)}")
                        
                        # Show weight classes
                        weight_classes = set(f['weight_class'] for f in fights)
                        print(f"   🏆 Weight classes: {', '.join(weight_classes)}")
                        print()
            else:
                print(f"❌ Error getting events: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error verifying event distribution: {e}")
    
    def verify_sample_fight_details(self):
        """Show detailed sample of a few fights"""
        print("🔍 Sample Fight Details...")
        print("=" * 50)
        
        try:
            # Get a few fights with all details
            response = requests.get(
                f"{self.supabase_url}/rest/v1/fights?select=id,event_id,weight_class,result&limit=5",
                headers=self.headers
            )
            
            if response.status_code == 200:
                fights = response.json()
                
                for fight in fights:
                    print(f"🥊 Fight {fight['id'][:8]}...")
                    print(f"   🏆 Weight Class: {fight['weight_class']}")
                    
                    result = fight.get('result', {})
                    if isinstance(result, dict):
                        print(f"   📋 Method: {result.get('method', 'Unknown')}")
                        print(f"   ⏰ Round: {result.get('round', 'Unknown')}, Time: {result.get('time', 'Unknown')}")
                        print(f"   🏆 Winner ID: {result.get('winner_id', 'None')}")
                    else:
                        print(f"   ❌ No result object")
                    
                    # Show result object
                    result = fight.get('result')
                    if result:
                        print(f"   📊 Result object: {json.dumps(result, indent=6)}")
                    else:
                        print(f"   ❌ No result object")
                    print()
            else:
                print(f"❌ Error getting fight details: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error getting sample fight details: {e}")
    
    def run_comprehensive_verification(self):
        """Run all verification checks"""
        print("🚀 Starting Comprehensive Past Events Data Verification")
        print("=" * 60)
        print()
        
        # Run all verification methods
        self.verify_events()
        self.verify_fighters()
        self.verify_fights()
        self.verify_winner_loser_data()
        self.verify_event_fight_distribution()
        self.verify_sample_fight_details()
        
        print("=" * 60)
        print("✅ Comprehensive verification complete!")
        print("🎯 If all checks passed, the data is ready for Flutter integration!")

def main():
    verifier = PastEventsVerifier()
    verifier.run_comprehensive_verification()

if __name__ == "__main__":
    main() 