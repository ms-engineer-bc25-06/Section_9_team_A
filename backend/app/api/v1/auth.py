from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.core.auth import get_current_user, get_current_active_user
from app.schemas.auth import Token, TokenData, UserResponse
from app.services.auth_service import AuthService

router = APIRouter()
security = HTTPBearer()
logger = structlog.get_logger()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user=Depends(get_current_active_user)):
    """現在のユーザー情報を取得"""
    return current_user


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user=Depends(get_current_user),
):
    """ユーザーログアウト（Firebase認証ではクライアント側で処理）"""
    try:
        logger.info(f"User logged out: {current_user.email}")
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    profile_data: dict,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """ユーザープロフィール更新"""
    try:
        auth_service = AuthService(db)
        updated_user = await auth_service.update_user_profile(
            current_user.id, profile_data
        )

        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return updated_user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/verify")
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user=Depends(get_current_user),
):
    """トークン検証"""
    try:
        return {
            "valid": True,
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "username": current_user.username,
                "full_name": current_user.full_name,
                "is_active": current_user.is_active,
                "is_verified": current_user.is_verified,
            },
        }
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
