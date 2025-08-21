from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.config import settings
from app.core.database import get_db
from app.core.auth import (
    get_current_user as _get_current_user,
    get_current_active_user as _get_current_active_user,
)
from app.models.user import User
from app.services.voice_session_service import VoiceSessionService
from app.core.exceptions import (
    BridgeLineException,
    ValidationException,
    NotFoundException,
    PermissionException,
)

# スタイルの依存関係を再エクスポート
async def get_current_user(user: User = Depends(_get_current_user)) -> User:
    """認証済みユーザー（アクティブである必要はない）"""
    return user

async def get_current_active_user(user: User = Depends(_get_current_active_user)) -> User:
    """アクティブユーザーのみ許可"""
    return user

async def get_session(db: Session = Depends(get_db)) -> Session:
    """DBセッション (AsyncSession) を DI するための薄いラッパ"""
    return db

def get_voice_session_service(
    db: Session = Depends(get_db),
) -> VoiceSessionService:
    """音声セッションサービスの依存関係"""
    return VoiceSessionService(db)


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """
    現在のユーザーが管理者権限を持っているかチェック
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="管理者権限が必要です"
        )
    return current_user


# 組織関連の関数は現在実装されていないため、コメントアウト
# 必要に応じて後で実装


def handle_bridge_line_exceptions(exc: BridgeLineException) -> HTTPException:
    """BridgeLine例外をHTTP例外に変換"""
    if isinstance(exc, ValidationException):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": exc.message, "error_code": exc.error_code},
        )
    elif isinstance(exc, NotFoundException):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": exc.message, "error_code": exc.error_code},
        )
    elif isinstance(exc, PermissionException):
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": exc.message, "error_code": exc.error_code},
        )
    else:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error", "error_code": "INTERNAL_ERROR"},
        )

async def get_current_superuser(current_user: User = Depends(get_current_user)) -> User:
    """スーパーユーザー（管理者）のみ許可"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="管理者権限が必要です"
        )
    return current_user
