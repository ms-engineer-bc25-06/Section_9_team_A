"""
Firebase Custom Claims設定スクリプト
admin@example.com のFirebase UIDを使用して管理者権限を設定
"""

from app.core.firebase_client import set_admin_claim, get_user_claims


def set_firebase_admin():
    """Firebase Admin権限を設定"""
    
    print("🔥 Firebase Custom Claims 設定")
    
    # ここに実際のFirebase UIDを入力してください
    firebase_uid = input("Firebase Console で確認した admin@example.com の UID を入力してください: ").strip()
    
    if not firebase_uid:
        print("❌ Firebase UID が入力されていません")
        return False
    
    try:
        # 管理者権限を設定
        success = set_admin_claim(firebase_uid, True)
        
        if success:
            print(f"✅ Firebase Custom Claims設定成功！")
            
            # 確認
            claims = get_user_claims(firebase_uid)
            print(f"現在のClaims: {claims}")
            
            print(f"""
🎉 設定完了！

📋 テスト準備完了:
1. フロントエンドで admin@example.com でログイン
2. 管理者画面にアクセス可能になります

🔧 使用したUID: {firebase_uid}
            """)
            return True
        else:
            print("❌ Firebase Custom Claims設定に失敗しました")
            return False
            
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False


if __name__ == "__main__":
    set_firebase_admin()