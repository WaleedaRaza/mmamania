#!/usr/bin/env python3
"""
Test Single Event Scraping
Test scraping a single UFC event to debug the fight card table detection
"""

import requests
from bs4 import BeautifulSoup

def test_single_event():
    """Test scraping a single UFC event"""
    event_url = "https://en.wikipedia.org/wiki/UFC_on_ESPN:_Taira_vs._Park"
    
    try:
        response = requests.get(event_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("🔍 Testing UFC on ESPN: Taira vs. Park")
        print("=" * 50)
        
        # Find all tables
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        for i, table in enumerate(tables):
            print(f"\n📊 Table {i+1}:")
            
            # Check if it has wikitable class
            if 'wikitable' in table.get('class', []):
                print("   ✅ Has 'wikitable' class")
            else:
                print("   ❌ No 'wikitable' class")
            
            # Get headers
            headers = table.find_all('th')
            if headers:
                header_texts = [h.get_text(strip=True) for h in headers]
                print(f"   📋 Headers: {header_texts}")
                
                # Check for fight indicators
                header_text = ' '.join(header_texts).lower()
                fight_indicators = ['weight class', 'fighter', 'def.', 'method', 'round', 'time']
                found_indicators = [indicator for indicator in fight_indicators if indicator in header_text]
                if found_indicators:
                    print(f"   ✅ Found fight indicators: {found_indicators}")
                else:
                    print(f"   ❌ No fight indicators found")
            else:
                print("   ❌ No headers found")
            
            # Show first few rows
            rows = table.find_all('tr')
            if rows:
                print(f"   📋 Has {len(rows)} rows")
                for j, row in enumerate(rows[:3]):  # Show first 3 rows
                    cells = row.find_all(['td', 'th'])
                    cell_texts = [cell.get_text(strip=True)[:30] for cell in cells]
                    print(f"      Row {j+1}: {cell_texts}")
                    
                    # Check for "def." pattern in this row
                    row_text = ' '.join(cell_texts).lower()
                    if 'def.' in row_text:
                        print(f"      ✅ Found 'def.' pattern in row {j+1}")
        
        # Test the table detection logic
        print(f"\n🔍 Testing table detection logic:")
        for i, table in enumerate(tables):
            # Check if this table is a fight card table
            headers = table.find_all('th')
            header_text = ' '.join([h.get_text(strip=True) for h in headers]).lower()
            
            # Look for fight card indicators
            fight_indicators = ['weight class', 'fighter', 'def.', 'method', 'round', 'time']
            has_indicators = any(indicator in header_text for indicator in fight_indicators)
            
            # Also check if the table has fight data in the rows
            rows = table.find_all('tr')
            has_def_pattern = False
            if len(rows) > 2:  # Need at least header + data rows
                # Check if any row contains "def." pattern
                for row in rows[1:]:  # Skip header row
                    cells = row.find_all(['td', 'th'])
                    cell_texts = [cell.get_text(strip=True) for cell in cells]
                    if any('def.' in text.lower() for text in cell_texts):
                        has_def_pattern = True
                        break
            
            is_fight_table = has_indicators or has_def_pattern
            
            print(f"   Table {i+1}: has_indicators={has_indicators}, has_def_pattern={has_def_pattern}, is_fight_table={is_fight_table}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_single_event() 