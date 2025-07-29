from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import uuid


class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    elo_rating = Column(Integer, default=1500, nullable=False)
    favorite_fighters = Column(JSON, default=list)  # List of fighter IDs
    prediction_history = Column(JSON, default=list)  # List of prediction IDs
    hot_takes = Column(JSON, default=list)  # List of hot take strings
    debates_participated = Column(JSON, default=list)  # List of debate IDs
    total_predictions = Column(Integer, default=0)
    correct_predictions = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="profile") 