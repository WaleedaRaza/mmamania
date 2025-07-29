from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import uuid


class FighterBase(BaseModel):
    name: str
    nickname: Optional[str] = None
    weight_class: str
    record: Dict[str, int]  # {"wins": int, "losses": int, "draws": int}
    reach: Optional[float] = None
    height: Optional[float] = None
    stance: Optional[str] = None
    style: Optional[str] = None
    stats: Dict[str, Any] = {}
    ufc_ranking: Optional[int] = None
    is_active: str = "Active"


class FighterCreate(FighterBase):
    pass


class FighterUpdate(BaseModel):
    name: Optional[str] = None
    nickname: Optional[str] = None
    weight_class: Optional[str] = None
    record: Optional[Dict[str, int]] = None
    reach: Optional[float] = None
    height: Optional[float] = None
    stance: Optional[str] = None
    style: Optional[str] = None
    stats: Optional[Dict[str, Any]] = None
    ufc_ranking: Optional[int] = None
    is_active: Optional[str] = None


class FighterInDB(FighterBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Fighter(FighterInDB):
    pass


class FighterWithStats(Fighter):
    recent_fights: Optional[list] = []
    prediction_accuracy: Optional[float] = None 