"""
チームメンバー管理サービス
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.models.team_member import TeamMember
from app.schemas.team import TeamMemberCreate, TeamMemberUpdate, TeamMemberResponse
from app.core.exceptions import BridgeLineException


class TeamMemberService:
    """チームメンバー管理サービス"""
    
    async def create_team_member(
        self, db: AsyncSession, team_member_data: TeamMemberCreate
    ) -> TeamMember:
        """チームメンバーを作成"""
        try:
            team_member = TeamMember(**team_member_data.model_dump())
            db.add(team_member)
            await db.commit()
            await db.refresh(team_member)
            return team_member
        except Exception as e:
            await db.rollback()
            raise BridgeLineException(f"チームメンバーの作成に失敗しました: {str(e)}")
    
    async def get_team_member(
        self, db: AsyncSession, member_id: str
    ) -> Optional[TeamMember]:
        """チームメンバーを取得"""
        result = await db.execute(
            select(TeamMember).where(TeamMember.id == member_id)
        )
        return result.scalar_one_or_none()
    
    async def get_team_members(
        self, db: AsyncSession, team_id: str
    ) -> List[TeamMember]:
        """チームのメンバー一覧を取得"""
        result = await db.execute(
            select(TeamMember).where(TeamMember.team_id == team_id)
        )
        return result.scalars().all()
    
    async def update_team_member(
        self, db: AsyncSession, member_id: str, team_member_data: TeamMemberUpdate
    ) -> Optional[TeamMember]:
        """チームメンバーを更新"""
        try:
            update_data = team_member_data.model_dump(exclude_unset=True)
            await db.execute(
                update(TeamMember)
                .where(TeamMember.id == member_id)
                .values(**update_data)
            )
            await db.commit()
            
            # 更新後のデータを取得
            return await self.get_team_member(db, member_id)
        except Exception as e:
            await db.rollback()
            raise BridgeLineException(f"チームメンバーの更新に失敗しました: {str(e)}")
    
    async def delete_team_member(
        self, db: AsyncSession, member_id: str
    ) -> bool:
        """チームメンバーを削除"""
        try:
            await db.execute(
                delete(TeamMember).where(TeamMember.id == member_id)
            )
            await db.commit()
            return True
        except Exception as e:
            await db.rollback()
            raise BridgeLineException(f"チームメンバーの削除に失敗しました: {str(e)}")
    
    async def get_user_teams(
        self, db: AsyncSession, user_id: str
    ) -> List[TeamMember]:
        """ユーザーが所属するチーム一覧を取得"""
        result = await db.execute(
            select(TeamMember).where(TeamMember.user_id == user_id)
        )
        return result.scalars().all()
    
    async def check_member_exists(
        self, db: AsyncSession, team_id: str, user_id: str
    ) -> bool:
        """チームメンバーの存在確認"""
        result = await db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id
            )
        )
        return result.scalar_one_or_none() is not None
