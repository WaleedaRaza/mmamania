#!/usr/bin/env python3
"""
Debug Wikipedia Structure
Check the actual structure of the Wikipedia UFC events page
"""

import requests
from bs4 import BeautifulSoup

def debug_wikipedia_structure():
    """Debug the structure of the Wikipedia UFC events page"""
    url = "https://en.wikipedia.org/wiki/List_of_UFC_events"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("🔍 Debugging Wikipedia UFC Events Page Structure")
        print("=" * 60)
        
        # Find all headings
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
        print(f"📋 Found {len(headings)} headings:")
        for i, heading in enumerate(headings[:10]):  # Show first 10
            print(f"   {i+1}. {heading.name}: {heading.get_text(strip=True)}")
        
        # Find all tables
        tables = soup.find_all('table')
        print(f"\n📊 Found {len(tables)} tables:")
        for i, table in enumerate(tables[:5]):  # Show first 5
            # Get table caption or first few cells
            caption = table.find('caption')
            if caption:
                print(f"   {i+1}. Table with caption: {caption.get_text(strip=True)}")
            else:
                # Get first row to understand structure
                first_row = table.find('tr')
                if first_row:
                    cells = first_row.find_all(['th', 'td'])
                    cell_texts = [cell.get_text(strip=True)[:20] for cell in cells[:3]]
                    print(f"   {i+1}. Table with cells: {cell_texts}")
        
        # Look specifically for "Past events" section
        print(f"\n🔍 Looking for 'Past events' section:")
        past_events_found = False
        for heading in headings:
            if 'past' in heading.get_text().lower():
                print(f"   ✅ Found heading: {heading.get_text(strip=True)}")
                past_events_found = True
                
                # Look for table after this heading
                print(f"   🔍 Checking what comes after 'Past events' heading:")
                current = heading
                for i in range(10):  # Check next 10 elements
                    current = current.find_next_sibling()
                    if current:
                        print(f"      {i+1}. {current.name}: {current.get_text(strip=True)[:50]}")
                        if current.name == 'table':
                            print(f"      📊 Found table after 'Past events' heading")
                            rows = current.find_all('tr')
                            print(f"      📋 Table has {len(rows)} rows")
                            
                            if rows:
                                # Show first row (headers)
                                first_row = rows[0]
                                headers = first_row.find_all(['th', 'td'])
                                header_texts = [h.get_text(strip=True) for h in headers]
                                print(f"      📋 Headers: {header_texts}")
                                
                                # Show a few data rows
                                for j, row in enumerate(rows[1:4]):  # Show first 3 data rows
                                    cells = row.find_all(['td', 'th'])
                                    cell_texts = [cell.get_text(strip=True)[:30] for cell in cells]
                                    print(f"      📋 Row {j+1}: {cell_texts}")
                            break
                    else:
                        print(f"      {i+1}. No more siblings")
                        break
                
                # Also check if there's a div or other container that might contain the table
                print(f"   🔍 Looking for containers that might have the table:")
                parent = heading.parent
                if parent:
                    print(f"      Parent: {parent.name}")
                    # Look for tables within the parent or nearby
                    nearby_tables = parent.find_all('table')
                    print(f"      Found {len(nearby_tables)} tables in parent")
                    
                    # Also check the next few siblings of the parent
                    parent_sibling = parent.find_next_sibling()
                    if parent_sibling:
                        print(f"      Parent sibling: {parent_sibling.name}")
                        sibling_tables = parent_sibling.find_all('table')
                        print(f"      Found {len(sibling_tables)} tables in parent sibling")
        
        if not past_events_found:
            print("   ❌ No 'Past events' heading found")
            
            # Look for any table with UFC event links
            print(f"\n🔍 Looking for tables with UFC event links:")
            for i, table in enumerate(tables):
                links = table.find_all('a')
                ufc_links = [link for link in links if 'ufc' in link.get_text().lower()]
                if ufc_links:
                    print(f"   📊 Table {i+1} has {len(ufc_links)} UFC links")
                    for link in ufc_links[:3]:  # Show first 3
                        print(f"      • {link.get_text(strip=True)}")
        
        # Also check all tables for UFC links
        print(f"\n🔍 Checking all tables for UFC event links:")
        for i, table in enumerate(tables):
            links = table.find_all('a')
            ufc_links = [link for link in links if 'ufc' in link.get_text().lower()]
            if ufc_links:
                print(f"   📊 Table {i+1} has {len(ufc_links)} UFC links")
                for link in ufc_links[:3]:  # Show first 3
                    print(f"      • {link.get_text(strip=True)}")
        
    except Exception as e:
        print(f"❌ Error debugging Wikipedia structure: {e}")

if __name__ == "__main__":
    debug_wikipedia_structure() 