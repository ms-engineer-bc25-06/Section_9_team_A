from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.core.auth import get_current_user, create_access_token
from app.schemas.auth import Token, TokenData, UserLogin, UserRegister, FirebaseAuthRequest, UserResponse
from app.services.auth_service import AuthService

router = APIRouter()
security = HTTPBearer()
logger = structlog.get_logger()


@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """ユーザーログイン（従来のメール/パスワード認証）"""
    try:
        auth_service = AuthService(db)
        user = await auth_service.authenticate_user(
            email=user_credentials.email, password=user_credentials.password
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_access_token(data={"sub": user.email})
        logger.info(f"User logged in successfully: {user.email}")

        return {"access_token": access_token, "token_type": "bearer", "user": user}
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/firebase-login")
async def firebase_login(
    request: FirebaseAuthRequest,
    db: AsyncSession = Depends(get_db)
):
    """Firebase認証によるログイン"""
    try:
        from app.integrations.firebase_client import get_firebase_client
        
        # Firebaseトークンを検証
        firebase_client = get_firebase_client()
        decoded_token = firebase_client.verify_id_token(request.id_token)
        
        if not decoded_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Firebase token"
            )
        
        # ユーザー情報を取得
        uid = decoded_token.get("uid")
        email = decoded_token.get("email")
        
        if not uid or not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token data"
            )
        
        # データベースでユーザーを検索または作成
        auth_service = AuthService(db)
        user = await auth_service.get_or_create_firebase_user(
            firebase_uid=uid,
            email=email,
            display_name=request.display_name or email
        )
        
        # アクセストークンを作成
        access_token = create_access_token(data={"sub": user.email, "uid": uid})
        
        logger.info(f"Firebase user logged in successfully: {email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "firebase_uid": user.firebase_uid,
                "is_admin": user.is_admin
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Firebase login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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
):
    """ユーザーログアウト"""
    try:
        # トークンをブラックリストに追加する処理をここに実装
        logger.info(f"User logged out: {current_user.email}")
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user=Depends(get_current_user)):
    """現在のユーザー情報を取得"""
    return current_user


@router.post("/refresh")
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user=Depends(get_current_user),
):
    """トークンリフレッシュ"""
    try:
        new_access_token = create_access_token(data={"sub": current_user.email})
        logger.info(f"Token refreshed for user: {current_user.email}")

        return {"access_token": new_access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
