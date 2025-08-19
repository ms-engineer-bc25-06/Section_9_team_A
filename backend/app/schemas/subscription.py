# REVIEW: サブスクリプションスキーマ仮実装
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SubscriptionBase(BaseModel):
    """サブスクリプションの基本スキーマ"""
    plan_name: str
    status: str
    price: float

class SubscriptionCreate(SubscriptionBase):
    """サブスクリプション作成スキーマ"""
    user_id: int

class SubscriptionUpdate(BaseModel):
    """サブスクリプション更新スキーマ"""
    plan_name: Optional[str] = None
    status: Optional[str] = None
    price: Optional[float] = None

class SubscriptionResponse(SubscriptionBase):
    """サブスクリプションレスポンススキーマ"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
