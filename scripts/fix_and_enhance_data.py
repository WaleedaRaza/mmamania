#!/usr/bin/env python3
"""
Fix and enhance UFC data with basic fighter profiles
"""

import json
import os
from datetime import datetime

def fix_division_names(division):
    """Fix malformed division names"""
    if not division:
        return "Unknown Division"
    
    # Clean up the division name
    division = division.replace("'S", "'s").replace("top Rank", "").strip()
    
    # Map common variations
    division_mapping = {
        "Men'S Pound For Pound": "Men's Pound for Pound",
        "Women'S Pound For Pound": "Women's Pound for Pound",
        "Men'S Flyweight": "Men's Flyweight",
        "Women'S Flyweight": "Women's Flyweight",
        "Men'S Bantamweight": "Men's Bantamweight",
        "Women'S Bantamweight": "Women's Bantamweight",
        "Men'S Featherweight": "Men's Featherweight",
        "Women'S Featherweight": "Women's Featherweight",
        "Men'S Lightweight": "Men's Lightweight",
        "Men'S Welterweight": "Men's Welterweight",
        "Men'S Middleweight": "Men's Middleweight",
        "Men'S Light Heavyweight": "Men's Light Heavyweight",
        "Men'S Heavyweight": "Men's Heavyweight",
        "Women'S Strawweight": "Women's Strawweight",
    }
    
    return division_mapping.get(division, division)

def create_basic_fighter_profile(ranking):
    """Create a basic fighter profile from ranking data"""
    fighter_id = ranking.get('fighter_url', '').split('/')[-1] if ranking.get('fighter_url') else ''
    
    return {
        'id': fighter_id,
        'name': ranking.get('fighter_name', 'Unknown'),
        'division': fix_division_names(ranking.get('division', '')),
        'record': {
            'wins': 0,  # We'll need to scrape this separately
            'losses': 0,
            'draws': 0
        },
        'image_url': None,
        'status': 'Active',
        'place_of_birth': None,
        'training_at': None,
        'fighting_style': None,
        'age': None,
        'height': None,
        'weight': None,
        'octagon_debut': None,
        'reach': None,
        'leg_reach': None,
        'stats': {
            'fight_win_streak': 0,
            'wins_by_knockout': 0,
            'wins_by_submission': 0,
            'striking_accuracy': 0.0,
            'sig_strikes_landed': 0,
            'sig_strikes_attempted': 0,
            'takedown_accuracy': 0.0,
            'takedowns_landed': 0,
            'takedowns_attempted': 0,
            'sig_strikes_landed_per_min': 0.0,
            'sig_strikes_absorbed_per_min': 0.0,
            'takedown_avg_per_15_min': 0.0,
            'submission_avg_per_15_min': 0.0,
            'sig_strikes_defense': 0.0,
            'takedown_defense': 0.0,
            'knockdown_avg': 0.0,
            'average_fight_time': '0:00'
        },
        'fight_history': [],
        'scraped_at': datetime.now().isoformat()
    }

def main():
    """Fix and enhance UFC data"""
    print("🔧 Fixing and enhancing UFC data...")
    
    # Load current data
    try:
        with open('assets/data/ufc_data.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ No existing UFC data found. Please run the scraper first.")
        return
    
    print(f"📊 Loaded {len(data.get('rankings', []))} rankings")
    
    # Fix rankings
    fixed_rankings = []
    fighters = []
    fighter_ids = set()
    
    for ranking in data.get('rankings', []):
        # Fix division name
        ranking['division'] = fix_division_names(ranking.get('division', ''))
        
        # Create unique ID
        fighter_url = ranking.get('fighter_url', '')
        fighter_id = fighter_url.split('/')[-1] if fighter_url else f"fighter_{len(fixed_rankings)}"
        ranking['id'] = fighter_id
        
        # Only add each fighter once
        if fighter_id not in fighter_ids:
            fighter_ids.add(fighter_id)
            fixed_rankings.append(ranking)
            
            # Create basic fighter profile
            fighter_profile = create_basic_fighter_profile(ranking)
            fighters.append(fighter_profile)
    
    # Create enhanced data
    enhanced_data = {
        'rankings': fixed_rankings,
        'fighters': fighters,
        'scraped_at': datetime.now().isoformat()
    }
    
    # Save enhanced data
    with open('assets/data/ufc_data.json', 'w') as f:
        json.dump(enhanced_data, f, indent=2)
    
    print(f"✅ Fixed {len(fixed_rankings)} rankings")
    print(f"✅ Created {len(fighters)} fighter profiles")
    print(f"📱 Data saved to assets/data/ufc_data.json")
    
    # Show sample data
    if fixed_rankings:
        print("\n📋 Sample Rankings:")
        for i, ranking in enumerate(fixed_rankings[:5]):
            print(f"  {i+1}. {ranking['fighter_name']} - {ranking['division']} #{ranking['rank']}")
    
    if fighters:
        print("\n👤 Sample Fighter Profiles:")
        for i, fighter in enumerate(fighters[:3]):
            print(f"  {i+1}. {fighter['name']} ({fighter['division']})")
            print(f"     ID: {fighter['id']}")
            print(f"     Record: {fighter['record']['wins']}-{fighter['record']['losses']}-{fighter['record']['draws']}")

if __name__ == "__main__":
    main() 