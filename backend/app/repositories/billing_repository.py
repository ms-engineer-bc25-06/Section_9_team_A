# REVIEW: 請求リポジトリ仮実装
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.models.billing import Billing
from app.schemas.billing import BillingCreate, BillingUpdate
from app.repositories.base import BaseRepository

class BillingRepository(BaseRepository[Billing, BillingCreate, BillingUpdate]):
    """請求リポジトリ"""

    def __init__(self):
        super().__init__(Billing)

    async def get_user_billings(
        self, 
        db: AsyncSession, 
        user_id: int
    ) -> List[Billing]:
        """ユーザーの請求履歴を取得"""
        try:
            query = (
                select(Billing)
                .where(Billing.user_id == user_id)
                .order_by(desc(Billing.created_at))
            )
            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            return []

# グローバルインスタンス
billing_repository = BillingRepository()
