from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import uuid


class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    fight_id = Column(UUID(as_uuid=True), ForeignKey("fights.id"), nullable=False)
    predicted_winner = Column(UUID(as_uuid=True), ForeignKey("fighters.id"), nullable=False)
    predicted_method = Column(String, nullable=False)  # KO/TKO, Submission, Decision
    predicted_round = Column(Integer, nullable=True)
    confidence = Column(Integer, default=50)  # 1-100 confidence level
    actual_result = Column(String, nullable=True)  # Correct, Incorrect, Partial
    elo_change = Column(Integer, default=0)
    points_earned = Column(Integer, default=0)
    is_correct = Column(Boolean, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="predictions")
    fight = relationship("Fight", back_populates="predictions")
    predicted_winner_fighter = relationship("Fighter", foreign_keys=[predicted_winner]) 