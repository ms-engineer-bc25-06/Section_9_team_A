from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, asc, update, delete
import structlog

from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.repositories.organization_repository import organization_repository
from app.schemas.team import TeamCreate, TeamUpdate, TeamResponse, OrganizationMemberCreate, OrganizationMemberUpdate, OrganizationMemberResponse
from app.core.exceptions import BridgeLineException

logger = structlog.get_logger()


class OrganizationService:
    """組織サービス（チーム機能を統合）"""

    # ==================== 組織基本管理 ====================

    async def create_organization(self, db: AsyncSession, org_data: TeamCreate, creator_id: int) -> Organization:
        """組織を作成"""
        try:
            # 組織データを準備
            org_dict = org_data.model_dump()
            org_dict['owner_id'] = creator_id
            
            # 組織を作成
            organization = await organization_repository.create(db, org_dict)
            
            # 作成者をオーナーとして追加
            await self.add_member(
                db, 
                organization.id, 
                creator_id, 
                role="owner"
            )
            
            logger.info(f"組織を作成しました: {organization.name} (ID: {organization.id})")
            return organization
            
        except Exception as e:
            logger.error(f"組織作成に失敗: {e}")
            raise BridgeLineException(f"組織の作成に失敗しました: {str(e)}")

    async def get_organization(self, db: AsyncSession, org_id: int) -> Optional[Organization]:
        """組織を取得"""
        try:
            return await organization_repository.get(db, org_id)
        except Exception as e:
            logger.error(f"組織取得に失敗: {e}")
            return None

    async def get_organizations(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[Organization]:
        """組織一覧を取得"""
        try:
            return await organization_repository.get_multi(db, skip=skip, limit=limit)
        except Exception as e:
            logger.error(f"組織一覧取得に失敗: {e}")
            return []

    async def update_organization(
        self, db: AsyncSession, org_id: int, org_data: TeamUpdate
    ) -> Optional[Organization]:
        """組織を更新"""
        try:
            org = await organization_repository.get(db, org_id)
            if not org:
                return None
            
            return await organization_repository.update(db, org, org_data)
        except Exception as e:
            logger.error(f"組織更新に失敗: {e}")
            raise BridgeLineException(f"組織の更新に失敗しました: {str(e)}")

    async def delete_organization(self, db: AsyncSession, org_id: int) -> bool:
        """組織を削除"""
        try:
            return await organization_repository.delete(db, org_id)
        except Exception as e:
            logger.error(f"組織削除に失敗: {e}")
            raise BridgeLineException(f"組織の削除に失敗しました: {str(e)}")

    async def get_user_organizations(
        self, db: AsyncSession, user_id: int
    ) -> List[Organization]:
        """ユーザーが所属する組織一覧を取得"""
        try:
            return await organization_repository.get_user_organizations(db, user_id)
        except Exception as e:
            logger.error(f"ユーザー組織一覧取得に失敗: {e}")
            return []

    # ==================== メンバー管理 ====================

    async def add_member(
        self, db: AsyncSession, org_id: int, user_id: int, role: str = "member"
    ) -> OrganizationMember:
        """組織にメンバーを追加"""
        try:
            # 既存メンバーかチェック
            existing_member = await self.get_member_by_user(db, org_id, user_id)
            if existing_member:
                raise BridgeLineException("ユーザーは既にこの組織のメンバーです")
            
            # メンバーを作成
            member_data = {
                "organization_id": org_id,
                "user_id": user_id,
                "role": role,
                "status": "active",
                "is_active": True
            }
            
            member = OrganizationMember(**member_data)
            db.add(member)
            await db.commit()
            await db.refresh(member)
            
            logger.info(f"メンバーを追加しました: 組織ID {org_id}, ユーザーID {user_id}, 役割 {role}")
            return member
            
        except Exception as e:
            await db.rollback()
            logger.error(f"メンバー追加に失敗: {e}")
            if isinstance(e, BridgeLineException):
                raise
            raise BridgeLineException(f"メンバーの追加に失敗しました: {str(e)}")

    async def remove_member(
        self, db: AsyncSession, org_id: int, user_id: int
    ) -> bool:
        """組織からメンバーを削除"""
        try:
            member = await self.get_member_by_user(db, org_id, user_id)
            if not member:
                raise BridgeLineException("指定されたユーザーはこの組織のメンバーではありません")
            
            # オーナーは削除できない
            if member.role == "owner":
                raise BridgeLineException("オーナーは削除できません")
            
            await db.delete(member)
            await db.commit()
            
            logger.info(f"メンバーを削除しました: 組織ID {org_id}, ユーザーID {user_id}")
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"メンバー削除に失敗: {e}")
            if isinstance(e, BridgeLineException):
                raise
            raise BridgeLineException(f"メンバーの削除に失敗しました: {str(e)}")

    async def update_member_role(
        self, db: AsyncSession, org_id: int, user_id: int, new_role: str
    ) -> Optional[OrganizationMember]:
        """メンバーの役割を更新"""
        try:
            member = await self.get_member_by_user(db, org_id, user_id)
            if not member:
                raise BridgeLineException("指定されたユーザーはこの組織のメンバーではありません")
            
            # オーナーの役割は変更できない
            if member.role == "owner":
                raise BridgeLineException("オーナーの役割は変更できません")
            
            member.role = new_role
            db.add(member)
            await db.commit()
            await db.refresh(member)
            
            logger.info(f"メンバーの役割を更新しました: 組織ID {org_id}, ユーザーID {user_id}, 新役割 {new_role}")
            return member
            
        except Exception as e:
            await db.rollback()
            logger.error(f"メンバー役割更新に失敗: {e}")
            if isinstance(e, BridgeLineException):
                raise
            raise BridgeLineException(f"メンバーの役割更新に失敗しました: {str(e)}")

    async def get_member_by_user(
        self, db: AsyncSession, org_id: int, user_id: int
    ) -> Optional[OrganizationMember]:
        """特定のユーザーの組織メンバー情報を取得"""
        try:
            result = await db.execute(
                select(OrganizationMember)
                .where(
                    and_(
                        OrganizationMember.organization_id == org_id,
                        OrganizationMember.user_id == user_id
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"メンバー取得に失敗: {e}")
            return None

    async def get_organization_members(
        self, db: AsyncSession, org_id: int
    ) -> List[OrganizationMember]:
        """組織のメンバー一覧を取得"""
        try:
            result = await db.execute(
                select(OrganizationMember)
                .where(OrganizationMember.organization_id == org_id)
                .order_by(OrganizationMember.joined_at)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"組織メンバー一覧取得に失敗: {e}")
            return []

    async def check_member_exists(
        self, db: AsyncSession, org_id: int, user_id: int
    ) -> bool:
        """組織メンバーの存在確認"""
        try:
            member = await self.get_member_by_user(db, org_id, user_id)
            return member is not None
        except Exception as e:
            logger.error(f"メンバー存在確認に失敗: {e}")
            return False

    async def get_member_role(
        self, db: AsyncSession, org_id: int, user_id: int
    ) -> Optional[str]:
        """組織メンバーの役割を取得"""
        try:
            member = await self.get_member_by_user(db, org_id, user_id)
            return member.role if member else None
        except Exception as e:
            logger.error(f"メンバー役割取得に失敗: {e}")
            return None

    # ==================== 権限チェック ====================

    async def is_owner(self, db: AsyncSession, org_id: int, user_id: int) -> bool:
        """ユーザーが組織のオーナーかチェック"""
        try:
            role = await self.get_member_role(db, org_id, user_id)
            return role == "owner"
        except Exception as e:
            logger.error(f"オーナーチェックに失敗: {e}")
            return False

    async def is_admin_or_owner(self, db: AsyncSession, org_id: int, user_id: int) -> bool:
        """ユーザーが組織の管理者またはオーナーかチェック"""
        try:
            role = await self.get_member_role(db, org_id, user_id)
            return role in ["admin", "owner"]
        except Exception as e:
            logger.error(f"管理者権限チェックに失敗: {e}")
            return False

    async def is_member(self, db: AsyncSession, org_id: int, user_id: int) -> bool:
        """ユーザーが組織のメンバーかチェック"""
        try:
            return await self.check_member_exists(db, org_id, user_id)
        except Exception as e:
            logger.error(f"メンバーチェックに失敗: {e}")
            return False

    # ==================== 統計・分析 ====================

    async def get_organization_stats(self, db: AsyncSession, org_id: int) -> Dict[str, Any]:
        """組織の統計情報を取得"""
        try:
            members = await self.get_organization_members(db, org_id)
            
            stats = {
                "total_members": len(members),
                "active_members": len([m for m in members if m.is_active]),
                "role_distribution": {},
                "created_at": None
            }
            
            # 役割別の分布を計算
            for member in members:
                role = member.role
                stats["role_distribution"][role] = stats["role_distribution"].get(role, 0) + 1
            
            # 組織の作成日を取得
            org = await self.get_organization(db, org_id)
            if org:
                stats["created_at"] = org.created_at.isoformat() if org.created_at else None
            
            return stats
            
        except Exception as e:
            logger.error(f"組織統計取得に失敗: {e}")
            return {}

    # ==================== 互換性メソッド（旧TeamService用） ====================

    async def create_team(self, db: AsyncSession, team_data: TeamCreate, creator_id: int) -> Organization:
        """チームを作成（互換性のため）"""
        return await self.create_organization(db, team_data, creator_id)

    async def get_team(self, db: AsyncSession, team_id: int) -> Optional[Organization]:
        """チームを取得（互換性のため）"""
        return await self.get_organization(db, team_id)

    async def get_teams(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[Organization]:
        """チーム一覧を取得（互換性のため）"""
        return await self.get_organizations(db, skip, limit)

    async def update_team(
        self, db: AsyncSession, team_id: int, team_data: TeamUpdate
    ) -> Optional[Organization]:
        """チームを更新（互換性のため）"""
        return await self.update_organization(db, team_id, team_data)

    async def delete_team(self, db: AsyncSession, team_id: int) -> bool:
        """チームを削除（互換性のため）"""
        return await self.delete_organization(db, team_id)

    async def get_user_teams(
        self, db: AsyncSession, user_id: int
    ) -> List[Organization]:
        """ユーザーが所属するチームを取得（互換性のため）"""
        return await self.get_user_organizations(db, user_id)


# シングルトンインスタンス
organization_service = OrganizationService()
