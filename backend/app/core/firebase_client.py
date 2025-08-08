import os
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from fastapi import HTTPException, status

# firebase-admin-key.json への正しいパス設定
# backendディレクトリから実行されることを前提とする
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
cred_path = os.path.join(backend_dir, "firebase-admin-key.json")

# Firebaseアプリがまだ初期化されていない場合のみ初期化
if not firebase_admin._apps:
    try:
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print(f"✅ Firebase initialized successfully with: {cred_path}")
        else:
            print(f"❌ Firebase credentials file not found at: {cred_path}")
            print(f"📁 Current working directory: {os.getcwd()}")
            print(f"📁 Backend directory: {backend_dir}")
    except Exception as e:
        print(f"❌ Firebase initialization failed: {e}")
        print(f"📁 Looking for file at: {cred_path}")

def verify_firebase_token(token: str):
    """Firebase IDトークンを検証してデコードする"""
    try:
        decoded_token = firebase_auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired Firebase token: {str(e)}",
        )

def set_admin_claim(uid: str, is_admin: bool = True):
    """Firebase Custom Claimsで管理者権限を設定"""
    try:
        custom_claims = {"admin": is_admin}
        firebase_auth.set_custom_user_claims(uid, custom_claims)
        print(f"✅ Admin claim set for user: {uid}")
        return True
    except Exception as e:
        print(f"❌ Failed to set admin claim: {e}")
        return False

def get_user_claims(uid: str):
    """ユーザーのCustom Claimsを取得"""
    try:
        user = firebase_auth.get_user(uid)
        return user.custom_claims or {}
    except Exception as e:
        print(f"❌ Failed to get user claims: {e}")
        return {}

def is_admin_user(uid: str) -> bool:
    """ユーザーが管理者かどうかを確認"""
    try:
        claims = get_user_claims(uid)
        return claims.get("admin", False)
    except Exception as e:
        print(f"❌ Failed to check admin status: {e}")
        return False
