# REVIEW: チームスキーマ仮実装
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TeamBase(BaseModel):
    """チームの基本スキーマ"""
    name: str
    description: Optional[str] = None
    is_public: bool = True

class TeamCreate(TeamBase):
    """チーム作成スキーマ"""
    owner_id: int

class TeamUpdate(BaseModel):
    """チーム更新スキーマ"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None

class TeamResponse(TeamBase):
    """チームレスポンススキーマ"""
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
