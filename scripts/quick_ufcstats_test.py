#!/usr/bin/env python3
"""
Quick UFCStats Test
Test the fixed UFCStats scraper with proper name handling
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def quick_ufcstats_test():
    """Quick test of the fixed UFCStats scraper"""
    print("🧪 Quick UFCStats Test - Fixed Name Handling")
    print("=" * 50)
    
    try:
        url = "http://ufcstats.com/statistics/fighters"
        response = requests.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the fighters table
            fighters_table = soup.find('table', class_='b-statistics__table')
            if not fighters_table:
                print("❌ No fighters table found")
                return
            
            # Get all fighter rows
            rows = fighters_table.find_all('tr', class_='b-statistics__table-row')
            print(f"📊 Found {len(rows)} fighter rows")
            
            # Process first 10 fighters
            fighters_found = 0
            for i, row in enumerate(rows):
                if fighters_found >= 10:
                    break
                    
                try:
                    cells = row.find_all('td')
                    if len(cells) < 11:
                        continue
                    
                    # Extract name components
                    first_name = cells[0].get_text(strip=True)
                    last_name = cells[1].get_text(strip=True)
                    nickname = cells[2].get_text(strip=True)
                    
                    # Skip if no first or last name
                    if not first_name or not last_name:
                        continue
                    
                    # Combine into full name
                    full_name = f"{first_name} {last_name}".strip()
                    if nickname:
                        full_name = f"{full_name} \"{nickname}\""
                    
                    # Extract record
                    wins = cells[7].get_text(strip=True)
                    losses = cells[8].get_text(strip=True)
                    draws = cells[9].get_text(strip=True)
                    
                    # Extract stats
                    height = cells[3].get_text(strip=True)
                    weight = cells[4].get_text(strip=True)
                    reach = cells[5].get_text(strip=True)
                    stance = cells[6].get_text(strip=True)
                    
                    fighters_found += 1
                    
                    print(f"{fighters_found}. {full_name}")
                    print(f"   Record: {wins}W-{losses}L-{draws}D")
                    print(f"   Height: {height} | Weight: {weight} | Reach: {reach}")
                    print(f"   Stance: {stance}")
                    print()
                    
                except Exception as e:
                    print(f"Error processing row {i}: {e}")
                    continue
            
            print(f"✅ Successfully processed {fighters_found} fighters with proper names!")
            
        else:
            print(f"❌ Failed to connect: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run the quick test"""
    quick_ufcstats_test()

if __name__ == "__main__":
    main() 