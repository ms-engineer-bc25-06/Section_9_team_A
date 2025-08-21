#!/usr/bin/env python3
"""
既存の管理者ユーザーの情報を確認するスクリプト
"""
import asyncio
from sqlalchemy import text
from app.core.database import get_db

async def check_admin_user():
    """既存の管理者ユーザーを確認"""
    try:
        async for db in get_db():
            # 管理者ユーザーを取得
            result = await db.execute(
                text("""
                    SELECT id, email, full_name, department, is_admin, 
                           has_temporary_password, is_first_login, is_active,
                           firebase_uid, created_at
                    FROM users 
                    WHERE email = :email
                """),
                {"email": "admin@example.com"}
            )
            
            user = result.fetchone()
            if user:
                print("✅ 管理者ユーザーが見つかりました！")
                print(f"🆔 ID: {user[0]}")
                print(f"📧 メールアドレス: {user[1]}")
                print(f"👤 氏名: {user[2]}")
                print(f"🏢 部署: {user[3]}")
                print(f"👑 管理者権限: {'はい' if user[4] else 'いいえ'}")
                print(f"🔑 仮パスワード使用中: {'はい' if user[5] else 'いいえ'}")
                print(f"🆕 初回ログイン: {'はい' if user[6] else 'いいえ'}")
                print(f"✅ アクティブ: {'はい' if user[7] else 'いいえ'}")
                print(f"🆔 Firebase UID: {user[8]}")
                print(f"📅 作成日: {user[9]}")
                print("\n💡 このユーザーでログインできます")
                print("🌐 ログインURL: http://localhost:3000/auth/login")
            else:
                print("❌ 管理者ユーザーが見つかりません")
            
            break
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        print(f"詳細: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(check_admin_user())
