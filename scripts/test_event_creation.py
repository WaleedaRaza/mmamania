#!/usr/bin/env python3
"""
Test Event Creation Script
Debug why events aren't being created in Supabase
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv('scripts/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

print(f"SUPABASE_URL: {SUPABASE_URL}")
print(f"SUPABASE_KEY: {SUPABASE_KEY[:20]}..." if SUPABASE_KEY else "None")

headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
}

# Test event creation without type field
test_event = {
    'name': 'UFC 300: Pereira vs Hill',
    'date': '2024-04-13',
    'venue': 'T-Mobile Arena',
    'location': 'Las Vegas, Nevada',
    'status': 'completed'
}

print(f"\nCreating test event: {test_event['name']}")

try:
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/events",
        headers=headers,
        json=test_event
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    print(f"Response body: {response.text}")
    
    if response.status_code == 201:
        print("✅ Event created successfully!")
        
        # Get the created event
        get_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/events?name=eq.{test_event['name']}",
            headers=headers
        )
        
        if get_response.status_code == 200:
            events = get_response.json()
            print(f"✅ Retrieved {len(events)} events")
            for event in events:
                print(f"   Event ID: {event['id']}")
                print(f"   Event Name: {event['name']}")
                print(f"   Event Fields: {list(event.keys())}")
    else:
        print("❌ Failed to create event")
        
except Exception as e:
    print(f"❌ Error: {e}") 