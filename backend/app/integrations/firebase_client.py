import firebase_admin
from firebase_admin import credentials, auth, firestore
from typing import Optional, Dict, Any
import structlog

from app.config import settings

logger = structlog.get_logger()


class FirebaseClient:
    """Firebaseクライアントクラス"""

    def __init__(self):
        """Firebaseクライアントを初期化"""
        self._app = None
        self._auth = None
        self._firestore = None
        self._initialized = False

    def initialize(self) -> bool:
        """Firebaseを初期化"""
        try:
            if self._initialized:
                return True

            # サービスアカウントキーファイルのパス
            service_account_path = "firebase-admin-key.json"
            
            # 認証情報を読み込み
            cred = credentials.Certificate(service_account_path)
            
            # 既存のアプリがあるかチェック
            try:
                self._app = firebase_admin.get_app()
                logger.info("Using existing Firebase app")
            except ValueError:
                # 新しいアプリを作成
                self._app = firebase_admin.initialize_app(cred)
                logger.info("Created new Firebase app")
            
            self._auth = auth
            self._firestore = firestore.client()
            self._initialized = True
            
            logger.info("Firebase initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Firebase initialization failed: {e}")
            return False

    def verify_id_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """IDトークンを検証"""
        try:
            if not self._initialized:
                if not self.initialize():
                    return None
            
            # 時刻の許容範囲を設定（60秒）
            decoded_token = self._auth.verify_id_token(id_token, check_revoked=True, clock_skew_seconds=60)
            return decoded_token
            
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None

    def get_user_by_uid(self, uid: str) -> Optional[Dict[str, Any]]:
        """UIDでユーザー情報を取得"""
        try:
            if not self._initialized:
                if not self.initialize():
                    return None
            
            user_record = self._auth.get_user(uid)
            return {
                "uid": user_record.uid,
                "email": user_record.email,
                "display_name": user_record.display_name,
                "photo_url": user_record.photo_url,
                "email_verified": user_record.email_verified,
                "disabled": user_record.disabled,
            }
            
        except Exception as e:
            logger.error(f"Failed to get user by UID {uid}: {e}")
            return None

    def create_user(self, email: str, password: str, display_name: str = None) -> Optional[Dict[str, Any]]:
        """ユーザーを作成"""
        try:
            if not self._initialized:
                if not self.initialize():
                    return None
            
            user_properties = {
                "email": email,
                "password": password,
            }
            
            if display_name:
                user_properties["display_name"] = display_name
            
            user_record = self._auth.create_user(**user_properties)
            
            return {
                "uid": user_record.uid,
                "email": user_record.email,
                "display_name": user_record.display_name,
            }
            
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return None

    def update_user(self, uid: str, **kwargs) -> Optional[Dict[str, Any]]:
        """ユーザー情報を更新"""
        try:
            if not self._initialized:
                if not self.initialize():
                    return None
            
            user_record = self._auth.update_user(uid, **kwargs)
            
            return {
                "uid": user_record.uid,
                "email": user_record.email,
                "display_name": user_record.display_name,
            }
            
        except Exception as e:
            logger.error(f"Failed to update user {uid}: {e}")
            return None

    def delete_user(self, uid: str) -> bool:
        """ユーザーを削除"""
        try:
            if not self._initialized:
                if not self.initialize():
                    return False
            
            self._auth.delete_user(uid)
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete user {uid}: {e}")
            return False

    def list_users(self, max_results: int = 1000) -> list:
        """ユーザーリストを取得"""
        try:
            if not self._initialized:
                if not self.initialize():
                    return []
            
            page = self._auth.list_users(max_results=max_results)
            users = []
            
            for user in page.users:
                users.append({
                    "uid": user.uid,
                    "email": user.email,
                    "display_name": user.display_name,
                    "email_verified": user.email_verified,
                    "disabled": user.disabled,
                })
            
            return users
            
        except Exception as e:
            logger.error(f"Failed to list users: {e}")
            return []


# グローバルインスタンス
firebase_client = FirebaseClient()


def get_firebase_client() -> FirebaseClient:
    """Firebaseクライアントを取得"""
    return firebase_client


# 管理者ユーザー作成用のヘルパー関数
def create_admin_user(email: str, password: str, display_name: str = "Admin") -> Optional[Dict[str, Any]]:
    """管理者ユーザーを作成"""
    client = get_firebase_client()
    return client.create_user(email, password, display_name)


def get_admin_user(uid: str) -> Optional[Dict[str, Any]]:
    """管理者ユーザー情報を取得"""
    client = get_firebase_client()
    return client.get_user_by_uid(uid)
