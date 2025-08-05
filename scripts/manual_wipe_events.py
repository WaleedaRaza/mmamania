#!/usr/bin/env python3
"""
Manual Wipe Events
Manually wipe all events from the database
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv('scripts/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

def manual_wipe_events():
    """Manually wipe all events from the database"""
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    print("🗑️ MANUAL WIPE - DELETING ALL EVENTS")
    print("=" * 50)
    print(f"Supabase URL: {SUPABASE_URL}")
    print(f"API Key: {SUPABASE_KEY[:20]}...")
    print()
    
    try:
        # First, let's check how many events we have
        response = requests.get(f"{SUPABASE_URL}/rest/v1/events?select=id&limit=1", headers=headers)
        if response.status_code == 200:
            print(f"✅ Database connection successful")
        
        # Now delete all events
        print("🗑️ Deleting all events...")
        
        # First, delete all fights (to handle foreign key constraints)
        print("🗑️ Deleting all fights first...")
        delete_fights_response = requests.delete(f"{SUPABASE_URL}/rest/v1/fights?event_id=not.is.null", headers=headers)
        
        if delete_fights_response.status_code == 200:
            print("✅ Successfully deleted all fights")
        else:
            print(f"⚠️ Failed to delete fights: {delete_fights_response.status_code}")
            print(f"Response: {delete_fights_response.text}")
        
        # Now delete all events
        print("🗑️ Deleting all events...")
        delete_response = requests.delete(f"{SUPABASE_URL}/rest/v1/events?name=not.is.null", headers=headers)
        
        if delete_response.status_code == 200:
            print("✅ Successfully deleted all events")
        else:
            print(f"❌ Failed to delete events: {delete_response.status_code}")
            print(f"Response: {delete_response.text}")
            
            # Try alternative approach
            print("🔄 Trying alternative delete approach...")
            delete_response2 = requests.delete(f"{SUPABASE_URL}/rest/v1/events?id=not.is.null", headers=headers)
            
            if delete_response2.status_code == 200:
                print("✅ Successfully deleted all events (alternative method)")
            else:
                print(f"❌ Alternative delete also failed: {delete_response2.status_code}")
                print(f"Response: {delete_response2.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    manual_wipe_events() 