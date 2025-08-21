"""Firebase Admin SDK設定"""
import firebase_admin
from firebase_admin import auth, credentials
from firebase_admin.exceptions import FirebaseError
import os
from typing import Optional, Dict, Any
from app.config import settings

# Firebase Admin SDKの初期化
def initialize_firebase_admin():
    """Firebase Admin SDKを初期化"""
    try:
        # 必須設定のチェック
        if not settings.FIREBASE_PROJECT_ID or settings.FIREBASE_PROJECT_ID == "your-firebase-project-id":
            print("Firebase設定が不完全です。FIREBASE_PROJECT_IDが設定されていません。")
            print("開発環境ではダミーUIDが生成されます。")
            return False
            
        if not settings.FIREBASE_CLIENT_EMAIL or settings.FIREBASE_CLIENT_EMAIL == "your-firebase-client-email":
            print("Firebase設定が不完全です。FIREBASE_CLIENT_EMAILが設定されていません。")
            print("開発環境ではダミーUIDが生成されます。")
            return False
            
        if not settings.FIREBASE_PRIVATE_KEY or settings.FIREBASE_PRIVATE_KEY == "your-private-key":
            print("Firebase設定が不完全です。FIREBASE_PRIVATE_KEYが設定されていません。")
            print("開発環境ではダミーUIDが生成されます。")
            return False
        
        # 環境変数からFirebase設定を取得
        firebase_config = {
            "type": "service_account",
            "project_id": settings.FIREBASE_PROJECT_ID,
            "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
            "private_key": settings.FIREBASE_PRIVATE_KEY.replace('\\n', '\n') if settings.FIREBASE_PRIVATE_KEY else None,
            "client_email": settings.FIREBASE_CLIENT_EMAIL,
            "client_id": settings.FIREBASE_CLIENT_ID,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": settings.FIREBASE_CLIENT_CERT_URL
        }
        
        # サービスアカウントキーで初期化
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred)
        
        print("Firebase Admin SDK初期化成功")
        return True
    except Exception as e:
        print(f"Firebase Admin SDK初期化エラー: {e}")
        print("開発環境ではダミーUIDが生成されます。")
        return False

def create_firebase_user(email: str, password: str, display_name: str = None) -> Optional[Dict[str, Any]]:
    """Firebase Authでユーザーを作成"""
    try:
        user_properties = {
            'email': email,
            'password': password,
            'email_verified': False,
            'disabled': False
        }
        
        if display_name:
            user_properties['display_name'] = display_name
        
        user_record = auth.create_user(**user_properties)
        
        return {
            'uid': user_record.uid,
            'email': user_record.email,
            'display_name': user_record.display_name,
            'email_verified': user_record.email_verified,
            'disabled': user_record.disabled
        }
    except FirebaseError as e:
        print(f"Firebaseユーザー作成エラー: {e}")
        return None

def update_firebase_user_password(uid: str, new_password: str) -> bool:
    """Firebase Authでユーザーのパスワードを更新"""
    try:
        auth.update_user(uid, password=new_password)
        return True
    except FirebaseError as e:
        print(f"Firebaseパスワード更新エラー: {e}")
        return False

def delete_firebase_user(uid: str) -> bool:
    """Firebase Authでユーザーを削除"""
    try:
        auth.delete_user(uid)
        return True
    except FirebaseError as e:
        print(f"Firebaseユーザー削除エラー: {e}")
        return False

def verify_firebase_token(id_token: str) -> Optional[Dict[str, Any]]:
    """Firebase IDトークンを検証"""
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except FirebaseError as e:
        print(f"Firebaseトークン検証エラー: {e}")
        return None

def get_firebase_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """メールアドレスでFirebase Authユーザーを取得"""
    try:
        user_record = auth.get_user_by_email(email)
        return {
            'uid': user_record.uid,
            'email': user_record.email,
            'display_name': user_record.display_name,
            'email_verified': user_record.email_verified,
            'disabled': user_record.disabled
        }
    except FirebaseError as e:
        print(f"Firebaseユーザー取得エラー: {e}")
        return None
