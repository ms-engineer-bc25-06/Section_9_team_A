from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.config import settings
from app.core.database import get_db
from app.core.auth import (
    get_current_user,
    get_current_active_user,
    get_current_admin_user,
)
from app.models.user import User
from app.services.voice_session_service import VoiceSessionService
from app.core.exceptions import (
    BridgeLineException,
    ValidationException,
    NotFoundException,
    PermissionException,
)

# 認証関数を直接再エクスポート（重複を避けるため）
# これにより、app.core.authの実装が一元的に管理される

async def get_session(db: Session = Depends(get_db)) -> Session:
    """DBセッション (AsyncSession) を DI するための薄いラッパ"""
    return db

def get_voice_session_service(
    db: Session = Depends(get_db),
) -> VoiceSessionService:
    """音声セッションサービスの依存関係"""
    return VoiceSessionService(db)

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
