#!/usr/bin/env python3
"""
Test script for the enhanced media scraper
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.enhanced_media_scraper import EnhancedMediaScraper

async def test_youtube_scraping():
    """Test YouTube scraping functionality"""
    print("🧪 Testing YouTube scraping...")
    
    async with EnhancedMediaScraper() as scraper:
        # Test basic YouTube search
        videos = await scraper._scrape_youtube_comprehensive(
            ['UFC highlights', 'MMA news'], 
            max_results=5
        )
        
        print(f"✅ Found {len(videos)} YouTube videos")
        
        for i, video in enumerate(videos[:3]):
            print(f"  {i+1}. {video.get('title', 'No title')}")
            print(f"     Channel: {video.get('author_name', 'Unknown')}")
            print(f"     Views: {video.get('view_count', 0)}")
            print(f"     Relevance: {video.get('relevance_score', 0)}")
            print()

async def test_twitter_scraping():
    """Test Twitter scraping functionality"""
    print("🧪 Testing Twitter scraping...")
    
    async with EnhancedMediaScraper() as scraper:
        # Test basic Twitter search
        tweets = await scraper._scrape_twitter_comprehensive(
            ['UFC filter:media', 'MMA news'], 
            max_results=5
        )
        
        print(f"✅ Found {len(tweets)} Twitter posts")
        
        for i, tweet in enumerate(tweets[:3]):
            print(f"  {i+1}. {tweet.get('title', 'No title')}")
            print(f"     Author: {tweet.get('author_name', 'Unknown')}")
            print(f"     Likes: {tweet.get('like_count', 0)}")
            print(f"     Relevance: {tweet.get('relevance_score', 0)}")
            print()

async def test_comprehensive_scraping():
    """Test comprehensive scraping with context"""
    print("🧪 Testing comprehensive scraping...")
    
    async with EnhancedMediaScraper() as scraper:
        # Test with event context
        result = await scraper.scrape_all_platforms(
            event_name="UFC 300",
            fighter_names=["Alex Pereira", "Israel Adesanya"],
            max_per_platform=10
        )
        
        print(f"✅ Comprehensive scraping results:")
        print(f"   Total content: {result.get('total_content', 0)}")
        print(f"   YouTube: {result.get('youtube_count', 0)}")
        print(f"   Twitter: {result.get('twitter_count', 0)}")
        print(f"   TikTok: {result.get('tiktok_count', 0)}")
        
        if result.get('content'):
            print(f"\n📋 Top content:")
            for i, item in enumerate(result['content'][:3]):
                print(f"  {i+1}. [{item.get('platform', 'unknown')}] {item.get('title', 'No title')}")
                print(f"     Score: {item.get('contextual_score', 0):.1f}")

async def test_search_terms_generation():
    """Test search terms generation"""
    print("🧪 Testing search terms generation...")
    
    async with EnhancedMediaScraper() as scraper:
        # Test with event
        terms = scraper._generate_search_terms(
            event_name="UFC 300",
            fighter_names=["Alex Pereira"]
        )
        
        print(f"✅ Generated search terms:")
        print(f"   YouTube: {len(terms['youtube'])} terms")
        print(f"   Twitter: {len(terms['twitter'])} terms")
        print(f"   TikTok: {len(terms['tiktok'])} terms")
        
        print(f"\n📝 Sample YouTube terms:")
        for term in terms['youtube'][:5]:
            print(f"   - {term}")

async def main():
    """Run all tests"""
    print("🚀 Starting Enhanced Media Scraper Tests\n")
    
    try:
        await test_search_terms_generation()
        print("-" * 50)
        
        await test_youtube_scraping()
        print("-" * 50)
        
        await test_twitter_scraping()
        print("-" * 50)
        
        await test_comprehensive_scraping()
        print("-" * 50)
        
        print("✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
