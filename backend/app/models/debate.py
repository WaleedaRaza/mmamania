from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import uuid


class DebateRoom(Base):
    __tablename__ = "debate_rooms"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic = Column(String, nullable=False)
    fight_id = Column(UUID(as_uuid=True), ForeignKey("fights.id"), nullable=True)
    status = Column(String, default="Active")  # Active, Ended, Cancelled
    max_participants = Column(Integer, default=10)
    current_participants = Column(Integer, default=0)
    participants = Column(JSON, default=list)  # List of user IDs
    winner_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    debate_type = Column(String, default="Structured")  # Structured, Free-form
    round_duration = Column(Integer, default=300)  # seconds per round
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    fight = relationship("Fight", back_populates="debates")
    winner = relationship("User", foreign_keys=[winner_user_id])
    creator = relationship("User", foreign_keys=[created_by])
    messages = relationship("DebateMessage", back_populates="debate_room")


class DebateMessage(Base):
    __tablename__ = "debate_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    debate_room_id = Column(UUID(as_uuid=True), ForeignKey("debate_rooms.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(String, default="General")  # Opening, Rebuttal, Closing, General
    round_number = Column(Integer, default=1)
    is_moderated = Column(Boolean, default=False)
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    debate_room = relationship("DebateRoom", back_populates="messages")
    user = relationship("User", back_populates="debate_messages") 