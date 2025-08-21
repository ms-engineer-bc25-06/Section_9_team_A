#!/usr/bin/env python3
"""
管理者ユーザーのFirebase UIDを修正するスクリプト
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.core.database import get_database_url

def fix_firebase_uid():
    """管理者ユーザーのFirebase UIDを修正"""
    try:
        print("=" * 50)
        print("🔧 Firebase UID修正")
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
        
        # 現在のUIDを表示
        print(f'現在のFirebase UID: {admin_user.firebase_uid}')
        
        # 正しいFirebase UIDに更新
        correct_uid = "g7lzX9SnUUeBpRAae9CjynV0CX43"
        admin_user.firebase_uid = correct_uid
        
        db.commit()
        
        print('✅ Firebase UIDを修正しました！')
        print(f'👤 ユーザー名: {admin_user.username}')
        print(f'👤 フルネーム: {admin_user.full_name}')
        print(f'📧 メール: {admin_user.email}')
        print(f'🏢 部署: {admin_user.department}')
        print(f'🔑 管理者: {"はい" if admin_user.is_admin else "いいえ"}')
        print(f'🆔 修正後のFirebase UID: {admin_user.firebase_uid}')
        
        print("=" * 50)
        print("🎉 Firebase UID修正完了！")
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
    fix_firebase_uid()
