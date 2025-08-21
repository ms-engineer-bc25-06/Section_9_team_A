"""管理者用ユーザー管理スキーマ"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    """ユーザー作成リクエスト"""
    email: EmailStr
    name: str
    department: str
    role: str = "member"  # "member" or "admin"

class UserResponse(BaseModel):
    """ユーザー情報レスポンス"""
    id: int
    firebase_uid: Optional[str]
    email: str
    name: Optional[str]
    department: Optional[str]
    role: str
    has_temporary_password: bool
    is_first_login: bool
    temporary_password: Optional[str] = None  # 作成時のみ返す
    created_at: datetime
    
    class Config:
        from_attributes = True
