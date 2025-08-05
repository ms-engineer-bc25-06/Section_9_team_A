from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import structlog

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.schemas.auth import UserResponse, UserUpdate
from app.services.auth_service import AuthService

router = APIRouter()
logger = structlog.get_logger()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """現在のユーザー情報を取得"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """現在のユーザー情報を更新"""
    try:
        auth_service = AuthService(db)

        # 更新データを辞書に変換
        update_data = user_update.dict(exclude_unset=True)

        updated_user = await auth_service.update_user(
            user_id=current_user.id, update_data=update_data
        )

        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update user"
            )

        return updated_user

    except Exception as e:
        logger.error(f"User update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.delete("/me")
async def delete_current_user(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """現在のユーザーアカウントを削除"""
    try:
        auth_service = AuthService(db)

        success = await auth_service.delete_user(user_id=current_user.id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to delete user"
            )

        return {"message": "User account deleted successfully"}

    except Exception as e:
        logger.error(f"User deletion failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """指定されたIDのユーザー情報を取得"""
    try:
        auth_service = AuthService(db)
        user = await auth_service.get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user by ID {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/profile/{username}", response_model=UserResponse)
async def get_user_by_username(
    username: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """指定されたユーザー名のユーザー情報を取得"""
    try:
        # ユーザー名でユーザーを検索
        result = await db.execute(
            "SELECT * FROM users WHERE username = :username", {"username": username}
        )
        user = result.fetchone()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user by username {username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
