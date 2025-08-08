from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import structlog
from datetime import datetime

from app.models.user import User
from app.models.role import Role, UserRole
from app.services.role_service import RoleService
from app.core.firebase_client import set_admin_claim
from app.config import settings

logger = structlog.get_logger()


class InitialSetupService:
    """初期設定サービス"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_if_admin_exists(self) -> bool:
        """管理者が存在するかチェック"""
        try:
            role_service = RoleService(self.db)
            
            # 管理者ロールを持つユーザーを確認
            result = await self.db.execute(
                select(UserRole, Role).join(Role).where(
                    Role.name == "admin"
                )
            )
            admin_users = result.all()
            
            return len(admin_users) > 0
            
        except Exception as e:
            logger.error(f"Failed to check admin existence: {e}")
            return False

    async def setup_initial_admin_from_env(self) -> bool:
        """環境変数から初期管理者を設定"""
        try:
            # 環境変数をチェック
            if not settings.INITIAL_ADMIN_EMAIL or not settings.INITIAL_ADMIN_FIREBASE_UID:
                logger.warning("Initial admin environment variables not set")
                return False
            
            # 既に管理者が存在するかチェック
            if await self.check_if_admin_exists():
                logger.info("Admin already exists, skipping initial setup")
                return True
            
            # デフォルトロールを作成
            role_service = RoleService(self.db)
            await role_service.create_default_roles()
            
            # ユーザーを作成または取得
            result = await self.db.execute(
                select(User).where(User.firebase_uid == settings.INITIAL_ADMIN_FIREBASE_UID)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                # 新規ユーザー作成
                user = User(
                    firebase_uid=settings.INITIAL_ADMIN_FIREBASE_UID,
                    email=settings.INITIAL_ADMIN_EMAIL,
                    display_name=settings.INITIAL_ADMIN_DISPLAY_NAME or "Initial Admin",
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                self.db.add(user)
                await self.db.commit()
                await self.db.refresh(user)
                logger.info(f"Created initial admin user: {settings.INITIAL_ADMIN_EMAIL}")
            else:
                logger.info(f"Using existing user as initial admin: {settings.INITIAL_ADMIN_EMAIL}")
            
            # 管理者ロールを割り当て
            success = await role_service.assign_role_to_user(
                user_id=user.id,
                role_name="admin",
                assigned_by=user.id,  # 自己割り当て
                expires_at=None  # 永続
            )
            
            if success:
                # Firebase Custom Claimsを設定
                firebase_success = set_admin_claim(settings.INITIAL_ADMIN_FIREBASE_UID, True)
                if firebase_success:
                    logger.info("Initial admin setup completed successfully")
                    return True
                else:
                    logger.warning("Firebase Custom Claims setup failed")
                    return False
            else:
                logger.error("Failed to assign admin role")
                return False
                
        except Exception as e:
            logger.error(f"Initial admin setup failed: {e}")
            return False

    async def setup_initial_admin_manual(
        self, 
        email: str, 
        firebase_uid: str, 
        display_name: str
    ) -> bool:
        """手動で初期管理者を設定"""
        try:
            # 既に管理者が存在するかチェック
            if await self.check_if_admin_exists():
                logger.warning("Admin already exists")
                return False
            
            # デフォルトロールを作成
            role_service = RoleService(self.db)
            await role_service.create_default_roles()
            
            # ユーザーを作成または取得
            result = await self.db.execute(
                select(User).where(User.firebase_uid == firebase_uid)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                # 新規ユーザー作成
                user = User(
                    firebase_uid=firebase_uid,
                    email=email,
                    display_name=display_name,
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                self.db.add(user)
                await self.db.commit()
                await self.db.refresh(user)
                logger.info(f"Created initial admin user: {email}")
            else:
                logger.info(f"Using existing user as initial admin: {email}")
            
            # 管理者ロールを割り当て
            success = await role_service.assign_role_to_user(
                user_id=user.id,
                role_name="admin",
                assigned_by=user.id,  # 自己割り当て
                expires_at=None  # 永続
            )
            
            if success:
                # Firebase Custom Claimsを設定
                firebase_success = set_admin_claim(firebase_uid, True)
                if firebase_success:
                    logger.info("Initial admin setup completed successfully")
                    return True
                else:
                    logger.warning("Firebase Custom Claims setup failed")
                    return False
            else:
                logger.error("Failed to assign admin role")
                return False
                
        except Exception as e:
            logger.error(f"Initial admin setup failed: {e}")
            return False
