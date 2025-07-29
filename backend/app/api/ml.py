from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import uuid

from ..core.database import get_db
from ..core.deps import get_current_active_user
from ..models.user import User
from ..models.fight import Fight
from ..models.fighter import Fighter
from ..services.ml_service import MLService

router = APIRouter()
ml_service = MLService()


@router.get("/fights/{fight_id}/predictions")
async def get_fight_predictions(
    fight_id: str,
    db: Session = Depends(get_db)
):
    """Get ML predictions for a specific fight"""
    fight = db.query(Fight).filter(Fight.id == fight_id).first()
    if not fight:
        raise HTTPException(status_code=404, detail="Fight not found")
    
    # Get fighter data
    fighter_a = db.query(Fighter).filter(Fighter.id == fight.fighter_a_id).first()
    fighter_b = db.query(Fighter).filter(Fighter.id == fight.fighter_b_id).first()
    
    if not fighter_a or not fighter_b:
        raise HTTPException(status_code=404, detail="Fighter data not found")
    
    # Generate ML predictions
    predictions = ml_service.predict_fight_outcome(fighter_a, fighter_b, fight)
    
    return {
        "fight_id": fight_id,
        "predictions": predictions,
        "confidence": predictions.get("confidence", 0.0),
        "recommended_pick": predictions.get("recommended_pick"),
        "style_analysis": predictions.get("style_analysis", {}),
        "key_factors": predictions.get("key_factors", [])
    }


@router.get("/fighters/{fighter_id}/analytics")
async def get_fighter_analytics(
    fighter_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed analytics for a fighter"""
    fighter = db.query(Fighter).filter(Fighter.id == fighter_id).first()
    if not fighter:
        raise HTTPException(status_code=404, detail="Fighter not found")
    
    # Generate fighter analytics
    analytics = ml_service.analyze_fighter(fighter)
    
    return {
        "fighter_id": fighter_id,
        "fighter_name": fighter.name,
        "analytics": analytics,
        "strengths": analytics.get("strengths", []),
        "weaknesses": analytics.get("weaknesses", []),
        "style_breakdown": analytics.get("style_breakdown", {}),
        "performance_trends": analytics.get("performance_trends", {})
    }


@router.get("/fights/{fight_id}/insights")
async def get_fight_insights(
    fight_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed insights for a fight matchup"""
    fight = db.query(Fight).filter(Fight.id == fight_id).first()
    if not fight:
        raise HTTPException(status_code=404, detail="Fight not found")
    
    # Get fighter data
    fighter_a = db.query(Fighter).filter(Fighter.id == fight.fighter_a_id).first()
    fighter_b = db.query(Fighter).filter(Fighter.id == fight.fighter_b_id).first()
    
    if not fighter_a or not fighter_b:
        raise HTTPException(status_code=404, detail="Fighter data not found")
    
    # Generate fight insights
    insights = ml_service.generate_fight_insights(fighter_a, fighter_b, fight)
    
    return {
        "fight_id": fight_id,
        "insights": insights,
        "matchup_analysis": insights.get("matchup_analysis", {}),
        "historical_comparison": insights.get("historical_comparison", {}),
        "betting_analysis": insights.get("betting_analysis", {}),
        "risk_factors": insights.get("risk_factors", [])
    }


@router.get("/leaderboard/predictions")
async def get_prediction_leaderboard(
    period: str = Query("all", description="Period: week, month, all"),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db)
):
    """Get ML prediction accuracy leaderboard"""
    # This would typically query the ML model's historical performance
    # For now, return mock data
    leaderboard = ml_service.get_prediction_leaderboard(period, limit)
    
    return {
        "period": period,
        "leaderboard": leaderboard,
        "total_participants": len(leaderboard)
    }


@router.post("/fights/{fight_id}/update-insights")
async def update_fight_insights(
    fight_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update ML insights for a fight (admin only)"""
    # TODO: Add admin check
    fight = db.query(Fight).filter(Fight.id == fight_id).first()
    if not fight:
        raise HTTPException(status_code=404, detail="Fight not found")
    
    # Get fighter data
    fighter_a = db.query(Fighter).filter(Fighter.id == fight.fighter_a_id).first()
    fighter_b = db.query(Fighter).filter(Fighter.id == fight.fighter_b_id).first()
    
    if not fighter_a or not fighter_b:
        raise HTTPException(status_code=404, detail="Fighter data not found")
    
    # Generate and update insights
    insights = ml_service.generate_fight_insights(fighter_a, fighter_b, fight)
    fight.ml_insights = insights
    
    db.commit()
    db.refresh(fight)
    
    return {"message": "Insights updated successfully", "fight_id": fight_id} 