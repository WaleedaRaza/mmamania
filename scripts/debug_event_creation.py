#!/usr/bin/env python3
"""
Debug Event Creation
Test creating a single event to see what's causing the JSON parsing error
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv('scripts/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

def debug_event_creation():
    """Debug event creation"""
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    print("🔍 DEBUGGING EVENT CREATION")
    print("=" * 50)
    print(f"Supabase URL: {SUPABASE_URL}")
    print(f"API Key: {SUPABASE_KEY[:20]}..." if SUPABASE_KEY else "❌ No API key")
    print()
    
    # Test event data
    test_event = {
        'name': 'UFC Test Event',
        'date': '2024-01-01T00:00:00',
        'location': 'Test Location',
        'venue': 'Test Venue',
        'status': 'completed'
    }
    
    print("📝 Test Event Data:")
    print(test_event)
    print()
    
    try:
        print("🚀 Attempting to create event...")
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/events",
            headers=headers,
            json=test_event
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        print(f"📊 Response Text: {response.text}")
        
        if response.status_code == 201:
            print("✅ Event created successfully!")
            created_event = response.json()
            print(f"Created event ID: {created_event[0]['id']}")
        else:
            print(f"❌ Failed to create event: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    debug_event_creation() 