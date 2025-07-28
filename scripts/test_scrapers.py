#!/usr/bin/env python3
"""
Test Scrapers - Validate Data Quality
Tests each scraper individually to ensure data quality
"""

import sys
import os
import json
from datetime import datetime

# Add scrapers to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers', 'ufc'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers', 'wikipedia'))

def test_ufc_rankings():
    """Test UFC rankings scraper"""
    print("🔍 Testing UFC Rankings Scraper...")
    
    try:
        from quick_rankings_scraper import QuickRankingsScraper
        
        scraper = QuickRankingsScraper()
        rankings = scraper.scrape_rankings()
        
        print(f"✅ Scraped {len(rankings)} rankings")
        
        # Show sample data
        if rankings:
            print("\n📊 Sample Rankings Data:")
            for i, ranking in enumerate(rankings[:3]):
                print(f"  {i+1}. {ranking.get('name', 'Unknown')} - {ranking.get('division', 'Unknown')} #{ranking.get('rank', 'Unknown')}")
        
        return rankings
        
    except Exception as e:
        print(f"❌ UFC Rankings scraper failed: {e}")
        return []

def test_ufc_fighter_profiles():
    """Test UFC fighter profile scraper"""
    print("\n🔍 Testing UFC Fighter Profile Scraper...")
    
    try:
        from quick_fighter_profile_scraper import QuickFighterProfileScraper
        
        scraper = QuickFighterProfileScraper()
        
        # Test with a few known fighter URLs
        test_urls = [
            "https://www.ufc.com/athlete/israel-adesanya",
            "https://www.ufc.com/athlete/alex-pereira",
            "https://www.ufc.com/athlete/jon-jones"
        ]
        
        profiles = scraper.scrape_fighter_profiles(test_urls, limit=3)
        
        print(f"✅ Scraped {len(profiles)} fighter profiles")
        
        # Show sample data
        if profiles:
            print("\n📊 Sample Fighter Data:")
            for i, profile in enumerate(profiles[:2]):
                print(f"  {i+1}. {profile.get('name', 'Unknown')} - {profile.get('record', 'Unknown')} - {profile.get('division', 'Unknown')}")
        
        return profiles
        
    except Exception as e:
        print(f"❌ UFC Fighter Profile scraper failed: {e}")
        return []

def test_wikipedia_scraper():
    """Test Wikipedia scraper"""
    print("\n🔍 Testing Wikipedia Scraper...")
    
    try:
        from quick_wikipedia_scraper import QuickWikipediaScraper
        
        scraper = QuickWikipediaScraper()
        # Test scraping recent events
        data = scraper.scrape_recent_events()
        
        print(f"✅ Scraped {len(data)} Wikipedia events")
        
        if data:
            print("\n📊 Sample Wikipedia Data:")
            for i, event in enumerate(data[:2]):
                print(f"  {i+1}. {event.get('name', 'Unknown')} - {event.get('date', 'Unknown')}")
        
        return data
        
    except Exception as e:
        print(f"❌ Wikipedia scraper failed: {e}")
        return []

def main():
    """Run all scraper tests"""
    print("🚀 Starting Scraper Validation Tests...\n")
    
    # Test each scraper
    rankings = test_ufc_rankings()
    profiles = test_ufc_fighter_profiles()
    wiki_data = test_wikipedia_scraper()
    
    # Summary
    print("\n📋 VALIDATION SUMMARY:")
    print(f"  UFC Rankings: {'✅' if rankings else '❌'} ({len(rankings)} items)")
    print(f"  Fighter Profiles: {'✅' if profiles else '❌'} ({len(profiles)} items)")
    print(f"  Wikipedia Data: {'✅' if wiki_data else '❌'}")
    
    # Save test results
    test_results = {
        'timestamp': datetime.now().isoformat(),
        'rankings_count': len(rankings),
        'profiles_count': len(profiles),
        'wiki_data': bool(wiki_data),
        'sample_rankings': rankings[:5] if rankings else [],
        'sample_profiles': profiles[:3] if profiles else []
    }
    
    with open('test_results.json', 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\n💾 Test results saved to test_results.json")

if __name__ == "__main__":
    main() 