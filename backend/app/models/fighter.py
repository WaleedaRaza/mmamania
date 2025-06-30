from sqlalchemy import Column, String, Integer, Float, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import uuid


class Fighter(Base):
    __tablename__ = "fighters"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)
    nickname = Column(String)
    weight_class = Column(String, nullable=False, index=True)
    record = Column(JSON, nullable=False)  # {"wins": int, "losses": int, "draws": int}
    reach = Column(Float)  # in inches
    height = Column(Float)  # in cm
    stance = Column(String)  # Orthodox, Southpaw, Switch
    style = Column(String)  # Striker, Grappler, Mixed
    stats = Column(JSON, default=dict)  # Detailed fight statistics
    ufc_ranking = Column(Integer)  # Current UFC ranking
    is_active = Column(String, default="Active")  # Active, Retired, Suspended
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    fights_as_fighter_a = relationship("Fight", foreign_keys="Fight.fighter_a_id", back_populates="fighter_a")
    fights_as_fighter_b = relationship("Fight", foreign_keys="Fight.fighter_b_id", back_populates="fighter_b") 