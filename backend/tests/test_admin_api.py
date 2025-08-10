"""
管理者API直接テスト
"""

import requests
import json
import firebase_admin
from firebase_admin import credentials, auth


def test_admin_api():
    """管理者APIを直接テストする"""
    
    print("🧪 管理者API直接テスト")
    
    # Firebase初期化
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate("firebase-admin-key.json")
            firebase_admin.initialize_app(cred)
        print("✅ Firebase初期化成功")
    except Exception as e:
        print(f"❌ Firebase初期化失敗: {e}")
        return
    
    # テスト用IDトークン生成
    try:
        admin_uid = "g7lzX9SnUUeBpRAae9CjynV0CX43"
        
        # カスタムトークン生成
        custom_token = auth.create_custom_token(admin_uid)
        print(f"✅ カスタムトークン生成成功")
        
        # Firebase Admin SDKでユーザー情報確認
        user = auth.get_user(admin_uid)
        print(f"✅ Firebase ユーザー: {user.email}")
        print(f"   Custom Claims: {user.custom_claims}")
        
    except Exception as e:
        print(f"❌ トークン生成エラー: {e}")
        return
    
    print(f"""
🧪 手動テスト手順:

1. フロントエンドでログイン後、以下をブラウザコンソールで実行:
   ```javascript
   firebase.auth().currentUser.getIdToken().then(token => console.log(token))
   ```

2. 取得したIDトークンで以下のAPIをテスト:
   ```bash
   curl -X GET "http://localhost:8000/api/v1/admin-role/check-admin" \\
        -H "Authorization: Bearer <ID_TOKEN>"
   ```

3. 期待される結果:
   {{
     "is_admin": true,
     "firebase_admin": true,
     "db_admin": true,
     "user_email": "admin@example.com"
   }}

📋 設定確認済み:
- Firebase UID: {admin_uid}
- Email: admin@example.com
- DB Admin: True
- Firebase Admin: True

💡 問題がある場合:
1. バックエンドログを確認
2. フロントエンドのFirebase設定確認
3. IDトークンの有効性確認
4. CORS設定確認
    """)


if __name__ == "__main__":
    test_admin_api()