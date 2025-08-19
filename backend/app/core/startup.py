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
        await setup_initial_admin()
        logger.info("Application initialization completed successfully")
    except Exception as e:
        logger.error(f"Application initialization failed: {e}")
        # 起動は継続する（データベース関連のエラーでアプリケーション全体を停止させない）


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
                existing_admin.full_name = admin_display_name
                existing_admin.is_admin = True
                existing_admin.is_active = True
                existing_admin.is_verified = True
                
                await db.commit()
                logger.info(f"Updated existing admin user: {admin_email}")
            else:
                # 新しい管理者ユーザーを作成
                admin_user = User(
                    firebase_uid=admin_uid,
                    email=admin_email,
                    username=admin_email,
                    full_name=admin_display_name,
                    is_admin=True,
                    is_active=True,
                    is_verified=True
                )
                
                db.add(admin_user)
                await db.commit()
                logger.info(f"Created new admin user: {admin_email}")
                
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to setup initial admin: {e}")


async def health_check():
    """
    ヘルスチェック用のデータベース接続テスト
    """
    try:
        async with async_session() as db:
            # データベース接続テスト
            result = await db.execute(text("SELECT 1"))
            result.scalar()
            logger.info("Database connection test successful")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


async def cleanup_resources():
    """
    アプリケーション終了時のリソースクリーンアップ
    """
    logger.info("Cleaning up application resources...")
    
    try:
        # データベース接続のクリーンアップ
        await async_session.close()
        logger.info("Database connections closed successfully")
        
    except Exception as e:
        logger.error(f"Resource cleanup failed: {e}")


# 起動時のイベントハンドラー
async def on_startup():
    """アプリケーション起動時の処理"""
    await startup_events()


# 終了時のイベントハンドラー
async def on_shutdown():
    """アプリケーション終了時の処理"""
    await cleanup_resources()


if __name__ == "__main__":
    # スクリプトとして実行された場合
    asyncio.run(startup_events())



