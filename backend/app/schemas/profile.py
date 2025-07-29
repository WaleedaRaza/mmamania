from pydantic import BaseModel
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
import uuid

if TYPE_CHECKING:
    from .user import User


class ProfileBase(BaseModel):
    elo_rating: int = 1500
    favorite_fighters: List[uuid.UUID] = []
    hot_takes: List[str] = []
    total_predictions: int = 0
    correct_predictions: int = 0


class ProfileCreate(ProfileBase):
    user_id: uuid.UUID


class ProfileUpdate(BaseModel):
    elo_rating: Optional[int] = None
    favorite_fighters: Optional[List[uuid.UUID]] = None
    hot_takes: Optional[List[str]] = None


class ProfileInDB(ProfileBase):
    id: uuid.UUID
    user_id: uuid.UUID
    prediction_history: List[uuid.UUID] = []
    debates_participated: List[uuid.UUID] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Profile(ProfileInDB):
    pass


class ProfileWithUser(Profile):
    user: "User" 