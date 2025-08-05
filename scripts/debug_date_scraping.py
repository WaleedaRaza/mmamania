#!/usr/bin/env python3
"""
Debug Date Scraping
Check what dates are being extracted from the Wikipedia table
"""

import requests
from bs4 import BeautifulSoup
import re

def debug_date_scraping():
    """Debug the date scraping from Wikipedia"""
    url = "https://en.wikipedia.org/wiki/List_of_UFC_events"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("🔍 DEBUGGING DATE SCRAPING")
        print("=" * 50)
        
        # Find all tables
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        # Find the table with the most UFC links
        best_table = None
        max_ufc_links = 0
        
        for table in tables:
            links = table.find_all('a', href=True)
            ufc_links = [link for link in links if 'UFC' in link.get_text()]
            if len(ufc_links) > max_ufc_links:
                max_ufc_links = len(ufc_links)
                best_table = table
        
        if best_table:
            print(f"Found table with {max_ufc_links} UFC event links")
            
            # Look at the first few rows to understand the structure
            rows = best_table.find_all('tr')
            print(f"\n📊 Table Structure Analysis:")
            print(f"Total rows: {len(rows)}")
            
            # Analyze first 5 rows
            for i, row in enumerate(rows[:5]):
                cells = row.find_all(['td', 'th'])
                print(f"\nRow {i+1}:")
                for j, cell in enumerate(cells):
                    cell_text = cell.get_text(strip=True)
                    print(f"  Cell {j+1}: '{cell_text}'")
            
            # Look for date patterns in the table
            print(f"\n🔍 Looking for date patterns in the table:")
            date_patterns = []
            
            for row in rows[1:10]:  # Check first 10 data rows
                cells = row.find_all(['td', 'th'])
                for cell in cells:
                    cell_text = cell.get_text(strip=True)
                    # Look for date patterns
                    if re.match(r'\d{4}-\d{2}-\d{2}', cell_text):
                        date_patterns.append(f"ISO format: {cell_text}")
                    elif re.match(r'\w+ \d{1,2}, \d{4}', cell_text):
                        date_patterns.append(f"Full month: {cell_text}")
                    elif re.match(r'\d{1,2}/\d{1,2}/\d{4}', cell_text):
                        date_patterns.append(f"Slash format: {cell_text}")
                    elif re.match(r'\d{1,2}-\d{1,2}-\d{4}', cell_text):
                        date_patterns.append(f"Dash format: {cell_text}")
            
            if date_patterns:
                print("✅ Found date patterns:")
                for pattern in date_patterns[:10]:  # Show first 10
                    print(f"  {pattern}")
            else:
                print("❌ No date patterns found in first 10 rows")
            
            # Check if dates are in a specific column
            print(f"\n📋 Column Analysis:")
            if rows:
                header_row = rows[0]
                header_cells = header_row.find_all(['td', 'th'])
                for i, cell in enumerate(header_cells):
                    cell_text = cell.get_text(strip=True)
                    print(f"  Column {i+1}: '{cell_text}'")
                
                # Check first few data rows for date column
                print(f"\n📅 Checking for date column:")
                for row_num in range(1, min(6, len(rows))):
                    row = rows[row_num]
                    cells = row.find_all(['td', 'th'])
                    print(f"\nRow {row_num}:")
                    for i, cell in enumerate(cells):
                        cell_text = cell.get_text(strip=True)
                        if any(word in cell_text.lower() for word in ['2024', '2023', '2022', '2021', '2020', '2019']):
                            print(f"  Column {i+1}: '{cell_text}' (contains year)")
                        elif re.search(r'\d{4}', cell_text):
                            print(f"  Column {i+1}: '{cell_text}' (contains 4 digits)")
                        else:
                            print(f"  Column {i+1}: '{cell_text}'")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_date_scraping() 