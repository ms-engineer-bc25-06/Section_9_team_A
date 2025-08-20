"""
統合されたチームAPI
チーム管理、チームダイナミクス、チームメンバーを統合
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from typing import List, Optional, Dict, Any

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.schemas.team import (
    TeamCreate, TeamUpdate, TeamResponse, TeamListResponse,
    OrganizationMemberCreate, OrganizationMemberUpdate, OrganizationMemberResponse
)
from app.schemas.team_dynamics import (
    TeamDynamicsCreate, TeamDynamicsUpdate, TeamDynamicsResponse,
    TeamDynamicsListResponse, TeamMetrics
)
from app.services.team_service import TeamService
from app.services.team_dynamics_service import TeamDynamicsService
from app.services.team_member_service import OrganizationMemberService

router = APIRouter()
logger = structlog.get_logger()


# ==================== チーム基本管理 ====================

@router.get("/", response_model=TeamListResponse)
async def get_teams(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="ページ番号"),
    page_size: int = Query(20, ge=1, le=100, description="ページサイズ"),
    team_name: Optional[str] = Query(None, description="チーム名でフィルタリング"),
    status: Optional[str] = Query(None, description="ステータスでフィルタリング")
):
    """ユーザーが所属するチーム一覧を取得"""
    try:
        team_service = TeamService()
        result = await team_service.get_user_teams(
            db=db,
            user=current_user,
            page=page,
            page_size=page_size,
            team_name=team_name,
            status=status
        )
        
        return TeamListResponse(
            teams=result["teams"],
            total_count=result["total_count"],
            page=result["page"],
            page_size=result["page_size"]
        )
        
    except Exception as e:
        logger.error("チーム一覧取得でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="チーム一覧の取得に失敗しました"
        )


@router.post("/", response_model=TeamResponse)
async def create_team(
    team_create: TeamCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """新しいチームを作成"""
    try:
        team_service = TeamService()
        team = await team_service.create_team(
            db=db,
            team_data=team_create,
            creator=current_user
        )
        
        logger.info(
            "チーム作成完了",
            user_id=current_user.id,
            team_id=team.id,
            team_name=team.name
        )
        
        return team
        
    except Exception as e:
        logger.error("チーム作成でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="チームの作成に失敗しました"
        )


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """チームの詳細を取得"""
    try:
        team_service = TeamService()
        team = await team_service.get_team(
            db=db,
            team_id=team_id,
            user=current_user
        )
        
        return team
        
    except Exception as e:
        logger.error("チーム詳細取得でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="チームの詳細取得に失敗しました"
        )


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: int,
    team_update: TeamUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """チームを更新"""
    try:
        team_service = TeamService()
        team = await team_service.update_team(
            db=db,
            team_id=team_id,
            team_data=team_update,
            user=current_user
        )
        
        return team
        
    except Exception as e:
        logger.error("チーム更新でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="チームの更新に失敗しました"
        )


@router.delete("/{team_id}")
async def delete_team(
    team_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """チームを削除"""
    try:
        team_service = TeamService()
        await team_service.delete_team(
            db=db,
            team_id=team_id,
            user=current_user
        )
        
        return {"message": "チームが正常に削除されました"}
        
    except Exception as e:
        logger.error("チーム削除でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="チームの削除に失敗しました"
        )


# ==================== チームメンバー管理 ====================

@router.get("/{team_id}/members", response_model=List[OrganizationMemberResponse])
async def get_team_members(
    team_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """チームメンバー一覧を取得"""
    try:
        member_service = OrganizationMemberService()
        members = await member_service.get_team_members(
            db=db,
            team_id=team_id,
            user=current_user
        )
        
        return members
        
    except Exception as e:
        logger.error("チームメンバー一覧取得でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="チームメンバー一覧の取得に失敗しました"
        )


@router.post("/{team_id}/members", response_model=OrganizationMemberResponse)
async def add_team_member(
    team_id: int,
    member_create: OrganizationMemberCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """チームにメンバーを追加"""
    try:
        member_service = OrganizationMemberService()
        member = await member_service.add_team_member(
            db=db,
            team_id=team_id,
            member_data=member_create,
            added_by=current_user
        )
        
        return member
        
    except Exception as e:
        logger.error("チームメンバー追加でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="チームメンバーの追加に失敗しました"
        )


@router.put("/{team_id}/members/{member_id}", response_model=OrganizationMemberResponse)
async def update_team_member(
    team_id: int,
    member_id: int,
    member_update: OrganizationMemberUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """チームメンバーを更新"""
    try:
        member_service = OrganizationMemberService()
        member = await member_service.update_team_member(
            db=db,
            team_id=team_id,
            member_id=member_id,
            member_data=member_update,
            updated_by=current_user
        )
        
        return member
        
    except Exception as e:
        logger.error("チームメンバー更新でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="チームメンバーの更新に失敗しました"
        )


@router.delete("/{team_id}/members/{member_id}")
async def remove_team_member(
    team_id: int,
    member_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """チームからメンバーを削除"""
    try:
        member_service = OrganizationMemberService()
        await member_service.remove_team_member(
            db=db,
            team_id=team_id,
            member_id=member_id,
            removed_by=current_user
        )
        
        return {"message": "チームメンバーが正常に削除されました"}
        
    except Exception as e:
        logger.error("チームメンバー削除でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="チームメンバーの削除に失敗しました"
        )


# ==================== チームダイナミクス ====================

@router.get("/{team_id}/dynamics", response_model=TeamDynamicsListResponse)
async def get_team_dynamics(
    team_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="ページ番号"),
    page_size: int = Query(20, ge=1, le=100, description="ページサイズ"),
    start_date: Optional[str] = Query(None, description="開始日"),
    end_date: Optional[str] = Query(None, description="終了日")
):
    """チームダイナミクス一覧を取得"""
    try:
        dynamics_service = TeamDynamicsService()
        result = await dynamics_service.get_team_dynamics(
            db=db,
            team_id=team_id,
            user=current_user,
            page=page,
            page_size=page_size,
            start_date=start_date,
            end_date=end_date
        )
        
        return TeamDynamicsListResponse(
            dynamics=result["dynamics"],
            total_count=result["total_count"],
            page=result["page"],
            page_size=result["page_size"]
        )
        
    except Exception as e:
        logger.error("チームダイナミクス一覧取得でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="チームダイナミクス一覧の取得に失敗しました"
        )


@router.post("/{team_id}/dynamics", response_model=TeamDynamicsResponse)
async def create_team_dynamics(
    team_id: int,
    dynamics_create: TeamDynamicsCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """チームダイナミクスを作成"""
    try:
        dynamics_service = TeamDynamicsService()
        dynamics = await dynamics_service.create_team_dynamics(
            db=db,
            team_id=team_id,
            dynamics_data=dynamics_create,
            created_by=current_user
        )
        
        return dynamics
        
    except Exception as e:
        logger.error("チームダイナミクス作成でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="チームダイナミクスの作成に失敗しました"
        )


@router.get("/{team_id}/dynamics/{dynamics_id}", response_model=TeamDynamicsResponse)
async def get_team_dynamics_detail(
    team_id: int,
    dynamics_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """チームダイナミクスの詳細を取得"""
    try:
        dynamics_service = TeamDynamicsService()
        dynamics = await dynamics_service.get_team_dynamics_detail(
            db=db,
            team_id=team_id,
            dynamics_id=dynamics_id,
            user=current_user
        )
        
        return dynamics
        
    except Exception as e:
        logger.error("チームダイナミクス詳細取得でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="チームダイナミクスの詳細取得に失敗しました"
        )


@router.put("/{team_id}/dynamics/{dynamics_id}", response_model=TeamDynamicsResponse)
async def update_team_dynamics(
    team_id: int,
    dynamics_id: int,
    dynamics_update: TeamDynamicsUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """チームダイナミクスを更新"""
    try:
        dynamics_service = TeamDynamicsService()
        dynamics = await dynamics_service.update_team_dynamics(
            db=db,
            team_id=team_id,
            dynamics_id=dynamics_id,
            dynamics_data=dynamics_update,
            updated_by=current_user
        )
        
        return dynamics
        
    except Exception as e:
        logger.error("チームダイナミクス更新でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="チームダイナミクスの更新に失敗しました"
        )


# ==================== チーム分析・メトリクス ====================

@router.get("/{team_id}/metrics", response_model=TeamMetrics)
async def get_team_metrics(
    team_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    start_date: Optional[str] = Query(None, description="開始日"),
    end_date: Optional[str] = Query(None, description="終了日")
):
    """チームメトリクスを取得"""
    try:
        dynamics_service = TeamDynamicsService()
        metrics = await dynamics_service.get_team_metrics(
            db=db,
            team_id=team_id,
            user=current_user,
            start_date=start_date,
            end_date=end_date
        )
        
        return metrics
        
    except Exception as e:
        logger.error("チームメトリクス取得でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="チームメトリクスの取得に失敗しました"
        )


@router.get("/{team_id}/analytics")
async def get_team_analytics(
    team_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    analysis_type: str = Query("overview", description="分析タイプ")
):
    """チーム分析データを取得"""
    try:
        team_service = TeamService()
        analytics = await team_service.get_team_analytics(
            db=db,
            team_id=team_id,
            user=current_user,
            analysis_type=analysis_type
        )
        
        return analytics
        
    except Exception as e:
        logger.error("チーム分析取得でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="チーム分析の取得に失敗しました"
        )


# ==================== チーム招待・参加管理 ====================

@router.post("/{team_id}/invite")
async def invite_to_team(
    team_id: int,
    email: str = Query(..., description="招待するユーザーのメールアドレス"),
    role: str = Query("member", description="招待するロール"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """チームにユーザーを招待"""
    try:
        team_service = TeamService()
        invitation = await team_service.invite_user_to_team(
            db=db,
            team_id=team_id,
            email=email,
            role=role,
            invited_by=current_user
        )
        
        return {
            "message": "招待が送信されました",
            "invitation_id": invitation.id,
            "email": email
        }
        
    except Exception as e:
        logger.error("チーム招待でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="チーム招待に失敗しました"
        )


@router.post("/{team_id}/join")
async def join_team(
    team_id: int,
    invitation_token: str = Query(..., description="招待トークン"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """チームに参加"""
    try:
        team_service = TeamService()
        member = await team_service.join_team(
            db=db,
            team_id=team_id,
            invitation_token=invitation_token,
            user=current_user
        )
        
        return {
            "message": "チームに参加しました",
            "team_id": team_id,
            "member_id": member.id
        }
        
    except Exception as e:
        logger.error("チーム参加でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="チーム参加に失敗しました"
        )


# ==================== ヘルスチェック ====================

@router.get("/health")
async def health_check():
    """チームサービス ヘルスチェック"""
    return {
        "status": "healthy",
        "service": "unified_team",
        "features": [
            "team_management",
            "member_management",
            "team_dynamics",
            "analytics",
            "invitations"
        ]
    }
