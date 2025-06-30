from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid


class FightBase(BaseModel):
    event_name: str
    date: datetime
    fighter_a_id: uuid.UUID
    fighter_b_id: uuid.UUID
    weight_class: str
    is_main_event: bool = False
    is_title_fight: bool = False
    odds: Dict[str, float] = {}
    winner_id: Optional[uuid.UUID] = None
    method: Optional[str] = None
    round: Optional[int] = None
    time: Optional[str] = None
    ml_insights: Dict[str, Any] = {}
    is_completed: bool = False


class FightCreate(FightBase):
    pass


class FightUpdate(BaseModel):
    event_name: Optional[str] = None
    date: Optional[datetime] = None
    odds: Optional[Dict[str, float]] = None
    winner_id: Optional[uuid.UUID] = None
    method: Optional[str] = None
    round: Optional[int] = None
    time: Optional[str] = None
    ml_insights: Optional[Dict[str, Any]] = None
    is_completed: Optional[bool] = None


class FightInDB(FightBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Fight(FightInDB):
    pass


class FightWithFighters(Fight):
    fighter_a: "Fighter"
    fighter_b: "Fighter"
    winner: Optional["Fighter"] = None


class PredictionBase(BaseModel):
    fight_id: uuid.UUID
    predicted_winner: uuid.UUID
    predicted_method: str
    predicted_round: Optional[int] = None
    confidence: int = 50


class PredictionCreate(PredictionBase):
    pass


class PredictionUpdate(BaseModel):
    predicted_winner: Optional[uuid.UUID] = None
    predicted_method: Optional[str] = None
    predicted_round: Optional[int] = None
    confidence: Optional[int] = None


class PredictionInDB(PredictionBase):
    id: uuid.UUID
    user_id: uuid.UUID
    actual_result: Optional[str] = None
    elo_change: int = 0
    points_earned: int = 0
    is_correct: Optional[bool] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Prediction(PredictionInDB):
    pass


class PredictionWithFight(Prediction):
    fight: Fight
    predicted_winner_fighter: "Fighter" 