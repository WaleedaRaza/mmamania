from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..core.database import get_db
from ..core.deps import get_current_active_user
from ..models.user import User
from ..models.prediction import Prediction
from ..models.profile import Profile
from ..models.fight import Fight
from ..schemas.prediction import Prediction as PredictionSchema, PredictionCreate, PredictionWithFight
from ..services.elo_service import EloService

router = APIRouter()
elo_service = EloService()


@router.get("/", response_model=List[PredictionWithFight])
async def get_user_predictions(
    current_user: User = Depends(get_current_active_user),
    limit: int = Query(20, le=100),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get current user's predictions"""
    predictions = db.query(Prediction).filter(
        Prediction.user_id == current_user.id
    ).order_by(Prediction.created_at.desc()).offset(skip).limit(limit).all()
    
    return predictions


@router.get("/leaderboard")
async def get_leaderboard(
    period: str = Query("all", description="Period: week, month, all"),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db)
):
    """Get Elo leaderboard"""
    # Get all profiles ordered by Elo rating
    profiles = db.query(Profile).order_by(Profile.elo_rating.desc()).limit(limit).all()
    
    leaderboard = []
    for i, profile in enumerate(profiles):
        user = db.query(User).filter(User.id == profile.user_id).first()
        if user:
            leaderboard.append({
                "rank": i + 1,
                "user_id": str(user.id),
                "username": user.username,
                "elo_rating": profile.elo_rating,
                "total_predictions": profile.total_predictions,
                "correct_predictions": profile.correct_predictions,
                "accuracy": round(profile.correct_predictions / max(profile.total_predictions, 1), 3),
                "rating_category": elo_service.get_rating_category(profile.elo_rating)
            })
    
    return {
        "period": period,
        "leaderboard": leaderboard,
        "total_participants": len(leaderboard)
    }


@router.get("/stats")
async def get_prediction_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's prediction statistics"""
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Get recent predictions
    recent_predictions = db.query(Prediction).filter(
        Prediction.user_id == current_user.id
    ).order_by(Prediction.created_at.desc()).limit(10).all()
    
    # Calculate accuracy by method
    method_stats = {}
    for prediction in recent_predictions:
        method = prediction.predicted_method
        if method not in method_stats:
            method_stats[method] = {"total": 0, "correct": 0}
        method_stats[method]["total"] += 1
        if prediction.is_correct:
            method_stats[method]["correct"] += 1
    
    # Calculate accuracy percentages
    for method in method_stats:
        total = method_stats[method]["total"]
        correct = method_stats[method]["correct"]
        method_stats[method]["accuracy"] = round(correct / total, 3) if total > 0 else 0
    
    return {
        "user_id": str(current_user.id),
        "username": current_user.username,
        "elo_rating": profile.elo_rating,
        "rating_category": elo_service.get_rating_category(profile.elo_rating),
        "total_predictions": profile.total_predictions,
        "correct_predictions": profile.correct_predictions,
        "overall_accuracy": round(profile.correct_predictions / max(profile.total_predictions, 1), 3),
        "method_stats": method_stats,
        "recent_predictions": [
            {
                "fight_id": str(pred.fight_id),
                "predicted_winner": str(pred.predicted_winner),
                "predicted_method": pred.predicted_method,
                "is_correct": pred.is_correct,
                "elo_change": pred.elo_change,
                "created_at": pred.created_at
            }
            for pred in recent_predictions
        ]
    }


@router.post("/{prediction_id}/update-result")
async def update_prediction_result(
    prediction_id: str,
    is_correct: bool,
    method_correct: bool = False,
    round_correct: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update prediction result and recalculate Elo (admin only)"""
    # TODO: Add admin check
    prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    # Get fight details for difficulty calculation
    fight = db.query(Fight).filter(Fight.id == prediction.fight_id).first()
    if not fight:
        raise HTTPException(status_code=404, detail="Fight not found")
    
    # Get user profile
    profile = db.query(Profile).filter(Profile.user_id == prediction.user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    # Calculate fight difficulty
    fight_difficulty = elo_service.calculate_fight_difficulty(
        fight.odds.get("fighter_a", 0),
        fight.odds.get("fighter_b", 0)
    )
    
    # Calculate Elo change
    elo_change, new_rating = elo_service.calculate_prediction_elo_change(
        profile.elo_rating,
        fight_difficulty,
        is_correct,
        method_correct,
        round_correct
    )
    
    # Update prediction
    prediction.is_correct = is_correct
    prediction.actual_result = "Correct" if is_correct else "Incorrect"
    prediction.elo_change = elo_change
    prediction.points_earned = elo_change if elo_change > 0 else 0
    
    # Update profile
    profile.elo_rating = new_rating
    profile.total_predictions += 1
    if is_correct:
        profile.correct_predictions += 1
    
    # Update prediction history
    if str(prediction.id) not in profile.prediction_history:
        profile.prediction_history.append(str(prediction.id))
    
    db.commit()
    db.refresh(prediction)
    db.refresh(profile)
    
    return {
        "message": "Prediction result updated",
        "prediction_id": prediction_id,
        "elo_change": elo_change,
        "new_rating": new_rating
    } 