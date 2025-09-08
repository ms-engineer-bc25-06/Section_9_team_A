from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User

router = APIRouter()
logger = structlog.get_logger()


@router.get("/")
async def get_billing_info(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """ユーザーの決済情報を取得"""
    return {"message": "Billing info endpoint - coming soon"}


@router.post("/create-payment-intent")
async def create_payment_intent(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Stripe決済インテントを作成"""
    return {"message": "Create payment intent - coming soon"}


@router.get("/payment-history")
async def get_payment_history(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """支払い履歴を取得"""
    return {"message": "Payment history - coming soon"}


@router.post("/cancel-subscription")
async def cancel_subscription(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """サブスクリプションをキャンセル"""
    return {"message": "Cancel subscription - coming soon"}


@router.post("/update-payment-method")
async def update_payment_method(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """支払い方法を更新"""
    return {"message": "Update payment method - coming soon"}
