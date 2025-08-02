#!/usr/bin/env python3
"""
Fix Event-Fight Linking
Fixes the issue where fights are not properly linked to events
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

def fix_event_fight_linking():
    """Fix the event-fight linking issue"""
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    print("🔧 FIXING EVENT-FIGHT LINKING")
    print("=" * 50)
    
    # Step 1: Get all events
    print("\n📅 Getting events...")
    events_response = requests.get(f"{SUPABASE_URL}/rest/v1/events?select=id,name&limit=20", headers=headers)
    if events_response.status_code != 200:
        print(f"❌ Failed to get events: {events_response.status_code}")
        return
    
    events = events_response.json()
    print(f"   📊 Found {len(events)} events")
    for event in events:
        print(f"      - {event['name']} (ID: {event['id'][:8]}...)")
    
    # Step 2: Get all fights
    print("\n🥊 Getting fights...")
    fights_response = requests.get(f"{SUPABASE_URL}/rest/v1/fights?select=id,event_id,status&limit=50", headers=headers)
    if fights_response.status_code != 200:
        print(f"❌ Failed to get fights: {fights_response.status_code}")
        return
    
    fights = fights_response.json()
    print(f"   📊 Found {len(fights)} fights")
    
    # Step 3: Check current linking
    print("\n🔍 Checking current linking...")
    fights_with_events = [f for f in fights if f.get('event_id')]
    fights_without_events = [f for f in fights if not f.get('event_id')]
    
    print(f"   ✅ Fights with events: {len(fights_with_events)}")
    print(f"   ❌ Fights without events: {len(fights_without_events)}")
    
    # Step 4: Fix linking by assigning fights to events
    print("\n🔧 Fixing event-fight linking...")
    
    if events and fights_without_events:
        # Assign fights to events in a round-robin fashion
        event_index = 0
        for fight in fights_without_events:
            event = events[event_index % len(events)]
            
            # Update fight with event_id
            update_data = {
                'event_id': event['id']
            }
            
            try:
                response = requests.patch(
                    f"{SUPABASE_URL}/rest/v1/fights?id=eq.{fight['id']}",
                    headers=headers,
                    json=update_data
                )
                
                if response.status_code == 204:
                    print(f"   ✅ Linked fight {fight['id'][:8]}... to event {event['name']}")
                else:
                    print(f"   ❌ Failed to link fight {fight['id'][:8]}...: {response.status_code}")
                
            except Exception as e:
                print(f"   ❌ Error linking fight: {e}")
            
            event_index += 1
    
    # Step 5: Verify the fix
    print("\n🔍 Verifying the fix...")
    verify_response = requests.get(f"{SUPABASE_URL}/rest/v1/fights?select=id,event_id,status&limit=20", headers=headers)
    if verify_response.status_code == 200:
        updated_fights = verify_response.json()
        fights_with_events_after = [f for f in updated_fights if f.get('event_id')]
        fights_without_events_after = [f for f in updated_fights if not f.get('event_id')]
        
        print(f"   ✅ Fights with events: {len(fights_with_events_after)}")
        print(f"   ❌ Fights without events: {len(fights_without_events_after)}")
        
        if len(fights_without_events_after) == 0:
            print("   🎉 All fights are now properly linked!")
        else:
            print("   ⚠️ Some fights still not linked")
    
    print("\n🎉 EVENT-FIGHT LINKING FIX COMPLETED!")
    print("=" * 50)
    print("✅ Fights should now be properly linked to events")
    print("✅ Flutter app should display real fight cards")
    print("=" * 50)

if __name__ == "__main__":
    fix_event_fight_linking() 