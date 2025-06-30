#!/usr/bin/env python3
"""
UFC Data Scraper and Processor Script
Runs the scraper and processes the data for FightHub
"""

import sys
import os
import json
from datetime import datetime

# Add the data directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data'))

from scrapers.ufc_scraper import UFCScraper
from processors.ufc_data_processor import UFCDataProcessor

def main():
    print("🚀 Starting UFC Data Scraping and Processing...")
    print("=" * 50)
    
    # Initialize scraper and processor
    scraper = UFCScraper()
    processor = UFCDataProcessor()
    
    try:
        # Step 1: Scrape raw data
        print("📊 Scraping UFC data...")
        raw_data = scraper.scrape_all_data()
        
        if not raw_data:
            print("❌ No data scraped. Exiting.")
            return
        
        print(f"✅ Scraped {len(raw_data.get('rankings', []))} rankings")
        print(f"✅ Scraped {len(raw_data.get('upcoming_events', []))} upcoming events")
        print(f"✅ Scraped {len(raw_data.get('past_events', []))} past events")
        print(f"✅ Scraped {len(raw_data.get('upcoming_fights', []))} upcoming fights")
        print(f"✅ Scraped {len(raw_data.get('past_results', []))} past results")
        
        # Step 2: Save raw data
        raw_data_file = 'ufc_raw_data.json'
        with open(raw_data_file, 'w') as f:
            json.dump(raw_data, f, indent=2)
        print(f"💾 Raw data saved to {raw_data_file}")
        
        # Step 3: Process data
        print("\n🔧 Processing data...")
        processed_data = processor.process_raw_data(raw_data)
        
        if not processed_data:
            print("❌ Data processing failed. Exiting.")
            return
        
        # Step 4: Save processed data
        processed_data_file = 'ufc_processed_data.json'
        processor.save_processed_data(processed_data_file)
        print(f"💾 Processed data saved to {processed_data_file}")
        
        # Step 5: Print statistics
        print("\n📈 Data Statistics:")
        print("-" * 30)
        metadata = processed_data.get('metadata', {})
        print(f"Total Fighters: {metadata.get('total_fighters', 0)}")
        print(f"Total Rankings: {metadata.get('total_rankings', 0)}")
        print(f"Upcoming Events: {metadata.get('total_upcoming_events', 0)}")
        print(f"Past Events: {metadata.get('total_past_events', 0)}")
        print(f"Upcoming Fights: {metadata.get('total_upcoming_fights', 0)}")
        print(f"Past Results: {metadata.get('total_past_results', 0)}")
        
        # Step 6: Copy to Flutter assets (if directory exists)
        flutter_assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'data')
        if os.path.exists(flutter_assets_dir):
            flutter_data_file = os.path.join(flutter_assets_dir, 'ufc_data.json')
            with open(flutter_data_file, 'w') as f:
                json.dump(processed_data, f, indent=2)
            print(f"📱 Data copied to Flutter assets: {flutter_data_file}")
        else:
            print("📱 Flutter assets directory not found. Create assets/data/ to auto-copy data.")
        
        print("\n🎉 UFC Data scraping and processing completed successfully!")
        print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ Error during scraping/processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 