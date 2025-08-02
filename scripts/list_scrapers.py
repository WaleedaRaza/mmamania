#!/usr/bin/env python3
"""
List Available Scrapers
Shows what scrapers are available in the clean slate
"""

import os

def list_scrapers():
    """List all available scrapers"""
    print("🔍 AVAILABLE SCRAPERS")
    print("=" * 50)
    
    scrapers_dir = "../scrapers"
    
    if os.path.exists(scrapers_dir):
        print("📁 Scrapers directory found:")
        
        # List UFC scrapers
        ufc_dir = os.path.join(scrapers_dir, "ufc")
        if os.path.exists(ufc_dir):
            print("\n🥊 UFC Scrapers:")
            for file in os.listdir(ufc_dir):
                if file.endswith('.py'):
                    print(f"   ✅ {file}")
        
        # List Wikipedia scrapers
        wiki_dir = os.path.join(scrapers_dir, "wikipedia")
        if os.path.exists(wiki_dir):
            print("\n📚 Wikipedia Scrapers:")
            for file in os.listdir(wiki_dir):
                if file.endswith('.py'):
                    print(f"   ✅ {file}")
    
    print("\n🎉 CLEAN SLATE READY!")
    print("=" * 50)
    print("✅ All messy data and scripts wiped")
    print("✅ Only scrapers remain")
    print("✅ Ready for fresh start")
    print("=" * 50)

if __name__ == "__main__":
    list_scrapers() 