from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import uuid


class Fight(Base):
    __tablename__ = "fights"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_name = Column(String, nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    fighter_a_id = Column(UUID(as_uuid=True), ForeignKey("fighters.id"), nullable=False)
    fighter_b_id = Column(UUID(as_uuid=True), ForeignKey("fighters.id"), nullable=False)
    weight_class = Column(String, nullable=False)
    is_main_event = Column(Boolean, default=False)
    is_title_fight = Column(Boolean, default=False)
    odds = Column(JSON, default=dict)  # {"fighter_a": float, "fighter_b": float}
    winner_id = Column(UUID(as_uuid=True), ForeignKey("fighters.id"), nullable=True)
    method = Column(String, nullable=True)  # KO/TKO, Submission, Decision, Draw, No Contest
    round = Column(Integer, nullable=True)
    time = Column(String, nullable=True)  # Time in round (e.g., "2:34")
    ml_insights = Column(JSON, default=dict)  # ML model predictions and insights
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    fighter_a = relationship("Fighter", foreign_keys=[fighter_a_id], back_populates="fights_as_fighter_a")
    fighter_b = relationship("Fighter", foreign_keys=[fighter_b_id], back_populates="fights_as_fighter_b")
    winner = relationship("Fighter", foreign_keys=[winner_id])
    predictions = relationship("Prediction", back_populates="fight")
    debates = relationship("DebateRoom", back_populates="fight") 