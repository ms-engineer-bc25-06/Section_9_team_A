from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import aliased
from typing import Optional, Dict, Any, List
import structlog
from datetime import datetime, date

from app.api.deps import get_session, get_current_user
from app.schemas.team import UserOut, UserProfileOut
from app.schemas.user import ProfileUpdate, ProfileResponse
from app.models.user import User
from app.models.team_member import TeamMember
from app.services.auth_service import AuthService


router = APIRouter()  # prefix は api.py 側で付与
logger = structlog.get_logger()

def _val(profile: Optional[Dict[str, Any]], key: str) -> Optional[str]:
    if isinstance(profile, dict):
        v = profile.get(key)
        if v is None:
            return None
        s = str(v).strip()
        return s if s else None
    return None


@router.get("/profile", response_model=ProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """現在のユーザーのプロフィール情報を取得"""
    try:
        return ProfileResponse(
            nickname=getattr(current_user, 'nickname') or "",
            department=getattr(current_user, 'department') or "",
            join_date=getattr(current_user, 'join_date').isoformat() if getattr(current_user, 'join_date') else "",
            birth_date=getattr(current_user, 'birth_date').isoformat() if getattr(current_user, 'birth_date') else "",
            hometown=getattr(current_user, 'hometown') or "",
            residence=getattr(current_user, 'residence') or "",
            hobbies=getattr(current_user, 'hobbies') or "",
            student_activities=getattr(current_user, 'student_activities') or "",
            holiday_activities=getattr(current_user, 'holiday_activities') or "",
            favorite_food=getattr(current_user, 'favorite_food') or "",
            favorite_media=getattr(current_user, 'favorite_media') or "",
            favorite_music=getattr(current_user, 'favorite_music') or "",
            pets_oshi=getattr(current_user, 'pets_oshi') or "",
            respected_person=getattr(current_user, 'respected_person') or "",
            motto=getattr(current_user, 'motto') or "",
            future_goals=getattr(current_user, 'future_goals') or ""
        )
    except Exception as e:
        logger.error(f"Profile retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.put("/profile", response_model=ProfileResponse)
async def update_user_profile(
    profile_update: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """現在のユーザーのプロフィール情報を更新"""
    try:
        auth_service = AuthService(db)

        # プロフィール更新データを辞書に変換
        update_data = profile_update.dict(exclude_unset=True)
        
        # データベースのフィールド名にマッピング
        db_update_data = {}
        field_mapping = {
            "nickname": "nickname",
            "department": "department",
            "join_date": "join_date",
            "birth_date": "birth_date",
            "hometown": "hometown",
            "residence": "residence",
            "hobbies": "hobbies",
            "student_activities": "student_activities",
            "holiday_activities": "holiday_activities",
            "favorite_food": "favorite_food",
            "favorite_media": "favorite_media",
            "favorite_music": "favorite_music",
            "pets_oshi": "pets_oshi",
            "respected_person": "respected_person",
            "motto": "motto",
            "future_goals": "future_goals"
        }
        
        for frontend_field, db_field in field_mapping.items():
            if frontend_field in update_data:
                value = update_data[frontend_field]
                
                # 日付フィールドの場合は文字列をdateオブジェクトに変換
                if db_field in ["join_date", "birth_date"] and value:
                    try:
                        if isinstance(value, str):
                            # YYYY-MM-DD形式の文字列をdateオブジェクトに変換
                            value = datetime.strptime(value, "%Y-%m-%d").date()
                        elif isinstance(value, datetime):
                            value = value.date()
                    except ValueError as e:
                        logger.warning(f"Invalid date format for {db_field}: {value}, error: {e}")
                        continue  # 無効な日付の場合はスキップ
                
                db_update_data[db_field] = value

        updated_user = await auth_service.update_user(
            user_id=int(current_user.id), update_data=db_update_data
        )

        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update profile"
            )

        # 更新されたプロフィール情報を返す
        return ProfileResponse(
            nickname=getattr(updated_user, 'nickname') or "",
            department=getattr(updated_user, 'department') or "",
            join_date=getattr(updated_user, 'join_date').isoformat() if getattr(updated_user, 'join_date') else "",
            birth_date=getattr(updated_user, 'birth_date').isoformat() if getattr(updated_user, 'birth_date') else "",
            hometown=getattr(updated_user, 'hometown') or "",
            residence=getattr(updated_user, 'residence') or "",
            hobbies=getattr(updated_user, 'hobbies') or "",
            student_activities=getattr(updated_user, 'student_activities') or "",
            holiday_activities=getattr(updated_user, 'holiday_activities') or "",
            favorite_food=getattr(updated_user, 'favorite_food') or "",
            favorite_media=getattr(updated_user, 'favorite_media') or "",
            favorite_music=getattr(updated_user, 'favorite_music') or "",
            pets_oshi=getattr(updated_user, 'pets_oshi') or "",
            respected_person=getattr(updated_user, 'respected_person') or "",
            motto=getattr(updated_user, 'motto') or "",
            future_goals=getattr(updated_user, 'future_goals') or ""
        )

    except Exception as e:
        logger.error(f"Profile update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/members", response_model=List[UserOut])
async def get_team_members(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """現在のユーザーと同じチームのメンバー一覧を取得"""
    try:
        # 現在のユーザーが所属するチームIDを取得
        team_query = select(TeamMember.team_id).where(TeamMember.user_id == current_user.id)
        team_result = await db.execute(team_query)
        user_teams = [row[0] for row in team_result.fetchall()]
        
        if not user_teams:
            return []
        
        # 同じチームのメンバーを取得
        members_query = (
            select(User, TeamMember.role, TeamMember.status)
            .join(TeamMember, User.id == TeamMember.user_id)
            .where(TeamMember.team_id.in_(user_teams))
            .distinct()
        )
        
        members_result = await db.execute(members_query)
        members = []
        
        for row in members_result.fetchall():
            user, role, status = row
            profile = UserProfileOut(
                department=getattr(user, 'department'),
                position=role,
                nickname=getattr(user, 'nickname'),
                join_date=str(getattr(user, 'join_date')) if getattr(user, 'join_date') else None,
                birth_date=str(getattr(user, 'birth_date')) if getattr(user, 'birth_date') else None,
                hometown=getattr(user, 'hometown'),
                residence=getattr(user, 'residence'),
                hobbies=getattr(user, 'hobbies'),
                student_activities=getattr(user, 'student_activities'),
                holiday_activities=getattr(user, 'holiday_activities'),
                favorite_food=getattr(user, 'favorite_food'),
                favorite_media=getattr(user, 'favorite_media'),
                favorite_music=getattr(user, 'favorite_music'),
                pets_oshi=getattr(user, 'pets_oshi'),
                respected_person=getattr(user, 'respected_person'),
                motto=getattr(user, 'motto'),
                future_goals=getattr(user, 'future_goals')
            )
            
            members.append(UserOut(
                id=str(user.id),
                display_name=getattr(user, 'full_name') or getattr(user, 'username') or "",
                avatar_url=getattr(user, 'avatar_url'),
                profile=profile
            ))
        
        return members
        
    except Exception as e:
        logger.error(f"Failed to get team members: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/{user_id}", response_model=UserOut)
async def get_user_detail(
    user_id: str,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # 同じチーム所属の確認（自己結合）
    A = aliased(TeamMember)
    B = aliased(TeamMember)
    same_team_stmt = (
        select(A.team_id)
        .join(B, A.team_id == B.team_id)
        .where(A.user_id == current_user.id, B.user_id == user_id)
        .limit(1)
    )
    if not (await db.execute(same_team_stmt)).first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="TEAM_ACCESS_DENIED")

    u = await db.get(User, user_id)
    if not u:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="USER_NOT_FOUND")

    prof: Optional[Dict[str, Any]] = getattr(u, "profile", None)

    return UserOut(
        id=str(u.id),
        display_name=getattr(u, 'full_name') or getattr(u, 'username') or "",
        avatar_url=getattr(u, 'avatar_url'),
        profile=None
        if prof is None
        else {
            "department": _val(prof, "department"),
            "position": _val(prof, "position"),
            "nickname": _val(prof, "nickname"),
            "join_date": _val(prof, "join_date"),
            "birth_date": _val(prof, "birth_date"),
            "hometown": _val(prof, "hometown"),
            "residence": _val(prof, "residence"),
            "hobbies": _val(prof, "hobbies"),
            "student_activities": _val(prof, "student_activities"),
            "holiday_activities": _val(prof, "holiday_activities"),
            "favorite_food": _val(prof, "favorite_food"),
            "favorite_media": _val(prof, "favorite_media"),
            "favorite_music": _val(prof, "favorite_music"),
            "pets_oshi": _val(prof, "pets_oshi"),
            "respected_person": _val(prof, "respected_person"),
            "motto": _val(prof, "motto"),
            "future_goals": _val(prof, "future_goals"),
            "feedback": prof.get("feedback"),
            "ai_analysis": prof.get("ai_analysis"),
        },
    )
