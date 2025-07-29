#!/usr/bin/env python3
"""
Debug script to examine UFC fighter page structure
"""

import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def debug_ufc_page():
    """Debug a UFC fighter page to understand its structure"""
    print("🔍 Debugging UFC Fighter Page Structure")
    print("=" * 50)
    
    # Initialize WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Navigate to Islam Makhachev's page
        url = "https://www.ufc.com/athlete/islam-makhachev"
        print(f"🌐 Loading: {url}")
        
        driver.get(url)
        time.sleep(5)  # Wait for page to load
        
        # Save page source
        with open('ufc_page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("💾 Page source saved to ufc_page_source.html")
        
        # Try to find key elements
        print("\n🔍 Searching for key elements...")
        
        # Look for any h1 elements
        h1_elements = driver.find_elements(By.TAG_NAME, "h1")
        print(f"H1 elements found: {len(h1_elements)}")
        for i, h1 in enumerate(h1_elements):
            print(f"  H1 {i+1}: {h1.text.strip()}")
        
        # Look for any elements with "record" in class or text
        record_elements = driver.find_elements(By.XPATH, "//*[contains(@class, 'record') or contains(text(), 'record') or contains(text(), '-')]")
        print(f"\nRecord-related elements found: {len(record_elements)}")
        for i, elem in enumerate(record_elements[:10]):  # Show first 10
            print(f"  Record {i+1}: {elem.text.strip()}")
        
        # Look for any elements with "stats" in class
        stats_elements = driver.find_elements(By.XPATH, "//*[contains(@class, 'stat') or contains(@class, 'stats')]")
        print(f"\nStats-related elements found: {len(stats_elements)}")
        for i, elem in enumerate(stats_elements[:10]):  # Show first 10
            print(f"  Stats {i+1}: {elem.text.strip()}")
        
        # Look for any table elements (fight history)
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"\nTables found: {len(tables)}")
        for i, table in enumerate(tables):
            print(f"  Table {i+1}: {table.text.strip()[:200]}...")
        
        # Look for any div elements with "history" in class
        history_elements = driver.find_elements(By.XPATH, "//*[contains(@class, 'history') or contains(@class, 'fight')]")
        print(f"\nHistory-related elements found: {len(history_elements)}")
        for i, elem in enumerate(history_elements[:10]):  # Show first 10
            print(f"  History {i+1}: {elem.text.strip()}")
        
        # Get all text content to see what's available
        body_text = driver.find_element(By.TAG_NAME, "body").text
        print(f"\n📄 Total body text length: {len(body_text)} characters")
        print("First 1000 characters:")
        print(body_text[:1000])
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    debug_ufc_page() 