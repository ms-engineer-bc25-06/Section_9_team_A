"""
管理者ロールのスキーマ
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RoleBase(BaseModel):
    """ロール基本スキーマ"""
    name: str = Field(..., description="ロール名", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="ロールの説明", max_length=500)
    permissions: List[str] = Field(default=[], description="権限リスト")
    is_active: bool = Field(True, description="アクティブ状態")


class RoleCreate(RoleBase):
    """ロール作成スキーマ"""
    pass


class RoleUpdate(BaseModel):
    """ロール更新スキーマ"""
    name: Optional[str] = Field(None, description="ロール名", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="ロールの説明", max_length=500)
    permissions: Optional[List[str]] = Field(None, description="権限リスト")
    is_active: Optional[bool] = Field(None, description="アクティブ状態")


class RoleResponse(RoleBase):
    """ロール応答スキーマ"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: int
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


class RoleListResponse(BaseModel):
    """ロール一覧応答スキーマ"""
    roles: List[RoleResponse]
    total_count: int
    page: int
    page_size: int
