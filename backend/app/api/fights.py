from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from ..core.database import get_db
from ..core.deps import get_current_active_user
from ..models.user import User
from ..models.fight import Fight
from ..models.fighter import Fighter
from ..models.prediction import Prediction
from ..schemas.fight import Fight as FightSchema, FightCreate, FightUpdate, FightWithFighters
from ..schemas.prediction import Prediction as PredictionSchema, PredictionCreate, PredictionWithFight
from ..services.elo_service import EloService

router = APIRouter()
elo_service = EloService()


@router.get("/", response_model=List[FightWithFighters])
async def get_fights(
    upcoming: bool = Query(True, description="Get upcoming fights only"),
    limit: int = Query(20, le=100),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get list of fights"""
    query = db.query(Fight)
    
    if upcoming:
        query = query.filter(Fight.date >= datetime.utcnow())
        query = query.order_by(Fight.date.asc())
    else:
        query = query.order_by(Fight.date.desc())
    
    fights = query.offset(skip).limit(limit).all()
    return fights


@router.get("/{fight_id}", response_model=FightWithFighters)
async def get_fight(fight_id: str, db: Session = Depends(get_db)):
    """Get specific fight details"""
    fight = db.query(Fight).filter(Fight.id == fight_id).first()
    if not fight:
        raise HTTPException(status_code=404, detail="Fight not found")
    return fight


@router.post("/", response_model=FightSchema)
async def create_fight(
    fight_data: FightCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new fight (admin only)"""
    # TODO: Add admin check
    db_fight = Fight(**fight_data.dict())
    db.add(db_fight)
    db.commit()
    db.refresh(db_fight)
    return db_fight


@router.put("/{fight_id}", response_model=FightSchema)
async def update_fight(
    fight_id: str,
    fight_data: FightUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update fight details (admin only)"""
    # TODO: Add admin check
    fight = db.query(Fight).filter(Fight.id == fight_id).first()
    if not fight:
        raise HTTPException(status_code=404, detail="Fight not found")
    
    for field, value in fight_data.dict(exclude_unset=True).items():
        setattr(fight, field, value)
    
    db.commit()
    db.refresh(fight)
    return fight


@router.post("/{fight_id}/predict", response_model=PredictionSchema)
async def create_prediction(
    fight_id: str,
    prediction_data: PredictionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a prediction for a fight"""
    # Check if fight exists and is upcoming
    fight = db.query(Fight).filter(Fight.id == fight_id).first()
    if not fight:
        raise HTTPException(status_code=404, detail="Fight not found")
    
    if fight.date <= datetime.utcnow():
        raise HTTPException(status_code=400, detail="Cannot predict on past fights")
    
    # Check if user already predicted this fight
    existing_prediction = db.query(Prediction).filter(
        Prediction.user_id == current_user.id,
        Prediction.fight_id == fight_id
    ).first()
    
    if existing_prediction:
        raise HTTPException(status_code=400, detail="Already predicted this fight")
    
    # Create prediction
    db_prediction = Prediction(
        user_id=current_user.id,
        fight_id=fight_id,
        **prediction_data.dict()
    )
    
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    
    return db_prediction


@router.get("/{fight_id}/predictions", response_model=List[PredictionWithFight])
async def get_fight_predictions(
    fight_id: str,
    limit: int = Query(50, le=100),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get all predictions for a specific fight"""
    predictions = db.query(Prediction).filter(
        Prediction.fight_id == fight_id
    ).offset(skip).limit(limit).all()
    
    return predictions


@router.get("/upcoming/main-events", response_model=List[FightWithFighters])
async def get_upcoming_main_events(db: Session = Depends(get_db)):
    """Get upcoming main events"""
    main_events = db.query(Fight).filter(
        Fight.is_main_event == True,
        Fight.date >= datetime.utcnow()
    ).order_by(Fight.date.asc()).limit(5).all()
    
    return main_events 