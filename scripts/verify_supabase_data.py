#!/usr/bin/env python3
"""
Verify Supabase Data
Show exactly what data should be visible in the Supabase dashboard
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv('scripts/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

def verify_supabase_data():
    """Verify and display all data in Supabase"""
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    print("🔍 VERIFYING SUPABASE DATABASE")
    print("=" * 60)
    print(f"Database URL: {SUPABASE_URL}")
    print(f"API Key: {SUPABASE_KEY[:20]}..." if SUPABASE_KEY else "❌ No API key found")
    print()
    
    # Check Events
    print("📊 EVENTS TABLE:")
    print("-" * 30)
    try:
        response = requests.get(f"{SUPABASE_URL}/rest/v1/events?select=*&limit=10", headers=headers)
        if response.status_code == 200:
            events = response.json()
            print(f"✅ Found {len(events)} events")
            for event in events:
                print(f"   • {event.get('name', 'N/A')} - {event.get('date', 'N/A')}")
        else:
            print(f"❌ Error getting events: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Exception getting events: {e}")
    
    print()
    
    # Check Fighters
    print("🥊 FIGHTERS TABLE:")
    print("-" * 30)
    try:
        response = requests.get(f"{SUPABASE_URL}/rest/v1/fighters?select=*&limit=10", headers=headers)
        if response.status_code == 200:
            fighters = response.json()
            print(f"✅ Found {len(fighters)} fighters")
            for fighter in fighters:
                print(f"   • {fighter.get('name', 'N/A')} - {fighter.get('weight_class', 'N/A')}")
        else:
            print(f"❌ Error getting fighters: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Exception getting fighters: {e}")
    
    print()
    
    # Check Fights
    print("👊 FIGHTS TABLE:")
    print("-" * 30)
    try:
        response = requests.get(f"{SUPABASE_URL}/rest/v1/fights?select=*&limit=10", headers=headers)
        if response.status_code == 200:
            fights = response.json()
            print(f"✅ Found {len(fights)} fights")
            for fight in fights:
                event_name = fight.get('event_name', 'N/A')
                fighter1_id = fight.get('fighter_a_id', 'N/A')
                fighter2_id = fight.get('fighter_b_id', 'N/A')
                result = fight.get('result', {})
                winner_id = result.get('winner_id') if isinstance(result, dict) else None
                print(f"   • Event: {event_name}")
                print(f"     Fighters: {fighter1_id} vs {fighter2_id}")
                print(f"     Winner: {winner_id}")
                print()
        else:
            print(f"❌ Error getting fights: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Exception getting fights: {e}")
    
    print()
    
    # Check Relationships
    print("🔗 RELATIONSHIPS VERIFICATION:")
    print("-" * 30)
    try:
        # Get a sample fight with fighter details
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/fights?select=*,fighters!fights_fighter_a_id_fkey(name),fighters!fights_fighter_b_id_fkey(name)&limit=3", 
            headers=headers
        )
        if response.status_code == 200:
            fights_with_fighters = response.json()
            print(f"✅ Found {len(fights_with_fighters)} fights with fighter relationships")
            for fight in fights_with_fighters:
                print(f"   • Event: {fight.get('event_name', 'N/A')}")
                print(f"     Fighter A: {fight.get('fighters', {}).get('name', 'N/A')}")
                print(f"     Fighter B: {fight.get('fighters', {}).get('name', 'N/A')}")
                print()
        else:
            print(f"❌ Error getting fights with relationships: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception getting relationships: {e}")
    
    print()
    print("📋 SUPABASE DASHBOARD CHECKLIST:")
    print("=" * 60)
    print("1. Go to your Supabase dashboard")
    print("2. Navigate to 'Table Editor'")
    print("3. Check these tables:")
    print("   • events - should show event names and dates")
    print("   • fighters - should show fighter names and weight classes")
    print("   • fights - should show fight details with winner/loser")
    print("4. Check 'Relationships' tab to see foreign key connections")
    print("5. Use 'SQL Editor' to run custom queries")

if __name__ == "__main__":
    verify_supabase_data() 