from typing import Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.services.voice_session_service import VoiceSessionService
from app.core.exceptions import (
    BridgeLineException,
    ValidationException,
    NotFoundException,
    PermissionException,
)


def get_voice_session_service(
    db: AsyncSession = Depends(get_db),
) -> VoiceSessionService:
    """音声セッションサービスの依存関係"""
    return VoiceSessionService(db)


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
