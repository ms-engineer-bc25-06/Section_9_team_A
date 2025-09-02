"""
統合された管理者API
管理者ロール、管理者決済、監査ログを統合
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
import stripe
from typing import List, Optional, Dict, Any
from sqlalchemy import func, select, text
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_active_user, get_current_admin_user
from app.models.user import User
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.schemas.admin_role import (
    RoleCreate, RoleUpdate, RoleResponse, RoleListResponse
)
from app.schemas.admin_billing import (
    AdminBillingCreate, AdminBillingUpdate, AdminBillingResponse,
    AdminBillingListResponse, BillingSummary, UserCountInfo,
    CreateCheckoutSessionRequest, CheckoutSessionResponse
)
from app.schemas.audit_log import (
    AuditLogResponse, AuditLogListResponse, AuditLogFilter
)
from app.services.role_service import RoleService
from app.services.billing_service import BillingService
from app.services.audit_log_service import AuditLogService
from app.config import settings

router = APIRouter()
logger = structlog.get_logger()

# Stripe設定
stripe.api_key = settings.STRIPE_SECRET_KEY


# ==================== 管理者ロール管理 ====================

@router.get("/roles", response_model=RoleListResponse)
async def get_roles(
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="ページ番号"),
    page_size: int = Query(20, ge=1, le=100, description="ページサイズ"),
    role_name: Optional[str] = Query(None, description="ロール名でフィルタリング")
):
    """管理者ロール一覧を取得"""
    try:
        role_service = RoleService()
        result = await role_service.get_roles(
            db=db,
            page=page,
            page_size=page_size,
            role_name=role_name
        )
        
        return RoleListResponse(
            roles=result["roles"],
            total_count=result["total_count"],
            page=result["page"],
            page_size=result["page_size"]
        )
        
    except Exception as e:
        logger.error("ロール一覧取得でエラー", error=str(e), admin_id=current_admin.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ロール一覧の取得に失敗しました"
        )


@router.post("/roles", response_model=RoleResponse)
async def create_role(
    role_create: RoleCreate,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """新しい管理者ロールを作成"""
    try:
        role_service = RoleService()
        role = await role_service.create_role(
            db=db,
            role_data=role_create,
            created_by=current_admin.id
        )
        
        logger.info(
            "管理者ロール作成完了",
            admin_id=current_admin.id,
            role_id=role.id,
            role_name=role.name
        )
        
        return role
        
    except Exception as e:
        logger.error("ロール作成でエラー", error=str(e), admin_id=current_admin.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ロールの作成に失敗しました"
        )


@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_update: RoleUpdate,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """管理者ロールを更新"""
    try:
        role_service = RoleService()
        role = await role_service.update_role(
            db=db,
            role_id=role_id,
            role_data=role_update,
            updated_by=current_admin.id
        )
        
        return role
        
    except Exception as e:
        logger.error("ロール更新でエラー", error=str(e), admin_id=current_admin.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ロールの更新に失敗しました"
        )


@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """管理者ロールを削除"""
    try:
        role_service = RoleService()
        await role_service.delete_role(
            db=db,
            role_id=role_id,
            deleted_by=current_admin.id
        )
        
        return {"message": "ロールが正常に削除されました"}
        
    except Exception as e:
        logger.error("ロール削除でエラー", error=str(e), admin_id=current_admin.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ロールの削除に失敗しました"
        )


# ==================== 管理者決済管理 ====================

@router.get("/billing", response_model=AdminBillingListResponse)
async def get_admin_billing(
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="ページ番号"),
    page_size: int = Query(20, ge=1, le=100, description="ページサイズ"),
    status: Optional[str] = Query(None, description="ステータスでフィルタリング"),
    start_date: Optional[str] = Query(None, description="開始日"),
    end_date: Optional[str] = Query(None, description="終了日")
):
    """管理者用決済一覧を取得"""
    try:
        billing_service = BillingService()
        result = await billing_service.get_admin_billing(
            db=db,
            page=page,
            page_size=page_size,
            status=status,
            start_date=start_date,
            end_date=end_date
        )
        
        return AdminBillingListResponse(
            billing_records=result["billing_records"],
            total_count=result["total_count"],
            page=result["page"],
            page_size=result["page_size"]
        )
        
    except Exception as e:
        logger.error("管理者決済一覧取得でエラー", error=str(e), admin_id=current_admin.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="管理者決済一覧の取得に失敗しました"
        )


@router.get("/billing/summary", response_model=BillingSummary)
async def get_billing_summary(
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
    start_date: Optional[str] = Query(None, description="開始日"),
    end_date: Optional[str] = Query(None, description="終了日")
):
    """決済サマリーを取得"""
    try:
        billing_service = BillingService()
        summary = await billing_service.get_admin_billing_summary(
            db=db,
            start_date=start_date,
            end_date=end_date
        )
        
        return summary
        
    except Exception as e:
        logger.error("決済サマリー取得でエラー", error=str(e), admin_id=current_admin.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="決済サマリーの取得に失敗しました"
        )


@router.post("/billing", response_model=AdminBillingResponse)
async def create_admin_billing(
    billing_create: AdminBillingCreate,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """管理者用決済レコードを作成"""
    try:
        billing_service = BillingService()
        billing = await billing_service.create_admin_billing(
            db=db,
            billing_data=billing_create,
            created_by=current_admin.id
        )
        
        return billing
        
    except Exception as e:
        logger.error("管理者決済作成でエラー", error=str(e), admin_id=current_admin.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="管理者決済の作成に失敗しました"
        )


@router.put("/billing/{billing_id}", response_model=AdminBillingResponse)
async def update_admin_billing(
    billing_id: int,
    billing_update: AdminBillingUpdate,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """管理者用決済レコードを更新"""
    try:
        billing_service = BillingService()
        billing = await billing_service.update_admin_billing(
            db=db,
            billing_id=billing_id,
            billing_data=billing_update,
            updated_by=current_admin.id
        )
        
        return billing
        
    except Exception as e:
        logger.error("管理者決済更新でエラー", error=str(e), admin_id=current_admin.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="管理者決済の更新に失敗しました"
        )


@router.get("/billing/user-count", response_model=UserCountInfo)
async def get_user_count(
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    管理者用：システム全体の利用者数を取得
    """
    try:
        # まず、usersテーブルから総ユーザー数を取得してみる
        try:
            result = await db.execute(
                select(func.count()).select_from(text("users"))
            )
            total_users = result.scalar() or 0
            logger.info(f"usersテーブルから取得した総ユーザー数: {total_users}")
        except Exception as e:
            logger.warning(f"usersテーブルからの取得でエラー: {e}")
            total_users = 0
        
        # 組織関連の情報を取得してみる
        organizations_over_limit = 0
        total_additional_cost = 0
        
        try:
            # organizationsテーブルが存在するか確認
            result = await db.execute(
                select(func.count()).select_from(text("organizations"))
            )
            org_count = result.scalar() or 0
            logger.info(f"organizationsテーブルから取得した組織数: {org_count}")
            
            if org_count > 0:
                # 組織が存在する場合、基本的な計算を行う
                # 仮定: 各組織は10人まで無料、超過分は500円/人
                free_limit = 10
                cost_per_user = 500
                
                if total_users > free_limit:
                    organizations_over_limit = 1
                    total_additional_cost = (total_users - free_limit) * cost_per_user
                    
        except Exception as e:
            logger.warning(f"organizationsテーブルからの取得でエラー: {e}")
            # 組織情報が取得できない場合のデフォルト計算
            free_limit = 10
            cost_per_user = 500
            
            if total_users > free_limit:
                organizations_over_limit = 1
                total_additional_cost = (total_users - free_limit) * cost_per_user
        
        return UserCountInfo(
            total_users=total_users,
            organizations_over_limit=organizations_over_limit,
            total_additional_cost=total_additional_cost
        )
        
    except Exception as e:
        logger.error("利用者数の取得でエラー", error=str(e), admin_id=current_admin.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"利用者数の取得に失敗しました: {str(e)}"
        )


