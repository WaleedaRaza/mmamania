from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import json
import os

from ..core.database import get_db
from ..models.ranking import Ranking
from ..schemas.ranking import RankingResponse, RankingsResponse
from ..services.ufc_scraper_service import UFCScraperService

router = APIRouter(prefix="/rankings", tags=["rankings"])

@router.get("/", response_model=RankingsResponse)
async def get_rankings(
    division: Optional[str] = None,
    limit: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get UFC rankings with optional filtering by division
    """
    try:
        # Get rankings from database
        query = db.query(Ranking)
        
        if division:
            query = query.filter(Ranking.division.ilike(f"%{division}%"))
        
        if limit:
            query = query.limit(limit)
        
        rankings = query.order_by(Ranking.division, Ranking.rank).all()
        
        # Get last update time
        last_update = db.query(Ranking.updated_at).order_by(Ranking.updated_at.desc()).first()
        
        return RankingsResponse(
            rankings=rankings,
            total_count=len(rankings),
            last_updated=last_update[0] if last_update else None,
            division_filter=division
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching rankings: {str(e)}")

@router.get("/divisions")
async def get_divisions(db: Session = Depends(get_db)):
    """
    Get all available divisions
    """
    try:
        divisions = db.query(Ranking.division).distinct().all()
        return {
            "divisions": [div[0] for div in divisions],
            "total_divisions": len(divisions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching divisions: {str(e)}")

@router.get("/{division}", response_model=RankingsResponse)
async def get_rankings_by_division(
    division: str,
    limit: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get rankings for a specific division
    """
    try:
        query = db.query(Ranking).filter(Ranking.division.ilike(f"%{division}%"))
        
        if limit:
            query = query.limit(limit)
        
        rankings = query.order_by(Ranking.rank).all()
        
        if not rankings:
            raise HTTPException(status_code=404, detail=f"No rankings found for division: {division}")
        
        # Get last update time
        last_update = db.query(Ranking.updated_at).order_by(Ranking.updated_at.desc()).first()
        
        return RankingsResponse(
            rankings=rankings,
            total_count=len(rankings),
            last_updated=last_update[0] if last_update else None,
            division_filter=division
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching rankings: {str(e)}")

@router.post("/refresh")
async def refresh_rankings(db: Session = Depends(get_db)):
    """
    Manually trigger a rankings refresh (with rate limiting)
    """
    try:
        # Check if we've updated recently (rate limiting)
        last_update = db.query(Ranking.updated_at).order_by(Ranking.updated_at.desc()).first()
        
        if last_update and last_update[0]:
            time_since_update = datetime.utcnow() - last_update[0]
            if time_since_update < timedelta(hours=1):  # Rate limit: 1 hour
                return {
                    "message": "Rankings updated recently. Please wait before refreshing again.",
                    "last_update": last_update[0],
                    "next_available": last_update[0] + timedelta(hours=1)
                }
        
        # Trigger scraping
        scraper_service = UFCScraperService()
        success = await scraper_service.update_rankings(db)
        
        if success:
            return {
                "message": "Rankings refreshed successfully",
                "timestamp": datetime.utcnow()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to refresh rankings")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing rankings: {str(e)}")

@router.get("/status")
async def get_rankings_status(db: Session = Depends(get_db)):
    """
    Get the status of rankings data
    """
    try:
        # Get last update time
        last_update = db.query(Ranking.updated_at).order_by(Ranking.updated_at.desc()).first()
        
        # Get total rankings count
        total_rankings = db.query(Ranking).count()
        
        # Get divisions count
        divisions_count = db.query(Ranking.division).distinct().count()
        
        # Check if data is stale (older than 24 hours)
        is_stale = False
        if last_update and last_update[0]:
            is_stale = datetime.utcnow() - last_update[0] > timedelta(hours=24)
        
        return {
            "last_updated": last_update[0] if last_update else None,
            "total_rankings": total_rankings,
            "divisions_count": divisions_count,
            "is_stale": is_stale,
            "status": "healthy" if not is_stale else "needs_update"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching status: {str(e)}") 