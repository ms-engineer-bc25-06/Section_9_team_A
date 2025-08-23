# 組織リポジトリ（チーム機能を統合）
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
import structlog

from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.schemas.team import TeamCreate, TeamUpdate
from app.repositories.base import BaseRepository

logger = structlog.get_logger()

class OrganizationRepository(BaseRepository[Organization, TeamCreate, TeamUpdate]):
    """組織リポジトリ（チーム機能を統合）"""

    def __init__(self):
        super().__init__(Organization)

    async def get_user_organizations(
        self, 
        db: AsyncSession, 
        user_id: int
    ) -> List[Organization]:
        """ユーザーが所属する組織一覧を取得"""
        try:
            query = (
                select(Organization)
                .join(OrganizationMember, Organization.id == OrganizationMember.organization_id)
                .where(OrganizationMember.user_id == user_id)
                .order_by(desc(Organization.created_at))
            )
            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting user organizations: {e}")
            return []

    async def add_member(
        self, 
        db: AsyncSession, 
        organization_id: int, 
        user_id: int, 
        role: str = "member"
    ) -> Optional[OrganizationMember]:
        """組織にメンバーを追加"""
        try:
            # 既存メンバーのチェック
            existing_member = await db.execute(
                select(OrganizationMember).where(
                    and_(
                        OrganizationMember.organization_id == organization_id,
                        OrganizationMember.user_id == user_id
                    )
                )
            )
            if existing_member.scalar_one_or_none():
                logger.warning(f"User {user_id} is already a member of organization {organization_id}")
                return None

            # 新しいメンバーを作成
            member = OrganizationMember(
                organization_id=organization_id,
                user_id=user_id,
                role=role,
                status="active",
                is_active=True
            )
            db.add(member)
            await db.commit()
            await db.refresh(member)
            
            logger.info(f"Added member {user_id} to organization {organization_id} with role {role}")
            return member
        except Exception as e:
            await db.rollback()
            logger.error(f"Error adding member to organization: {e}")
            return None

    async def remove_member(
        self, 
        db: AsyncSession, 
        organization_id: int, 
        user_id: int
    ) -> bool:
        """組織からメンバーを削除"""
        try:
            # メンバーを取得
            member_query = select(OrganizationMember).where(
                and_(
                    OrganizationMember.organization_id == organization_id,
                    OrganizationMember.user_id == user_id
                )
            )
            result = await db.execute(member_query)
            member = result.scalar_one_or_none()
            
            if not member:
                logger.warning(f"Member {user_id} not found in organization {organization_id}")
                return False
            
            # オーナーは削除できない
            if member.role == "owner":
                logger.warning(f"Cannot remove owner {user_id} from organization {organization_id}")
                return False
            
            # メンバーを削除
            await db.delete(member)
            await db.commit()
            
            logger.info(f"Removed member {user_id} from organization {organization_id}")
            return True
        except Exception as e:
            await db.rollback()
            logger.error(f"Error removing member from organization: {e}")
            return False

    async def update_member_role(
        self, 
        db: AsyncSession, 
        organization_id: int, 
        user_id: int,
        new_role: str
    ) -> Optional[OrganizationMember]:
        """メンバーの役割を更新"""
        try:
            # メンバーを取得
            member_query = select(OrganizationMember).where(
                and_(
                    OrganizationMember.organization_id == organization_id,
                    OrganizationMember.user_id == user_id
                )
            )
            result = await db.execute(member_query)
            member = result.scalar_one_or_none()
            
            if not member:
                logger.warning(f"Member {user_id} not found in organization {organization_id}")
                return None
            
            # オーナーの役割は変更できない
            if member.role == "owner":
                logger.warning(f"Cannot change role of owner {user_id} in organization {organization_id}")
                return None
            
            # 役割を更新
            member.role = new_role
            db.add(member)
            await db.commit()
            await db.refresh(member)
            
            logger.info(f"Updated role of member {user_id} in organization {organization_id} to {new_role}")
            return member
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating member role: {e}")
            return None

    async def get_organization_members(
        self, 
        db: AsyncSession, 
        organization_id: int
    ) -> List[OrganizationMember]:
        """組織のメンバー一覧を取得"""
        try:
            query = (
                select(OrganizationMember)
                .where(OrganizationMember.organization_id == organization_id)
                .order_by(OrganizationMember.joined_at)
            )
            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting organization members: {e}")
            return []

    async def get_member_by_user(
        self, 
        db: AsyncSession, 
        organization_id: int, 
        user_id: int
    ) -> Optional[OrganizationMember]:
        """特定のユーザーの組織メンバー情報を取得"""
        try:
            query = select(OrganizationMember).where(
                and_(
                    OrganizationMember.organization_id == organization_id,
                    OrganizationMember.user_id == user_id
                )
            )
            result = await db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting member by user: {e}")
            return None

    async def check_member_exists(
        self, 
        db: AsyncSession, 
        organization_id: int, 
        user_id: int
    ) -> bool:
        """組織メンバーの存在確認"""
        try:
            member = await self.get_member_by_user(db, organization_id, user_id)
            return member is not None
        except Exception as e:
            logger.error(f"Error checking member existence: {e}")
            return False

    # ==================== 互換性メソッド（旧TeamRepository用） ====================

    async def get_user_teams(
        self, 
        db: AsyncSession, 
        user_id: int
    ) -> List[Organization]:
        """ユーザーが所属するチーム一覧を取得（互換性のため）"""
        return await self.get_user_organizations(db, user_id)

    async def create_with_schema(
        self, 
        db: AsyncSession, 
        *, 
        obj_in: TeamCreate
    ) -> Organization:
        """TeamCreateスキーマで組織を作成（互換性のため）"""
        try:
            return await self.create(db, obj_in=obj_in)
        except Exception as e:
            logger.error(f"Error creating organization with TeamCreate schema: {e}")
            raise

    async def update_with_schema(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: Organization, 
        obj_in: TeamUpdate
    ) -> Organization:
        """TeamUpdateスキーマで組織を更新（互換性のため）"""
        try:
            return await self.update(db, db_obj=db_obj, obj_in=obj_in)
        except Exception as e:
            logger.error(f"Error updating organization with TeamUpdate schema: {e}")
            raise

# グローバルインスタンス
organization_repository = OrganizationRepository()
