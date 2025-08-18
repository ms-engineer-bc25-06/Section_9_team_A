"""
アプリケーション起動時の初期化処理
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.core.database import async_session
from app.models.user import User
from app.models.role import Role, UserRole
from app.core.config import settings
from app.integrations.firebase_client import get_firebase_client
import structlog

logger = structlog.get_logger()


async def startup_events():
    """
    アプリケーション起動時のイベント処理
    """
    logger.info("Starting application initialization...")
    
    try:
        await create_default_roles()
        await setup_initial_admin()
        logger.info("Application initialization completed successfully")
    except Exception as e:
        logger.error(f"Application initialization failed: {e}")
        # 起動は継続する（データベース関連のエラーでアプリケーション全体を停止させない）


async def create_default_roles():
    """
    デフォルトのロールを作成
    """
    async with async_session() as db:
        try:
            # adminロールの存在確認
            admin_role = await db.execute(
                select(Role).where(Role.name == "admin")
            )
            admin_role = admin_role.scalar_one_or_none()
            
            if not admin_role:
                admin_role = Role(
                    name="admin",
                    display_name="管理者",
                    description="システム管理者"
                )
                db.add(admin_role)
                logger.info("Created admin role")
            
            # userロールの存在確認
            user_role = await db.execute(
                select(Role).where(Role.name == "user")
            )
            user_role = user_role.scalar_one_or_none()
            
            if not user_role:
                user_role = Role(
                    name="user",
                    display_name="一般ユーザー",
                    description="一般ユーザー"
                )
                db.add(user_role)
                logger.info("Created user role")
            
            await db.commit()
            logger.info("Default roles created successfully")
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create default roles: {e}")


async def setup_initial_admin():
    """
    初期管理者の設定
    """
    # 環境変数から初期管理者情報を取得
    admin_uid = settings.INITIAL_ADMIN_FIREBASE_UID
    admin_email = settings.INITIAL_ADMIN_EMAIL
    admin_display_name = settings.INITIAL_ADMIN_DISPLAY_NAME
    
    if not admin_uid or not admin_email:
        logger.info("Initial admin configuration not found, skipping admin setup")
        return
    
    async with async_session() as db:
        try:
            # 既存の管理者ユーザーを確認
            existing_admin = await db.execute(
                select(User).where(User.firebase_uid == admin_uid)
            )
            existing_admin = existing_admin.scalar_one_or_none()
            
            if existing_admin:
                # 既存管理者の情報を更新
                existing_admin.email = admin_email
                existing_admin.username = admin_email
                if admin_display_name:
                    existing_admin.full_name = admin_display_name
                existing_admin.is_admin = True
                existing_admin.is_active = True
                existing_admin.is_verified = True
                
                logger.info(f"Updated existing admin user: {admin_email}")
            else:
                # 新しい管理者ユーザーを作成
                admin_user = User(
                    firebase_uid=admin_uid,
                    email=admin_email,
                    username=admin_email,
                    full_name=admin_display_name or "Administrator",
                    is_admin=True,
                    is_active=True,
                    is_verified=True
                )
                db.add(admin_user)
                await db.flush()  # IDを取得するため
                existing_admin = admin_user
                logger.info(f"Created new admin user: {admin_email}")
            
            # adminロールを取得
            admin_role = await db.execute(
                select(Role).where(Role.name == "admin")
            )
            admin_role = admin_role.scalar_one_or_none()
            
            if admin_role:
                # ユーザーロールの存在確認
                existing_user_role = await db.execute(
                    select(UserRole).where(
                        UserRole.user_id == existing_admin.id,
                        UserRole.role_id == admin_role.id
                    )
                )
                existing_user_role = existing_user_role.scalar_one_or_none()
                
                if not existing_user_role:
                    user_role = UserRole(
                        user_id=existing_admin.id,
                        role_id=admin_role.id,
                        is_active=True
                    )
                    db.add(user_role)
                    logger.info("Assigned admin role to user")
            
            await db.commit()
            
            # Firebase Custom Claims を設定
            try:
                firebase_client = get_firebase_client()
                # Firebase Custom Claims の設定は後で実装
                logger.info(f"Admin user setup completed for: {admin_uid}")
            except Exception as firebase_error:
                logger.warning(f"Failed to set Firebase custom claims: {firebase_error}")
            
            logger.info("Initial admin setup completed successfully")
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to setup initial admin: {e}")


if __name__ == "__main__":
    # スクリプトとして実行された場合
    asyncio.run(startup_events())



