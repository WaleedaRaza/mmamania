#!/usr/bin/env python3
"""
Test script for comprehensive UFC scraper with detailed fighter profiles
"""

import sys
import os
import json
from datetime import datetime

# Add the data directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data'))

from scrapers.ufc_scraper import UFCScraper

def main():
    """Run comprehensive UFC scraper test"""
    print("🥊 UFC Comprehensive Scraper Test")
    print("=" * 50)
    
    # Initialize scraper
    scraper = UFCScraper()
    
    try:
        # Run comprehensive scraping
        print("🚀 Starting comprehensive UFC data scraping...")
        print("This will scrape rankings and detailed fighter profiles.")
        print("This may take several minutes...")
        print()
        
        start_time = datetime.now()
        
        # Scrape all data
        data = scraper.scrape_all_data()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print()
        print("✅ Scraping completed!")
        print(f"⏱️  Duration: {duration}")
        print()
        
        # Display results
        print("📊 Results Summary:")
        print(f"   • Rankings: {len(data.get('rankings', []))}")
        print(f"   • Fighter Profiles: {len(data.get('fighters', []))}")
        print()
        
        # Show sample fighter data
        if data.get('fighters'):
            print("👤 Sample Fighter Profile:")
            sample_fighter = data['fighters'][0]
            print(f"   • Name: {sample_fighter.get('name', 'Unknown')}")
            print(f"   • Division: {sample_fighter.get('division', 'Unknown')}")
            print(f"   • Record: {sample_fighter.get('record', {})}")
            print(f"   • Age: {sample_fighter.get('age', 'Unknown')}")
            print(f"   • Height: {sample_fighter.get('height', 'Unknown')} inches")
            print(f"   • Weight: {sample_fighter.get('weight', 'Unknown')} lbs")
            print(f"   • Reach: {sample_fighter.get('reach', 'Unknown')} inches")
            print(f"   • Fighting Style: {sample_fighter.get('fighting_style', 'Unknown')}")
            print(f"   • Training At: {sample_fighter.get('training_at', 'Unknown')}")
            print(f"   • Fight History: {len(sample_fighter.get('fight_history', []))} fights")
            print(f"   • Stats Available: {len(sample_fighter.get('stats', {}))} metrics")
            print()
        
        # Save raw data
        raw_file = f"ufc_comprehensive_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(raw_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Raw data saved to: {raw_file}")
        
        # Save processed data for Flutter
        processed_file = "assets/data/ufc_data.json"
        os.makedirs(os.path.dirname(processed_file), exist_ok=True)
        with open(processed_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"📱 Processed data saved to: {processed_file}")
        
        # Show detailed stats for first few fighters
        if data.get('fighters'):
            print()
            print("📈 Detailed Stats Sample:")
            for i, fighter in enumerate(data['fighters'][:3]):
                print(f"\n{i+1}. {fighter.get('name', 'Unknown')}:")
                stats = fighter.get('stats', {})
                if stats:
                    print(f"   • Win Streak: {stats.get('fight_win_streak', 0)}")
                    print(f"   • KO Wins: {stats.get('wins_by_knockout', 0)}")
                    print(f"   • Submission Wins: {stats.get('wins_by_submission', 0)}")
                    print(f"   • Striking Accuracy: {stats.get('striking_accuracy', 0)}%")
                    print(f"   • Takedown Accuracy: {stats.get('takedown_accuracy', 0)}%")
                    print(f"   • Average Fight Time: {stats.get('average_fight_time', '0:00')}")
        
        print()
        print("🎉 Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 