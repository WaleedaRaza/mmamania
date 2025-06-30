from pydantic import BaseModel
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
import uuid

if TYPE_CHECKING:
    from .user import User
    from .fight import Fight


class DebateRoomBase(BaseModel):
    topic: str
    fight_id: Optional[uuid.UUID] = None
    max_participants: int = 10
    debate_type: str = "Structured"
    round_duration: int = 300


class DebateRoomCreate(DebateRoomBase):
    pass


class DebateRoomUpdate(BaseModel):
    topic: Optional[str] = None
    status: Optional[str] = None
    winner_user_id: Optional[uuid.UUID] = None


class DebateRoomInDB(DebateRoomBase):
    id: uuid.UUID
    status: str = "Active"
    current_participants: int = 0
    participants: List[uuid.UUID] = []
    winner_user_id: Optional[uuid.UUID] = None
    created_by: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DebateRoom(DebateRoomInDB):
    pass


class DebateRoomWithDetails(DebateRoom):
    fight: Optional["Fight"] = None
    creator: "User"
    winner: Optional["User"] = None
    messages: List["DebateMessage"] = []


class DebateMessageBase(BaseModel):
    content: str
    message_type: str = "General"
    round_number: int = 1


class DebateMessageCreate(DebateMessageBase):
    pass


class DebateMessageUpdate(BaseModel):
    content: Optional[str] = None
    message_type: Optional[str] = None
    round_number: Optional[int] = None


class DebateMessageInDB(DebateMessageBase):
    id: uuid.UUID
    debate_room_id: uuid.UUID
    user_id: uuid.UUID
    is_moderated: bool = False
    upvotes: int = 0
    downvotes: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class DebateMessage(DebateMessageInDB):
    pass


class DebateMessageWithUser(DebateMessage):
    user: "User" 