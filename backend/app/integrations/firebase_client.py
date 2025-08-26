import firebase_admin
from firebase_admin import credentials, auth, firestore
from typing import Optional, Dict, Any
import structlog
import os

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
            print("🔥 Firebase初期化開始...")
            if self._initialized:
                print("✅ Firebase既に初期化済み")
                return True

            # firebase-admin-key.jsonファイルから直接読み込み
            import json
            import os
            
            firebase_key_path = os.path.join(os.path.dirname(__file__), '..', '..', 'firebase-admin-key.json')
            
            if not os.path.exists(firebase_key_path):
                print(f"❌ Firebase設定ファイルが見つかりません: {firebase_key_path}")
                logger.warning(f"Firebase設定ファイルが見つかりません: {firebase_key_path}")
                logger.info("開発環境ではダミーUIDが生成されます。")
                return False

            # 設定ファイルを読み込み
            with open(firebase_key_path, 'r', encoding='utf-8') as f:
                service_account_info = json.load(f)

            print(f"🔥 Firebase設定確認: PROJECT_ID = {service_account_info['project_id']}")
            logger.info("Firebase設定確認:")
            logger.info(f"  PROJECT_ID: {service_account_info['project_id']}")
            logger.info(f"  CLIENT_EMAIL: {service_account_info['client_email']}")

            cred = credentials.Certificate(service_account_info)
            logger.info("Using Firebase credentials from file")

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
            print(f"❌ Firebase初期化失敗: {e}")
            logger.error(f"Firebase initialization failed: {e}")
            # 開発環境では初期化失敗を許容
            if os.getenv("ENVIRONMENT", "development") == "development":
                print("⚠️ 開発環境での初期化失敗を許容")
                logger.info(
                    "Firebase initialization failed in development, will use mock authentication"
                )
                return False
            return False

    def verify_id_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """IDトークンを検証"""
        try:
            if not self._initialized or self._auth is None:
                if not self.initialize():
                    return None

            assert self._auth is not None
            # 時刻の許容範囲を設定（60秒）
            decoded_token = self._auth.verify_id_token(
                id_token, check_revoked=True, clock_skew_seconds=60
            )
            return decoded_token

        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None

    def get_user_by_uid(self, uid: str) -> Optional[Dict[str, Any]]:
        """UIDでユーザー情報を取得"""
        try:
            if not self._initialized or self._auth is None:
                if not self.initialize():
                    return None

            assert self._auth is not None
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

    def create_user(
        self, email: str, password: str, display_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """ユーザーを作成（Firebase Auth SDK互換）"""
        try:
            if not self._initialized or self._auth is None:
                if not self.initialize():
                    return None

            # self._authがNoneでないことを確認
            if self._auth is None:
                logger.error("Firebase Auth is not initialized")
                return None

            print(f"🔥 Firebase Admin SDKでユーザー作成開始: {email}")
            print(f"🔑 パスワード設定: {'設定済み' if password else '未設定'}")
            print(f"🔑 パスワード値: {password}")

            # ユーザーをメールアドレスとパスワードで一度に作成
            user_properties = {
                "email": email,
                "password": password,  # パスワードを直接設定
                "email_verified": True,  # メール認証を有効化（認証不要にする）
                "disabled": False,  # ユーザーを有効化
            }

            if display_name:
                user_properties["display_name"] = display_name

            user_record = self._auth.create_user(**user_properties)

            print(f"✅ Firebaseユーザー作成成功: {user_record.uid}")
            print(f"📧 作成されたメール: {user_record.email}")
            print(f"👤 表示名: {user_record.display_name}")
            print(f"🔑 パスワード設定: 完了")

            return {
                "uid": user_record.uid,
                "email": user_record.email,
                "display_name": user_record.display_name,
            }

        except Exception as e:
            print(f"❌ Firebaseユーザー作成失敗: {e}")
            logger.error(f"Failed to create user: {e}")
            return None

    def update_user(self, uid: str, **kwargs) -> Optional[Dict[str, Any]]:
        """ユーザー情報を更新"""
        try:
            if not self._initialized or self._auth is None:
                if not self.initialize():
                    return None

            assert self._auth is not None
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
            if not self._initialized or self._auth is None:
                if not self.initialize():
                    return False

            assert self._auth is not None
            self._auth.delete_user(uid)
            return True

        except Exception as e:
            logger.error(f"Failed to delete user {uid}: {e}")
            return False

    def list_users(self, max_results: int = 1000) -> list:
        """ユーザーリストを取得"""
        try:
            if not self._initialized or self._auth is None:
                if not self.initialize():
                    return []

            assert self._auth is not None
            page = self._auth.list_users(max_results=max_results)
            users = []

            for user in page.users:
                users.append(
                    {
                        "uid": user.uid,
                        "email": user.email,
                        "display_name": user.display_name,
                        "email_verified": user.email_verified,
                        "disabled": user.disabled,
                    }
                )

            return users

        except Exception as e:
            logger.error(f"Failed to list users: {e}")
            return []

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """メールアドレスでユーザーを取得"""
        try:
            if not self._initialized:
                if not self.initialize():
                    return None

            # self._authがNoneでないことを確認
            if self._auth is None:
                logger.error("Firebase Auth is not initialized")
                return None

            user_record = self._auth.get_user_by_email(email)

            return {
                "uid": user_record.uid,
                "email": user_record.email,
                "display_name": user_record.display_name,
                "email_verified": user_record.email_verified,
                "disabled": user_record.disabled,
            }

        except Exception as e:
            logger.error(f"Failed to get user by email {email}: {e}")
            return None

    def update_user_password(self, uid: str, new_password: str) -> bool:
        """ユーザーのパスワードを更新"""
        try:
            if not self._initialized:
                if not self.initialize():
                    return False

            if self._auth is None:
                logger.error("Firebase Auth is not initialized")
                return False

            self._auth.update_user(uid, password=new_password)
            logger.info(f"Password updated for user {uid}")
            return True

        except Exception as e:
            logger.error(f"Failed to update password for user {uid}: {e}")
            return False


# グローバルインスタンス
firebase_client = FirebaseClient()


def get_firebase_client() -> FirebaseClient:
    """Firebaseクライアントを取得"""
    return firebase_client


# 管理者ユーザー作成用のヘルパー関数
def create_admin_user(
    email: str, password: str, display_name: str = "Admin"
) -> Optional[Dict[str, Any]]:
    """管理者ユーザーを作成"""
    client = get_firebase_client()
    return client.create_user(email, password, display_name)


def get_admin_user(uid: str) -> Optional[Dict[str, Any]]:
    """管理者ユーザー情報を取得"""
    client = get_firebase_client()
    return client.get_user_by_uid(uid)


def set_admin_claim(uid: str, is_admin: bool = True) -> bool:
    """ユーザーに管理者権限を設定"""
    try:
        if not firebase_client._initialized or firebase_client._auth is None:
            if not firebase_client.initialize():
                return False

        assert firebase_client._auth is not None
        # カスタムクレームを設定
        claims = {"admin": is_admin}
        firebase_client._auth.set_custom_user_claims(uid, claims)

        logger.info(f"Admin claim set for user {uid}: {is_admin}")
        return True

    except Exception as e:
        logger.error(f"Failed to set admin claim for user {uid}: {e}")
        return False


def get_user_claims(uid: str) -> Optional[Dict[str, Any]]:
    """ユーザーのカスタムクレームを取得"""
    try:
        if not firebase_client._initialized or firebase_client._auth is None:
            if not firebase_client.initialize():
                return None

        assert firebase_client._auth is not None
        # ユーザー情報を取得（カスタムクレームを含む）
        user_record = firebase_client._auth.get_user(uid)
        return user_record.custom_claims or {}

    except Exception as e:
        logger.error(f"Failed to get user claims for user {uid}: {e}")
        return None


# firebase_admin.pyとの互換性のための関数
def initialize_firebase_admin() -> bool:
    """Firebase Admin SDKを初期化（firebase_admin.pyとの互換性）"""
    return firebase_client.initialize()


def create_firebase_user(
    email: str, password: str, display_name: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Firebase Authでユーザーを作成（firebase_admin.pyとの互換性）"""
    return firebase_client.create_user(email, password, display_name)


def update_firebase_user_password(uid: str, new_password: str) -> bool:
    """Firebase Authでユーザーのパスワードを更新（firebase_admin.pyとの互換性）"""
    return firebase_client.update_user_password(uid, new_password)


def delete_firebase_user(uid: str) -> bool:
    """Firebase Authでユーザーを削除（firebase_admin.pyとの互換性）"""
    return firebase_client.delete_user(uid)


def verify_firebase_token(id_token: str) -> Optional[Dict[str, Any]]:
    """Firebase IDトークンを検証（firebase_admin.pyとの互換性）"""
    return firebase_client.verify_id_token(id_token)


def get_firebase_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """メールアドレスでFirebase Authユーザーを取得（firebase_admin.pyとの互換性）"""
    return firebase_client.get_user_by_email(email)
