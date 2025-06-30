#!/usr/bin/env python3
"""
Check UFC data structure and records
"""

import json

def check_data():
    """Check the UFC data structure"""
    with open('assets/data/ufc_data.json', 'r') as f:
        data = json.load(f)
    
    rankings = data['rankings']
    
    print("📊 Sample rankings with records:")
    for i, r in enumerate(rankings[:5]):
        print(f"{i+1}. {r['fighter_name']}: {r['record']}")
    
    print("\n🔍 Checking fighter profiles:")
    profiles_with_records = [r for r in rankings if r.get('has_detailed_profile') and r.get('fighter_profile')]
    print(f"Rankings with profiles: {len(profiles_with_records)}")
    
    if profiles_with_records:
        sample = profiles_with_records[0]
        print(f"Sample profile record: {sample['fighter_profile']['record']}")
        print(f"Sample profile name: {sample['fighter_profile']['name']}")
    
    print(f"\n📈 Total rankings: {len(rankings)}")
    print(f"📈 Total fighters: {len(data['fighters'])}")
    print(f"📈 Rankings with profiles: {data['rankings_with_profiles']}")

if __name__ == "__main__":
    check_data() 