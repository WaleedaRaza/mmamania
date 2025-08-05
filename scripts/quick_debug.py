#!/usr/bin/env python3
"""
Quick Debug - Event-Fight Relationship
=====================================
Simple script to quickly identify why only UFC 300 has fights.
"""

import os
import sys
from supabase import create_client, Client

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize Supabase client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

def quick_debug():
    """Quick debug of the event-fight relationship"""
    print("🔍 QUICK DEBUG - EVENT-FIGHT RELATIONSHIP")
    print("=" * 50)
    
    try:
        # 1. Count total events and fights
        print("\n📊 STEP 1: BASIC COUNTS")
        print("-" * 30)
        
        events_response = supabase.table('events').select('id, name').execute()
        events = events_response.data
        print(f"📋 Total events: {len(events)}")
        
        fights_response = supabase.table('fights').select('id, event_id').execute()
        fights = fights_response.data
        print(f"🥊 Total fights: {len(fights)}")
        
        # 2. Check event_id distribution in fights
        print("\n📊 STEP 2: EVENT_ID DISTRIBUTION")
        print("-" * 30)
        
        event_id_counts = {}
        for fight in fights:
            event_id = fight.get('event_id')
            if event_id:
                event_id_counts[event_id] = event_id_counts.get(event_id, 0) + 1
        
        print(f"📊 Fights distributed across {len(event_id_counts)} different event_ids")
        
        # Show top 5 event_ids with most fights
        sorted_event_ids = sorted(event_id_counts.items(), key=lambda x: x[1], reverse=True)
        print("\n📋 Top event_ids by fight count:")
        for event_id, count in sorted_event_ids[:5]:
            print(f"  - {event_id}: {count} fights")
        
        # 3. Check which events actually exist
        print("\n📊 STEP 3: EVENT EXISTENCE CHECK")
        print("-" * 30)
        
        existing_event_ids = {event['id'] for event in events}
        print(f"📋 Existing event IDs: {len(existing_event_ids)}")
        
        # Check which event_ids in fights actually exist
        valid_event_ids = []
        invalid_event_ids = []
        
        for event_id in event_id_counts.keys():
            if event_id in existing_event_ids:
                valid_event_ids.append(event_id)
            else:
                invalid_event_ids.append(event_id)
        
        print(f"✅ Valid event_ids (exist in events table): {len(valid_event_ids)}")
        print(f"❌ Invalid event_ids (don't exist in events table): {len(invalid_event_ids)}")
        
        if invalid_event_ids:
            print("\n📋 Invalid event_ids:")
            for event_id in invalid_event_ids[:5]:
                count = event_id_counts[event_id]
                print(f"  - {event_id}: {count} fights")
        
        # 4. Show events with fights
        print("\n📊 STEP 4: EVENTS WITH FIGHTS")
        print("-" * 30)
        
        events_with_fights = []
        for event in events:
            event_id = event['id']
            fight_count = event_id_counts.get(event_id, 0)
            if fight_count > 0:
                events_with_fights.append({
                    'name': event.get('name', 'Unknown'),
                    'id': event_id,
                    'fight_count': fight_count
                })
        
        print(f"📊 Events with fights: {len(events_with_fights)}")
        for item in events_with_fights:
            print(f"  - {item['name']}: {item['fight_count']} fights")
        
        # 5. Summary
        print("\n🎯 SUMMARY")
        print("-" * 30)
        print(f"📊 Total events: {len(events)}")
        print(f"📊 Total fights: {len(fights)}")
        print(f"📊 Events with fights: {len(events_with_fights)}")
        print(f"📊 Valid event_ids: {len(valid_event_ids)}")
        print(f"📊 Invalid event_ids: {len(invalid_event_ids)}")
        
        if len(events_with_fights) == 1:
            print("\n🚨 ISSUE: Only one event has fights!")
            print("All fights are linked to the same event.")
        
        if invalid_event_ids:
            print("\n🚨 ISSUE: Orphaned fights found!")
            print("Some fights have event_ids that don't exist.")
        
        print("\n💡 NEXT STEPS:")
        print("1. Check the fight scraper to ensure correct event_id assignment")
        print("2. Verify events are created before fights")
        print("3. Consider data migration to fix relationships")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    quick_debug() 