from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..core.database import get_db
from ..core.deps import get_current_active_user
from ..models.user import User
from ..models.fighter import Fighter
from ..schemas.fighter import Fighter as FighterSchema, FighterCreate, FighterUpdate, FighterWithStats

router = APIRouter()


@router.get("/", response_model=List[FighterSchema])
async def get_fighters(
    weight_class: Optional[str] = Query(None, description="Filter by weight class"),
    active_only: bool = Query(True, description="Show only active fighters"),
    limit: int = Query(50, le=100),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get list of fighters"""
    query = db.query(Fighter)
    
    if weight_class:
        query = query.filter(Fighter.weight_class == weight_class)
    
    if active_only:
        query = query.filter(Fighter.is_active == "Active")
    
    fighters = query.offset(skip).limit(limit).all()
    return fighters


@router.get("/{fighter_id}", response_model=FighterWithStats)
async def get_fighter(fighter_id: str, db: Session = Depends(get_db)):
    """Get specific fighter details"""
    fighter = db.query(Fighter).filter(Fighter.id == fighter_id).first()
    if not fighter:
        raise HTTPException(status_code=404, detail="Fighter not found")
    return fighter


@router.post("/", response_model=FighterSchema)
async def create_fighter(
    fighter_data: FighterCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new fighter (admin only)"""
    # TODO: Add admin check
    db_fighter = Fighter(**fighter_data.dict())
    db.add(db_fighter)
    db.commit()
    db.refresh(db_fighter)
    return db_fighter


@router.put("/{fighter_id}", response_model=FighterSchema)
async def update_fighter(
    fighter_id: str,
    fighter_data: FighterUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update fighter details (admin only)"""
    # TODO: Add admin check
    fighter = db.query(Fighter).filter(Fighter.id == fighter_id).first()
    if not fighter:
        raise HTTPException(status_code=404, detail="Fighter not found")
    
    for field, value in fighter_data.dict(exclude_unset=True).items():
        setattr(fighter, field, value)
    
    db.commit()
    db.refresh(fighter)
    return fighter


@router.get("/weight-classes/list")
async def get_weight_classes(db: Session = Depends(get_db)):
    """Get list of all weight classes"""
    weight_classes = db.query(Fighter.weight_class).distinct().all()
    return [wc[0] for wc in weight_classes if wc[0]]


@router.get("/rankings/{weight_class}")
async def get_rankings(
    weight_class: str,
    limit: int = Query(15, le=20),
    db: Session = Depends(get_db)
):
    """Get UFC rankings for a weight class"""
    ranked_fighters = db.query(Fighter).filter(
        Fighter.weight_class == weight_class,
        Fighter.ufc_ranking.isnot(None),
        Fighter.is_active == "Active"
    ).order_by(Fighter.ufc_ranking.asc()).limit(limit).all()
    
    return {
        "weight_class": weight_class,
        "rankings": [
            {
                "rank": fighter.ufc_ranking,
                "fighter_id": str(fighter.id),
                "name": fighter.name,
                "record": fighter.record
            }
            for fighter in ranked_fighters
        ]
    }


@router.get("/search/{name}")
async def search_fighters(
    name: str,
    limit: int = Query(10, le=20),
    db: Session = Depends(get_db)
):
    """Search fighters by name"""
    fighters = db.query(Fighter).filter(
        Fighter.name.ilike(f"%{name}%"),
        Fighter.is_active == "Active"
    ).limit(limit).all()
    
    return [
        {
            "fighter_id": str(fighter.id),
            "name": fighter.name,
            "nickname": fighter.nickname,
            "weight_class": fighter.weight_class,
            "record": fighter.record
        }
        for fighter in fighters
    ] 