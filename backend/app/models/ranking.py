from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from .base import Base

class Ranking(Base):
    __tablename__ = "rankings"

    id = Column(Integer, primary_key=True, index=True)
    division = Column(String(100), nullable=False, index=True)
    rank = Column(Integer, nullable=False)
    fighter_name = Column(String(200), nullable=False)
    record_string = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Ranking(id={self.id}, division='{self.division}', rank={self.rank}, fighter='{self.fighter_name}')>" 