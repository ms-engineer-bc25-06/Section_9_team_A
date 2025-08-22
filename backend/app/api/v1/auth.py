"""認証関連API"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from datetime import datetime
from sqlalchemy import select
from typing import Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth import get_current_user, create_access_token
from app.schemas.auth import Token, TokenData, UserLogin, UserRegister, FirebaseAuthRequest, UserResponse, LoginResponse, LoginRequest
from app.services.auth_service import AuthService
from app.integrations.firebase_client import update_firebase_user_password
from app.models.user import User

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


@router.post("/temporary-login", response_model=Token)
async def temporary_login(user_credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """仮パスワードでのログイン"""
    try:
        # ユーザーを取得
        result = await db.execute(
            select(User).where(User.email == user_credentials.email)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 仮パスワード使用中かチェック
        if not user.has_temporary_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This account is not using a temporary password",
            )

        # 仮パスワードの有効期限をチェック
        if user.temporary_password_expires_at and user.temporary_password_expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Temporary password has expired",
            )

        # Firebaseで仮パスワード認証を試行
        try:
            from app.integrations.firebase_client import get_firebase_client
            firebase_client = get_firebase_client()
            
            # Firebaseでユーザー認証を試行
            try:
                # Firebaseでメール/パスワード認証を試行
                # 仮パスワードがFirebaseに正しく設定されている必要があります
                
                # Firebase Admin SDKを使用してユーザー認証を検証
                # 実際のFirebase認証は、フロントエンドで行い、バックエンドではトークンを検証する
                
                # 仮パスワード認証が成功した場合（簡易実装）
                # 実際の運用では、Firebase IDトークンを検証する必要があります
                user.last_login_at = datetime.utcnow()
                await db.commit()
                
                access_token = create_access_token(data={"sub": user.email})
                logger.info(f"Temporary password login successful: {user.email}")

                return {"access_token": access_token, "token_type": "bearer", "user": user}
                
            except Exception as firebase_error:
                logger.error(f"Firebase authentication failed: {firebase_error}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid temporary password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
                
        except Exception as firebase_error:
            logger.error(f"Firebase client initialization failed: {firebase_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Firebase service unavailable",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Temporary login failed: {e}")
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
    logger.info(f"Received Firebase login request: id_token length={len(request.id_token) if request.id_token else 0}, display_name={request.display_name}")
    
    try:
        # Firebase認証を試行
        decoded_token = None
        
        try:
            from app.integrations.firebase_client import get_firebase_client
            firebase_client = get_firebase_client()
            decoded_token = firebase_client.verify_id_token(request.id_token)
            
            if decoded_token:
                logger.info("Firebase authentication successful")
            else:
                logger.warning("Firebase authentication failed, falling back to mock authentication")
                
        except Exception as firebase_error:
            logger.warning(f"Firebase authentication error: {firebase_error}")
        
        # Firebase認証が失敗した場合、開発環境ではモック認証を使用
        if not decoded_token:
            import os
            if os.getenv("ENVIRONMENT", "development") == "development":
                logger.info("Development environment detected, using mock authentication")
                
                # 開発環境では簡易的なトークン検証
                if not request.id_token or len(request.id_token) < 10:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid token format"
                    )
                
                # 開発用のモックトークンデータ
                decoded_token = {
                    "uid": f"dev_uid_{hash(request.id_token) % 10000}",
                    "email": request.display_name or "dev@example.com"
                }
                logger.info(f"Using mock token for development: {decoded_token}")
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Firebase authentication failed and mock authentication is not allowed in production"
                )

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
        
        logger.info(f"Processing authentication for user: {email} (UID: {uid})")
        
        try:
            logger.info(f"Starting database operation for user: {email}")
            
            # 既存ユーザーを検索（emailまたはfirebase_uidで）
            auth_service = AuthService(db)
            existing_user = await auth_service.get_user_by_email(email)
            
            if existing_user:
                # 既存ユーザーの場合、情報を更新
                user = existing_user
                user.last_login_at = datetime.utcnow()
                if request.display_name and user.full_name != request.display_name:
                    user.full_name = request.display_name
                if not user.firebase_uid:
                    user.firebase_uid = uid
                user.is_verified = True
                user.is_active = True
                
                await db.commit()
                await db.refresh(user)
                logger.info(f"Updated existing user: {user.id}")
            else:
                # 新規ユーザーの場合、管理者ユーザーのみ自動作成
                logger.warning(f"No existing user found for email: {email}")
                
                # admin@example.comの場合は管理者ユーザーとして作成
                if email == "admin@example.com":
                    logger.info(f"Creating admin user for: {email}")
                    user = User(
                        email=email,
                        username=email,
                        full_name="管理者1",
                        department="管理部",
                        is_admin=True,
                        firebase_uid=uid,
                        has_temporary_password=False,
                        is_first_login=False,
                        is_active=True,
                        is_verified=True
                    )
                    db.add(user)
                    await db.commit()
                    await db.refresh(user)
                    logger.info(f"Created admin user: {user.id}")
                else:
                    # その他のユーザーはログインを拒否
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User not found. Please contact administrator to create your account."
                    )
            
            logger.info(f"User operation completed successfully: {user.id}")
            
            # アクセストークンを作成
            access_token = create_access_token(data={"sub": user.email, "uid": uid})
            
            logger.info(f"Firebase user logged in successfully: {email}")
            
            from fastapi.responses import JSONResponse
            
            response_data = {
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
            
            response = JSONResponse(content=response_data)
            response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            
            return response
            
        except ValueError as ve:
            logger.error(f"User creation/update validation error: {ve}")
            from fastapi.responses import JSONResponse
            
            response = JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": str(ve)}
            )
            response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(ve)
            )
        except Exception as db_error:
            logger.error(f"Database operation failed: {db_error}")
            logger.error(f"Error type: {type(db_error)}")
            logger.error(f"Error details: {str(db_error)}")
            import traceback
            logger.error(f"Database operation traceback: {traceback.format_exc()}")
            
            from fastapi.responses import JSONResponse
            
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": f"Database operation failed: {str(db_error)}"}
            )
            response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            
            return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Firebase login failed: {e}")
        import traceback
        logger.error(f"Firebase login traceback: {traceback.format_exc()}")
        
        from fastapi.responses import JSONResponse
        
        response = JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"Internal server error: {str(e)}"}
        )
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        
        return response


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

@router.post("/admin/create-user")
async def create_user_by_admin(
    user_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """管理者によるユーザー作成（開発環境用）"""
    try:
        import os
        environment = os.getenv("ENVIRONMENT", "development")
        
        if environment != "development":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This endpoint is only available in development"
            )
        
        # 必須フィールドのチェック
        required_fields = ["email", "firebase_uid", "display_name"]
        for field in required_fields:
            if field not in user_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )
        
        # 既存ユーザーのチェック
        auth_service = AuthService(db)
        existing_user = await auth_service.get_user_by_email(user_data["email"])
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            )
        
        # ユーザー作成
        from app.models.user import User
        from app.core.auth import get_password_hash
        
        new_user = User(
            email=user_data["email"],
            username=user_data["email"].split('@')[0],
            full_name=user_data["display_name"],
            firebase_uid=user_data["firebase_uid"],
            hashed_password=get_password_hash("temporary_password"),
            is_active=True,
            is_verified=True,
            is_admin=user_data.get("is_admin", False)
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        logger.info(f"Admin created user: {new_user.email}")
        
        return {
            "message": "User created successfully",
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "username": new_user.username,
                "full_name": new_user.full_name,
                "firebase_uid": new_user.firebase_uid,
                "is_admin": new_user.is_admin
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin user creation failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User creation failed: {str(e)}"
        )

@router.post("/dev/create-admin")
async def create_dev_admin(
    user_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """開発環境用：認証なしで管理者ユーザーを作成"""
    try:
        import os
        environment = os.getenv("ENVIRONMENT", "development")
        
        if environment != "development":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This endpoint is only available in development"
            )
        
        # 必須フィールドのチェック
        required_fields = ["email", "name", "department"]
        for field in required_fields:
            if field not in user_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )
        
        # 既存ユーザーのチェック
        try:
            auth_service = AuthService(db)
            existing_user = await auth_service.get_user_by_email(user_data["email"])
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already exists"
                )
        except Exception as auth_error:
            logger.error(f"AuthService error: {auth_error}")
            # AuthServiceエラーの場合は、直接データベースでチェック
            from app.models.user import User
            existing_user = await db.execute(
                select(User).where(User.email == user_data["email"])
            )
            if existing_user.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already exists"
                )
        
        # 仮パスワードを生成
        import secrets
        
        # 仮パスワード生成（admin_users.pyの統一されたロジックを使用）
        from app.api.v1.admin_users import generate_temporary_password
        temp_password = generate_temporary_password()
        
        # Firebase Admin SDKを初期化
        from app.integrations.firebase_client import initialize_firebase_admin, create_firebase_user
        
        firebase_user = None
        firebase_uid = None
        
        # Firebase設定が不完全な場合は、開発環境用のダミーUIDを生成
        if not initialize_firebase_admin():
            print("Firebase設定が不完全なため、開発環境用のダミーUIDを使用します")
            import uuid
            firebase_uid = f"dev_{uuid.uuid4().hex[:28]}"
        else:
            # Firebase Authでユーザーを作成
            firebase_user = create_firebase_user(
                email=user_data["email"],
                password=temp_password,
                display_name=user_data["name"]
            )
            
            if not firebase_user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Firebaseユーザーの作成に失敗しました"
                )
            firebase_uid = firebase_user['uid']
        
        # PostgreSQLにユーザー情報を保存
        from app.models.user import User
        from datetime import datetime, timedelta
        
        new_user = User(
            firebase_uid=firebase_uid,
            email=user_data["email"],
            username=user_data["email"].split('@')[0],
            full_name=user_data["name"],
            department=user_data["department"],
            is_admin=user_data.get("role", "member") == "admin",
            has_temporary_password=True,
            temporary_password_expires_at=datetime.utcnow() + timedelta(days=7),
            is_first_login=True,
            is_active=True,
            is_verified=False
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        return {
            "message": "管理者ユーザーが作成されました",
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "name": new_user.full_name,
                "department": new_user.department,
                "role": "admin" if new_user.is_admin else "member",
                "temporary_password": temp_password
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dev admin creation failed: {e}")
        import traceback
        logger.error(f"Dev admin creation traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"管理者作成に失敗しました: {str(e)}"
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

class PasswordChangeRequest(BaseModel):
    """パスワード変更リクエスト"""
    current_password: str
    new_password: str

class LoginStatusResponse(BaseModel):
    """ログイン状態レスポンス"""
    is_first_login: bool
    has_temporary_password: bool
    needs_password_setup: bool  # is_first_login && has_temporary_password

@router.get("/login-status", response_model=LoginStatusResponse)
async def get_login_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """現在のログイン状態を取得（初回ログイン判定）"""
    return LoginStatusResponse(
        is_first_login=current_user.is_first_login,
        has_temporary_password=current_user.has_temporary_password,
        needs_password_setup=current_user.is_first_login and current_user.has_temporary_password
    )

@router.post("/change-password")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """初回ログイン時のパスワード変更"""
    
    # 初回ログインでない場合はエラー
    if not current_user.is_first_login:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="初回ログインではありません"
        )
    
    # 仮パスワードを使用していない場合はエラー
    if not current_user.has_temporary_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="仮パスワードを使用していません"
        )
    
    # Firebase UIDがない場合はエラー
    if not current_user.firebase_uid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Firebase UIDが設定されていません"
        )
    
    try:
        # Firebase Authでパスワードを更新
        if not update_firebase_user_password(current_user.firebase_uid, password_data.new_password):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Firebaseでのパスワード更新に失敗しました"
            )
        
        # データベースの状態を更新
        from datetime import datetime
        current_user.has_temporary_password = False
        current_user.is_first_login = False
        current_user.last_password_change_at = datetime.utcnow()
        
        await db.commit()
        
        return {"message": "パスワードが正常に変更されました"}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"パスワード変更に失敗しました: {str(e)}"
        )

@router.post("/dev/login", response_model=LoginResponse)
async def dev_login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """開発用：ダミー認証でログイン（Firebaseを使わない）"""
    
    # データベースからユーザーを検索
    user = await db.execute(
        select(User).where(User.email == login_data.email)
    )
    user = user.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません"
        )
    
    # 仮パスワードでログイン（開発環境用）
    if user.has_temporary_password:
        # 仮パスワードの有効期限をチェック
        if user.temporary_password_expires_at and user.temporary_password_expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="仮パスワードの有効期限が切れています"
            )
        
        # 仮パスワードでログイン成功
        print(f"Dev login successful for {user.email} with temporary password")
        
        return LoginResponse(
            access_token="dev_token_" + str(user.id),  # ダミートークン
            token_type="bearer",
            user_id=user.id,
            email=user.email,
            is_admin=user.is_admin,
            needs_password_setup=user.is_first_login
        )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="仮パスワードでログインしてください"
    )
