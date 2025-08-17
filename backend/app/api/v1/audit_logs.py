from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.schemas.audit_log import (
    AuditLogResponse,
    AuditLogList,
    AuditLogFilter,
    AuditLogStats,
    SystemAuditLogCreate,
    UserAuditLogCreate,
)
from app.services.audit_log_service import audit_log_service

router = APIRouter()


@router.get("/", response_model=AuditLogList)
async def get_audit_logs(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    action: Optional[str] = Query(None, description="アクションでフィルター"),
    resource_type: Optional[str] = Query(None, description="リソースタイプでフィルター"),
    user_id: Optional[int] = Query(None, description="ユーザーIDでフィルター"),
    page: int = Query(1, ge=1, description="ページ番号"),
    size: int = Query(50, ge=1, le=100, description="ページサイズ"),
):
    """監査ログ一覧を取得"""
    try:
        filter_params = AuditLogFilter(
            action=action,
            resource_type=resource_type,
            user_id=user_id,
            page=page,
            size=size
        )
        result = await audit_log_service.get_audit_logs(db, filter_params, current_user)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"監査ログの取得に失敗しました: {str(e)}")


@router.get("/{audit_log_id}", response_model=AuditLogResponse)
async def get_audit_log(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    audit_log_id: int,
):
    """特定の監査ログを取得"""
    try:
        audit_log = await audit_log_service.get_audit_log(db, audit_log_id, current_user)
        if not audit_log:
            raise HTTPException(status_code=404, detail="監査ログが見つかりません")
        return audit_log
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"監査ログの取得に失敗しました: {str(e)}")


@router.post("/system", response_model=AuditLogResponse)
async def create_system_audit_log(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user = Depends(deps.get_current_superuser),
    audit_log_data: SystemAuditLogCreate,
):
    """システム監査ログを作成（管理者のみ）"""
    try:
        audit_log = await audit_log_service.create_system_log(db, audit_log_data)
        return audit_log
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"システム監査ログの作成に失敗しました: {str(e)}")


@router.post("/user", response_model=AuditLogResponse)
async def create_user_audit_log(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    audit_log_data: UserAuditLogCreate,
):
    """ユーザー監査ログを作成"""
    try:
        # 自分のログのみ作成可能
        if audit_log_data.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="自分のログのみ作成可能です")
        
        audit_log = await audit_log_service.create_user_log(db, audit_log_data)
        return audit_log
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ユーザー監査ログの作成に失敗しました: {str(e)}")


@router.get("/stats/summary", response_model=AuditLogStats)
async def get_audit_log_stats(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """監査ログ統計を取得"""
    try:
        stats = await audit_log_service.get_audit_log_stats(db, current_user)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"監査ログ統計の取得に失敗しました: {str(e)}")


@router.get("/user/{user_id}", response_model=List[AuditLogResponse])
async def get_user_audit_logs(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    user_id: int,
    limit: int = Query(100, ge=1, le=1000, description="取得件数"),
):
    """特定ユーザーの監査ログを取得"""
    try:
        # 自分のログまたは管理者のみアクセス可能
        if user_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="アクセス権限がありません")
        
        audit_logs = await audit_log_service.get_user_audit_logs(db, user_id, limit)
        return audit_logs
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ユーザー監査ログの取得に失敗しました: {str(e)}")


@router.delete("/{audit_log_id}")
async def delete_audit_log(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user = Depends(deps.get_current_superuser),
    audit_log_id: int,
):
    """監査ログを削除（管理者のみ）"""
    try:
        success = await audit_log_service.delete_audit_log(db, audit_log_id)
        if not success:
            raise HTTPException(status_code=404, detail="監査ログが見つかりません")
        return {"message": "監査ログが削除されました"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"監査ログの削除に失敗しました: {str(e)}")
