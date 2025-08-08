from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.core.auth import get_current_user, create_access_token, create_refresh_token, verify_refresh_token
from app.schemas.auth import Token, TokenData, UserLogin, UserRegister, FirebaseAuthRequest, RefreshTokenRequest
from app.services.auth_service import AuthService
from app.services.role_service import RoleService
from app.core.firebase_client import verify_firebase_token

router = APIRouter()
security = HTTPBearer()
logger = structlog.get_logger()


@router.post("/login", response_model=Token)
async def firebase_login(
    auth_data: FirebaseAuthRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Firebase認証によるログイン
    """
    try:
        # Firebaseトークン検証
        decoded = verify_firebase_token(auth_data.id_token)
        firebase_uid = decoded.get("uid")
        email = decoded.get("email")
        if not firebase_uid or not email:
            raise HTTPException(
                status_code=401, 
                detail="Invalid Firebase token",
                headers={"X-Error-Code": "AUTH_001"}
            )

        auth_service = AuthService(db)
        role_service = RoleService(db)
        
        # DBユーザー検索
        user = await auth_service.get_user_by_firebase_uid(firebase_uid)
        if not user:
            # 新規作成
            user = await auth_service.create_user_by_firebase(
                firebase_uid=firebase_uid,
                email=email,
                display_name=auth_data.display_name,
                avatar_url=auth_data.avatar_url
            )
            
            # デフォルトロール（user）を割り当て
            await role_service.assign_role_to_user(
                user_id=user.id,
                role_name="user",
                assigned_by=user.id  # 自己割り当て
            )

        # ログイン時にFirebase Custom Claimsを同期
        await role_service.sync_user_roles_to_firebase(user)

        # アクセストークンとリフレッシュトークンを発行
        access_token = create_access_token(data={"sub": user.email})
        refresh_token = create_refresh_token(data={"sub": user.email})
        
        logger.info(f"User logged in successfully: {email}")
        
        return {
            "access_token": access_token, 
            "refresh_token": refresh_token,
            "token_type": "bearer", 
            "user": user
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Firebase login failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error",
            headers={"X-Error-Code": "AUTH_002"}
        )


@router.post("/register", response_model=Token)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    """ユーザー登録"""
    try:
        auth_service = AuthService(db)
        user = await auth_service.create_user(user_data)

        access_token = create_access_token(data={"sub": user.email})
        logger.info(f"User registered successfully: {user.email}")

        return {"access_token": access_token, "token_type": "bearer", "user": user}
    except ValueError as e:
        logger.warning(f"Registration failed - validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """ユーザーログアウト"""
    try:
        # トークンをブラックリストに追加する処理
        # 実際の実装では、RedisやDBにブラックリストを保存
        token = credentials.credentials
        
        # ユーザーの最終ログアウト時刻を更新
        auth_service = AuthService(db)
        await auth_service.update_user_logout_time(current_user.id)
        
        logger.info(f"User logged out: {current_user.email}")
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/me")
async def get_current_user_info(current_user=Depends(get_current_user)):
    """現在のユーザー情報を取得"""
    return current_user


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """トークンリフレッシュ"""
    try:
        # リフレッシュトークンを検証
        payload = await verify_refresh_token(refresh_data.refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        # ユーザーが存在するか確認
        auth_service = AuthService(db)
        user = await auth_service.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        # 新しいアクセストークンとリフレッシュトークンを発行
        new_access_token = create_access_token(data={"sub": user.email})
        new_refresh_token = create_refresh_token(data={"sub": user.email})
        
        logger.info(f"Token refreshed for user: {user.email}")

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
