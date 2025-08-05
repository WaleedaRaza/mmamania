#!/usr/bin/env python3
"""
Diagnose Data Structure Issues
Analyze the current database structure and identify what needs to be fixed
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv('scripts/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

def diagnose_data_structure():
    """Diagnose the current data structure issues"""
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    print("🔍 DATA STRUCTURE DIAGNOSIS")
    print("=" * 60)
    
    # Check current schema
    print("📊 CURRENT SCHEMA ANALYSIS:")
    print("-" * 40)
    
    # Check events table structure
    try:
        response = requests.get(f"{SUPABASE_URL}/rest/v1/events?select=*&limit=1", headers=headers)
        if response.status_code == 200:
            events = response.json()
            if events:
                event = events[0]
                print("✅ EVENTS TABLE COLUMNS:")
                for key, value in event.items():
                    print(f"   • {key}: {type(value).__name__}")
        else:
            print(f"❌ Error getting events: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception getting events: {e}")
    
    print()
    
    # Check fights table structure
    try:
        response = requests.get(f"{SUPABASE_URL}/rest/v1/fights?select=*&limit=1", headers=headers)
        if response.status_code == 200:
            fights = response.json()
            if fights:
                fight = fights[0]
                print("✅ FIGHTS TABLE COLUMNS:")
                for key, value in fight.items():
                    print(f"   • {key}: {type(value).__name__}")
        else:
            print(f"❌ Error getting fights: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception getting fights: {e}")
    
    print()
    
    # Check data relationships
    print("🔗 RELATIONSHIP ANALYSIS:")
    print("-" * 40)
    
    # Check if fights have event_id
    try:
        response = requests.get(f"{SUPABASE_URL}/rest/v1/fights?select=event_id&limit=5", headers=headers)
        if response.status_code == 200:
            fights = response.json()
            has_event_id = any('event_id' in fight for fight in fights)
            print(f"✅ Fights have event_id: {has_event_id}")
        else:
            print("❌ Fights table missing event_id column")
    except Exception as e:
        print(f"❌ Exception checking event_id: {e}")
    
    # Check if fights have winner_id/loser_id
    try:
        response = requests.get(f"{SUPABASE_URL}/rest/v1/fights?select=winner_id,loser_id&limit=5", headers=headers)
        if response.status_code == 200:
            fights = response.json()
            has_winner_loser = any('winner_id' in fight or 'loser_id' in fight for fight in fights)
            print(f"✅ Fights have winner_id/loser_id: {has_winner_loser}")
        else:
            print("❌ Fights table missing winner_id/loser_id columns")
    except Exception as e:
        print(f"❌ Exception checking winner/loser: {e}")
    
    print()
    
    # Check data population
    print("📈 DATA POPULATION ANALYSIS:")
    print("-" * 40)
    
    try:
        # Count events
        response = requests.get(f"{SUPABASE_URL}/rest/v1/events?select=id&limit=1000", headers=headers)
        if response.status_code == 200:
            events = response.json()
            print(f"✅ Events count: {len(events)}")
        
        # Count fights
        response = requests.get(f"{SUPABASE_URL}/rest/v1/fights?select=id&limit=1000", headers=headers)
        if response.status_code == 200:
            fights = response.json()
            print(f"✅ Fights count: {len(fights)}")
        
        # Count fighters
        response = requests.get(f"{SUPABASE_URL}/rest/v1/fighters?select=id&limit=1000", headers=headers)
        if response.status_code == 200:
            fighters = response.json()
            print(f"✅ Fighters count: {len(fighters)}")
            
    except Exception as e:
        print(f"❌ Exception counting data: {e}")
    
    print()
    
    # Show sample fight data
    print("🔍 SAMPLE FIGHT DATA ANALYSIS:")
    print("-" * 40)
    
    try:
        response = requests.get(f"{SUPABASE_URL}/rest/v1/fights?select=*&limit=3", headers=headers)
        if response.status_code == 200:
            fights = response.json()
            for i, fight in enumerate(fights):
                print(f"Fight {i+1}:")
                for key, value in fight.items():
                    print(f"   {key}: {value}")
                print()
        else:
            print(f"❌ Error getting sample fights: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception getting sample fights: {e}")
    
    print()
    print("📋 REQUIRED FIXES:")
    print("=" * 60)
    print("1. Add event_id column to fights table")
    print("2. Add winner_id and loser_id columns to fights table")
    print("3. Update scraper to populate correct structure")
    print("4. Fix data relationships between events and fights")
    print("5. Ensure proper winner/loser identification")

if __name__ == "__main__":
    diagnose_data_structure() 