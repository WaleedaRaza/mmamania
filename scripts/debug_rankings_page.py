#!/usr/bin/env python3
"""
Debug UFC Rankings Page Structure
Analyze the actual HTML structure of UFC rankings pages
"""

import requests
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def debug_rankings_page():
    """Debug the structure of UFC rankings page"""
    print("🔍 Debugging UFC rankings page structure...")
    
    # Initialize WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Navigate to rankings page
        url = "https://www.ufc.com/rankings"
        driver.get(url)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Get page source
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        print(f"📄 Page title: {soup.title.string if soup.title else 'No title'}")
        print()
        
        # Look for rankings tables
        print("🔍 Looking for rankings tables...")
        tables = soup.find_all('table')
        print(f"   Found {len(tables)} tables")
        
        for i, table in enumerate(tables[:5]):  # Check first 5 tables
            print(f"   Table {i+1}:")
            print(f"      Classes: {table.get('class', [])}")
            
            # Look for headers
            headers = table.find_all('th')
            if headers:
                print(f"      Headers: {[h.get_text(strip=True) for h in headers]}")
            
            # Look for rows
            rows = table.find_all('tr')
            print(f"      Rows: {len(rows)}")
            
            # Check first few rows for content
            for j, row in enumerate(rows[:3]):
                cells = row.find_all(['td', 'th'])
                if cells:
                    cell_texts = [cell.get_text(strip=True) for cell in cells]
                    print(f"      Row {j+1}: {cell_texts}")
            print()
        
        # Look for specific rankings sections
        print("🔍 Looking for rankings sections...")
        rankings_sections = soup.find_all(['section', 'div'], class_=lambda x: x and 'rankings' in x.lower())
        print(f"   Found {len(rankings_sections)} rankings sections")
        
        for i, section in enumerate(rankings_sections[:3]):
            print(f"   Section {i+1}:")
            print(f"      Classes: {section.get('class', [])}")
            
            # Look for champion info
            champions = section.find_all(['h5', 'h3', 'h4'])
            if champions:
                print(f"      Champions/Headers: {[c.get_text(strip=True)[:50] for c in champions[:3]]}")
            
            # Look for fighter names
            fighter_links = section.find_all('a')
            if fighter_links:
                print(f"      Fighter links: {[link.get_text(strip=True)[:30] for link in fighter_links[:5]]}")
            print()
        
        # Look for any record patterns
        print("🔍 Looking for record patterns...")
        page_text = soup.get_text()
        
        import re
        # Look for W-L-D patterns
        record_patterns = re.findall(r'(\d+)-(\d+)-(\d+)', page_text)
        if record_patterns:
            print(f"   W-L-D patterns found: {record_patterns[:10]}")
        
        # Look for W-L patterns
        record_patterns_2 = re.findall(r'(\d+)-(\d+)(?!\d)', page_text)
        if record_patterns_2:
            print(f"   W-L patterns found: {record_patterns_2[:10]}")
        
        # Save HTML for manual inspection
        html_file = "debug_rankings_page.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(page_source)
        print(f"💾 Saved HTML to: {html_file}")
        
    except Exception as e:
        print(f"❌ Error debugging rankings page: {e}")
    finally:
        driver.quit()

def main():
    """Debug the rankings page"""
    print("🔍 UFC Rankings Page Structure Debugger")
    print("=" * 50)
    
    debug_rankings_page()

if __name__ == "__main__":
    main() 