from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
import structlog
import os

from app.config import settings

logger = structlog.get_logger()

# データベースURL
DATABASE_URL = settings.DATABASE_URL

# Alembic実行時は非同期エンジンを作成しない
if not os.environ.get("ALEMBIC_RUNNING"):
    # 非同期エンジン作成
    engine = create_async_engine(
        DATABASE_URL, echo=settings.DEBUG, poolclass=NullPool, future=True
    )

    # セッションファクトリー作成
    AsyncSessionLocal = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )


# ベースクラス
class Base(DeclarativeBase):
    pass


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


# データベース接続テスト
async def test_database_connection():
    """データベース接続をテスト"""
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
