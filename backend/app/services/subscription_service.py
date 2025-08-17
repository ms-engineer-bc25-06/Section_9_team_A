from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, asc
import structlog

from app.repositories.subscription_repository import subscription_repository

logger = structlog.get_logger()


class SubscriptionService:
    """サブスクリプションサービス"""

    async def get_user_subscription(
        self, db: AsyncSession, user_id: int
    ) -> Optional[Any]:
        """ユーザーのサブスクリプションを取得"""
        return await subscription_repository.get_user_subscription(db, user_id)

    async def create_subscription(
        self, db: AsyncSession, subscription_data: Dict[str, Any]
    ) -> Any:
        """サブスクリプションを作成"""
        return await subscription_repository.create_subscription(db, subscription_data)

    async def update_subscription(
        self, db: AsyncSession, subscription_id: int, update_data: Dict[str, Any]
    ) -> Optional[Any]:
        """サブスクリプションを更新"""
        return await subscription_repository.update_subscription(db, subscription_id, update_data)

    async def cancel_subscription(
        self, db: AsyncSession, subscription_id: int
    ) -> bool:
        """サブスクリプションをキャンセル"""
        return await subscription_repository.cancel_subscription(db, subscription_id)

    async def get_active_subscriptions(
        self, db: AsyncSession, user_id: int
    ) -> List[Any]:
        """アクティブなサブスクリプションを取得"""
        return await subscription_repository.get_active_subscriptions(db, user_id)

    async def check_subscription_status(
        self, db: AsyncSession, user_id: int
    ) -> Dict[str, Any]:
        """サブスクリプションの状態をチェック"""
        return await subscription_repository.check_subscription_status(db, user_id)


# シングルトンインスタンス
subscription_service = SubscriptionService()
