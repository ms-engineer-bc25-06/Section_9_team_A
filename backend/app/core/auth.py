from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
import firebase_admin
from firebase_admin import auth, credentials
import structlog

from app.core.config import settings
from app.models.user import User
from app.core.database import get_db, AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

logger = structlog.get_logger()

# パスワードハッシュ化
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT設定
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Firebase初期化
try:
    if not firebase_admin._apps:
        # 設定ファイルから直接読み込み
        import json
        import os
        
        # 現在のディレクトリからfirebase-admin-key.jsonを読み込み
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        firebase_key_path = os.path.join(current_dir, "firebase-admin-key.json")
        
        if os.path.exists(firebase_key_path):
            with open(firebase_key_path, 'r') as f:
                firebase_config = json.load(f)
            
            cred = credentials.Certificate(firebase_config)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized successfully from config file")
        else:
            # 環境変数から読み込み（フォールバック）
            if settings.FIREBASE_PROJECT_ID and settings.FIREBASE_PRIVATE_KEY:
                cred = credentials.Certificate({
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
                })
                firebase_admin.initialize_app(cred)
                logger.info("Firebase initialized successfully from environment variables")
            else:
                logger.warning("Firebase configuration not found, Firebase features will be disabled")
except Exception as e:
    logger.warning(f"Firebase initialization failed: {e}")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """パスワード検証"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """パスワードハッシュ化"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """アクセストークン作成"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def verify_token(token: str) -> Optional[dict]:
    """JWTトークン検証"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return payload
    except JWTError:
        return None


async def verify_firebase_token(id_token: str) -> Optional[dict]:
    """Firebaseトークン検証"""
    try:
        # 時刻の許容範囲を設定（60秒）
        decoded_token = auth.verify_id_token(id_token, check_revoked=True, clock_skew_seconds=60)
        return decoded_token
    except Exception as e:
        logger.error(f"Firebase token verification failed: {e}")
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: AsyncSession = Depends(get_db),
) -> User:
    """現在のユーザー取得（JWTトークンまたはFirebaseトークン対応）"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials

        # まずJWTトークンとして検証を試行
        payload = await verify_token(token)
        if payload:
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception

            # ユーザー取得
            result = await db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()

            if user is None:
                raise credentials_exception

            return user

        # JWTトークンが無効な場合、Firebaseトークンとして検証を試行
        firebase_payload = await verify_firebase_token(token)
        if firebase_payload:
            uid: str = firebase_payload.get("uid")
            email: str = firebase_payload.get("email")
            
            if not uid or not email:
                raise credentials_exception

            # Firebase UIDでユーザーを検索
            result = await db.execute(select(User).where(User.firebase_uid == uid))
            user = result.scalar_one_or_none()

            if user is None:
                raise credentials_exception

            return user

        # どちらのトークンも無効
        raise credentials_exception

    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise credentials_exception


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """現在のアクティブユーザー取得"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def authenticate_user(email: str, password: str, db: AsyncSession) -> Optional[User]:
    """ユーザー認証"""
    # この関数は後でAuthServiceで実装
    pass


async def get_current_user_from_token(token: str) -> Optional[User]:
    """トークンから現在のユーザーを取得（WebSocket等の非依存性コンテキスト用）"""
    try:
        payload = await verify_token(token)
        if payload is None:
            return None
        email: Optional[str] = payload.get("sub")
        if not email:
            return None

        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            return user
    except Exception as e:
        logger.error(f"get_current_user_from_token failed: {e}")
        return None
