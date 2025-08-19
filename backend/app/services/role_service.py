from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional, Dict, Any
import json
import structlog
from datetime import datetime

from app.models.role import Role, UserRole
from app.models.user import User
from app.integrations.firebase_client import set_admin_claim, get_user_claims

logger = structlog.get_logger()


class RoleService:
    """ロール管理サービス"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_roles(self, user_id: int) -> List[Dict[str, Any]]:
        """ユーザーのロール一覧を取得"""
        try:
            result = await self.db.execute(
                select(UserRole, Role).join(Role).where(
                    and_(
                        UserRole.user_id == user_id,
                        UserRole.is_active == True,
                        Role.is_active == True
                    )
                )
            )
            user_roles = result.all()
            
            roles = []
            for user_role, role in user_roles:
                # 有効期限チェック
                if user_role.expires_at and user_role.expires_at < datetime.utcnow():
                    continue
                
                roles.append({
                    "id": role.id,
                    "name": role.name,
                    "display_name": role.display_name,
                    "description": role.description,
                    "permissions": json.loads(role.permissions) if role.permissions else {},
                    "assigned_at": user_role.assigned_at,
                    "expires_at": user_role.expires_at
                })
            
            return roles
        except Exception as e:
            logger.error(f"Failed to get user roles: {e}")
            return []

    async def assign_role_to_user(
        self, 
        user_id: int, 
        role_name: str, 
        assigned_by: int,
        expires_at: Optional[datetime] = None
    ) -> bool:
        """ユーザーにロールを割り当て"""
        try:
            # ロールを取得
            role_result = await self.db.execute(
                select(Role).where(Role.name == role_name)
            )
            role = role_result.scalar_one_or_none()
            
            if not role:
                logger.error(f"Role not found: {role_name}")
                return False
            
            # 既存の割り当てを無効化
            await self.db.execute(
                select(UserRole).where(
                    and_(
                        UserRole.user_id == user_id,
                        UserRole.role_id == role.id,
                        UserRole.is_active == True
                    )
                )
            )
            
            # 新しい割り当てを作成
            user_role = UserRole(
                user_id=user_id,
                role_id=role.id,
                assigned_by=assigned_by,
                expires_at=expires_at
            )
            
            self.db.add(user_role)
            await self.db.commit()
            
            logger.info(f"Role {role_name} assigned to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to assign role: {e}")
            await self.db.rollback()
            return False

    async def remove_role_from_user(self, user_id: int, role_name: str) -> bool:
        """ユーザーからロールを削除"""
        try:
            # ロールを取得
            role_result = await self.db.execute(
                select(Role).where(Role.name == role_name)
            )
            role = role_result.scalar_one_or_none()
            
            if not role:
                logger.error(f"Role not found: {role_name}")
                return False
            
            # 既存の割り当てを無効化
            result = await self.db.execute(
                select(UserRole).where(
                    and_(
                        UserRole.user_id == user_id,
                        UserRole.role_id == role.id,
                        UserRole.is_active == True
                    )
                )
            )
            user_role = result.scalar_one_or_none()
            
            if user_role:
                user_role.is_active = False
                await self.db.commit()
                logger.info(f"Role {role_name} removed from user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove role: {e}")
            await self.db.rollback()
            return False

    async def sync_user_roles_to_firebase(self, user: User) -> bool:
        """ユーザーのロールをFirebase Custom Claimsに同期"""
        try:
            user_roles = await self.get_user_roles(user.id)
            
            # 管理者権限を確認
            is_admin = any(role["name"] == "admin" for role in user_roles)
            
            # 権限情報を構築
            permissions = {}
            for role in user_roles:
                permissions.update(role.get("permissions", {}))
            
            # Firebase Custom Claimsを設定
            custom_claims = {
                "admin": is_admin,
                "roles": [role["name"] for role in user_roles],
                "permissions": permissions
            }
            
            # Firebaseに設定
            success = set_admin_claim(user.firebase_uid, is_admin)
            if success:
                logger.info(f"Firebase claims synced for user {user.email}")
                return True
            else:
                logger.error(f"Failed to sync Firebase claims for user {user.email}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to sync user roles to Firebase: {e}")
            return False

    async def create_default_roles(self) -> bool:
        """デフォルトロールを作成"""
        try:
            default_roles = [
                {
                    "name": "user",
                    "display_name": "ユーザー",
                    "description": "一般ユーザー",
                    "permissions": json.dumps({"read": True})
                },
                {
                    "name": "admin",
                    "display_name": "管理者",
                    "description": "システム管理者",
                    "permissions": json.dumps({
                        "read": True,
                        "write": True,
                        "admin": True,
                        "user_management": True
                    })
                },
                {
                    "name": "moderator",
                    "display_name": "モデレーター",
                    "description": "コンテンツモデレーター",
                    "permissions": json.dumps({
                        "read": True,
                        "write": True,
                        "moderate": True
                    })
                }
            ]
            
            for role_data in default_roles:
                # 既存のロールをチェック
                result = await self.db.execute(
                    select(Role).where(Role.name == role_data["name"])
                )
                existing_role = result.scalar_one_or_none()
                
                if not existing_role:
                    role = Role(**role_data)
                    self.db.add(role)
            
            await self.db.commit()
            logger.info("Default roles created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create default roles: {e}")
            await self.db.rollback()
            return False