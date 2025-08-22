from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from typing import List, Optional, Dict, Any

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.schemas.feedback_approval import (
    ApprovalRequest, FeedbackApprovalUpdate, UserConfirmationRequest,
    StagedPublicationRequest, FeedbackApprovalStats,
    FeedbackApprovalListResponse, FeedbackApprovalResponse
)
from app.services.feedback_approval_service import feedback_approval_service
from app.core.exceptions import (
    NotFoundException, PermissionException, ValidationException,
    BusinessLogicException
)

router = APIRouter()
logger = structlog.get_logger()


@router.post("/", response_model=FeedbackApprovalResponse)
async def create_approval_request(
    approval_data: ApprovalRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """承認リクエストを作成"""
    try:
        approval = await feedback_approval_service.create_approval_request(
            db, current_user, approval_data
        )
        
        # レスポンス用のデータを構築
        response_data = {
            "id": approval.id,
            "analysis_id": approval.analysis_id,
            "requester_id": approval.requester_id,
            "reviewer_id": approval.reviewer_id,
            "approval_status": approval.approval_status,
            "visibility_level": approval.visibility_level,
            "request_reason": approval.request_reason,
            "is_staged_publication": approval.is_staged_publication,
            "publication_stages": approval.publication_stages,
            "current_stage": approval.current_stage,
            "requires_confirmation": approval.requires_confirmation,
            "is_confirmed": approval.is_confirmed,
            "confirmation_date": approval.confirmation_date,
            "requested_at": approval.requested_at,
            "reviewed_at": approval.reviewed_at,
            "published_at": approval.published_at
        }
        
        return FeedbackApprovalResponse(**response_data)
        
    except (NotFoundException, PermissionException, ValidationException, BusinessLogicException) as e:
        logger.error(f"承認リクエスト作成でエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"承認リクエスト作成で予期しないエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="承認リクエストの作成に失敗しました"
        )


@router.get("/my", response_model=FeedbackApprovalListResponse)
async def get_my_approvals(
    page: int = Query(1, ge=1, description="ページ番号"),
    page_size: int = Query(20, ge=1, le=100, description="ページサイズ"),
    analysis_id: Optional[int] = Query(None, description="分析IDでフィルタリング"),
    approval_status: Optional[str] = Query(None, description="承認ステータスでフィルタリング"),
    visibility_level: Optional[str] = Query(None, description="可視性レベルでフィルタリング"),
    is_confirmed: Optional[bool] = Query(None, description="本人確認済みでフィルタリング"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """自分の承認リクエスト一覧を取得"""
    try:
        # フィルターの構築
        filters = {}
        if analysis_id:
            filters["analysis_id"] = analysis_id
        if approval_status:
            filters["approval_status"] = approval_status
        if visibility_level:
            filters["visibility_level"] = visibility_level
        if is_confirmed is not None:
            filters["is_confirmed"] = is_confirmed
        
        approvals, total_count = await feedback_approval_service.get_user_approvals(
            db, current_user, page, page_size, filters
        )
        
        # レスポンス用のデータを構築
        approval_responses = []
        for approval in approvals:
            response_data = {
                "id": approval.id,
                "analysis_id": approval.analysis_id,
                "requester_id": approval.requester_id,
                "reviewer_id": approval.reviewer_id,
                "approval_status": approval.approval_status,
                "visibility_level": approval.visibility_level,
                "request_reason": approval.request_reason,
                "is_staged_publication": approval.is_staged_publication,
                "publication_stages": approval.publication_stages,
                "current_stage": approval.current_stage,
                "requires_confirmation": approval.requires_confirmation,
                "is_confirmed": approval.is_confirmed,
                "confirmation_date": approval.confirmation_date,
                "requested_at": approval.requested_at,
                "reviewed_at": approval.reviewed_at,
                "published_at": approval.published_at,
                "requester_name": approval.requester.full_name if approval.requester else None,
                "reviewer_name": approval.reviewer.full_name if approval.reviewer else None,
                "analysis_title": approval.analysis.title if approval.analysis else None
            }
            approval_responses.append(FeedbackApprovalResponse(**response_data))
        
        return FeedbackApprovalListResponse(
            approvals=approval_responses,
            total_count=total_count,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"承認リクエスト一覧取得でエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="承認リクエスト一覧の取得に失敗しました"
        )


@router.get("/pending", response_model=FeedbackApprovalListResponse)
async def get_pending_approvals(
    page: int = Query(1, ge=1, description="ページ番号"),
    page_size: int = Query(20, ge=1, le=100, description="ページサイズ"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """レビュー待ちの承認リクエスト一覧を取得（レビュアー用）"""
    try:
        approvals, total_count = await feedback_approval_service.get_pending_approvals(
            db, current_user, page, page_size
        )
        
        # レスポンス用のデータを構築
        approval_responses = []
        for approval in approvals:
            response_data = {
                "id": approval.id,
                "analysis_id": approval.analysis_id,
                "requester_id": approval.requester_id,
                "reviewer_id": approval.reviewer_id,
                "approval_status": approval.approval_status,
                "visibility_level": approval.visibility_level,
                "request_reason": approval.request_reason,
                "is_staged_publication": approval.is_staged_publication,
                "publication_stages": approval.publication_stages,
                "current_stage": approval.current_stage,
                "requires_confirmation": approval.requires_confirmation,
                "is_confirmed": approval.is_confirmed,
                "confirmation_date": approval.confirmation_date,
                "requested_at": approval.requested_at,
                "reviewed_at": approval.reviewed_at,
                "published_at": approval.published_at,
                "requester_name": approval.requester.full_name if approval.requester else None,
                "reviewer_name": approval.reviewer.full_name if approval.reviewer else None,
                "analysis_title": approval.analysis.title if approval.analysis else None
            }
            approval_responses.append(FeedbackApprovalResponse(**response_data))
        
        return FeedbackApprovalListResponse(
            approvals=approval_responses,
            total_count=total_count,
            page=page,
            page_size=page_size
        )
        
    except PermissionException as e:
        logger.error(f"レビュー待ち承認リクエスト取得で権限エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"レビュー待ち承認リクエスト取得でエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="レビュー待ち承認リクエスト一覧の取得に失敗しました"
        )


@router.put("/{approval_id}/review", response_model=FeedbackApprovalResponse)
async def review_approval(
    approval_id: int,
    review_data: FeedbackApprovalUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """承認リクエストをレビュー"""
    try:
        approval = await feedback_approval_service.review_approval(
            db, current_user, approval_id, review_data
        )
        
        # レスポンス用のデータを構築
        response_data = {
            "id": approval.id,
            "analysis_id": approval.analysis_id,
            "requester_id": approval.requester_id,
            "reviewer_id": approval.reviewer_id,
            "approval_status": approval.approval_status,
            "visibility_level": approval.visibility_level,
            "request_reason": approval.request_reason,
            "is_staged_publication": approval.is_staged_publication,
            "publication_stages": approval.publication_stages,
            "current_stage": approval.current_stage,
            "requires_confirmation": approval.requires_confirmation,
            "is_confirmed": approval.is_confirmed,
            "confirmation_date": approval.confirmation_date,
            "requested_at": approval.requested_at,
            "reviewed_at": approval.reviewed_at,
            "published_at": approval.published_at
        }
        
        return FeedbackApprovalResponse(**response_data)
        
    except (NotFoundException, PermissionException, ValidationException) as e:
        logger.error(f"承認リクエストレビューでエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"承認リクエストレビューで予期しないエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="承認リクエストのレビューに失敗しました"
        )


@router.post("/{approval_id}/confirm", response_model=FeedbackApprovalResponse)
async def confirm_approval(
    approval_id: int,
    confirmation_data: UserConfirmationRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """本人確認を実行"""
    try:
        # approval_idを設定
        confirmation_data.approval_id = approval_id
        
        approval = await feedback_approval_service.confirm_by_user(
            db, current_user, confirmation_data
        )
        
        if not approval:
            # 確認を拒否した場合
            return {"message": "承認リクエストが削除されました"}
        
        # レスポンス用のデータを構築
        response_data = {
            "id": approval.id,
            "analysis_id": approval.analysis_id,
            "requester_id": approval.requester_id,
            "reviewer_id": approval.reviewer_id,
            "approval_status": approval.approval_status,
            "visibility_level": approval.visibility_level,
            "request_reason": approval.request_reason,
            "is_staged_publication": approval.is_staged_publication,
            "publication_stages": approval.publication_stages,
            "current_stage": approval.current_stage,
            "requires_confirmation": approval.requires_confirmation,
            "is_confirmed": approval.is_confirmed,
            "confirmation_date": approval.confirmation_date,
            "requested_at": approval.requested_at,
            "reviewed_at": approval.reviewed_at,
            "published_at": approval.published_at
        }
        
        return FeedbackApprovalResponse(**response_data)
        
    except (NotFoundException, PermissionException) as e:
        logger.error(f"本人確認でエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"本人確認で予期しないエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="本人確認に失敗しました"
        )


@router.post("/{approval_id}/publish")
async def publish_analysis(
    approval_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """承認済みの分析結果を公開"""
    try:
        success = await feedback_approval_service.publish_approved_analysis(
            db, approval_id
        )
        
        if success:
            return {"message": "分析結果が公開されました"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="公開条件を満たしていません"
            )
        
    except (NotFoundException, BusinessLogicException) as e:
        logger.error(f"分析結果公開でエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"分析結果公開で予期しないエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="分析結果の公開に失敗しました"
        )


@router.post("/{approval_id}/advance-stage")
async def advance_publication_stage(
    approval_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """段階的公開の次の段階に進む"""
    try:
        success = await feedback_approval_service.advance_publication_stage(
            db, approval_id
        )
        
        if success:
            return {"message": "次の公開段階に進行しました"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="段階的公開の進行に失敗しました"
            )
        
    except (NotFoundException, BusinessLogicException) as e:
        logger.error(f"段階的公開進行でエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"段階的公開進行で予期しないエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="段階的公開の進行に失敗しました"
        )


@router.get("/stats", response_model=FeedbackApprovalStats)
async def get_approval_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """承認統計を取得"""
    try:
        stats = await feedback_approval_service.get_approval_stats(db, current_user)
        return stats
        
    except Exception as e:
        logger.error(f"承認統計取得でエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="承認統計の取得に失敗しました"
        )


@router.delete("/{approval_id}")
async def delete_approval(
    approval_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """承認リクエストを削除（申請者のみ）"""
    try:
        # 承認リクエストの存在確認と権限チェック
        approval = await feedback_approval_service._get_approval(db, approval_id)
        
        if approval.requester_id != current_user.id:
            raise PermissionException("申請者本人のみが削除できます")
        
        # 削除
        await db.delete(approval)
        await db.commit()
        
        return {"message": "承認リクエストが削除されました"}
        
    except (NotFoundException, PermissionException) as e:
        logger.error(f"承認リクエスト削除でエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"承認リクエスト削除で予期しないエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="承認リクエストの削除に失敗しました"
        )
