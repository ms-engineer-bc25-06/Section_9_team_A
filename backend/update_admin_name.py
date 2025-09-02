"""
admin@example.comの名前を「管理者」に変更するスクリプト
"""

import asyncio
import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import async_session
from sqlalchemy import text


async def update_admin_name():
    """admin@example.comの名前を「管理者」に変更"""
    print("🔧 admin@example.comの名前を「管理者」に変更中...")
    
    try:
        async with async_session() as db:
            # 現在の情報を確認
            result = await db.execute(text("""
                SELECT id, email, full_name, username
                FROM users 
                WHERE email = 'admin@example.com'
            """))
            user = result.fetchone()
            
            if not user:
                print("❌ admin@example.comのユーザーが見つかりません")
                return
            
            print(f"📋 現在の情報:")
            print(f"  ID: {user[0]}")
            print(f"  Email: {user[1]}")
            print(f"  Full Name: {user[2] or '未設定'}")
            print(f"  Username: {user[3]}")
            
            # 名前を「管理者」に更新
            await db.execute(text("""
                UPDATE users 
                SET full_name = '管理者'
                WHERE email = 'admin@example.com'
            """))
            
            await db.commit()
            
            # 更新後の情報を確認
            result2 = await db.execute(text("""
                SELECT id, email, full_name, username
                FROM users 
                WHERE email = 'admin@example.com'
            """))
            updated_user = result2.fetchone()
            
            print(f"\n✅ 更新完了:")
            print(f"  ID: {updated_user[0]}")
            print(f"  Email: {updated_user[1]}")
            print(f"  Full Name: {updated_user[2]}")
            print(f"  Username: {updated_user[3]}")
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """メイン実行"""
    print("🚀 管理者名変更ツール")
    print("=" * 50)
    
    await update_admin_name()
    
    print("✅ 処理完了")


if __name__ == "__main__":
    asyncio.run(main())
