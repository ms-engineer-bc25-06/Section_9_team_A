import asyncio
from app.core.database import get_db
from app.models.user import User
from sqlalchemy import select

async def test_db_connection():
    """データベース接続をテスト"""
    try:
        async for db in get_db():
            result = await db.execute(select(User))
            print("✅ データベース接続成功")
            break
    except Exception as e:
        print(f"❌ データベース接続エラー: {e}")

if __name__ == "__main__":
    asyncio.run(test_db_connection())
