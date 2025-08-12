from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, date

class UserBase(BaseModel):
    """ユーザーの基本スキーマ"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    nickname: Optional[str] = None
    department: Optional[str] = None
    join_date: Optional[date] = None
    birth_date: Optional[date] = None
    hometown: Optional[str] = None
    residence: Optional[str] = None
    hobbies: Optional[str] = None
    student_activities: Optional[str] = None
    holiday_activities: Optional[str] = None
    favorite_food: Optional[str] = None
    favorite_media: Optional[str] = None
    favorite_music: Optional[str] = None
    pets_oshi: Optional[str] = None
    respected_person: Optional[str] = None
    motto: Optional[str] = None
    future_goals: Optional[str] = None

class UserCreate(UserBase):
    """ユーザー作成スキーマ"""
    firebase_uid: Optional[str] = None
    hashed_password: Optional[str] = None

class UserUpdate(BaseModel):
    """ユーザー更新スキーマ"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    nickname: Optional[str] = None
    department: Optional[str] = None
    join_date: Optional[date] = None
    birth_date: Optional[date] = None
    hometown: Optional[str] = None
    residence: Optional[str] = None
    hobbies: Optional[str] = None
    student_activities: Optional[str] = None
    holiday_activities: Optional[str] = None
    favorite_food: Optional[str] = None
    favorite_media: Optional[str] = None
    favorite_music: Optional[str] = None
    pets_oshi: Optional[str] = None
    respected_person: Optional[str] = None
    motto: Optional[str] = None
    future_goals: Optional[str] = None

class UserResponse(UserBase):
    """ユーザーレスポンススキーマ"""
    id: int
    firebase_uid: Optional[str] = None
    is_active: bool
    is_verified: bool
    is_premium: bool
    is_admin: bool
    subscription_status: str
    subscription_end_date: Optional[datetime] = None
    monthly_voice_minutes: int
    monthly_analysis_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True
