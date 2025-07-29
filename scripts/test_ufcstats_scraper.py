#!/usr/bin/env python3
"""
Test UFCStats Scraper
Simple test to verify UFCStats.com scraping works
"""

import requests
from bs4 import BeautifulSoup
import re
import json

def test_ufcstats_scraping():
    """Test scraping UFCStats.com"""
    print("🧪 Testing UFCStats.com scraping...")
    
    try:
        # Test the main fighters page
        url = "http://ufcstats.com/statistics/fighters"
        response = requests.get(url)
        
        if response.status_code == 200:
            print("✅ Successfully connected to UFCStats.com")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for fighter links
            fighter_links = soup.find_all('a', href=re.compile(r'/fighter-details/'))
            print(f"📊 Found {len(fighter_links)} fighter links")
            
            if fighter_links:
                # Test scraping one fighter
                test_fighter_url = fighter_links[0]['href']
                test_fighter_name = fighter_links[0].get_text(strip=True)
                
                print(f"🔍 Testing fighter: {test_fighter_name}")
                print(f"   URL: {test_fighter_url}")
                
                # Show first few fighter names to debug
                print("   First 10 fighter names:")
                for i, link in enumerate(fighter_links[:10]):
                    name = link.get_text(strip=True)
                    print(f"   {i+1}. '{name}'")
                
                # Scrape the fighter's page
                if test_fighter_url.startswith('http'):
                    fighter_response = requests.get(test_fighter_url)
                else:
                    fighter_response = requests.get(f"http://ufcstats.com{test_fighter_url}")
                
                if fighter_response.status_code == 200:
                    fighter_soup = BeautifulSoup(fighter_response.content, 'html.parser')
                    
                    # Extract basic info
                    name_elem = fighter_soup.find('span', class_='b-content__title-highlight')
                    if name_elem:
                        name = name_elem.get_text(strip=True)
                        print(f"   ✅ Name: {name}")
                    
                    # Extract record
                    record_elem = fighter_soup.find('span', class_='b-content__title-record')
                    if record_elem:
                        record_text = record_elem.get_text(strip=True)
                        print(f"   ✅ Record: {record_text}")
                        
                        # Parse record
                        record_match = re.search(r'(\d+)-(\d+)-(\d+)', record_text)
                        if record_match:
                            wins = int(record_match.group(1))
                            losses = int(record_match.group(2))
                            draws = int(record_match.group(3))
                            print(f"   ✅ Parsed: {wins}W-{losses}L-{draws}D")
                    
                    # Extract stats
                    stats_table = fighter_soup.find('div', class_='b-list__info-box')
                    if stats_table:
                        stats = {}
                        rows = stats_table.find_all('li', class_='b-list__box-list-item')
                        for row in rows:
                            text = row.get_text(strip=True)
                            if 'Height:' in text:
                                stats['height'] = text.split('Height:')[1].strip()
                            elif 'Weight:' in text:
                                stats['weight'] = text.split('Weight:')[1].strip()
                            elif 'Reach:' in text:
                                stats['reach'] = text.split('Reach:')[1].strip()
                            elif 'STANCE:' in text:
                                stats['stance'] = text.split('STANCE:')[1].strip()
                        
                        if stats:
                            print(f"   ✅ Stats: {stats}")
                    
                    # Extract fight history
                    fights_table = fighter_soup.find('tbody', class_='b-fight-details__table-body')
                    if fights_table:
                        fight_rows = fights_table.find_all('tr', class_='b-fight-details__table-row')
                        print(f"   ✅ Fight History: {len(fight_rows)} fights")
                        
                        # Show first fight
                        if fight_rows:
                            first_fight = fight_rows[0]
                            cells = first_fight.find_all('td')
                            if len(cells) >= 7:
                                opponent = cells[1].get_text(strip=True)
                                result = cells[2].get_text(strip=True)
                                method = cells[3].get_text(strip=True)
                                print(f"   ✅ Latest Fight: {result} vs {opponent} by {method}")
                    
                    print("🎉 UFCStats scraping test successful!")
                    return True
                else:
                    print(f"❌ Failed to load fighter page: {fighter_response.status_code}")
            else:
                print("❌ No fighter links found")
        else:
            print(f"❌ Failed to connect to UFCStats: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing UFCStats: {e}")
    
    return False

def main():
    """Run the test"""
    print("🥊 UFCStats Scraper Test")
    print("=" * 40)
    
    success = test_ufcstats_scraping()
    
    if success:
        print("\n✅ Test passed! UFCStats scraping is working.")
        print("🚀 Ready to run comprehensive scraper.")
    else:
        print("\n❌ Test failed! Need to debug UFCStats scraping.")

if __name__ == "__main__":
    main() 