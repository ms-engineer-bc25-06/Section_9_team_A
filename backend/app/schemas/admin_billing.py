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


# 管理者用決済・課金APIで使用するスキーマ

class OrganizationBillingInfo(BaseModel):
    """組織の決済・課金情報スキーマ"""
    organization_id: int
    organization_name: str
    organization_slug: str
    member_count: int
    free_user_limit: int
    cost_per_user: int
    is_over_limit: bool
    additional_users: int
    additional_cost: int
    subscription_status: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    last_payment_date: Optional[datetime] = None
    last_payment_amount: Optional[int] = None

    class Config:
        from_attributes = True


class BillingSummaryResponse(BaseModel):
    """決済・課金サマリーレスポンススキーマ"""
    total_organizations: int
    total_users: int
    total_additional_cost: int
    organizations_over_limit: int
    organizations: List[OrganizationBillingInfo]

    class Config:
        from_attributes = True


class UserCountInfo(BaseModel):
    """利用者数情報スキーマ"""
    total_users: int
    organizations_over_limit: int
    total_additional_cost: int

    class Config:
        from_attributes = True


class CreateCheckoutSessionRequest(BaseModel):
    """Stripe Checkout Session作成リクエストスキーマ"""
    organization_id: int
    additional_users: int
    amount: int  # セント単位
    currency: str = "JPY"
    return_url: Optional[str] = None

    class Config:
        from_attributes = True


class CheckoutSessionResponse(BaseModel):
    """Stripe Checkout Session作成レスポンススキーマ"""
    session_id: str
    checkout_url: str
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True
