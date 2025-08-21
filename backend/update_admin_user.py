#!/usr/bin/env python3
"""
管理者ユーザーの情報を更新するスクリプト
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.core.database import get_database_url

def update_admin_user():
    """管理者ユーザーを更新"""
    try:
        print("=" * 50)
        print("🔧 管理者ユーザー更新")
        print("=" * 50)
        
        # データベース接続（同期）
        database_url = get_database_url()
        # asyncpgをpsycopg2に変更
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # 管理者ユーザーを検索
        admin_user = db.query(User).filter(User.email == 'admin@example.com').first()
        
        if not admin_user:
            print('❌ 管理者ユーザーが見つかりません')
            return
        
        # 管理者ユーザーの情報を更新
        admin_user.full_name = "管理者1"
        admin_user.department = "管理部"
        admin_user.is_admin = True
        admin_user.is_active = True
        admin_user.is_verified = True
        
        db.commit()
        
        print('✅ 管理者ユーザーを更新しました！')
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
    update_admin_user()
