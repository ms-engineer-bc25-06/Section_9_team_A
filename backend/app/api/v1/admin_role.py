from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.core.database import get_db_session
from app.models.user import User
from app.schemas.auth import UserResponse
import structlog

logger = structlog.get_logger()

router = APIRouter()


@router.get("/check-admin")
async def check_admin_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    現在のユーザーが管理者かどうかをチェック
    """
    try:
        logger.info("Admin check requested", user_id=current_user.id, email=current_user.email)
        
        # Firebase Custom Claims の admin フラグをチェック
        # これは get_current_user で既にチェック済み
        
        # データベースでも管理者フラグをチェック
        if not current_user.is_admin:
            logger.warning("User is not admin in database", user_id=current_user.id)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="このアカウントは管理者ではありません"
            )
        
        logger.info("Admin check passed", user_id=current_user.id)
        return {
            "status": "success",
            "message": "管理者権限が確認されました",
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "firebase_uid": current_user.firebase_uid,
                "is_admin": current_user.is_admin
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Admin check failed", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="管理者権限の確認中にエラーが発生しました"
        )


@router.post("/bootstrap-admin")
async def bootstrap_admin(
    db: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    初期管理者のブートストラップ（一回限り使用）
    """
    # このエンドポイントは緊急時用です
    # 実装は必要に応じて追加
    return {"message": "Bootstrap endpoint - not implemented"}





