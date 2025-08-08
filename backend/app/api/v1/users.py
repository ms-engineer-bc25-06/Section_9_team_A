from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import structlog

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.schemas.auth import UserResponse, UserUpdate
from app.services.auth_service import AuthService
from app.api.deps import get_current_user
from app.schemas.user import UserMeResponse, UserProfileResponse, TeamSummaryResponse

router = APIRouter()
logger = structlog.get_logger()


@router.get("/me", response_model=UserMeResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    # プロファイル
    profile = None
    if hasattr(current_user, "profile") and current_user.profile:
        profile = UserProfileResponse(
            bio=getattr(current_user.profile, "bio", None),
            department=getattr(current_user.profile, "department", None),
            position=getattr(current_user.profile, "position", None),
            interests=getattr(current_user.profile, "interests", None),
            communication_style=getattr(current_user.profile, "communication_style", None),
            collaboration_score=getattr(current_user.profile, "collaboration_score", None),
            leadership_score=getattr(current_user.profile, "leadership_score", None),
            empathy_score=getattr(current_user.profile, "empathy_score", None),
            assertiveness_score=getattr(current_user.profile, "assertiveness_score", None),
            creativity_score=getattr(current_user.profile, "creativity_score", None),
            analytical_score=getattr(current_user.profile, "analytical_score", None),
            visibility_settings=getattr(current_user.profile, "visibility_settings", None),
            total_chat_sessions=getattr(current_user.profile, "total_chat_sessions", None),
            total_speaking_time_seconds=getattr(current_user.profile, "total_speaking_time_seconds", None),
            last_analysis_at=getattr(current_user.profile, "last_analysis_at", None),
        )
    # チーム
    teams = []
    if hasattr(current_user, "teams"):
        for tm in current_user.teams:
            if hasattr(tm, "team") and tm.team:
                teams.append(TeamSummaryResponse(
                    id=str(getattr(tm.team, "id", "")),
                    name=getattr(tm.team, "name", ""),
                    role=getattr(tm, "role", "")
                ))
    return UserMeResponse(
        id=str(current_user.id),
        firebase_uid=current_user.firebase_uid,
        email=current_user.email,
        display_name=current_user.full_name or current_user.username,
        avatar_url=current_user.avatar_url,
        profile=profile,
        teams=teams,
        last_active_at=current_user.last_login_at,
        created_at=current_user.created_at
    )


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
