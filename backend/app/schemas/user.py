from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserProfileResponse(BaseModel):
    bio: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    interests: Optional[List[str]] = None
    communication_style: Optional[str] = None
    collaboration_score: Optional[float] = None
    leadership_score: Optional[float] = None
    empathy_score: Optional[float] = None
    assertiveness_score: Optional[float] = None
    creativity_score: Optional[float] = None
    analytical_score: Optional[float] = None
    visibility_settings: Optional[dict] = None
    total_chat_sessions: Optional[int] = None
    total_speaking_time_seconds: Optional[int] = None
    last_analysis_at: Optional[datetime] = None

class TeamSummaryResponse(BaseModel):
    id: str
    name: str
    role: str

class UserMeResponse(BaseModel):
    id: str
    firebase_uid: str
    email: str
    display_name: str
    avatar_url: Optional[str] = None
    profile: Optional[UserProfileResponse] = None
    teams: List[TeamSummaryResponse] = []
    last_active_at: Optional[datetime] = None
    created_at: datetime
