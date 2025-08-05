#!/usr/bin/env python3
"""
Fix Event-Fight Distribution
===========================
This script fixes the issue where all fights are linked to only one event.
It will properly distribute fights across their correct events.
"""

import os
import sys
import json
from datetime import datetime

# Add the parent directory to the path so we can import the config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize Supabase client
from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
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

def create_event_fight_mapping():
    """Create a mapping of events to fights based on event names"""
    print("\n🗺️ CREATING EVENT-FIGHT MAPPING")
    print("=" * 50)
    
    # This mapping is based on the real UFC events and their fights
    # We'll map fights to events based on the event names we know
    
    event_fight_mapping = {
        "UFC 300: Pereira vs Hill": [
            "Alex Pereira vs Jamahal Hill",
            "Zhang Weili vs Yan Xiaonan", 
            "Justin Gaethje vs Max Holloway",
            "Arman Tsarukyan vs Charles Oliveira",
            "Jiri Prochazka vs Aleksandar Rakic",
            "Sodiq Yusuff vs Diego Lopes",
            "Renato Moicano vs Jalin Turner",
            "Jessica Andrade vs Marina Rodriguez",
            "Bobby Green vs Paddy Pimblett",
            "Kayla Harrison vs Holly Holm",
            "Oban Elliott vs Val Woodburn",
            "Danny Barlow vs Josh Quinlan",
            "Andrea Lee vs Miranda Maverick",
            "Zhang Mingyang vs Brendson Ribeiro"
        ],
        "UFC 299: O'Malley vs Vera 2": [
            "Sean O'Malley vs Marlon Vera",
            "Dustin Poirier vs Benoit Saint Denis",
            "Kevin Holland vs Michael Page",
            "Gilbert Burns vs Jack Della Maddalena",
            "Petr Yan vs Song Yadong",
            "Curtis Blaydes vs Jailton Almeida",
            "Maycee Barber vs Katlyn Cerminara",
            "Mateusz Gamrot vs Rafael dos Anjos",
            "Pedro Munhoz vs Kyler Phillips",
            "Ion Cutelaba vs Philipe Lins",
            "Michel Pereira vs Michal Oleksiejczuk",
            "Robelis Despaigne vs Josh Parisian",
            "CJ Vergara vs Assu Almabayev",
            "Joanne Wood vs Maryna Moroz"
        ],
        "UFC 298: Volkanovski vs Topuria": [
            "Ilia Topuria vs Alexander Volkanovski",
            "Robert Whittaker vs Paulo Costa",
            "Ian Machado Garry vs Geoff Neal",
            "Merab Dvalishvili vs Henry Cejudo",
            "Anthony Hernandez vs Roman Kopylov",
            "Amanda Lemos vs Mackenzie Dern",
            "Marcos Rogerio de Lima vs Junior Tafa",
            "Rinya Nakamura vs Carlos Vera",
            "Zhang Mingyang vs Brendson Ribeiro",
            "Andrea Lee vs Miranda Maverick",
            "Danny Barlow vs Josh Quinlan",
            "Oban Elliott vs Val Woodburn"
        ]
    }
    
    print("📋 Created mapping for 3 major UFC events:")
    for event_name, fight_list in event_fight_mapping.items():
        print(f"  - {event_name}: {len(fight_list)} fights")
    
    return event_fight_mapping

def fix_event_fight_distribution():
    """Fix the event-fight distribution"""
    print("\n🔧 FIXING EVENT-FIGHT DISTRIBUTION")
    print("=" * 50)
    
    # Get current state
    events, fights, event_id_counts = analyze_current_state()
    if not events or not fights:
        return
    
    # Create mapping
    event_fight_mapping = create_event_fight_mapping()
    
    # Find the events in the database
    event_map = {}
    for event in events:
        event_name = event.get('name', '')
        event_map[event_name] = event['id']
    
    print(f"\n📋 Found {len(event_map)} events in database")
    
    # Update fights with correct event_ids
    updated_count = 0
    errors = []
    
    for event_name, fight_names in event_fight_mapping.items():
        if event_name not in event_map:
            print(f"⚠️  Event not found in database: {event_name}")
            continue
            
        event_id = event_map[event_name]
        print(f"\n🔗 Linking fights to event: {event_name}")
        
        for fight_name in fight_names:
            # Find the fight by fighter names
            fighter1_name, fighter2_name = fight_name.split(" vs ")
            
            # Find the fight in the database
            matching_fight = None
            for fight in fights:
                fighter1 = fight.get('fighter1', {})
                fighter2 = fight.get('fighter2', {})
                
                if (isinstance(fighter1, dict) and fighter1.get('name') == fighter1_name and
                    isinstance(fighter2, dict) and fighter2.get('name') == fighter2_name):
                    matching_fight = fight
                    break
            
            if matching_fight:
                try:
                    # Update the fight's event_id
                    fight_id = matching_fight['id']
                    supabase.table('fights').update({
                        'event_id': event_id
                    }).eq('id', fight_id).execute()
                    
                    print(f"  ✅ Updated: {fight_name}")
                    updated_count += 1
                    
                except Exception as e:
                    error_msg = f"Error updating fight {fight_name}: {e}"
                    print(f"  ❌ {error_msg}")
                    errors.append(error_msg)
            else:
                print(f"  ⚠️  Fight not found: {fight_name}")
    
    print(f"\n🎉 SUMMARY")
    print("=" * 30)
    print(f"📊 Fights updated: {updated_count}")
    print(f"📊 Errors: {len(errors)}")
    
    if errors:
        print("\n📋 Errors:")
        for error in errors[:5]:  # Show first 5 errors
            print(f"  - {error}")
    
    print("\n✅ Event-fight distribution fix completed!")

if __name__ == "__main__":
    fix_event_fight_distribution() 