#!/usr/bin/env python3
"""
Check Fighter Names in Supabase
Compare fighter names between fights.csv and Supabase database
"""

import os
import csv
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FighterNameChecker:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.service_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        self.headers = {
            'apikey': self.service_key,
            'Authorization': f'Bearer {self.service_key}',
            'Content-Type': 'application/json',
        }
    
    def get_supabase_fighters(self):
        """Get all fighter names from Supabase"""
        try:
            response = requests.get(
                f"{self.supabase_url}/rest/v1/fighters",
                headers=self.headers,
                params={'select': 'id,name'}
            )
            
            if response.status_code == 200:
                fighters = response.json()
                return {fighter['name']: fighter['id'] for fighter in fighters}
            else:
                print(f"❌ Failed to get fighters: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Error getting fighters: {e}")
            return {}
    
    def get_csv_fighter_names(self):
        """Get unique fighter names from fights.csv"""
        fighter_names = set()
        
        try:
            csv_path = "../data/processed/fights.csv"
            
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    fighter_names.add(row['fighter1'])
                    fighter_names.add(row['fighter2'])
            
            return fighter_names
            
        except Exception as e:
            print(f"❌ Error reading CSV: {e}")
            return set()
    
    def analyze_mismatches(self):
        """Analyze mismatches between CSV and Supabase fighter names"""
        print("🔍 Analyzing fighter name mismatches...")
        
        # Get fighter names from both sources
        supabase_fighters = self.get_supabase_fighters()
        csv_fighters = self.get_csv_fighter_names()
        
        print(f"\n📊 Summary:")
        print(f"   Supabase fighters: {len(supabase_fighters)}")
        print(f"   CSV unique fighters: {len(csv_fighters)}")
        
        # Find fighters in CSV but not in Supabase
        missing_fighters = csv_fighters - set(supabase_fighters.keys())
        
        print(f"\n❌ Missing fighters ({len(missing_fighters)}):")
        for fighter in sorted(missing_fighters):
            print(f"   - {fighter}")
        
        # Find fighters in Supabase but not in CSV
        extra_fighters = set(supabase_fighters.keys()) - csv_fighters
        
        print(f"\n✅ Extra fighters in Supabase ({len(extra_fighters)}):")
        for fighter in sorted(extra_fighters)[:10]:  # Show first 10
            print(f"   - {fighter}")
        
        if len(extra_fighters) > 10:
            print(f"   ... and {len(extra_fighters) - 10} more")
        
        # Show some examples of fighters that exist in both
        common_fighters = csv_fighters & set(supabase_fighters.keys())
        print(f"\n✅ Common fighters ({len(common_fighters)}):")
        for fighter in sorted(common_fighters)[:10]:  # Show first 10
            print(f"   - {fighter}")
        
        if len(common_fighters) > 10:
            print(f"   ... and {len(common_fighters) - 10} more")
        
        return missing_fighters, extra_fighters, common_fighters

def main():
    checker = FighterNameChecker()
    missing, extra, common = checker.analyze_mismatches()
    
    print(f"\n🎯 Recommendations:")
    print(f"   1. Missing fighters need to be added to Supabase")
    print(f"   2. Consider name normalization for better matching")
    print(f"   3. Check if Wikipedia scraper uses different name formats")

if __name__ == "__main__":
    main() 