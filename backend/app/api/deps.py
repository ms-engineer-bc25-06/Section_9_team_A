from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.core.config import settings
from app.core.database import get_db
from app.core.auth import (
    get_current_user as _get_current_user,
    get_current_active_user as _get_current_active_user,
)
from app.models.user import User
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
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


async def get_organization_by_id(
    organization_id: int,
    db: Session = Depends(get_db)
) -> Organization:
    """
    組織IDで組織を取得
    """
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="組織が見つかりません"
        )
    return organization


async def get_organization_member(
    organization_id: int,
    user_id: int,
    db: Session = Depends(get_db)
) -> OrganizationMember:
    """
    組織のメンバー情報を取得
    """
    member = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == organization_id,
        OrganizationMember.user_id == user_id
    ).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="組織メンバーが見つかりません"
        )
    return member


async def check_organization_admin_access(
    organization_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> OrganizationMember:
    """
    現在のユーザーが指定された組織の管理者権限を持っているかチェック
    """
    member = await get_organization_member(organization_id, current_user.id, db)
    if member.role not in ['admin', 'owner']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="組織の管理者権限が必要です"
        )
    return member


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
