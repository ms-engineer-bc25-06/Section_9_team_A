from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.api.deps import get_current_admin_user_db, get_current_admin_user, get_current_user
from app.core.firebase_client import set_admin_claim, get_user_claims, is_admin_user
from app.models.user import User
from app.schemas.auth import UserResponse
from app.services.role_service import RoleService

router = APIRouter()
logger = structlog.get_logger()


@router.get("/check-admin")
async def check_admin_status(current_user: User = Depends(get_current_user)):
    """現在のユーザーの管理者権限をチェック"""
    try:
        # Firebase Custom Claimsをチェック
        is_firebase_admin = is_admin_user(current_user.firebase_uid)
        
        # DBの管理者フラグもチェック
        is_db_admin = current_user.is_admin
        
        # どちらかが管理者の場合は許可
        if is_firebase_admin or is_db_admin:
            return {
                "is_admin": True,
                "firebase_admin": is_firebase_admin,
                "db_admin": is_db_admin,
                "user_email": current_user.email
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="管理者権限がありません"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="管理者権限の確認に失敗しました"
        )


@router.get("/admin-only")
async def admin_only_endpoint(current_user: User = Depends(get_current_admin_user_db)):
    """管理者専用エンドポイント（DB管理）"""
    return {"message": "管理者専用エンドポイント", "user": current_user.email}


@router.get("/admin-only-firebase")
async def admin_only_firebase_endpoint(current_user: User = Depends(get_current_admin_user)):
    """管理者専用エンドポイント（Firebase Custom Claims管理）"""
    return {"message": "Firebase管理者専用エンドポイント", "user": current_user.email}


@router.post("/set-admin/{firebase_uid}")
async def set_admin_user(
    firebase_uid: str,
    is_admin: bool = True,
    current_admin: User = Depends(get_current_admin_user_db)
):
    """Firebase Custom Claimsで管理者権限を設定"""
    try:
        success = set_admin_claim(firebase_uid, is_admin)
        if success:
            return {
                "message": f"管理者権限を{'設定' if is_admin else '解除'}しました",
                "firebase_uid": firebase_uid,
                "is_admin": is_admin
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="管理者権限の設定に失敗しました"
            )
    except Exception as e:
        logger.error(f"Admin claim setting failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="管理者権限の設定に失敗しました"
        )


@router.get("/admin-status/{firebase_uid}")
async def get_admin_status(
    firebase_uid: str,
    current_admin: User = Depends(get_current_admin_user_db)
):
    """ユーザーの管理者権限を確認"""
    try:
        claims = get_user_claims(firebase_uid)
        is_admin = claims.get("admin", False)
        
        return {
            "firebase_uid": firebase_uid,
            "is_admin": is_admin,
            "claims": claims
        }
    except Exception as e:
        logger.error(f"Admin status check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="管理者権限の確認に失敗しました"
        )


@router.get("/admin-users")
async def list_admin_users(current_admin: User = Depends(get_current_admin_user_db)):
    """管理者ユーザー一覧を取得"""
    try:
        from sqlalchemy import select
        
        async for db in get_db():
            try:
                # DBの管理者ユーザーを取得
                result = await db.execute(select(User).where(User.is_admin == True))
                db_admin_users = result.scalars().all()
                
                admin_users = []
                for user in db_admin_users:
                    # Firebase Custom Claimsも確認
                    firebase_admin = is_admin_user(user.firebase_uid)
                    claims = get_user_claims(user.firebase_uid)
                    
                    admin_users.append({
                        "id": user.id,
                        "email": user.email,
                        "firebase_uid": user.firebase_uid,
                        "display_name": user.full_name or user.username,
                        "db_admin": user.is_admin,
                        "firebase_admin": firebase_admin,
                        "claims": claims
                    })
                
                return {
                    "admin_users": admin_users,
                    "total": len(admin_users)
                }
                
            except Exception as e:
                logger.error(f"Failed to get admin users: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="管理者ユーザーの取得に失敗しました"
                )
            finally:
                await db.close()
                
    except Exception as e:
        logger.error(f"Admin users list failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="管理者ユーザー一覧の取得に失敗しました"
        )


# 新しいロール管理API
@router.post("/assign-role/{user_id}")
async def assign_role(
    user_id: int,
    role_name: str,
    expires_at: Optional[datetime] = None,
    current_admin: User = Depends(get_current_admin_user_db),
    db: AsyncSession = Depends(get_db)
):
    """ユーザーにロールを割り当て"""
    try:
        role_service = RoleService(db)
        success = await role_service.assign_role_to_user(
            user_id=user_id,
            role_name=role_name,
            assigned_by=current_admin.id,
            expires_at=expires_at
        )
        
        if success:
            # ユーザーを取得してFirebase Custom Claimsを同期
            from app.services.auth_service import AuthService
            auth_service = AuthService(db)
            user = await auth_service.get_user_by_id(user_id)
            if user:
                await role_service.sync_user_roles_to_firebase(user)
            
            return {
                "message": f"ロール '{role_name}' をユーザーに割り当てました",
                "user_id": user_id,
                "role_name": role_name
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ロールの割り当てに失敗しました"
            )
    except Exception as e:
        logger.error(f"Role assignment failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ロールの割り当てに失敗しました"
        )


@router.delete("/remove-role/{user_id}")
async def remove_role(
    user_id: int,
    role_name: str,
    current_admin: User = Depends(get_current_admin_user_db),
    db: AsyncSession = Depends(get_db)
):
    """ユーザーからロールを削除"""
    try:
        role_service = RoleService(db)
        success = await role_service.remove_role_from_user(
            user_id=user_id,
            role_name=role_name
        )
        
        if success:
            # ユーザーを取得してFirebase Custom Claimsを同期
            from app.services.auth_service import AuthService
            auth_service = AuthService(db)
            user = await auth_service.get_user_by_id(user_id)
            if user:
                await role_service.sync_user_roles_to_firebase(user)
            
            return {
                "message": f"ロール '{role_name}' をユーザーから削除しました",
                "user_id": user_id,
                "role_name": role_name
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ロールの削除に失敗しました"
            )
    except Exception as e:
        logger.error(f"Role removal failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ロールの削除に失敗しました"
        )


@router.get("/user-roles/{user_id}")
async def get_user_roles(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user_db),
    db: AsyncSession = Depends(get_db)
):
    """ユーザーのロール一覧を取得"""
    try:
        role_service = RoleService(db)
        roles = await role_service.get_user_roles(user_id)
        
        return {
            "user_id": user_id,
            "roles": roles
        }
    except Exception as e:
        logger.error(f"Failed to get user roles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ユーザーロールの取得に失敗しました"
        )


@router.post("/sync-user-roles/{user_id}")
async def sync_user_roles(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user_db),
    db: AsyncSession = Depends(get_db)
):
    """ユーザーのロールをFirebase Custom Claimsに同期"""
    try:
        from app.services.auth_service import AuthService
        auth_service = AuthService(db)
        role_service = RoleService(db)
        
        user = await auth_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ユーザーが見つかりません"
            )
        
        success = await role_service.sync_user_roles_to_firebase(user)
        
        if success:
            return {
                "message": "ユーザーロールをFirebase Custom Claimsに同期しました",
                "user_id": user_id
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Firebase Custom Claimsの同期に失敗しました"
            )
    except Exception as e:
        logger.error(f"Role sync failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ロールの同期に失敗しました"
        )
