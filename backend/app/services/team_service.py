from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, asc
import structlog

from app.models.team import Team
from app.models.team_member import TeamMember
from app.repositories.team_repository import team_repository
from app.schemas.team import TeamCreate, TeamUpdate, TeamResponse

logger = structlog.get_logger()


class TeamService:
    """チームサービス"""

    async def create_team(self, db: AsyncSession, team_data: TeamCreate) -> Team:
        """チームを作成"""
        return await team_repository.create(db, team_data)

    async def get_team(self, db: AsyncSession, team_id: int) -> Optional[Team]:
        """チームを取得"""
        return await team_repository.get(db, team_id)

    async def get_teams(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[Team]:
        """チーム一覧を取得"""
        return await team_repository.get_multi(db, skip=skip, limit=limit)

    async def update_team(
        self, db: AsyncSession, team_id: int, team_data: TeamUpdate
    ) -> Optional[Team]:
        """チームを更新"""
        return await team_repository.update(db, team_id, team_data)

    async def delete_team(self, db: AsyncSession, team_id: int) -> bool:
        """チームを削除"""
        return await team_repository.delete(db, team_id)

    async def get_user_teams(
        self, db: AsyncSession, user_id: int
    ) -> List[Team]:
        """ユーザーが所属するチームを取得"""
        return await team_repository.get_user_teams(db, user_id)

    async def add_member(
        self, db: AsyncSession, team_id: int, user_id: int, role: str = "member"
    ) -> TeamMember:
        """チームにメンバーを追加"""
        return await team_repository.add_member(db, team_id, user_id, role)

    async def remove_member(
        self, db: AsyncSession, team_id: int, user_id: int
    ) -> bool:
        """チームからメンバーを削除"""
        return await team_repository.remove_member(db, team_id, user_id)

    async def update_member_role(
        self, db: AsyncSession, team_id: int, user_id: int, new_role: str
    ) -> Optional[TeamMember]:
        """メンバーの役割を更新"""
        return await team_repository.update_member_role(db, team_id, user_id, new_role)


# シングルトンインスタンス
team_service = TeamService()
