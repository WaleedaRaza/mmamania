#!/usr/bin/env python3
"""
Quick UFC Rankings Scraper
Get rankings with real records only - no complex fighter profiles
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data'))

from scrapers.ufc_scraper import UFCScraper
import json
from datetime import datetime

def quick_rankings_scrape():
    """Quick scrape of rankings with real records"""
    print("🚀 Quick UFC Rankings Scraper")
    print("=" * 40)
    
    try:
        # Initialize scraper
        scraper = UFCScraper()
        
        # Scrape rankings with real records
        print("📊 Scraping UFC rankings with real records...")
        rankings = scraper.scrape_rankings()
        
        if not rankings:
            print("❌ No rankings found")
            return
            
        print(f"✅ Successfully scraped {len(rankings)} rankings")
        
        # Show sample data
        if rankings:
            sample = rankings[0]
            print(f"📊 Sample: {sample['fighter_name']} - {sample['record']['wins']}W-{sample['record']['losses']}L-{sample['record']['draws']}D")
        
        # Create data structure for Flutter
        data = {
            'rankings': rankings,
            'fighters': [],  # Empty for now
            'scraped_at': datetime.now().isoformat(),
            'total_rankings': len(rankings)
        }
        
        # Save to multiple locations
        output_files = [
            'scripts/assets/data/ufc_data.json',
            'assets/data/ufc_data.json'
        ]
        
        for output_file in output_files:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved to: {output_file}")
        
        # Print summary
        print("\n📈 Data Summary:")
        print("-" * 20)
        divisions = {}
        for ranking in rankings:
            div = ranking['division']
            if div not in divisions:
                divisions[div] = 0
            divisions[div] += 1
        
        for division, count in divisions.items():
            print(f"   {division}: {count} fighters")
        
        print(f"\n🎉 Quick scraping completed successfully!")
        print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    quick_rankings_scrape() 