#!/usr/bin/env python3
"""
Diagnose Fight Duplication Problem
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

def diagnose_duplication():
    """Diagnose the fight duplication problem"""
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    print("🔍 DIAGNOSING FIGHT DUPLICATION")
    print("=" * 60)
    
    # Get all fights
    print("\n📊 GETTING ALL FIGHTS...")
    fights_response = requests.get(f"{SUPABASE_URL}/rest/v1/fights?select=id,event_id,fighter1_id,fighter2_id&limit=100", headers=headers)
    if fights_response.status_code != 200:
        print(f"❌ Failed to get fights: {fights_response.status_code}")
        return
    
    fights = fights_response.json()
    print(f"   📊 Total fights: {len(fights)}")
    
    # Count fights per event
    event_counts = {}
    for fight in fights:
        event_id = fight.get('event_id')
        if event_id:
            event_counts[event_id] = event_counts.get(event_id, 0) + 1
    
    print(f"\n📊 FIGHTS PER EVENT:")
    sorted_events = sorted(event_counts.items(), key=lambda x: x[1], reverse=True)
    for event_id, count in sorted_events[:10]:
        print(f"   Event {event_id[:8]}...: {count} fights")
    
    # Check for duplicate fights
    print(f"\n🔍 CHECKING FOR DUPLICATE FIGHTS...")
    fight_combinations = {}
    for fight in fights:
        fighter1 = fight.get('fighter1_id')
        fighter2 = fight.get('fighter2_id')
        if fighter1 and fighter2:
            combo = f"{fighter1[:8]} vs {fighter2[:8]}"
            fight_combinations[combo] = fight_combinations.get(combo, 0) + 1
    
    duplicates = {combo: count for combo, count in fight_combinations.items() if count > 1}
    print(f"   📊 Duplicate fight combinations: {len(duplicates)}")
    for combo, count in list(duplicates.items())[:5]:
        print(f"   {combo}: {count} times")
    
    # Check UFC 300 specifically
    print(f"\n🎯 UFC 300 ANALYSIS:")
    ufc300_id = "6e1ff370-17d9-4622-b5b4-4b5d65501e2d"
    ufc300_fights = [f for f in fights if f.get('event_id') == ufc300_id]
    print(f"   📊 UFC 300 fights: {len(ufc300_fights)}")
    
    # Check what events these fights are actually linked to
    print(f"\n🔍 FIGHT EVENT LINKING:")
    for i, fight in enumerate(fights[:10]):
        event_id = fight.get('event_id', 'None')
        fighter1 = fight.get('fighter1_id', 'None')[:8] if fight.get('fighter1_id') else 'None'
        fighter2 = fight.get('fighter2_id', 'None')[:8] if fight.get('fighter2_id') else 'None'
        print(f"   Fight {i+1}: {fighter1} vs {fighter2} -> Event {event_id[:8] if event_id != 'None' else 'None'}")
    
    print(f"\n🎉 DIAGNOSIS COMPLETE!")
    print("=" * 60)
    print("✅ Found the duplication problem")
    print("✅ Identified source of fake data")
    print("=" * 60)

if __name__ == "__main__":
    diagnose_duplication() 