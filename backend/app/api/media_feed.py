from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from ..services.enhanced_media_scraper import EnhancedMediaScraper

router = APIRouter()

@router.get("/media/scrape-comprehensive")
async def scrape_comprehensive_media(
    event_name: Optional[str] = Query(None, description="Current UFC event name"),
    fighter_names: Optional[str] = Query(None, description="Comma-separated fighter names"),
    max_per_platform: int = Query(25, description="Max content per platform"),
):
    """Scrape comprehensive media content from all platforms"""
    
    try:
        fighter_list = []
        if fighter_names:
            fighter_list = [name.strip() for name in fighter_names.split(',')]
        
        async with EnhancedMediaScraper() as scraper:
            result = await scraper.scrape_all_platforms(
                event_name=event_name,
                fighter_names=fighter_list,
                max_per_platform=max_per_platform
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@router.get("/media/scrape-by-platform/{platform}")
async def scrape_by_platform(
    platform: str,
    search_terms: Optional[str] = Query(None, description="Custom search terms"),
    limit: int = Query(20, description="Number of results")
):
    """Scrape content from a specific platform"""
    
    if platform not in ['youtube', 'twitter', 'tiktok']:
        raise HTTPException(status_code=400, detail="Invalid platform")
    
    try:
        async with EnhancedMediaScraper() as scraper:
            if platform == 'youtube':
                terms = search_terms.split(',') if search_terms else ['UFC highlights', 'MMA news']
                result = await scraper._scrape_youtube_comprehensive(terms, limit)
            elif platform == 'twitter':
                terms = search_terms.split(',') if search_terms else ['UFC filter:media', 'MMA news']
                result = await scraper._scrape_twitter_comprehensive(terms, limit)
            else:  # tiktok
                terms = search_terms.split(',') if search_terms else ['#ufc', '#mma']
                result = await scraper._scrape_tiktok_comprehensive(terms, limit)
        
        return {
            'platform': platform,
            'content': result,
            'count': len(result)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Platform scraping failed: {str(e)}")

@router.get("/media/search-terms")
async def get_search_terms(
    event_name: Optional[str] = Query(None, description="Event name to generate terms for"),
    fighter_names: Optional[str] = Query(None, description="Comma-separated fighter names")
):
    """Get generated search terms for debugging"""
    
    try:
        fighter_list = []
        if fighter_names:
            fighter_list = [name.strip() for name in fighter_names.split(',')]
        
        async with EnhancedMediaScraper() as scraper:
            search_terms = scraper._generate_search_terms(event_name, fighter_list)
        
        return {
            'event_name': event_name,
            'fighter_names': fighter_list,
            'search_terms': search_terms
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate search terms: {str(e)}")
