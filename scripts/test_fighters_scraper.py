#!/usr/bin/env python3
"""
Test fighters scraper with a small batch
"""

import subprocess
import os

def create_test_urls():
    """Create a test file with just a few URLs"""
    test_urls = [
        "/athlete/islam-makhachev",
        "/athlete/alexander-volkanovski"
    ]
    
    os.makedirs('ufc_scraper/input', exist_ok=True)
    with open('ufc_scraper/input/test_urls.txt', 'w') as f:
        for url in test_urls:
            f.write(f"{url}\n")
    
    print(f"✅ Created test file with {len(test_urls)} URLs")

def run_test_scraper():
    """Run the fighters scraper with test URLs"""
    print("👊 Running test fighters scraper...")
    
    try:
        result = subprocess.run([
            "cd ufc_scraper && scrapy crawl fighters -a input_file=input/test_urls.txt -o test_fighters.json -L DEBUG"
        ], shell=True, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Test fighters scraper completed successfully")
            print("Output:", result.stdout[-500:])  # Last 500 chars
            return True
        else:
            print(f"❌ Test fighters scraper failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Test scraper timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ Error running test scraper: {e}")
        return False

def main():
    """Main function"""
    print("🧪 Testing UFC Fighters Scraper")
    print("=" * 30)
    
    # Step 1: Create test URLs
    create_test_urls()
    
    # Step 2: Run test scraper
    success = run_test_scraper()
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("The scraper works with a small batch.")
        print("The issue was likely too many concurrent requests.")
    else:
        print("\n❌ Test failed. Check the error messages above.")

if __name__ == "__main__":
    main() 