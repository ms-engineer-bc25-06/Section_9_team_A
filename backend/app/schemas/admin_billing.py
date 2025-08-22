"""
管理者決済のスキーマ
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class AdminBillingBase(BaseModel):
    """管理者決済基本スキーマ"""
    user_id: int = Field(..., description="ユーザーID")
    amount: Decimal = Field(..., description="金額", ge=0)
    currency: str = Field(default="JPY", description="通貨")
    billing_type: str = Field(..., description="決済タイプ")
    description: Optional[str] = Field(None, description="説明", max_length=500)
    status: str = Field(default="pending", description="ステータス")


class AdminBillingCreate(AdminBillingBase):
    """管理者決済作成スキーマ"""
    pass


class AdminBillingUpdate(BaseModel):
    """管理者決済更新スキーマ"""
    amount: Optional[Decimal] = Field(None, description="金額", ge=0)
    currency: Optional[str] = Field(None, description="通貨")
    billing_type: Optional[str] = Field(None, description="決済タイプ")
    description: Optional[str] = Field(None, description="説明", max_length=500)
    status: Optional[str] = Field(None, description="ステータス")


class AdminBillingResponse(AdminBillingBase):
    """管理者決済応答スキーマ"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: int
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


class AdminBillingListResponse(BaseModel):
    """管理者決済一覧応答スキーマ"""
    billing_records: List[AdminBillingResponse]
    total_count: int
    page: int
    page_size: int


class BillingSummary(BaseModel):
    """決済サマリースキーマ"""
    total_amount: Decimal
    total_count: int
    pending_amount: Decimal
    pending_count: int
    completed_amount: Decimal
    completed_count: int
    failed_amount: Decimal
    failed_count: int
    currency: str
    period_start: datetime
    period_end: datetime
