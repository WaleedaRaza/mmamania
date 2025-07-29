#!/usr/bin/env python3
"""
Test script for deep UFC fighter profile scraping
"""

import sys
import os
import json
from datetime import datetime

# Add the data directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data'))

from scrapers.ufc_scraper import UFCScraper

def test_deep_scraper():
    """Test the deep scraper with a few top fighters"""
    print("🧪 Testing Deep UFC Fighter Profile Scraper")
    print("=" * 50)
    
    scraper = UFCScraper()
    
    try:
        # First get rankings to find fighter URLs
        print("📊 Getting UFC rankings...")
        rankings = scraper.scrape_rankings()
        
        if not rankings:
            print("❌ No rankings found")
            return
        
        print(f"✅ Found {len(rankings)} rankings")
        
        # Test deep scraping with top 3 fighters
        test_fighters = rankings[:3]
        
        for i, ranking in enumerate(test_fighters):
            if not ranking.get('fighter_url'):
                continue
                
            print(f"\n🔍 Testing deep scrape for {ranking['fighter_name']} ({i+1}/3)")
            print(f"URL: {ranking['fighter_url']}")
            
            try:
                profile = scraper.get_deep_fighter_profile(ranking['fighter_url'])
                
                if profile:
                    print(f"✅ Successfully scraped profile for {profile['name']}")
                    print(f"   Division: {profile['division']}")
                    print(f"   Record: {profile['record']}")
                    print(f"   Stats found: {len([k for k, v in profile['stats'].items() if v != 0])}")
                    print(f"   Fight history: {len(profile['fight_history'])} fights")
                    print(f"   Personal info: {len([k for k, v in profile['personal_info'].items() if v != 'Unknown' and v != 0])} items")
                    
                    # Save individual profile
                    filename = f"test_profile_{profile['id']}.json"
                    with open(filename, 'w') as f:
                        json.dump(profile, f, indent=2)
                    print(f"   💾 Profile saved to {filename}")
                else:
                    print(f"❌ Failed to scrape profile")
                    
            except Exception as e:
                print(f"❌ Error scraping {ranking['fighter_name']}: {e}")
            
            print("-" * 40)
        
        # Test full scrape with limited fighters
        print("\n🚀 Testing full scrape with deep profiles...")
        data = scraper.scrape_all_data()
        
        print(f"✅ Full scrape completed!")
        print(f"   Rankings: {len(data['rankings'])}")
        print(f"   Fighters: {len(data['fighters'])}")
        print(f"   Deep profiles: {len([f for f in data['fighters'] if f.get('stats', {}).get('fight_win_streak', 0) > 0])}")
        
        # Save full data
        with open('test_full_data.json', 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Full data saved to test_full_data.json")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
    finally:
        scraper._close_driver()

if __name__ == "__main__":
    test_deep_scraper() 