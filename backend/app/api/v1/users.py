from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import aliased
from typing import Optional, Dict, Any

from app.api.deps import get_session, get_current_user
from app.schemas.team import UserOut
from app.models.user import User
from app.models.team_member import TeamMember  # ← ここがポイント

router = APIRouter()  # prefix は api.py 側で付与

def _val(profile: Optional[Dict[str, Any]], key: str) -> Optional[str]:
    if isinstance(profile, dict):
        v = profile.get(key)
        if v is None:
            return None
        s = str(v).strip()
        return s if s else None
    return None

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
        display_name=u.display_name or "",
        avatar_url=getattr(u, "avatar_url", None),
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
        },
    )
