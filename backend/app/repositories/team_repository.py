# REVIEW: チームリポジトリ仮実装
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.models.organization import Organization
from app.schemas.team import TeamCreate, TeamUpdate
from app.repositories.base import BaseRepository

class TeamRepository(BaseRepository[Organization, TeamCreate, TeamUpdate]):
    """チームリポジトリ"""

    def __init__(self):
        super().__init__(Organization)

    async def get_user_teams(
        self, 
        db: AsyncSession, 
        user_id: int
    ) -> List[Organization]:
        """ユーザーが所属するチーム一覧を取得"""
        try:
            query = (
                select(Organization)
                .join(Organization.members)
                .where(Organization.members.any(user_id=user_id))
                .order_by(desc(Organization.created_at))
            )
            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            return []

# グローバルインスタンス
team_repository = TeamRepository()
