from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.privacy import PrivacyLevel, DataCategory
from app.services.privacy_service import PrivacyService
from app.core.exceptions import PrivacyError, AccessDeniedError

router = APIRouter()
logger = structlog.get_logger()

@router.get("/settings")
async def get_privacy_settings(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """ユーザーのプライバシー設定を取得"""
    try:
        privacy_service = PrivacyService()
        
        settings = await privacy_service.get_privacy_settings(db, current_user)
        
        # 監査ログに記録
        await privacy_service.log_privacy_action(
            db=db,
            user=current_user,
            action="view_privacy_settings",
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None,
            success=True
        )
        
        return {
            "user_id": settings.user_id,
            "default_profile_privacy": settings.default_profile_privacy.value,
            "default_analysis_privacy": settings.default_analysis_privacy.value,
            "default_goals_privacy": settings.default_goals_privacy.value,
            "default_improvement_privacy": settings.default_improvement_privacy.value,
            "auto_delete_after_days": settings.auto_delete_after_days,
            "auto_delete_enabled": settings.auto_delete_enabled,
            "allow_team_sharing": settings.allow_team_sharing,
            "allow_manager_access": settings.allow_manager_access,
            "allow_anonymous_analytics": settings.allow_anonymous_analytics,
            "notify_on_access": settings.notify_on_access,
            "notify_on_breach": settings.notify_on_breach,
            "created_at": settings.created_at,
            "updated_at": settings.updated_at
        }
        
    except PrivacyError as e:
        logger.error("プライバシー設定取得でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error("予期しないエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="プライバシー設定の取得に失敗しました"
        )

@router.put("/settings")
async def update_privacy_settings(
    settings_update: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """プライバシー設定を更新"""
    try:
        privacy_service = PrivacyService()
        
        # プライバシーレベルの文字列をEnumに変換
        processed_update = {}
        for key, value in settings_update.items():
            if key.endswith("_privacy") and isinstance(value, str):
                try:
                    processed_update[key] = PrivacyLevel(value)
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"無効なプライバシーレベル: {value}"
                    )
            else:
                processed_update[key] = value
        
        # 設定を更新
        updated_settings = await privacy_service.update_privacy_settings(
            db, current_user, processed_update
        )
        
        # 監査ログに記録
        await privacy_service.log_privacy_action(
            db=db,
            user=current_user,
            action="update_privacy_settings",
            action_details={"updated_fields": list(settings_update.keys())},
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None,
            success=True
        )
        
        logger.info(
            "プライバシー設定更新完了",
            user_id=current_user.id,
            updated_fields=list(settings_update.keys())
        )
        
        return {
            "message": "プライバシー設定が更新されました",
            "updated_fields": list(settings_update.keys())
        }
        
    except HTTPException:
        raise
    except PrivacyError as e:
        logger.error("プライバシー設定更新でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error("予期しないエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="プライバシー設定の更新に失敗しました"
        )

@router.post("/data/{data_id}/share")
async def share_data(
    data_id: str,
    target_user_id: int,
    permissions: Dict[str, bool],
    expires_at: Optional[datetime] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """データの共有権限を付与"""
    try:
        privacy_service = PrivacyService()
        
        # 対象ユーザーを取得（実際の実装ではユーザー検索が必要）
        # ここでは簡易実装
        target_user = User(id=target_user_id, username="target_user")
        
        # 暗号化データを取得（実際の実装ではdata_idから検索が必要）
        # ここでは簡易実装
        encrypted_data = None
        
        # 権限を付与
        permission = await privacy_service.grant_access_permission(
            db=db,
            owner=current_user,
            target_user=target_user,
            encrypted_data=encrypted_data,
            permissions=permissions,
            expires_at=expires_at
        )
        
        # 監査ログに記録
        await privacy_service.log_privacy_action(
            db=db,
            user=current_user,
            action="share_data",
            data_id=data_id,
            action_details={
                "target_user_id": target_user_id,
                "permissions": permissions,
                "expires_at": expires_at.isoformat() if expires_at else None
            },
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None,
            success=True
        )
        
        logger.info(
            "データ共有権限付与完了",
            user_id=current_user.id,
            target_user_id=target_user_id,
            data_id=data_id
        )
        
        return {
            "message": "データの共有権限が付与されました",
            "permission_id": permission.id,
            "target_user_id": target_user_id
        }
        
    except PrivacyError as e:
        logger.error("データ共有でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error("予期しないエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="データの共有に失敗しました"
        )

@router.delete("/data/{data_id}/share/{target_user_id}")
async def revoke_data_access(
    data_id: str,
    target_user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """データのアクセス権限を削除"""
    try:
        privacy_service = PrivacyService()
        
        # 対象ユーザーを取得（実際の実装ではユーザー検索が必要）
        target_user = User(id=target_user_id, username="target_user")
        
        # 暗号化データを取得（実際の実装ではdata_idから検索が必要）
        encrypted_data = None
        
        # 権限を削除
        success = await privacy_service.revoke_access_permission(
            db=db,
            owner=current_user,
            target_user=target_user,
            encrypted_data=encrypted_data
        )
        
        if success:
            # 監査ログに記録
            await privacy_service.log_privacy_action(
                db=db,
                user=current_user,
                action="revoke_data_access",
                data_id=data_id,
                action_details={"target_user_id": target_user_id},
                ip_address=request.client.host if request else None,
                user_agent=request.headers.get("user-agent") if request else None,
                success=True
            )
            
            logger.info(
                "データアクセス権限削除完了",
                user_id=current_user.id,
                target_user_id=target_user_id,
                data_id=data_id
            )
            
            return {"message": "データのアクセス権限が削除されました"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="削除する権限が見つかりません"
            )
        
    except HTTPException:
        raise
    except PrivacyError as e:
        logger.error("データアクセス権限削除でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error("予期しないエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="データアクセス権限の削除に失敗しました"
        )

@router.get("/audit-logs")
async def get_privacy_audit_logs(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """プライバシー監査ログを取得"""
    try:
        privacy_service = PrivacyService()
        
        # 監査ログに記録
        await privacy_service.log_privacy_action(
            db=db,
            user=current_user,
            action="view_audit_logs",
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None,
            success=True
        )
        
        # 仮の監査ログを返す（実際の実装ではデータベースから取得）
        return {
            "logs": [
                {
                    "id": 1,
                    "action": "view_privacy_settings",
                    "timestamp": datetime.utcnow().isoformat(),
                    "success": True,
                    "ip_address": request.client.host if request else None
                },
                {
                    "id": 2,
                    "action": "share_data",
                    "timestamp": datetime.utcnow().isoformat(),
                    "success": True,
                    "ip_address": request.client.host if request else None
                }
            ],
            "total_count": 2,
            "page": page,
            "page_size": page_size
        }
        
    except Exception as e:
        logger.error("監査ログ取得でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="監査ログの取得に失敗しました"
        )

@router.post("/data/{data_id}/encrypt")
async def encrypt_user_data(
    data_id: str,
    data: Dict[str, Any],
    data_type: str,
    data_category: str,
    privacy_level: str = "private",
    expires_at: Optional[datetime] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """ユーザーデータを暗号化して保存"""
    try:
        privacy_service = PrivacyService()
        
        # データカテゴリとプライバシーレベルをEnumに変換
        try:
            category_enum = DataCategory(data_category)
            level_enum = PrivacyLevel(privacy_level)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"無効な値: {str(e)}"
            )
        
        # データを暗号化
        encrypted_data = await privacy_service.encrypt_data(
            db=db,
            user=current_user,
            data=data,
            data_type=data_type,
            data_category=category_enum,
            privacy_level=level_enum,
            expires_at=expires_at
        )
        
        # 監査ログに記録
        await privacy_service.log_privacy_action(
            db=db,
            user=current_user,
            action="encrypt_data",
            data_id=encrypted_data.data_id,
            action_details={
                "original_data_id": data_id,
                "data_type": data_type,
                "privacy_level": privacy_level
            },
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None,
            success=True
        )
        
        logger.info(
            "データ暗号化完了",
            user_id=current_user.id,
            data_id=encrypted_data.data_id,
            original_data_id=data_id
        )
        
        return {
            "message": "データが暗号化されました",
            "encrypted_data_id": encrypted_data.data_id,
            "data_type": data_type,
            "privacy_level": privacy_level
        }
        
    except HTTPException:
        raise
    except PrivacyError as e:
        logger.error("データ暗号化でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error("予期しないエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="データの暗号化に失敗しました"
        )

@router.get("/data/{data_id}")
async def get_encrypted_data(
    data_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """暗号化されたデータを取得（復号化）"""
    try:
        privacy_service = PrivacyService()
        
        # 暗号化データを検索（実際の実装ではdata_idから検索が必要）
        # ここでは簡易実装
        encrypted_data = None
        
        # データを復号化
        decrypted_data = await privacy_service.decrypt_data(
            db=db,
            user=current_user,
            encrypted_data=encrypted_data,
            requesting_user=current_user
        )
        
        # 監査ログに記録
        await privacy_service.log_privacy_action(
            db=db,
            user=current_user,
            action="access_encrypted_data",
            data_id=data_id,
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None,
            success=True
        )
        
        return {
            "data_id": data_id,
            "decrypted_data": decrypted_data,
            "accessed_at": datetime.utcnow().isoformat()
        }
        
    except AccessDeniedError as e:
        logger.warning("データアクセス拒否", user_id=current_user.id, data_id=data_id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="このデータへのアクセス権限がありません"
        )
    except PrivacyError as e:
        logger.error("データ復号化でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error("予期しないエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="データの取得に失敗しました"
        )
