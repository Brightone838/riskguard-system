from pydantic import BaseModel
from typing import Optional, List  # Add List here
from datetime import datetime

class ActivityCreate(BaseModel):
    user_id: str
    action: str
    login_attempts: int = 0
    records_accessed: int = 0
    authenticated: bool = True
    hour: int = 12
    location: Optional[str] = None
    usual_location: Optional[str] = None
    data_sensitivity: Optional[str] = "low"

class ActivityResponse(BaseModel):
    id: int
    user_id: str
    action: str
    login_attempts: int
    records_accessed: int
    authenticated: bool
    hour: int
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class ActivityListResponse(BaseModel):
    total: int
    activities: List[ActivityResponse]  # This needs List imported