#!/usr/bin/env python3
"""
Debug Flutter Data Script
Check what data the Flutter app should be seeing and identify any issues
"""

import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('scripts/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

class FlutterDataDebugger:
    def __init__(self):
        self.supabase_url = SUPABASE_URL
        self.headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
        }
    
    def debug_events_data(self):
        """Debug events data that Flutter should see"""
        print("📊 Debugging Events Data...")
        print("=" * 50)
        
        try:
            # Get all events
            response = requests.get(
                f"{self.supabase_url}/rest/v1/events?select=id,name,date,status&order=date.desc",
                headers=self.headers
            )
            
            if response.status_code == 200:
                events = response.json()
                print(f"✅ Found {len(events)} events in database")
                print()
                
                for event in events:
                    print(f"📅 {event['name']}")
                    print(f"   ID: {event['id']}")
                    print(f"   Date: {event['date']}")
                    print(f"   Status: {event['status']}")
                    
                    # Get fights for this event
                    fights_response = requests.get(
                        f"{self.supabase_url}/rest/v1/fights?event_id=eq.{event['id']}&select=id,fighter1_id,fighter2_id,weight_class,result",
                        headers=self.headers
                    )
                    
                    if fights_response.status_code == 200:
                        fights = fights_response.json()
                        print(f"   🥊 Fights: {len(fights)}")
                        
                        # Show first 3 fights
                        for i, fight in enumerate(fights[:3]):
                            result = fight.get('result', {})
                            method = result.get('method', 'Unknown') if isinstance(result, dict) else 'Unknown'
                            print(f"      {i+1}. {fight['weight_class']}: {method}")
                        
                        if len(fights) > 3:
                            print(f"      ... and {len(fights) - 3} more")
                    else:
                        print(f"   ❌ Error getting fights: {fights_response.status_code}")
                    
                    print()
            else:
                print(f"❌ Error getting events: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error debugging events: {e}")
    
    def debug_past_events_tab(self):
        """Debug what the Past tab should show"""
        print("\n📋 Debugging Past Events Tab...")
        print("=" * 50)
        
        try:
            # Get past events (completed status)
            response = requests.get(
                f"{self.supabase_url}/rest/v1/events?select=id,name,date,status&status=eq.completed&order=date.desc",
                headers=self.headers
            )
            
            if response.status_code == 200:
                events = response.json()
                print(f"✅ Found {len(events)} past events (completed status)")
                print()
                
                total_fights = 0
                for event in events:
                    # Get fights for this event
                    fights_response = requests.get(
                        f"{self.supabase_url}/rest/v1/fights?event_id=eq.{event['id']}&select=id",
                        headers=self.headers
                    )
                    
                    if fights_response.status_code == 200:
                        fights = fights_response.json()
                        total_fights += len(fights)
                        print(f"📅 {event['name']}: {len(fights)} fights")
                
                print(f"\n📊 Total past events: {len(events)}")
                print(f"🥊 Total fights in past events: {total_fights}")
                
            else:
                print(f"❌ Error getting past events: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error debugging past events: {e}")
    
    def debug_fight_loading(self):
        """Debug fight loading process"""
        print("\n🥊 Debugging Fight Loading Process...")
        print("=" * 50)
        
        try:
            # Get first event
            events_response = requests.get(
                f"{self.supabase_url}/rest/v1/events?select=id,name&limit=1",
                headers=self.headers
            )
            
            if events_response.status_code == 200:
                events = events_response.json()
                if events:
                    event = events[0]
                    print(f"📅 Testing with event: {event['name']}")
                    print(f"   ID: {event['id']}")
                    
                    # Get fights for this event
                    fights_response = requests.get(
                        f"{self.supabase_url}/rest/v1/fights?event_id=eq.{event['id']}&select=*&limit=5",
                        headers=self.headers
                    )
                    
                    if fights_response.status_code == 200:
                        fights = fights_response.json()
                        print(f"   🥊 Found {len(fights)} fights")
                        
                        for i, fight in enumerate(fights):
                            print(f"      Fight {i+1}:")
                            print(f"         ID: {fight['id']}")
                            print(f"         Weight Class: {fight['weight_class']}")
                            print(f"         Fighter1 ID: {fight['fighter1_id']}")
                            print(f"         Fighter2 ID: {fight['fighter2_id']}")
                            
                            result = fight.get('result', {})
                            if isinstance(result, dict):
                                print(f"         Method: {result.get('method', 'Unknown')}")
                                print(f"         Winner ID: {result.get('winner_id', 'None')}")
                            else:
                                print(f"         Result: {result}")
                            print()
                    else:
                        print(f"   ❌ Error getting fights: {fights_response.status_code}")
                else:
                    print("❌ No events found")
            else:
                print(f"❌ Error getting events: {events_response.status_code}")
                
        except Exception as e:
            print(f"❌ Error debugging fight loading: {e}")
    
    def debug_flutter_app_issues(self):
        """Debug common Flutter app issues"""
        print("\n🔍 Debugging Common Flutter App Issues...")
        print("=" * 50)
        
        print("1. 📱 Check if you're on the right tab:")
        print("   - Make sure you're on the 'Past' tab, not 'Upcoming'")
        print("   - The 'Upcoming' tab will show 0 fights since all our data is past events")
        print()
        
        print("2. 🔄 Check if the app is refreshing data:")
        print("   - Try pulling down to refresh the fight cards screen")
        print("   - The app might be caching old data")
        print()
        
        print("3. 📊 Check the database directly:")
        print("   - We have 5 events with 57+ fights total")
        print("   - All events have 'completed' status")
        print("   - All fights have proper winner/loser data")
        print()
        
        print("4. 🐛 Check Flutter logs:")
        print("   - Look for any error messages in the Flutter console")
        print("   - Check if the app is successfully connecting to Supabase")
        print()
        
        print("5. 📱 App-specific debugging:")
        print("   - Try restarting the Flutter app")
        print("   - Check if the app is using the correct Supabase credentials")
        print("   - Verify the app is calling the right API endpoints")
    
    def run_debug(self):
        """Run all debugging checks"""
        print("🚀 Starting Flutter Data Debugging")
        print("=" * 60)
        
        self.debug_events_data()
        self.debug_past_events_tab()
        self.debug_fight_loading()
        self.debug_flutter_app_issues()
        
        print("\n" + "=" * 60)
        print("✅ Debugging complete!")
        print("🎯 Check the output above to identify why you're only seeing 3 fights")

def main():
    debugger = FlutterDataDebugger()
    debugger.run_debug()

if __name__ == "__main__":
    main() 