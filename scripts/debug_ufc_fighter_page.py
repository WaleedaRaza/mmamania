#!/usr/bin/env python3
"""
Debug UFC Fighter Page Structure
Analyze the actual HTML structure to find correct selectors for fighter records
"""

import requests
from bs4 import BeautifulSoup
import json

def debug_ufc_fighter_page():
    """Debug the structure of a UFC fighter page"""
    print("🔍 Debugging UFC Fighter Page Structure...")
    
    # Test with Islam Makhachev's page
    fighter_url = "/athlete/islam-makhachev"
    base_url = "https://www.ufc.com"
    full_url = f"{base_url}{fighter_url}"
    
    try:
        response = requests.get(full_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            print(f"✅ Successfully loaded: {full_url}")
            print(f"📄 Page title: {soup.title.string if soup.title else 'No title'}")
            
            # Look for record-related elements
            print("\n🔍 Searching for record elements...")
            
            # Try different selectors
            selectors_to_try = [
                'div.hero-content__record',
                'span.hero-content__record',
                'div[class*="record"]',
                'span[class*="record"]',
                '.hero-content .record',
                '.athlete-record',
                '.fighter-record',
                '[class*="record"]',
                'h1', 'h2', 'h3',  # Check headers
                '.hero-content',  # Check hero section
            ]
            
            for selector in selectors_to_try:
                elements = soup.select(selector)
                if elements:
                    print(f"\n✅ Found {len(elements)} elements with selector: '{selector}'")
                    for i, elem in enumerate(elements[:3]):  # Show first 3
                        text = elem.get_text(strip=True)
                        print(f"   {i+1}. Text: '{text}'")
                        print(f"      HTML: {str(elem)[:100]}...")
                else:
                    print(f"❌ No elements found with selector: '{selector}'")
            
            # Look for any text that might contain a record pattern
            print("\n🔍 Searching for record patterns in text...")
            all_text = soup.get_text()
            lines = all_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if line and ('-' in line) and any(char.isdigit() for char in line):
                    # Look for patterns like "25-3-0" or "25-3"
                    parts = line.split('-')
                    if len(parts) >= 2 and all(part.strip().isdigit() for part in parts[:2]):
                        print(f"📊 Potential record found: '{line}'")
            
            # Save the HTML for manual inspection
            with open('debug_fighter_page.html', 'w', encoding='utf-8') as f:
                f.write(str(soup))
            print(f"\n💾 Full HTML saved to: debug_fighter_page.html")
            
        else:
            print(f"❌ Failed to load page: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_ufc_fighter_page() 