from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
import stripe
from typing import Dict, Any
from sqlalchemy import select
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.config import settings
from app.models.user import User
from app.models.payment import Payment
from app.models.subscription import Subscription
from app.models.organization import Organization

router = APIRouter()
logger = structlog.get_logger()

# Stripe設定
stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/stripe")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Stripe Webhook"""
    try:
        # リクエストボディを取得
        body = await request.body()
        
        # Webhook署名を検証
        signature = request.headers.get("stripe-signature")
        if not signature:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing stripe-signature header"
            )
        
        # Webhookイベントを検証・解析
        try:
            event = stripe.Webhook.construct_event(
                body, signature, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid payload"
            )
        except stripe.error.SignatureVerificationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid signature"
            )
        
        # イベントタイプに応じて処理
        event_type = event["type"]
        
        if event_type == "checkout.session.completed":
            await handle_checkout_completed(event, db)
        elif event_type == "invoice.payment_succeeded":
            await handle_payment_succeeded(event, db)
        elif event_type == "invoice.payment_failed":
            await handle_payment_failed(event, db)
        elif event_type == "customer.subscription.updated":
            await handle_subscription_updated(event, db)
        elif event_type == "customer.subscription.deleted":
            await handle_subscription_deleted(event, db)
        else:
            # 未対応のイベントタイプはログ出力のみ
            logger.info(f"Unhandled event type: {event_type}")
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed"
        )


async def handle_checkout_completed(event: Dict[str, Any], db: AsyncSession):
    """チェックアウト完了時の処理"""
    session = event["data"]["object"]
    
    # 決済情報を取得
    payment_intent_id = session.get("payment_intent")
    if not payment_intent_id:
        return
    
    # 決済詳細を取得
    payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
    
    # メタデータから追加ユーザー数を取得
    metadata = session.get("metadata", {})
    additional_users = int(metadata.get("additional_users", 0))
    organization_id = int(metadata.get("organization_id", 0))
    
    if additional_users > 0 and organization_id > 0:
        # 組織のメンバー数を更新
        await update_organization_member_count(db, organization_id, additional_users)
        
        # 決済レコードを更新
        await update_payment_status(db, payment_intent_id, "succeeded")

async def handle_payment_succeeded(event: Dict[str, Any], db: AsyncSession):
    """支払い成功時の処理"""
    invoice = event["data"]["object"]
    subscription_id = invoice.get("subscription")
    
    if subscription_id:
        # サブスクリプション情報を更新
        await update_subscription_status(db, subscription_id, "active")

async def handle_payment_failed(event: Dict[str, Any], db: AsyncSession):
    """支払い失敗時の処理"""
    invoice = event["data"]["object"]
    subscription_id = invoice.get("subscription")
    
    if subscription_id:
        # サブスクリプションステータスを更新
        await update_subscription_status(db, subscription_id, "past_due")

async def handle_subscription_updated(event: Dict[str, Any], db: AsyncSession):
    """サブスクリプション更新時の処理"""
    subscription = event["data"]["object"]
    stripe_subscription_id = subscription["id"]
    
    # サブスクリプション情報を更新
    await update_subscription_info(db, stripe_subscription_id, subscription)

async def handle_subscription_deleted(event: Dict[str, Any], db: AsyncSession):
    """サブスクリプション削除時の処理"""
    subscription = event["data"]["object"]
    stripe_subscription_id = subscription["id"]
    
    # サブスクリプション情報を更新
    await update_subscription_status(db, subscription_id, "canceled")

async def update_organization_member_count(db: AsyncSession, organization_id: int, additional_users: int):
    """組織のメンバー数を更新"""
    try:
        # 組織情報を取得
        result = await db.execute(
            select(Organization).where(Organization.id == organization_id)
        )
        organization = result.scalar_one_or_none()
        
        if organization:
            # 現在のメンバー数に追加
            current_members = organization.member_count or 0
            organization.member_count = current_members + additional_users
            organization.updated_at = datetime.utcnow()
            
            await db.commit()
            logger.info(f"Updated organization {organization_id} member count to {organization.member_count}")
    except Exception as e:
        logger.error(f"Error updating organization member count: {str(e)}")
        await db.rollback()

async def update_payment_status(db: AsyncSession, payment_intent_id: str, status: str):
    """決済ステータスを更新"""
    try:
        result = await db.execute(
            select(Payment).where(Payment.stripe_payment_intent_id == payment_intent_id)
        )
        payment = result.scalar_one_or_none()
        
        if payment:
            payment.status = status
            payment.updated_at = datetime.utcnow()
            
            await db.commit()
            logger.info(f"Updated payment {payment_intent_id} status to {status}")
    except Exception as e:
        logger.error(f"Error updating payment status: {str(e)}")
        await db.rollback()

async def update_subscription_status(db: AsyncSession, stripe_subscription_id: str, status: str):
    """サブスクリプションステータスを更新"""
    try:
        result = await db.execute(
            select(Subscription).where(Subscription.stripe_subscription_id == stripe_subscription_id)
        )
        data = result.scalar_one_or_none()
        
        if data:
            data.status = status
            data.updated_at = datetime.utcnow()
            
            await db.commit()
            logger.info(f"Updated subscription {stripe_subscription_id} status to {status}")
    except Exception as e:
        logger.error(f"Error updating subscription status: {str(e)}")
        await db.rollback()

async def update_subscription_info(db: AsyncSession, stripe_subscription_id: str, stripe_data: Dict[str, Any]):
    """サブスクリプション情報を更新"""
    try:
        result = await db.execute(
            select(Subscription).where(Subscription.stripe_subscription_id == stripe_subscription_id)
        )
        data = result.scalar_one_or_none()
        
        if data:
            # Stripeデータから情報を更新
            data.status = stripe_data.get("status", data.status)
            data.current_period_start = datetime.fromtimestamp(
                stripe_data.get("current_period_start", 0)
            ) if stripe_data.get("current_period_start") else None
            data.current_period_end = datetime.fromtimestamp(
                stripe_data.get("current_period_end", 0)
            ) if stripe_data.get("current_period_end") else None
            data.quantity = stripe_data.get("quantity", data.quantity)
            data.updated_at = datetime.utcnow()
            
            await db.commit()
            logger.info(f"Updated subscription {stripe_subscription_id} info")
    except Exception as e:
        logger.error(f"Error updating subscription info: {str(e)}")
        await db.rollback()


@router.post("/firebase")
async def firebase_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Firebase Webhook"""
    # TODO: Firebase Webhook処理を実装
    return {"message": "Firebase webhook - coming soon"}


@router.post("/openai")
async def openai_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """OpenAI Webhook"""
    # TODO: OpenAI Webhook処理を実装
    return {"message": "OpenAI webhook - coming soon"}
