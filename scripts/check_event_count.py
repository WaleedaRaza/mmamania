#!/usr/bin/env python3
"""
Check Event Count
Check how many events are actually in the database
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv('scripts/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

def check_event_count():
    """Check the actual count of events"""
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    print("🔍 CHECKING EVENT COUNT")
    print("=" * 40)
    
    try:
        # Get total count
        response = requests.get(f"{SUPABASE_URL}/rest/v1/events?select=id&limit=1000", headers=headers)
        if response.status_code == 200:
            events = response.json()
            print(f"✅ Total events in database: {len(events)}")
            
            # Show a few examples
            print("\n📋 Sample events:")
            for i, event in enumerate(events[:5]):
                print(f"   {i+1}. {event.get('id', 'N/A')}")
                
        else:
            print(f"❌ Error getting events: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    check_event_count() 