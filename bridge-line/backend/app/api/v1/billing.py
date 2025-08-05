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
    # TODO: 決済モデルとサービスを実装後に完成
    return {"message": "Billing info endpoint - coming soon"}


@router.post("/create-payment-intent")
async def create_payment_intent(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Stripe決済インテントを作成"""
    # TODO: Stripe決済機能を実装
    return {"message": "Create payment intent - coming soon"}


@router.get("/payment-history")
async def get_payment_history(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """支払い履歴を取得"""
    # TODO: 支払い履歴取得機能を実装
    return {"message": "Payment history - coming soon"}


@router.post("/cancel-subscription")
async def cancel_subscription(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """サブスクリプションをキャンセル"""
    # TODO: サブスクリプションキャンセル機能を実装
    return {"message": "Cancel subscription - coming soon"}


@router.post("/update-payment-method")
async def update_payment_method(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """支払い方法を更新"""
    # TODO: 支払い方法更新機能を実装
    return {"message": "Update payment method - coming soon"}
