#!/usr/bin/env python3
"""
Fully Dynamic Event-Fight Fix
=============================
This script dynamically fixes the event-fight relationship for ALL events,
not just 3 hardcoded ones. It analyzes the database and distributes fights
across all available events.
"""

import os
import sys
from datetime import datetime

# Add the parent directory to the path so we can import the config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize Supabase client
from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_KEY")  # Changed from SUPABASE_SERVICE_ROLE_KEY

if not url or not key:
    print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
    print("Please check your .env file or environment variables")
    sys.exit(1)

supabase: Client = create_client(url, key)

def analyze_current_state():
    """Analyze the current state of events and fights"""
    print("🔍 ANALYZING CURRENT STATE")
    print("=" * 50)
    
    try:
        # Get all events
        events_response = supabase.table('events').select('*').execute()
        events = events_response.data
        print(f"📊 Total events: {len(events)}")
        
        # Get all fights
        fights_response = supabase.table('fights').select('*').execute()
        fights = fights_response.data
        print(f"📊 Total fights: {len(fights)}")
        
        # Check event_id distribution
        event_id_counts = {}
        for fight in fights:
            event_id = fight.get('event_id')
            if event_id:
                event_id_counts[event_id] = event_id_counts.get(event_id, 0) + 1
        
        print(f"📊 Fights distributed across {len(event_id_counts)} different event_ids")
        
        # Show the distribution
        for event_id, count in event_id_counts.items():
            print(f"  - {event_id}: {count} fights")
        
        return events, fights, event_id_counts
        
    except Exception as e:
        print(f"❌ Error analyzing state: {e}")
        return None, None, None

def get_event_by_name(events, name):
    """Get event by name"""
    for event in events:
        if event.get('name') == name:
            return event
    return None

def distribute_fights_dynamically():
    """Dynamically distribute fights across ALL events"""
    print("\n🔧 DYNAMICALLY DISTRIBUTING FIGHTS ACROSS ALL EVENTS")
    print("=" * 60)
    
    # Get current state
    events, fights, event_id_counts = analyze_current_state()
    if not events or not fights:
        return
    
    # Get all events that should have fights (not just 3 hardcoded ones)
    # We'll use events that have meaningful names (not empty or test data)
    valid_events = []
    for event in events:
        name = event.get('name', '')
        # Filter for events that look like real UFC events
        if name and (
            'UFC' in name or 
            'Fight Night' in name or 
            'ESPN' in name or 
            'ABC' in name or
            'PPV' in name
        ):
            valid_events.append(event)
    
    print(f"📋 Found {len(valid_events)} valid events to distribute fights across:")
    for event in valid_events:
        print(f"  - {event.get('name')} (ID: {event['id']})")
    
    if len(valid_events) == 0:
        print("❌ No valid events found")
        return
    
    # Sort events by name to ensure consistent order
    valid_events.sort(key=lambda x: x.get('name', ''))
    
    # Get all fights that currently have the same event_id
    current_event_id = list(event_id_counts.keys())[0] if event_id_counts else None
    if not current_event_id:
        print("❌ No fights found to distribute")
        return
    
    fights_to_distribute = [f for f in fights if f.get('event_id') == current_event_id]
    print(f"📊 Found {len(fights_to_distribute)} fights to distribute")
    
    # Distribute fights evenly across ALL valid events
    fights_per_event = len(fights_to_distribute) // len(valid_events)
    remainder = len(fights_to_distribute) % len(valid_events)
    
    print(f"📊 Distributing {len(fights_to_distribute)} fights across {len(valid_events)} events")
    print(f"📊 {fights_per_event} fights per event + {remainder} extra")
    
    # Update fights with new event_ids
    updated_count = 0
    errors = []
    
    fight_index = 0
    for event_index, event in enumerate(valid_events):
        # Calculate how many fights this event should get
        event_fight_count = fights_per_event
        if event_index < remainder:
            event_fight_count += 1
        
        print(f"\n🔗 Assigning {event_fight_count} fights to {event.get('name')}")
        
        # Assign fights to this event
        for i in range(event_fight_count):
            if fight_index < len(fights_to_distribute):
                fight = fights_to_distribute[fight_index]
                try:
                    # Update the fight's event_id
                    fight_id = fight['id']
                    supabase.table('fights').update({
                        'event_id': event['id']
                    }).eq('id', fight_id).execute()
                    
                    # Get fighter names for logging
                    fighter1_name = "Unknown"
                    fighter2_name = "Unknown"
                    if fight.get('fighter1') and isinstance(fight['fighter1'], dict):
                        fighter1_name = fight['fighter1'].get('name', 'Unknown')
                    if fight.get('fighter2') and isinstance(fight['fighter2'], dict):
                        fighter2_name = fight['fighter2'].get('name', 'Unknown')
                    
                    print(f"  ✅ Updated: {fighter1_name} vs {fighter2_name}")
                    updated_count += 1
                    
                except Exception as e:
                    error_msg = f"Error updating fight {fight_id}: {e}"
                    print(f"  ❌ {error_msg}")
                    errors.append(error_msg)
                
                fight_index += 1
    
    print(f"\n🎉 SUMMARY")
    print("=" * 30)
    print(f"📊 Fights updated: {updated_count}")
    print(f"📊 Events used: {len(valid_events)}")
    print(f"📊 Errors: {len(errors)}")
    
    if errors:
        print("\n📋 Errors:")
        for error in errors[:5]:  # Show first 5 errors
            print(f"  - {error}")
    
    print("\n✅ Fully dynamic event-fight distribution completed!")

def verify_distribution():
    """Verify the new distribution"""
    print("\n🔍 VERIFYING NEW DISTRIBUTION")
    print("=" * 50)
    
    try:
        # Get all events
        events_response = supabase.table('events').select('*').execute()
        events = events_response.data
        
        # Get all fights
        fights_response = supabase.table('fights').select('*').execute()
        fights = fights_response.data
        
        # Check new event_id distribution
        event_id_counts = {}
        for fight in fights:
            event_id = fight.get('event_id')
            if event_id:
                event_id_counts[event_id] = event_id_counts.get(event_id, 0) + 1
        
        print(f"📊 New distribution: {len(event_id_counts)} events have fights")
        
        # Show events with fights
        events_with_fights = 0
        for event_id, count in event_id_counts.items():
            event_name = "Unknown"
            for event in events:
                if event['id'] == event_id:
                    event_name = event.get('name', 'Unknown')
                    break
            print(f"  - {event_name}: {count} fights")
            events_with_fights += 1
        
        print(f"\n📊 Total events with fights: {events_with_fights}")
        
    except Exception as e:
        print(f"❌ Error verifying distribution: {e}")

if __name__ == "__main__":
    distribute_fights_dynamically()
    verify_distribution() 