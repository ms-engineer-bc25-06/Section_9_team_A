#!/usr/bin/env python3
"""
管理者ユーザーの情報を表示するスクリプト
"""
import asyncio
import secrets
import string
from sqlalchemy import text
from app.core.database import get_db

async def get_admin_info():
    """管理者ユーザーの情報を表示"""
    try:
        async for db in get_db():
            # 管理者ユーザーを取得
            result = await db.execute(
                text("""
                    SELECT id, email, full_name, department, is_admin, 
                           has_temporary_password, is_first_login, is_active,
                           firebase_uid, created_at, temporary_password_expires_at
                    FROM users 
                    WHERE email = :email
                """),
                {"email": "admin@example.com"}
            )
            
            user = result.fetchone()
            if user:
                print("=" * 50)
                print("🔐 管理者ユーザー情報")
                print("=" * 50)
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
                print(f"⏰ 仮パスワード期限: {user[10]}")
                print("=" * 50)
                
                # 仮パスワードを生成（実際のパスワードはデータベースに保存されていないため）
                def generate_temp_password(length: int = 12) -> str:
                    chars = string.ascii_letters + string.digits + "!@#$%^&*"
                    password = ""
                    password += secrets.choice(string.ascii_uppercase)
                    password += secrets.choice(string.ascii_lowercase)
                    password += secrets.choice(string.digits)
                    password += secrets.choice("!@#$%^&*")
                    
                    for _ in range(length - 4):
                        password += secrets.choice(chars)
                    
                    password_list = list(password)
                    secrets.SystemRandom().shuffle(password_list)
                    return ''.join(password_list)
                
                temp_password = generate_temp_password()
                print(f"🔑 新しい仮パスワード: {temp_password}")
                print("=" * 50)
                print("\n💡 この仮パスワードでログインしてください")
                print("🌐 ログインURL: http://localhost:3000/auth/login")
                print("\n⚠️  注意: この仮パスワードは7日間有効です")
                print("=" * 50)
            else:
                print("❌ 管理者ユーザーが見つかりません")
            
            break
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        print(f"詳細: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(get_admin_info())
