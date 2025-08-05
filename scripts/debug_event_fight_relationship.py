#!/usr/bin/env python3
"""
Debug Event-Fight Relationship Issue
===================================
This script analyzes the database to understand why only UFC 300 has fights
and all other events show 0 fights.
"""

import os
import sys
import json
from datetime import datetime
from supabase import create_client, Client

# Add the parent directory to the path so we can import the config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize Supabase client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

def debug_event_fight_relationship():
    """Debug the event-fight relationship issue"""
    print("🔍 DEBUGGING EVENT-FIGHT RELATIONSHIP ISSUE")
    print("=" * 60)
    
    try:
        # 1. Check all events
        print("\n📋 STEP 1: CHECKING ALL EVENTS")
        print("-" * 40)
        events_response = supabase.table('events').select('*').execute()
        events = events_response.data
        
        print(f"📊 Total events in database: {len(events)}")
        
        # Group events by name to see duplicates
        event_names = {}
        for event in events:
            name = event.get('name', 'Unknown')
            if name not in event_names:
                event_names[name] = []
            event_names[name].append(event)
        
        print(f"📊 Unique event names: {len(event_names)}")
        print("\n📋 Event breakdown:")
        for name, event_list in event_names.items():
            print(f"  - {name}: {len(event_list)} instances")
        
        # 2. Check all fights
        print("\n🥊 STEP 2: CHECKING ALL FIGHTS")
        print("-" * 40)
        fights_response = supabase.table('fights').select('*').execute()
        fights = fights_response.data
        
        print(f"📊 Total fights in database: {len(fights)}")
        
        # Check event_id distribution
        event_ids = {}
        for fight in fights:
            event_id = fight.get('event_id')
            if event_id not in event_ids:
                event_ids[event_id] = []
            event_ids[event_id].append(fight)
        
        print(f"📊 Fights distributed across {len(event_ids)} different event_ids")
        print("\n📋 Event ID breakdown:")
        for event_id, fight_list in event_ids.items():
            print(f"  - {event_id}: {len(fight_list)} fights")
        
        # 3. Cross-reference events and fights
        print("\n🔗 STEP 3: CROSS-REFERENCING EVENTS AND FIGHTS")
        print("-" * 40)
        
        # Get all event IDs
        all_event_ids = [event['id'] for event in events]
        print(f"📊 All event IDs: {all_event_ids}")
        
        # Check which events have fights
        events_with_fights = []
        events_without_fights = []
        
        for event in events:
            event_id = event['id']
            event_fights = [f for f in fights if f.get('event_id') == event_id]
            
            if event_fights:
                events_with_fights.append({
                    'event': event,
                    'fight_count': len(event_fights)
                })
            else:
                events_without_fights.append(event)
        
        print(f"📊 Events WITH fights: {len(events_with_fights)}")
        print(f"📊 Events WITHOUT fights: {len(events_without_fights)}")
        
        print("\n📋 Events WITH fights:")
        for item in events_with_fights:
            event = item['event']
            count = item['fight_count']
            print(f"  - {event.get('name', 'Unknown')} (ID: {event['id']}): {count} fights")
        
        print("\n📋 Events WITHOUT fights:")
        for event in events_without_fights[:10]:  # Show first 10
            print(f"  - {event.get('name', 'Unknown')} (ID: {event['id']})")
        if len(events_without_fights) > 10:
            print(f"  ... and {len(events_without_fights) - 10} more")
        
        # 4. Check if there are orphaned fights (fights with event_id that doesn't exist)
        print("\n🚨 STEP 4: CHECKING FOR ORPHANED FIGHTS")
        print("-" * 40)
        
        orphaned_fights = []
        for fight in fights:
            event_id = fight.get('event_id')
            if event_id and event_id not in all_event_ids:
                orphaned_fights.append(fight)
        
        print(f"📊 Orphaned fights (event_id doesn't exist): {len(orphaned_fights)}")
        if orphaned_fights:
            print("📋 Orphaned fight event_ids:")
            orphaned_event_ids = set(f.get('event_id') for f in orphaned_fights)
            for event_id in orphaned_event_ids:
                count = len([f for f in orphaned_fights if f.get('event_id') == event_id])
                print(f"  - {event_id}: {count} fights")
        
        # 5. Check fight data structure
        print("\n📊 STEP 5: ANALYZING FIGHT DATA STRUCTURE")
        print("-" * 40)
        
        if fights:
            sample_fight = fights[0]
            print("📋 Sample fight structure:")
            for key, value in sample_fight.items():
                print(f"  - {key}: {value}")
        
        # 6. Check event data structure
        print("\n📊 STEP 6: ANALYZING EVENT DATA STRUCTURE")
        print("-" * 40)
        
        if events:
            sample_event = events[0]
            print("📋 Sample event structure:")
            for key, value in sample_event.items():
                print(f"  - {key}: {value}")
        
        # 7. Summary and recommendations
        print("\n🎯 STEP 7: SUMMARY AND RECOMMENDATIONS")
        print("-" * 40)
        
        print(f"📊 Total events: {len(events)}")
        print(f"📊 Total fights: {len(fights)}")
        print(f"📊 Events with fights: {len(events_with_fights)}")
        print(f"📊 Events without fights: {len(events_without_fights)}")
        print(f"📊 Orphaned fights: {len(orphaned_fights)}")
        
        if len(events_with_fights) == 1:
            print("\n🚨 ISSUE IDENTIFIED: Only one event has fights!")
            print("This suggests that all fights are linked to the same event.")
            print("Possible causes:")
            print("1. Fight scraper only populated one event")
            print("2. Event IDs are not being set correctly")
            print("3. Database relationship issue")
        
        if orphaned_fights:
            print("\n🚨 ISSUE IDENTIFIED: Orphaned fights found!")
            print("Some fights have event_ids that don't exist in the events table.")
            print("This will cause the Flutter app to show 0 fights for those events.")
        
        print("\n💡 RECOMMENDATIONS:")
        print("1. Check the fight scraper to ensure it sets correct event_ids")
        print("2. Verify that events are created before fights")
        print("3. Consider running a data migration to fix event-fight relationships")
        
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_event_fight_relationship() 