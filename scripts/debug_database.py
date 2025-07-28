#!/usr/bin/env python3
"""
Debug script to check what's in the database
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def check_database():
    supabase_url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    headers = {
        'apikey': service_key,
        'Authorization': f'Bearer {service_key}',
        'Content-Type': 'application/json',
    }
    
    print("🔍 Checking database contents...")
    
    # Check fighters
    print("\n📊 Fighters:")
    response = requests.get(f"{supabase_url}/rest/v1/fighters", headers=headers)
    if response.status_code == 200:
        fighters = response.json()
        print(f"✅ Found {len(fighters)} fighters")
        for fighter in fighters[:5]:  # Show first 5
            print(f"  - {fighter.get('name')} ({fighter.get('weight_class')})")
    else:
        print(f"❌ Error getting fighters: {response.status_code}")
    
    # Check rankings
    print("\n🏆 Rankings:")
    response = requests.get(f"{supabase_url}/rest/v1/rankings", headers=headers)
    if response.status_code == 200:
        rankings = response.json()
        print(f"✅ Found {len(rankings)} rankings")
        
        # Group by weight class
        weight_classes = {}
        for ranking in rankings:
            weight_class = ranking.get('weight_class', 'Unknown')
            if weight_class not in weight_classes:
                weight_classes[weight_class] = []
            weight_classes[weight_class].append(ranking)
        
        print("\n📋 Weight classes in database:")
        for weight_class, rankings_list in weight_classes.items():
            print(f"  - {weight_class}: {len(rankings_list)} rankings")
            for ranking in rankings_list[:3]:  # Show first 3 per class
                print(f"    * Rank {ranking.get('rank_position')}: {ranking.get('fighter_id')}")
    else:
        print(f"❌ Error getting rankings: {response.status_code}")
    
    # Check events
    print("\n📅 Events:")
    response = requests.get(f"{supabase_url}/rest/v1/events", headers=headers)
    if response.status_code == 200:
        events = response.json()
        print(f"✅ Found {len(events)} events")
        for event in events[:3]:  # Show first 3
            print(f"  - {event.get('name')}")
    else:
        print(f"❌ Error getting events: {response.status_code}")

if __name__ == "__main__":
    check_database() 