from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any

from app.api.deps import get_session, get_current_user
from app.schemas.team import TeamsListResponse, OrganizationMemberOut, TeamDetailOut, TeamMini
from app.models.user import User
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember  # ← ここがポイント

router = APIRouter()  # prefix は api.py 側で付与

def _get_department_from_profile(profile: Optional[Dict[str, Any]]) -> Optional[str]:
    if isinstance(profile, dict):
        dept = profile.get("department")
        if isinstance(dept, str) and dept.strip():
            return dept.strip()
    return None

@router.get("", response_model=TeamsListResponse)
async def list_my_teams(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(Organization)
        .join(OrganizationMember, OrganizationMember.organization_id == Organization.id)
        .where(OrganizationMember.user_id == current_user.id)
        .order_by(Organization.created_at.desc())
    )
    result = await db.execute(stmt)
    teams = result.scalars().all()
    minis = [TeamMini(id=str(t.id), name=t.name) for t in teams]
    return {"teams": minis, "total": len(minis), "has_more": False}

@router.get("/{team_id}", response_model=TeamDetailOut)
async def get_team_detail(
    team_id: str,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # アクセス権（所属チェック）
    member_stmt = select(OrganizationMember).where(
        OrganizationMember.organization_id == team_id,
        OrganizationMember.user_id == current_user.id,
    ).limit(1)
    if not (await db.execute(member_stmt)).first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="TEAM_ACCESS_DENIED")

    team = await db.get(Organization, team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TEAM_NOT_FOUND")

    # メンバー取得（User.profile は JSON を想定、Python 側でフィルタ）
    stmt = (
        select(User, OrganizationMember)
        .join(OrganizationMember, OrganizationMember.user_id == User.id)
        .where(OrganizationMember.organization_id == team_id)
    )
    rows = (await db.execute(stmt)).all()

    members: List[OrganizationMemberOut] = []
    for u, tm in rows:
        name_ok = isinstance(u.display_name, str) and u.display_name.strip()
        department = _get_department_from_profile(getattr(u, "profile", None))
        if not name_ok or not department:
            continue
        members.append(
            OrganizationMemberOut(
                id=str(u.id),
                display_name=u.display_name,
                avatar_url=getattr(u, "avatar_url", None),
                role=getattr(tm, "role", None),
                status=getattr(tm, "status", None),
                profile={"department": department},
            )
        )

    return {"id": str(team.id), "name": team.name, "members": members}

@router.get("/{team_id}/members", response_model=dict)
async def list_team_members_minimal(
    team_id: str,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    member_stmt = select(OrganizationMember).where(
        OrganizationMember.organization_id == team_id,
        OrganizationMember.user_id == current_user.id,
    ).limit(1)
    if not (await db.execute(member_stmt)).first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="TEAM_ACCESS_DENIED")

    stmt = (
        select(User, OrganizationMember)
        .join(OrganizationMember, OrganizationMember.user_id == User.id)
        .where(OrganizationMember.organization_id == team_id)
    )
    rows = (await db.execute(stmt)).all()

    members = []
    for u, tm in rows:
        name_ok = isinstance(u.display_name, str) and u.display_name.strip()
        department = _get_department_from_profile(getattr(u, "profile", None))
        if not name_ok or not department:
            continue
        members.append(
            {
                "id": str(u.id),
                "display_name": u.display_name,
                "avatar_url": getattr(u, "avatar_url", None),
                "role": getattr(tm, "role", None),
                "status": getattr(tm, "status", None),
                "profile": {"department": department},
            }
        )

    return {"members": members}
