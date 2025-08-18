from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class UserCountInfo(BaseModel):
    """利用者数情報"""
    total_users: int
    organizations_over_limit: int
    total_additional_cost: int


class OrganizationBillingInfo(BaseModel):
    """組織の決済・課金情報"""
    organization_id: int
    organization_name: str
    organization_slug: str
    member_count: int
    free_user_limit: int
    cost_per_user: int
    is_over_limit: bool
    additional_users: int
    additional_cost: int
    subscription_status: str
    stripe_customer_id: Optional[str] = None
    last_payment_date: Optional[datetime] = None
    last_payment_amount: Optional[int] = None

    class Config:
        from_attributes = True


class BillingSummary(BaseModel):
    """決済・課金サマリー"""
    total_organizations: int
    total_users: int
    total_additional_cost: int
    organizations_over_limit: int
    organizations: List[OrganizationBillingInfo]

    class Config:
        from_attributes = True


class CreateCheckoutSessionRequest(BaseModel):
    """チェックアウトセッション作成リクエスト"""
    organization_id: int
    additional_users: int
    amount: int  # Amount in cents
    currency: str = "jpy"
    success_url: str
    cancel_url: str


class CheckoutSessionResponse(BaseModel):
    """チェックアウトセッション作成レスポンス"""
    session_id: str
    checkout_url: str
    amount: int
    currency: str
    organization_id: int
    additional_users: int


class PaymentConfirmationRequest(BaseModel):
    """決済完了確認リクエスト"""
    session_id: str
    payment_intent_id: str
    organization_id: int


class PaymentConfirmationResponse(BaseModel):
    """決済完了確認レスポンス"""
    success: bool
    payment_id: int
    amount: int
    currency: str
    status: str
    message: str
