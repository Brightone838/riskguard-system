from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database.base import Base

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    action = Column(String)
    login_attempts = Column(Integer, default=0)
    records_accessed = Column(Integer, default=0)
    authenticated = Column(Boolean, default=True)
    hour = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())