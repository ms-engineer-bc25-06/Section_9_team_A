from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
import structlog

from app.config import settings

logger = structlog.get_logger()

# データベースURL
DATABASE_URL = settings.DATABASE_URL

# 非同期エンジン作成
engine = create_async_engine(
    DATABASE_URL, echo=settings.DEBUG, poolclass=NullPool, future=True
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
            await conn.execute("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
