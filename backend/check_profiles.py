"""
プロフィール情報を確認するスクリプト
"""

import asyncio
import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import async_session
from sqlalchemy import text


async def check_profiles():
    """プロフィール情報を確認"""
    print("🔍 プロフィール情報を確認中...")
    
    try:
        async with async_session() as db:
            # 全ユーザーのプロフィール情報を取得
            result = await db.execute(text("""
                SELECT id, email, full_name, department, is_active
                FROM users 
                WHERE is_active = true
                ORDER BY id
            """))
            users = result.fetchall()
            
            print(f"📋 アクティブユーザー数: {len(users)}")
            print("\n👥 プロフィール情報:")
            for user in users:
                print(f"  ID: {user[0]}")
                print(f"    Email: {user[1]}")
                print(f"    Full Name: {user[2] or '未設定'}")
                print(f"    Department: {user[3] or '未設定'}")
                print(f"    Active: {user[4]}")
                print()
            
            # プロフィール登録済みユーザーを確認
            result2 = await db.execute(text("""
                SELECT id, email, full_name, department
                FROM users 
                WHERE is_active = true 
                AND full_name IS NOT NULL 
                AND full_name != ''
                AND department IS NOT NULL 
                AND department != ''
                ORDER BY id
            """))
            profile_users = result2.fetchall()
            
            print(f"📋 プロフィール登録済みユーザー数: {len(profile_users)}")
            print("\n✅ プロフィール登録済みユーザー:")
            for user in profile_users:
                print(f"  ID: {user[0]} - {user[1]} - {user[2]} ({user[3]})")
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """メイン実行"""
    print("🚀 プロフィール確認ツール")
    print("=" * 50)
    
    await check_profiles()
    
    print("✅ 確認完了")


if __name__ == "__main__":
    asyncio.run(main())
