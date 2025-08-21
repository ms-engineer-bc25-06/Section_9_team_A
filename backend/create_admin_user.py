#!/usr/bin/env python3
"""
管理者ユーザーをPostgreSQLに登録するスクリプト
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.core.database import get_database_url

def create_admin_user():
    """管理者ユーザーを作成"""
    try:
        print("=" * 50)
        print("🔧 管理者ユーザー作成")
        print("=" * 50)
        
        # データベース接続（同期）
        database_url = get_database_url()
        # asyncpgをpsycopg2に変更
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # 既存の管理者ユーザーをチェック
        existing_admin = db.query(User).filter(User.email == 'admin@example.com').first()
        
        if existing_admin:
            print('✅ 管理者ユーザーは既に存在します')
            print(f'👤 ユーザー名: {existing_admin.username}')
            print(f'👤 フルネーム: {existing_admin.full_name}')
            print(f'📧 メール: {existing_admin.email}')
            print(f'🏢 部署: {existing_admin.department}')
            print(f'🔑 管理者: {"はい" if existing_admin.is_admin else "いいえ"}')
            print(f'🆔 Firebase UID: {existing_admin.firebase_uid}')
            return
        
        # 新しい管理者ユーザーを作成
        admin_user = User(
            email='admin@example.com',
            username='admin',
            full_name='管理者1',
            department='管理部',
            is_admin=True,
            firebase_uid='admin_uid',  # Firebase AuthのUID
            has_temporary_password=False,
            is_first_login=False,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        
        print('✅ 管理者ユーザーを作成しました！')
        print(f'👤 ユーザー名: {admin_user.username}')
        print(f'👤 フルネーム: {admin_user.full_name}')
        print(f'📧 メール: {admin_user.email}')
        print(f'🏢 部署: {admin_user.department}')
        print(f'🔑 管理者: {"はい" if admin_user.is_admin else "いいえ"}')
        print(f'🆔 Firebase UID: {admin_user.firebase_uid}')
        
        print("=" * 50)
        print("🎉 管理者ログインが可能になりました！")
        print("🌐 ログインURL: http://localhost:3000/auth/login")
        print("📧 メール: admin@example.com")
        print("🔑 パスワード: password2346")
        print("=" * 50)
        
    except Exception as e:
        print(f'❌ エラーが発生しました: {e}')
        import traceback
        print(f'詳細: {traceback.format_exc()}')
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
