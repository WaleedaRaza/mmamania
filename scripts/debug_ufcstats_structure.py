#!/usr/bin/env python3
"""
Debug UFCStats HTML Structure
Understand how fighter names are structured in the HTML
"""

import requests
from bs4 import BeautifulSoup
import re

def debug_ufcstats_structure():
    """Debug the HTML structure of UFCStats fighters page"""
    print("🔍 Debugging UFCStats HTML structure...")
    
    try:
        url = "http://ufcstats.com/statistics/fighters"
        response = requests.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the fighters table
            fighters_table = soup.find('table', class_='b-statistics__table')
            if fighters_table:
                print("✅ Found fighters table")
                
                # Look at the table structure
                rows = fighters_table.find_all('tr', class_='b-statistics__table-row')
                print(f"📊 Found {len(rows)} fighter rows")
                
                if rows:
                    # Examine first few rows
                    for i, row in enumerate(rows[:5]):
                        print(f"\n🔍 Row {i+1}:")
                        
                        # Get all cells in the row
                        cells = row.find_all('td')
                        print(f"   Cells: {len(cells)}")
                        
                        for j, cell in enumerate(cells):
                            cell_text = cell.get_text(strip=True)
                            cell_html = str(cell)[:100]  # First 100 chars
                            print(f"   Cell {j}: '{cell_text}' | HTML: {cell_html}...")
                        
                        # Look for fighter links specifically
                        fighter_links = row.find_all('a', href=re.compile(r'/fighter-details/'))
                        print(f"   Fighter links: {len(fighter_links)}")
                        
                        for k, link in enumerate(fighter_links):
                            link_text = link.get_text(strip=True)
                            link_html = str(link)[:100]
                            print(f"   Link {k}: '{link_text}' | HTML: {link_html}...")
                
                # Look for the actual structure
                print("\n🔍 Looking for fighter name structure...")
                
                # Check if names are in separate columns
                name_cells = soup.find_all('td', class_=lambda x: x and 'name' in x.lower())
                if name_cells:
                    print(f"Found {len(name_cells)} name cells")
                    for i, cell in enumerate(name_cells[:3]):
                        print(f"   Name cell {i+1}: '{cell.get_text(strip=True)}'")
                
                # Look for any table headers to understand structure
                headers = soup.find_all('th')
                if headers:
                    print(f"\n📋 Table headers: {[h.get_text(strip=True) for h in headers]}")
                
            else:
                print("❌ No fighters table found")
                
                # Look for any tables
                tables = soup.find_all('table')
                print(f"Found {len(tables)} tables")
                
                for i, table in enumerate(tables):
                    print(f"Table {i+1} classes: {table.get('class', [])}")
                    
                    # Look for fighter links in this table
                    fighter_links = table.find_all('a', href=re.compile(r'/fighter-details/'))
                    if fighter_links:
                        print(f"  Found {len(fighter_links)} fighter links")
                        for j, link in enumerate(fighter_links[:3]):
                            print(f"    Link {j+1}: '{link.get_text(strip=True)}'")
            
        else:
            print(f"❌ Failed to connect: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run the debug"""
    print("🥊 UFCStats HTML Structure Debug")
    print("=" * 50)
    
    debug_ufcstats_structure()

if __name__ == "__main__":
    main() 