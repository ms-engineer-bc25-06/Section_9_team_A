from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
import firebase_admin
from firebase_admin import auth, credentials
import structlog

from app.config import settings
from app.models.user import User
from app.core.database import get_db, AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

logger = structlog.get_logger()

# パスワードハッシュ化
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Firebase初期化
try:
    if not firebase_admin._apps:
        # 設定ファイルから直接読み込み
        import json
        import os

        # 現在のディレクトリからfirebase-admin-key.jsonを読み込み
        current_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        firebase_key_path = os.path.join(current_dir, "firebase-admin-key.json")

        if os.path.exists(firebase_key_path):
            with open(firebase_key_path, "r") as f:
                firebase_config = json.load(f)

            cred = credentials.Certificate(firebase_config)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized successfully from config file")
        else:
            # 環境変数から読み込み（フォールバック）
            if settings.FIREBASE_PROJECT_ID and settings.FIREBASE_PRIVATE_KEY:
                cred = credentials.Certificate(
                    {
                        "type": "service_account",
                        "project_id": settings.FIREBASE_PROJECT_ID,
                        "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
                        "private_key": settings.FIREBASE_PRIVATE_KEY.replace(
                            "\\n", "\n"
                        )
                        if settings.FIREBASE_PRIVATE_KEY
                        else None,
                        "client_email": settings.FIREBASE_CLIENT_EMAIL,
                        "client_id": settings.FIREBASE_CLIENT_ID,
                        "auth_uri": settings.FIREBASE_AUTH_URI,
                        "token_uri": settings.FIREBASE_TOKEN_URI,
                        "auth_provider_x509_cert_url": settings.FIREBASE_AUTH_PROVIDER_X509_CERT_URL,
                        "client_x509_cert_url": settings.FIREBASE_CLIENT_X509_CERT_URL,
                    }
                )
                firebase_admin.initialize_app(cred)
                logger.info(
                    "Firebase initialized successfully from environment variables"
                )
            else:
                logger.warning(
                    "Firebase configuration not found, Firebase features will be disabled"
                )
except Exception as e:
    logger.warning(f"Firebase initialization failed: {e}")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """パスワード検証"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """パスワードハッシュ化"""
    return pwd_context.hash(password)


# JWT関連の関数は削除（Firebase IDトークンのみを使用）


async def verify_firebase_token(id_token: str) -> Optional[dict]:
    """Firebaseトークン検証"""
    try:
        # 時刻の許容範囲を設定（60秒）
        decoded_token = auth.verify_id_token(
            id_token, check_revoked=True, clock_skew_seconds=60
        )
        return decoded_token
    except Exception as e:
        logger.error(f"Firebase token verification failed: {e}")
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: AsyncSession = Depends(get_db),
) -> User:
    """現在のユーザー取得（Firebase IDトークンのみ）"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials

        # Firebase IDトークンの検証
        firebase_payload = await verify_firebase_token(token)
        if not firebase_payload:
            raise credentials_exception

        uid = firebase_payload.get("uid")
        email = firebase_payload.get("email")

        if not uid or not email:
            raise credentials_exception

        # Firebase UIDでユーザーを検索
        result = await db.execute(select(User).where(User.firebase_uid == uid))
        user = result.scalar_one_or_none()

        if user is None:
            raise credentials_exception

        return user

    except Exception as e:
        logger.error(
            "Authentication failed", error_type=type(e).__name__, error_message=str(e)
        )
        raise credentials_exception


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """現在のアクティブユーザー取得"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """現在の管理者ユーザー取得"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="管理者権限が必要です"
        )
    return current_user


def authenticate_user(email: str, password: str, db: AsyncSession) -> Optional[User]:
    """ユーザー認証"""
    # この関数は後でAuthServiceで実装
    pass


async def get_current_user_from_token(token: str) -> Optional[User]:
    """トークンから現在のユーザーを取得（Firebase IDトークンのみ）"""
    try:
        # Firebase IDトークンの検証
        firebase_payload = await verify_firebase_token(token)
        if not firebase_payload:
            return None

        uid = firebase_payload.get("uid")
        email = firebase_payload.get("email")

        if not uid or not email:
            return None

        # Firebase UIDでユーザーを検索
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.firebase_uid == uid))
            user = result.scalar_one_or_none()
            return user

    except Exception as e:
        logger.error(
            "get_current_user_from_token failed",
            error_type=type(e).__name__,
            error_message=str(e),
        )
        return None
