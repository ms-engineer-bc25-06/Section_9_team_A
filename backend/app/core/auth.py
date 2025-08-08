from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import auth, credentials
import structlog

from app.config import settings
from app.models.user import User
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

logger = structlog.get_logger()

# Firebase初期化
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(
            {
                "type": "service_account",
                "project_id": settings.FIREBASE_PROJECT_ID,
                "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
                "private_key": settings.FIREBASE_PRIVATE_KEY.replace("\\n", "\n")
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
    logger.info("Firebase initialized successfully")
except Exception as e:
    logger.warning(f"Firebase initialization failed: {e}")


async def verify_firebase_token(id_token: str) -> Optional[dict]:
    """Firebaseトークン検証"""
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        logger.error(f"Firebase token verification failed: {e}")
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: AsyncSession = Depends(get_db),
) -> User:
    """現在のユーザー取得（Firebase認証）"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials

        # Firebaseトークン検証
        decoded_token = await verify_firebase_token(token)
        if decoded_token is None:
            raise credentials_exception

        firebase_uid = decoded_token.get("uid")
        email = decoded_token.get("email")

        if not firebase_uid or not email:
            raise credentials_exception

        # ユーザー取得（Firebase UIDまたはメールアドレスで検索）
        result = await db.execute(
            select(User).where(
                (User.firebase_uid == firebase_uid) | (User.email == email)
            )
        )
        user = result.scalar_one_or_none()

        if user is None:
            # ユーザーが存在しない場合は作成
            user = await create_user_from_firebase(decoded_token, db)

        if not user:
            raise credentials_exception

        # 最終ログイン時刻更新
        user.last_login_at = datetime.utcnow()
        await db.commit()

        return user

    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise credentials_exception


async def create_user_from_firebase(
    firebase_user: dict, db: AsyncSession
) -> Optional[User]:
    """Firebaseユーザー情報からユーザーを作成"""
    try:
        firebase_uid = firebase_user.get("uid")
        email = firebase_user.get("email")
        name = firebase_user.get("name", "")

        if not firebase_uid or not email:
            return None

        # ユーザー作成
        user = User(
            email=email,
            username=email.split("@")[0],  # メールアドレスの@前をユーザー名として使用
            full_name=name,
            firebase_uid=firebase_uid,
            is_verified=firebase_user.get("email_verified", False),
            is_active=True,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        logger.info(f"User created from Firebase: {email}")
        return user

    except Exception as e:
        logger.error(f"Failed to create user from Firebase: {e}")
        await db.rollback()
        return None


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """現在のアクティブユーザー取得"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_user_by_firebase_uid(
    firebase_uid: str, db: AsyncSession
) -> Optional[User]:
    """Firebase UIDでユーザー取得"""
    try:
        result = await db.execute(select(User).where(User.firebase_uid == firebase_uid))
        return result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Failed to get user by Firebase UID {firebase_uid}: {e}")
        return None
