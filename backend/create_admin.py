#!/usr/bin/env python3
"""
管理者ユーザーを直接データベースに作成するスクリプト
"""
import asyncio
import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.user import User

async def create_admin_user():
    """管理者ユーザーを作成"""
    try:
        # データベースセッションを取得
        async for db in get_db():
            # 管理者ユーザーの情報
            admin_email = "admin@example.com"
            admin_name = "管理者"
            admin_department = "管理部"
            
            # 既存ユーザーをチェック
            from sqlalchemy import select
            existing_user = await db.execute(
                select(User).where(User.email == admin_email)
            )
            if existing_user.scalar_one_or_none():
                print(f"ユーザー {admin_email} は既に存在します")
                return
            
            # 仮パスワードを生成
            import secrets
            import string
            
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
            
            # 開発環境用のダミーUIDを生成
            firebase_uid = f"dev_{uuid.uuid4().hex[:28]}"
            
            # 新しい管理者ユーザーを作成
            new_user = User(
                firebase_uid=firebase_uid,
                email=admin_email,
                username=admin_email.split('@')[0],
                full_name=admin_name,
                department=admin_department,
                is_admin=True,
                has_temporary_password=True,
                temporary_password_expires_at=datetime.utcnow() + timedelta(days=7),
                is_first_login=True,
                is_active=True,
                is_verified=False
            )
            
            # データベースに保存
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            
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
    asyncio.run(create_admin_user())
