#!/usr/bin/env python3
"""
Extract fighter URLs from rankings and run fighters scraper in batches
"""

import json
import subprocess
import os
import time

def extract_fighter_urls():
    """Extract fighter URLs from rankings JSON"""
    print("🔗 Extracting fighter URLs from rankings...")
    
    try:
        with open('ufc_scraper/rankings_clean.json', 'r') as f:
            rankings = json.load(f)
        
        fighter_urls = []
        for ranking in rankings:
            fighter_url = ranking.get('fighter_url', '')
            if fighter_url and fighter_url not in fighter_urls:
                fighter_urls.append(fighter_url)
        
        print(f"✅ Found {len(fighter_urls)} unique fighter URLs")
        
        # Save to input file
        os.makedirs('ufc_scraper/input', exist_ok=True)
        with open('ufc_scraper/input/urls.txt', 'w') as f:
            for url in fighter_urls:
                f.write(f"{url}\n")
        
        print(f"💾 Saved fighter URLs to ufc_scraper/input/urls.txt")
        return fighter_urls
        
    except Exception as e:
        print(f"❌ Error extracting fighter URLs: {e}")
        return []

def run_fighters_scraper_batch(urls, batch_num, total_batches):
    """Run the fighters scraper for a batch of URLs"""
    print(f"\n👊 Running fighters scraper batch {batch_num}/{total_batches} ({len(urls)} URLs)...")
    
    # Create batch file
    batch_file = f'ufc_scraper/input/batch_{batch_num}.txt'
    with open(batch_file, 'w') as f:
        for url in urls:
            f.write(f"{url}\n")
    
    try:
        result = subprocess.run([
            f"cd ufc_scraper && scrapy crawl fighters -a input_file=input/batch_{batch_num}.txt -o fighters_batch_{batch_num}.json -L INFO"
        ], shell=True, capture_output=True, text=True, timeout=300)  # 5 minute timeout
        
        if result.returncode == 0:
            print(f"✅ Batch {batch_num} completed successfully")
            return True
        else:
            print(f"❌ Batch {batch_num} failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ Batch {batch_num} timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Error running batch {batch_num}: {e}")
        return False

def run_fighters_scraper_in_batches(fighter_urls, batch_size=10):
    """Run fighters scraper in smaller batches to avoid hanging"""
    print(f"\n🔄 Processing {len(fighter_urls)} fighter URLs in batches of {batch_size}")
    
    # Split URLs into batches
    batches = [fighter_urls[i:i + batch_size] for i in range(0, len(fighter_urls), batch_size)]
    total_batches = len(batches)
    
    successful_batches = 0
    
    for i, batch in enumerate(batches, 1):
        success = run_fighters_scraper_batch(batch, i, total_batches)
        if success:
            successful_batches += 1
        
        # Add delay between batches to be respectful
        if i < total_batches:
            print(f"⏳ Waiting 3 seconds before next batch...")
            time.sleep(3)
    
    print(f"\n📊 Batch processing complete: {successful_batches}/{total_batches} batches successful")
    return successful_batches == total_batches

def merge_batch_files():
    """Merge all batch fighter files into one"""
    print("\n🔄 Merging batch files...")
    
    all_fighters = []
    batch_num = 1
    
    while os.path.exists(f'ufc_scraper/fighters_batch_{batch_num}.json'):
        try:
            with open(f'ufc_scraper/fighters_batch_{batch_num}.json', 'r') as f:
                batch_fighters = json.load(f)
                all_fighters.extend(batch_fighters)
                print(f"✅ Merged batch {batch_num} ({len(batch_fighters)} fighters)")
        except Exception as e:
            print(f"⚠️ Error merging batch {batch_num}: {e}")
        
        batch_num += 1
    
    # Save merged fighters
    with open('ufc_scraper/fighters.json', 'w') as f:
        json.dump(all_fighters, f, indent=2)
    
    print(f"💾 Saved {len(all_fighters)} total fighters to ufc_scraper/fighters.json")
    return all_fighters

def merge_data():
    """Merge rankings and fighters data"""
    print("\n🔄 Merging data...")
    
    try:
        # Load rankings
        with open('ufc_scraper/rankings_clean.json', 'r') as f:
            rankings = json.load(f)
        
        # Load fighters
        with open('ufc_scraper/fighters.json', 'r') as f:
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
            'scraped_at': '2025-06-30T22:00:00.000000',
            'total_rankings': len(merged_rankings),
            'total_fighters': len(fighters),
            'rankings_with_profiles': len([r for r in merged_rankings if r['has_detailed_profile']])
        }
        
        # Save merged data
        os.makedirs('assets/data', exist_ok=True)
        with open('assets/data/ufc_data.json', 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved merged data to assets/data/ufc_data.json")
        print(f"\n📊 Final Data Summary:")
        print(f"   Rankings: {merged_data['total_rankings']}")
        print(f"   Fighters: {merged_data['total_fighters']}")
        print(f"   Rankings with profiles: {merged_data['rankings_with_profiles']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error merging data: {e}")
        return False

def main():
    """Main function"""
    print("🚀 UFC Data Pipeline (Batch Processing)")
    print("=" * 40)
    
    # Step 1: Extract fighter URLs
    fighter_urls = extract_fighter_urls()
    if not fighter_urls:
        return
    
    # Step 2: Run fighters scraper in batches
    if not run_fighters_scraper_in_batches(fighter_urls, batch_size=10):
        print("⚠️ Some batches failed, but continuing with merge...")
    
    # Step 3: Merge batch files
    merge_batch_files()
    
    # Step 4: Merge data
    if not merge_data():
        return
    
    print("\n🎉 UFC data pipeline completed successfully!")

if __name__ == "__main__":
    main() 