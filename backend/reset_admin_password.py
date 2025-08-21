#!/usr/bin/env python3
"""
管理者ユーザーの仮パスワードをリセットするスクリプト
"""
import asyncio
import secrets
import string
from datetime import datetime, timedelta
from sqlalchemy import text
from app.core.database import get_db

async def reset_admin_password():
    """管理者ユーザーの仮パスワードをリセット"""
    try:
        # 仮パスワードを生成
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
        admin_email = "admin@example.com"
        
        async for db in get_db():
            # 管理者ユーザーのパスワードをリセット
            result = await db.execute(
                text("""
                    UPDATE users 
                    SET has_temporary_password = true,
                        is_first_login = true,
                        temporary_password_expires_at = :expires_at,
                        updated_at = :updated_at
                    WHERE email = :email
                    RETURNING id, full_name, department
                """),
                {
                    "email": admin_email,
                    "expires_at": datetime.utcnow() + timedelta(days=7),
                    "updated_at": datetime.utcnow()
                }
            )
            
            updated_user = result.fetchone()
            if updated_user:
                await db.commit()
                print("✅ 管理者ユーザーのパスワードがリセットされました！")
                print(f"🆔 ID: {updated_user[0]}")
                print(f"👤 氏名: {updated_user[1]}")
                print(f"🏢 部署: {updated_user[2]}")
                print(f"📧 メールアドレス: {admin_email}")
                print(f"🔑 新しい仮パスワード: {temp_password}")
                print("\n💡 この仮パスワードでログインしてください")
                print("🌐 ログインURL: http://localhost:3000/auth/login")
                print("\n⚠️  注意: この仮パスワードは7日間有効です")
            else:
                print("❌ 管理者ユーザーが見つかりません")
            
            break
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        print(f"詳細: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(reset_admin_password())
