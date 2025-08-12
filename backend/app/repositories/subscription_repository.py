# REVIEW: サブスクリプションリポジトリ仮実装
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.models.subscription import Subscription
from app.schemas.subscription import SubscriptionCreate, SubscriptionUpdate
from app.repositories.base import BaseRepository

class SubscriptionRepository(BaseRepository[Subscription, SubscriptionCreate, SubscriptionUpdate]):
    """サブスクリプションリポジトリ"""

    def __init__(self):
        super().__init__(Subscription)

    async def get_active_subscriptions(
        self, 
        db: AsyncSession, 
        user_id: int
    ) -> List[Subscription]:
        """ユーザーのアクティブなサブスクリプションを取得"""
        try:
            query = (
                select(Subscription)
                .where(Subscription.user_id == user_id)
                .where(Subscription.status == "active")
                .order_by(desc(Subscription.created_at))
            )
            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            return []

# グローバルインスタンス
subscription_repository = SubscriptionRepository()
