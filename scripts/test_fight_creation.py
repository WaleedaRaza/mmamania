#!/usr/bin/env python3
"""
Test Fight Creation Script
Debug why fights aren't being created in Supabase
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv('scripts/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
}

# First, get an event ID
print("📅 Getting event ID...")
try:
    events_response = requests.get(
        f"{SUPABASE_URL}/rest/v1/events?select=id,name&limit=1",
        headers=headers
    )
    
    if events_response.status_code == 200:
        events = events_response.json()
        if events:
            event_id = events[0]['id']
            event_name = events[0]['name']
            print(f"✅ Found event: {event_name} (ID: {event_id})")
        else:
            print("❌ No events found")
            exit(1)
    else:
        print(f"❌ Error getting events: {events_response.status_code}")
        exit(1)
        
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Get or create fighters
print("\n👊 Getting/Creating fighters...")
fighter1_name = "Alex Pereira"
fighter2_name = "Jamahal Hill"

# Check if fighters exist
fighter1_response = requests.get(
    f"{SUPABASE_URL}/rest/v1/fighters?name=eq.{fighter1_name}",
    headers=headers
)

fighter1_id = None
if fighter1_response.status_code == 200:
    fighters = fighter1_response.json()
    if fighters:
        fighter1_id = fighters[0]['id']
        print(f"✅ Found fighter1: {fighter1_name} (ID: {fighter1_id})")
    else:
        # Create fighter1
        fighter1_data = {
            'name': fighter1_name,
            'weight_class': 'Light Heavyweight',
            'record': {'wins': 0, 'losses': 0, 'draws': 0},
            'is_active': 'Active'
        }
        
        create_response = requests.post(
            f"{SUPABASE_URL}/rest/v1/fighters",
            headers=headers,
            json=fighter1_data
        )
        
        if create_response.status_code == 201:
            # Get the created fighter ID
            get_response = requests.get(
                f"{SUPABASE_URL}/rest/v1/fighters?name=eq.{fighter1_name}",
                headers=headers
            )
            if get_response.status_code == 200:
                fighters = get_response.json()
                if fighters:
                    fighter1_id = fighters[0]['id']
                    print(f"✅ Created fighter1: {fighter1_name} (ID: {fighter1_id})")

# Same for fighter2
fighter2_response = requests.get(
    f"{SUPABASE_URL}/rest/v1/fighters?name=eq.{fighter2_name}",
    headers=headers
)

fighter2_id = None
if fighter2_response.status_code == 200:
    fighters = fighter2_response.json()
    if fighters:
        fighter2_id = fighters[0]['id']
        print(f"✅ Found fighter2: {fighter2_name} (ID: {fighter2_id})")
    else:
        # Create fighter2
        fighter2_data = {
            'name': fighter2_name,
            'weight_class': 'Light Heavyweight',
            'record': {'wins': 0, 'losses': 0, 'draws': 0},
            'is_active': 'Active'
        }
        
        create_response = requests.post(
            f"{SUPABASE_URL}/rest/v1/fighters",
            headers=headers,
            json=fighter2_data
        )
        
        if create_response.status_code == 201:
            # Get the created fighter ID
            get_response = requests.get(
                f"{SUPABASE_URL}/rest/v1/fighters?name=eq.{fighter2_name}",
                headers=headers
            )
            if get_response.status_code == 200:
                fighters = get_response.json()
                if fighters:
                    fighter2_id = fighters[0]['id']
                    print(f"✅ Created fighter2: {fighter2_name} (ID: {fighter2_id})")

if not fighter1_id or not fighter2_id:
    print("❌ Could not get/create fighters")
    exit(1)

# Now try to create a fight
print(f"\n🥊 Creating fight: {fighter1_name} vs {fighter2_name}")

winner_id = fighter1_id  # Alex Pereira wins

fight_data = {
    'event_id': event_id,
    'fighter1_id': fighter1_id,
    'fighter2_id': fighter2_id,
    'status': 'completed',
    'result': {
        'method': 'TKO (punches)',
        'round': 1,
        'time': '3:14',
        'winner_id': winner_id
    },
    'weight_class': 'Light Heavyweight',
    'method': 'TKO (punches)',
    'round': 1,
    'time': '3:14',
    'winner_id': winner_id,
    'is_completed': True
}

print(f"Fight data: {json.dumps(fight_data, indent=2)}")

try:
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/fights",
        headers=headers,
        json=fight_data
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    
    if response.status_code == 201:
        print("✅ Fight created successfully!")
        
        # Get the created fight
        fights_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/fights?event_id=eq.{event_id}",
            headers=headers
        )
        
        if fights_response.status_code == 200:
            fights = fights_response.json()
            print(f"✅ Retrieved {len(fights)} fights for event")
            for fight in fights:
                print(f"   Fight ID: {fight['id']}")
                print(f"   Winner ID: {fight.get('winner_id')}")
                print(f"   Method: {fight.get('method')}")
    else:
        print("❌ Failed to create fight")
        
except Exception as e:
    print(f"❌ Error: {e}") 