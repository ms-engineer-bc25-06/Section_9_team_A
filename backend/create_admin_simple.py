#!/usr/bin/env python3
"""
SQLを直接実行して管理者ユーザーを作成するシンプルなスクリプト
"""
import asyncio
import uuid
import secrets
import string
from datetime import datetime, timedelta
from sqlalchemy import text
from app.core.database import get_db

async def create_admin_user_simple():
    """SQLを直接実行して管理者ユーザーを作成"""
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
        firebase_uid = f"dev_{uuid.uuid4().hex[:28]}"
        admin_email = "admin@example.com"
        admin_name = "管理者"
        admin_department = "管理部"
        
        # データベースセッションを取得
        async for db in get_db():
            # 既存ユーザーをチェック
            result = await db.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": admin_email}
            )
            if result.fetchone():
                print(f"ユーザー {admin_email} は既に存在します")
                return
            
            # 新しい管理者ユーザーを作成
            await db.execute(
                text("""
                    INSERT INTO users (
                        firebase_uid, email, username, full_name, department,
                        is_admin, has_temporary_password, temporary_password_expires_at,
                        is_first_login, is_active, is_verified, created_at, updated_at
                    ) VALUES (
                        :firebase_uid, :email, :username, :full_name, :department,
                        :is_admin, :has_temporary_password, :temporary_password_expires_at,
                        :is_first_login, :is_active, :is_verified, :created_at, :updated_at
                    )
                """),
                {
                    "firebase_uid": firebase_uid,
                    "email": admin_email,
                    "username": admin_email.split('@')[0],
                    "full_name": admin_name,
                    "department": admin_department,
                    "is_admin": True,
                    "has_temporary_password": True,
                    "temporary_password_expires_at": datetime.utcnow() + timedelta(days=7),
                    "is_first_login": True,
                    "is_active": True,
                    "is_verified": False,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            )
            
            await db.commit()
            
            print("✅ 管理者ユーザーが作成されました！")
            print(f"📧 メールアドレス: {admin_email}")
            print(f"👤 氏名: {admin_name}")
            print(f"🏢 部署: {admin_department}")
            print(f"🔑 仮パスワード: {temp_password}")
            print(f"🆔 Firebase UID: {firebase_uid}")
            print("\n💡 この仮パスワードでログインしてください")
            print("🌐 ログインURL: http://localhost:3000/auth/login")
            
            break
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        print(f"詳細: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(create_admin_user_simple())
