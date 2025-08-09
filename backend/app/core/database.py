from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text
import structlog
import os

from app.config import settings

logger = structlog.get_logger()

# データベースURL
DATABASE_URL = settings.DATABASE_URL


# 環境に応じたデータベースURLの設定
def get_database_url():
    """環境に応じたデータベースURLを取得"""
    # 環境変数で明示的に指定されている場合
    if os.environ.get("DATABASE_URL"):
        return os.environ.get("DATABASE_URL")

    # テスト環境の場合
    if os.environ.get("TESTING"):
        return settings.TEST_DATABASE_URL or DATABASE_URL

    # デフォルト
    return DATABASE_URL


# Alembic実行時は非同期エンジンを作成しない
if not os.environ.get("ALEMBIC_RUNNING"):
    # 非同期エンジン作成
    engine = create_async_engine(
        get_database_url(),
        echo=settings.DEBUG,
        poolclass=NullPool,
        future=True,
        # 接続プールの設定
        pool_pre_ping=True,
        pool_recycle=3600,
    )

    # セッションファクトリー作成
    AsyncSessionLocal = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

# async_session エイリアス（startup.pyで使用）
async_session = AsyncSessionLocal


# ベースクラスは後で import（循環import回避）


# データベースセッション依存性
async def get_db() -> AsyncSession:
    """データベースセッションを取得"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


# データベースセッション依存性（新しい名前）
async def get_db_session() -> AsyncSession:
    """データベースセッションを取得（新しい関数名）"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


# データベース接続テスト
async def test_database_connection():
    """データベース接続をテスト"""
    try:
        async with engine.begin() as conn:
            # 基本的な接続テスト
            result = await conn.execute(text("SELECT 1"))
            row = result.fetchone()
            logger.info(f"Basic connection test: {row[0]}")

            # データベース情報の取得
            db_info = await conn.execute(
                text("SELECT current_database(), current_user, version()")
            )
            db_data = db_info.fetchone()
            logger.info(f"Connected to database: {db_data[0]}, User: {db_data[1]}")

        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        logger.error(f"Database URL: {get_database_url()}")
        return False