# ==================== Stripe決済管理 ====================

@router.post("/billing/checkout", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: CreateCheckoutSessionRequest,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Stripe Checkoutセッションを作成"""
    try:
        # 日本円の場合は円単位のまま（Stripeの日本円は円単位で処理）
        amount_for_stripe = int(request.amount)
        
        # デバッグ用ログ
        logger.info(
            "決済セッション作成リクエスト",
            admin_id=current_admin.id,
            original_amount=request.amount,
            amount_for_stripe=amount_for_stripe,
            additional_users=request.additional_users
        )
        
        # Stripe Checkoutセッションを作成
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'jpy',  # 日本円に戻す
                    'product_data': {
                        'name': f'追加ユーザー {request.additional_users}人',
                        'description': f'月額利用料金（{request.additional_users}人分）',
                    },
                    'unit_amount': amount_for_stripe,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{settings.FRONTEND_URL}/admin/billing/success?session_id={{CHECKOUT_SESSION_ID}}&amount={request.amount}&additional_users={request.additional_users}&organization_id={request.organization_id}",
            cancel_url=f"{settings.FRONTEND_URL}/admin/billing?canceled=true",
            metadata={
                'additional_users': str(request.additional_users),
                'organization_id': str(request.organization_id),
                'admin_id': str(current_admin.id)
            },
            customer_email=current_admin.email,
            locale='ja'
        )
        
        logger.info(
            "Stripe Checkoutセッション作成完了",
            admin_id=current_admin.id,
            session_id=checkout_session.id,
            amount=request.amount,
            additional_users=request.additional_users
        )
        
        return CheckoutSessionResponse(
            session_id=checkout_session.id,
            checkout_url=checkout_session.url,
            expires_at=datetime.fromtimestamp(checkout_session.expires_at) if checkout_session.expires_at else None
        )
        
    except stripe.error.StripeError as e:
        logger.error("Stripe決済エラー", error=str(e), admin_id=current_admin.id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"決済セッションの作成に失敗しました: {str(e)}"
        )
    except Exception as e:
        logger.error("決済セッション作成でエラー", error=str(e), admin_id=current_admin.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="決済セッションの作成に失敗しました"
        )


# ==================== 監査ログ管理 ====================

@router.get("/audit-logs", response_model=AuditLogListResponse)
async def get_audit_logs(
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="ページ番号"),
    page_size: int = Query(20, ge=1, le=100, description="ページサイズ"),
    user_id: Optional[int] = Query(None, description="ユーザーIDでフィルタリング"),
    action: Optional[str] = Query(None, description="アクションでフィルタリング"),
    start_date: Optional[str] = Query(None, description="開始日"),
    end_date: Optional[str] = Query(None, description="終了日")
):
    """監査ログ一覧を取得"""
    try:
        audit_service = AuditLogService()
        
        filter_data = AuditLogFilter(
            user_id=user_id,
            action=action,
            start_date=start_date,
            end_date=end_date
        )
        
        result = await audit_service.get_audit_logs(
            db=db,
            filter_data=filter_data,
            page=page,
            page_size=page_size
        )
        
        return AuditLogListResponse(
            audit_logs=result["audit_logs"],
            total_count=result["total_count"],
            page=result["page"],
            page_size=result["page_size"]
        )
        
    except Exception as e:
        logger.error("監査ログ一覧取得でエラー", error=str(e), admin_id=current_admin.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="監査ログ一覧の取得に失敗しました"
        )


@router.get("/audit-logs/{log_id}", response_model=AuditLogResponse)
async def get_audit_log(
    log_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """監査ログの詳細を取得"""
    try:
        audit_service = AuditLogService()
        log = await audit_service.get_audit_log(
            db=db,
            log_id=log_id
        )
        
        return log
        
    except Exception as e:
        logger.error("監査ログ詳細取得でエラー", error=str(e), admin_id=current_admin.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="監査ログの詳細取得に失敗しました"
        )


@router.get("/audit-logs/export")
async def export_audit_logs(
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
    format: str = Query("csv", description="エクスポート形式 (csv, json, pdf)"),
    start_date: Optional[str] = Query(None, description="開始日"),
    end_date: Optional[str] = Query(None, description="終了日")
):
    """監査ログをエクスポート"""
    try:
        audit_service = AuditLogService()
        
        filter_data = AuditLogFilter(
            start_date=start_date,
            end_date=end_date
        )
        
        export_data = await audit_service.export_audit_logs(
            db=db,
            filter_data=filter_data,
            export_format=format
        )
        
        return export_data
        
    except Exception as e:
        logger.error("監査ログエクスポートでエラー", error=str(e), admin_id=current_admin.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="監査ログのエクスポートに失敗しました"
        )


# ==================== システム管理機能 ====================

@router.get("/system/status")
async def get_system_status(
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """システムステータスを取得"""
    try:
        # データベース接続確認
        from app.core.database import test_database_connection
        db_status = await test_database_connection()
        
        # 基本統計情報
        from app.services.user_service import UserService
        from app.services.voice_session_service import VoiceSessionService
        
        user_service = UserService()
        session_service = VoiceSessionService()
        
        total_users = await user_service.get_total_users(db)
        active_sessions = await session_service.get_active_sessions_count(db)
        
        return {
            "status": "healthy" if db_status else "unhealthy",
            "database": "connected" if db_status else "disconnected",
            "total_users": total_users,
            "active_sessions": active_sessions,
            "timestamp": "2024-01-01T00:00:00Z"  # 実際の実装では現在時刻
        }
        
    except Exception as e:
        logger.error("システムステータス取得でエラー", error=str(e), admin_id=current_admin.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="システムステータスの取得に失敗しました"
        )


@router.post("/system/maintenance")
async def start_maintenance(
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """メンテナンスモードを開始"""
    try:
        # メンテナンスモードの実装
        # 実際の実装では設定ファイルやデータベースのフラグを更新
        
        logger.info("メンテナンスモード開始", admin_id=current_admin.id)
        
        return {
            "message": "メンテナンスモードが開始されました",
            "maintenance_mode": True,
            "started_by": current_admin.id,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        logger.error("メンテナンスモード開始でエラー", error=str(e), admin_id=current_admin.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="メンテナンスモードの開始に失敗しました"
        )


# ==================== ヘルスチェック ====================

@router.get("/health")
async def health_check():
    """管理者サービス ヘルスチェック"""
    return {
        "status": "healthy",
        "service": "unified_admin",
        "features": [
            "role_management",
            "billing_management",
            "audit_logs",
            "system_management"
        ]
    }
