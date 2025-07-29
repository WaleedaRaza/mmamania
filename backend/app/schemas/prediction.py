from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PredictionBase(BaseModel):
    fight_id: str
    winner: str
    method: str
    round: int
    confidence: float

class PredictionCreate(PredictionBase):
    pass

class Prediction(PredictionBase):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class PredictionWithFight(Prediction):
    fight_title: Optional[str] = None
    fight_date: Optional[datetime] = None 