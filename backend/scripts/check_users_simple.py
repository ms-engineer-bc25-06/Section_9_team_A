"""
既存のユーザーを確認するスクリプト
"""

import asyncio
import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import async_session
from sqlalchemy import text


async def check_users():
    """既存のユーザーを確認"""
    print("🔍 既存のユーザーを確認中...")
    
    try:
        async with async_session() as db:
            # 全ユーザーを取得
            result = await db.execute(text("""
                SELECT id, email, firebase_uid, is_active, is_verified
                FROM users 
                ORDER BY id
            """))
            users = result.fetchall()
            
            print(f"📋 ユーザー数: {len(users)}")
            print("\n👥 ユーザー一覧:")
            for user in users:
                print(f"  ID: {user[0]}")
                print(f"    Email: {user[1]}")
                print(f"    Firebase UID: {user[2] or '未設定'}")
                print(f"    Active: {user[3] or False}")
                print(f"    Verified: {user[4] or False}")
                print()
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """メイン実行"""
    print("🚀 ユーザー確認ツール")
    print("=" * 50)
    
    await check_users()
    
    print("✅ 確認完了")


if __name__ == "__main__":
    asyncio.run(main())

