# REVIEW: 請求スキーマ仮実装
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BillingBase(BaseModel):
    """請求の基本スキーマ"""
    amount: float
    currency: str = "JPY"
    description: str
    status: str

class BillingCreate(BillingBase):
    """請求作成スキーマ"""
    user_id: int

class BillingUpdate(BaseModel):
    """請求更新スキーマ"""
    amount: Optional[float] = None
    currency: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class BillingResponse(BillingBase):
    """請求レスポンススキーマ"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
