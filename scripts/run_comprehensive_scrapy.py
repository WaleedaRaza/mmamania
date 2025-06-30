#!/usr/bin/env python3
"""
Comprehensive UFC Scrapy Runner
Run both rankings and fighters scrapers, then merge data for Flutter integration
"""

import os
import sys
import subprocess
import json
from datetime import datetime

def run_comprehensive_scrapy():
    """Run comprehensive UFC scraping with Scrapy"""
    print("🚀 UFC Comprehensive Scrapy Runner")
    print("=" * 50)
    
    # Change to Scrapy project directory
    scrapy_dir = "ufc_scraper"
    if not os.path.exists(scrapy_dir):
        print(f"❌ Scrapy project not found: {scrapy_dir}")
        return
    
    os.chdir(scrapy_dir)
    
    try:
        # Step 1: Run rankings scraper
        print("\n📊 Step 1: Scraping UFC Rankings...")
        rankings_result = subprocess.run([
            "scrapy", "crawl", "rankings", 
            "-o", "rankings.json",
            "--nolog"
        ], capture_output=True, text=True)
        
        if rankings_result.returncode == 0:
            print("✅ Rankings scraper completed successfully")
        else:
            print(f"❌ Rankings scraper failed: {rankings_result.stderr}")
            return
        
        # Step 2: Extract fighter URLs from rankings
        print("\n🔗 Step 2: Extracting fighter URLs from rankings...")
        fighter_urls = extract_fighter_urls("rankings.json")
        
        if not fighter_urls:
            print("❌ No fighter URLs found in rankings")
            return
        
        # Save fighter URLs to input file
        with open("input/urls.txt", "w") as f:
            for url in fighter_urls:
                f.write(f"{url}\n")
        
        print(f"✅ Extracted {len(fighter_urls)} fighter URLs")
        
        # Step 3: Run fighters scraper
        print(f"\n👊 Step 3: Scraping {len(fighter_urls)} Fighter Profiles...")
        fighters_result = subprocess.run([
            "scrapy", "crawl", "fighters",
            "-a", f"input_file=input/urls.txt",
            "-o", "fighters.json",
            "--nolog"
        ], capture_output=True, text=True)
        
        if fighters_result.returncode == 0:
            print("✅ Fighters scraper completed successfully")
        else:
            print(f"❌ Fighters scraper failed: {fighters_result.stderr}")
            return
        
        # Step 4: Merge data
        print("\n🔄 Step 4: Merging rankings and fighters data...")
        merged_data = merge_data("rankings.json", "fighters.json")
        
        # Step 5: Save merged data
        print("\n💾 Step 5: Saving merged data...")
        save_merged_data(merged_data)
        
        print("\n🎉 Comprehensive UFC scraping completed successfully!")
        print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ Error during comprehensive scraping: {e}")
    finally:
        # Return to original directory
        os.chdir("..")

def extract_fighter_urls(rankings_file):
    """Extract fighter URLs from rankings JSON"""
    try:
        with open(rankings_file, 'r') as f:
            rankings = json.load(f)
        
        fighter_urls = []
        for ranking in rankings:
            fighter_url = ranking.get('fighter_url', '')
            if fighter_url and fighter_url not in fighter_urls:
                fighter_urls.append(fighter_url)
        
        return fighter_urls
    except Exception as e:
        print(f"❌ Error extracting fighter URLs: {e}")
        return []

def merge_data(rankings_file, fighters_file):
    """Merge rankings and fighters data"""
    try:
        # Load rankings
        with open(rankings_file, 'r') as f:
            rankings = json.load(f)
        
        # Load fighters
        with open(fighters_file, 'r') as f:
            fighters = json.load(f)
        
        # Create fighters lookup by URL
        fighters_by_url = {}
        for fighter in fighters:
            fighters_by_url[fighter['fighter_url']] = fighter
        
        # Merge fighter data into rankings
        merged_rankings = []
        for ranking in rankings:
            fighter_url = ranking.get('fighter_url', '')
            fighter_data = fighters_by_url.get(fighter_url, {})
            
            # Merge fighter data into ranking
            merged_ranking = ranking.copy()
            merged_ranking.update({
                'fighter_profile': fighter_data,
                'has_detailed_profile': bool(fighter_data),
                'nickname': fighter_data.get('nickname', ''),
                'personal_info': fighter_data.get('personal_info', {}),
                'stats': fighter_data.get('stats', {}),
                'fight_history': fighter_data.get('fight_history', [])
            })
            
            merged_rankings.append(merged_ranking)
        
        # Create final merged data structure
        merged_data = {
            'rankings': merged_rankings,
            'fighters': fighters,
            'scraped_at': datetime.now().isoformat(),
            'total_rankings': len(merged_rankings),
            'total_fighters': len(fighters),
            'rankings_with_profiles': len([r for r in merged_rankings if r['has_detailed_profile']])
        }
        
        return merged_data
    except Exception as e:
        print(f"❌ Error merging data: {e}")
        return {}

def save_merged_data(merged_data):
    """Save merged data to multiple locations"""
    output_files = [
        "ufc_merged_data.json",
        "../assets/data/ufc_data.json"
    ]
    
    for output_file in output_files:
        try:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(merged_data, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved to: {output_file}")
        except Exception as e:
            print(f"❌ Error saving to {output_file}: {e}")
    
    # Print summary
    print(f"\n📊 Final Data Summary:")
    print(f"   Rankings: {merged_data.get('total_rankings', 0)}")
    print(f"   Fighters: {merged_data.get('total_fighters', 0)}")
    print(f"   Rankings with profiles: {merged_data.get('rankings_with_profiles', 0)}")

if __name__ == "__main__":
    run_comprehensive_scrapy() 