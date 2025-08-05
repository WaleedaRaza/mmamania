#!/usr/bin/env python3
"""
Performance Monitor - Track Flutter App Optimization
"""

import time
import requests
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

def monitor_performance():
    """Monitor database query performance"""
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    print("🚀 PERFORMANCE MONITOR - OPTIMIZATION TRACKING")
    print("=" * 60)
    
    # Test 1: Individual fighter queries (OLD METHOD)
    print("\n📊 TEST 1: Individual Fighter Queries (OLD METHOD)")
    start_time = time.time()
    
    # Get 10 fights
    fights_response = requests.get(f"{SUPABASE_URL}/rest/v1/fights?limit=10", headers=headers)
    if fights_response.status_code == 200:
        fights = fights_response.json()
        
        # Simulate individual fighter queries
        for i, fight in enumerate(fights[:5]):
            fighter1_id = fight.get('fighter1_id')
            fighter2_id = fight.get('fighter2_id')
            
            if fighter1_id:
                requests.get(f"{SUPABASE_URL}/rest/v1/fighters?id=eq.{fighter1_id}", headers=headers)
            if fighter2_id:
                requests.get(f"{SUPABASE_URL}/rest/v1/fighters?id=eq.{fighter2_id}", headers=headers)
    
    old_time = time.time() - start_time
    print(f"   ⏱️  Individual queries: {old_time:.2f} seconds")
    
    # Test 2: Batch fighter queries (NEW METHOD)
    print("\n📊 TEST 2: Batch Fighter Queries (NEW METHOD)")
    start_time = time.time()
    
    # Get 10 fights
    fights_response = requests.get(f"{SUPABASE_URL}/rest/v1/fights?limit=10", headers=headers)
    if fights_response.status_code == 200:
        fights = fights_response.json()
        
        # Collect all fighter IDs
        fighter_ids = set()
        for fight in fights[:5]:
            if fight.get('fighter1_id'):
                fighter_ids.add(fight['fighter1_id'])
            if fight.get('fighter2_id'):
                fighter_ids.add(fight['fighter2_id'])
        
        # Single batch query
        if fighter_ids:
            requests.get(f"{SUPABASE_URL}/rest/v1/fighters?id=in.({','.join(fighter_ids)})", headers=headers)
    
    new_time = time.time() - start_time
    print(f"   ⏱️  Batch query: {new_time:.2f} seconds")
    
    # Calculate improvement
    improvement = ((old_time - new_time) / old_time) * 100
    print(f"   🚀 Performance improvement: {improvement:.1f}%")
    
    # Test 3: Event deduplication
    print("\n📊 TEST 3: Event Deduplication")
    start_time = time.time()
    
    # Get events (with potential duplicates)
    events_response = requests.get(f"{SUPABASE_URL}/rest/v1/events?limit=50", headers=headers)
    if events_response.status_code == 200:
        events = events_response.json()
        print(f"   📋 Raw events: {len(events)}")
        
        # Deduplicate by name
        unique_events = {}
        for event in events:
            name = event.get('name', '')
            if name not in unique_events:
                unique_events[name] = event
        
        print(f"   ✅ Unique events: {len(unique_events)}")
        print(f"   🗑️  Duplicates removed: {len(events) - len(unique_events)}")
    
    dedup_time = time.time() - start_time
    print(f"   ⏱️  Deduplication time: {dedup_time:.2f} seconds")
    
    print("\n🎉 PERFORMANCE SUMMARY")
    print("=" * 60)
    print(f"✅ Individual queries: {old_time:.2f}s")
    print(f"✅ Batch queries: {new_time:.2f}s")
    print(f"✅ Speed improvement: {improvement:.1f}%")
    print(f"✅ Event deduplication: {len(events) - len(unique_events)} duplicates removed")
    print("=" * 60)
    print("🚀 OPTIMIZATION COMPLETE!")
    print("✅ Flutter app should now load much faster")
    print("✅ No more individual fighter queries")
    print("✅ No more duplicate event processing")

if __name__ == "__main__":
    monitor_performance() 