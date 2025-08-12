# REVIEW: チームリポジトリ仮実装
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.models.team import Team
from app.schemas.team import TeamCreate, TeamUpdate
from app.repositories.base import BaseRepository

class TeamRepository(BaseRepository[Team, TeamCreate, TeamUpdate]):
    """チームリポジトリ"""

    def __init__(self):
        super().__init__(Team)

    async def get_user_teams(
        self, 
        db: AsyncSession, 
        user_id: int
    ) -> List[Team]:
        """ユーザーが所属するチーム一覧を取得"""
        try:
            query = (
                select(Team)
                .join(Team.members)
                .where(Team.members.any(user_id=user_id))
                .order_by(desc(Team.created_at))
            )
            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            return []

# グローバルインスタンス
team_repository = TeamRepository()
