from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class RankingBase(BaseModel):
    division: str
    rank: int
    fighter_name: str
    record: str

class RankingResponse(RankingBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class RankingsResponse(BaseModel):
    rankings: List[RankingResponse]
    total_count: int
    last_updated: Optional[datetime] = None
    division_filter: Optional[str] = None

class RankingsStatus(BaseModel):
    last_updated: Optional[datetime] = None
    total_rankings: int
    divisions_count: int
    is_stale: bool
    status: str

class RefreshResponse(BaseModel):
    message: str
    timestamp: datetime
    last_update: Optional[datetime] = None
    next_available: Optional[datetime] = None 