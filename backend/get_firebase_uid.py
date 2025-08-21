#!/usr/bin/env python3
"""
Firebase Authから実際のUIDを取得するスクリプト
"""
import requests
import json

def get_firebase_uid():
    """Firebase AuthからUIDを取得"""
    try:
        print("=" * 50)
        print("🔍 Firebase Auth UID取得")
        print("=" * 50)
        
        # Firebase Auth REST APIを使用してユーザー情報を取得
        # 注意: これは開発用の簡易的な方法です
        # 実際の運用ではFirebase Admin SDKを使用します
        
        # Firebase Auth REST APIのエンドポイント
        api_key = "AIzaSyCmF1yAgtZ2xQDfEq5_cDIXxm_cDljKEkQ"  # フロントエンドの設定から取得
        
        # ユーザー一覧を取得（管理者権限が必要）
        url = f"https://identitytoolkit.googleapis.com/v1/projects/bridge-line-ai/accounts:query"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "filter": "email = admin@example.com"
        }
        
        response = requests.post(f"{url}?key={api_key}", headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            if "userInfo" in result and len(result["userInfo"]) > 0:
                user_info = result["userInfo"][0]
                uid = user_info.get("localId")
                email = user_info.get("email")
                
                print(f"✅ Firebase Authユーザーが見つかりました！")
                print(f"🆔 UID: {uid}")
                print(f"📧 メール: {email}")
                
                return uid
            else:
                print("❌ Firebase Authユーザーが見つかりません")
                return None
        else:
            print(f"❌ API呼び出しに失敗: {response.status_code}")
            print(f"レスポンス: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        print(f"詳細: {traceback.format_exc()}")
        return None

if __name__ == "__main__":
    uid = get_firebase_uid()
    if uid:
        print("=" * 50)
        print(f"💡 このUIDをPostgreSQLのfirebase_uidに設定してください: {uid}")
        print("=" * 50)
