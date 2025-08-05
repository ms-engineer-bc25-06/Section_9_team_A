from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User

router = APIRouter()
logger = structlog.get_logger()


@router.get("/")
async def get_subscriptions(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """ユーザーのサブスクリプション情報を取得"""
    # TODO: サブスクリプションモデルとサービスを実装後に完成
    return {"message": "Subscriptions endpoint - coming soon"}


@router.post("/subscribe")
async def subscribe(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """新しいサブスクリプションを開始"""
    # TODO: サブスクリプション開始機能を実装
    return {"message": "Subscribe - coming soon"}


@router.post("/upgrade")
async def upgrade_subscription(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """サブスクリプションをアップグレード"""
    # TODO: サブスクリプションアップグレード機能を実装
    return {"message": "Upgrade subscription - coming soon"}


@router.post("/downgrade")
async def downgrade_subscription(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """サブスクリプションをダウングレード"""
    # TODO: サブスクリプションダウングレード機能を実装
    return {"message": "Downgrade subscription - coming soon"}


@router.get("/usage")
async def get_usage_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """使用量統計を取得"""
    # TODO: 使用量統計取得機能を実装
    return {"message": "Usage stats - coming soon"}
