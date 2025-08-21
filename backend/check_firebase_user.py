#!/usr/bin/env python3
"""
Firebase Authに存在するユーザーの情報を確認するスクリプト
"""
import asyncio
from app.core.firebase_admin import initialize_firebase_admin, get_firebase_user_by_email

async def check_firebase_user():
    """Firebase Authユーザーを確認"""
    try:
        print("=" * 50)
        print("🔍 Firebase Authユーザー確認")
        print("=" * 50)
        
        # Firebase Admin SDKを初期化
        if not initialize_firebase_admin():
            print("❌ Firebase Admin SDK初期化に失敗しました")
            return
        
        # 管理者ユーザーを確認
        email = "admin@example.com"
        firebase_user = get_firebase_user_by_email(email)
        
        if firebase_user:
            print("✅ Firebase Authユーザーが見つかりました！")
            print(f"🆔 UID: {firebase_user['uid']}")
            print(f"📧 メールアドレス: {firebase_user['email']}")
            print(f"👤 表示名: {firebase_user['display_name']}")
            print(f"✅ メール認証済み: {'はい' if firebase_user['email_verified'] else 'いいえ'}")
            print(f"🚫 無効化: {'はい' if firebase_user['disabled'] else 'いいえ'}")
            print("=" * 50)
            print("\n💡 このユーザーでログインを試してください")
            print("🌐 ログインURL: http://localhost:3000/auth/login")
            print("=" * 50)
        else:
            print("❌ Firebase Authユーザーが見つかりません")
            print("=" * 50)
            print("\n💡 開発環境用エンドポイントでユーザーを作成してください")
            print("🌐 URL: http://localhost:3000/dev/create-admin")
            print("=" * 50)

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        print(f"詳細: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(check_firebase_user())

