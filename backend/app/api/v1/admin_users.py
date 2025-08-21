"""管理者用ユーザー管理API"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime, timedelta
import secrets
import string

from app.core.database import get_db
from app.models.user import User
from app.schemas.admin_users import UserCreate, UserResponse
from app.core.firebase_admin import create_firebase_user, initialize_firebase_admin
from app.api.deps import get_current_admin_user

router = APIRouter()

def generate_temporary_password(length: int = 12) -> str:
    """仮パスワードを生成"""
    # 大文字、小文字、数字、記号を含む
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ""
    
    # 最低1つの大文字、小文字、数字、記号を含む
    password += secrets.choice(string.ascii_uppercase)
    password += secrets.choice(string.ascii_lowercase)
    password += secrets.choice(string.digits)
    password += secrets.choice("!@#$%^&*")
    
    # 残りの文字をランダムに生成
    for _ in range(length - 4):
        password += secrets.choice(chars)
    
    # パスワードをシャッフル
    password_list = list(password)
    secrets.SystemRandom().shuffle(password_list)
    return ''.join(password_list)

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
    # current_admin: User = Depends(get_current_admin_user)  # 一時的に無効化
):
    """管理者がユーザーを作成（仮パスワード付き）"""
    
    # Firebase Admin SDKを初期化（開発環境では失敗しても続行）
    firebase_initialized = initialize_firebase_admin()
    if not firebase_initialized:
        print("Warning: Firebase Admin SDK初期化に失敗しました。開発環境用のダミーUIDを使用します。")
    
    # 既存のユーザーをチェック
    existing_user = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このメールアドレスは既に使用されています"
        )
    
    # 仮パスワードを生成
    temporary_password = generate_temporary_password()
    
    # Firebase Authでユーザーを作成（開発環境ではダミーUIDを使用）
    firebase_user = None
    if firebase_initialized:
        firebase_user = create_firebase_user(
            email=user_data.email,
            password=temporary_password,
            display_name=user_data.name
        )
    
    if not firebase_user:
        # 開発環境用のダミーUIDを生成
        import hashlib
        firebase_uid = f"dev_uid_{hashlib.md5(user_data.email.encode()).hexdigest()[:12]}"
        firebase_user = {
            'uid': firebase_uid,
            'email': user_data.email
        }
        print(f"Using dummy Firebase UID: {firebase_uid}")
    
    # PostgreSQLにユーザー情報を保存
    new_user = User(
        firebase_uid=firebase_user['uid'],
        email=user_data.email,
        username=user_data.email.split('@')[0],  # メールアドレスの@前をユーザー名として使用
        full_name=user_data.name,
        department=user_data.department,
        is_admin=user_data.role == "admin",
        has_temporary_password=True,
        temporary_password_expires_at=datetime.utcnow() + timedelta(days=7),  # 7日間有効
        is_first_login=True,
        is_active=True,
        is_verified=False
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return UserResponse(
        id=new_user.id,
        firebase_uid=new_user.firebase_uid,
        email=new_user.email,
        name=new_user.full_name,
        department=new_user.department,
        role="admin" if new_user.is_admin else "member",
        has_temporary_password=new_user.has_temporary_password,
        is_first_login=new_user.is_first_login,
        temporary_password=temporary_password,  # 仮パスワードを返す（実際の運用では安全な方法で送信）
        created_at=new_user.created_at
    )

@router.post("/users/dev", response_model=UserResponse)
async def create_user_dev(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
    # 認証を無効化（開発用）
):
    """開発用：管理者がユーザーを作成（仮パスワード付き）- 認証不要"""
    
    # Firebase Admin SDKを初期化（開発環境では失敗しても続行）
    firebase_initialized = initialize_firebase_admin()
    if not firebase_initialized:
        print("Warning: Firebase Admin SDK初期化に失敗しました。開発環境用のダミーUIDを使用します。")
    
    # 既存のユーザーをチェック
    existing_user = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このメールアドレスは既に使用されています"
        )
    
    # 仮パスワードを生成
    temporary_password = generate_temporary_password()
    
    # Firebase Authでユーザーを作成（開発環境ではダミーUIDを使用）
    firebase_user = None
    if firebase_initialized:
        firebase_user = create_firebase_user(
            email=user_data.email,
            password=temporary_password,
            display_name=user_data.name
        )
    
    if not firebase_user:
        # 開発環境用のダミーUIDを生成
        import hashlib
        firebase_uid = f"dev_uid_{hashlib.md5(user_data.email.encode()).hexdigest()[:12]}"
        firebase_user = {
            'uid': firebase_uid,
            'email': user_data.email
        }
        print(f"Using dummy Firebase UID: {firebase_uid}")
    
    # PostgreSQLにユーザー情報を保存
    new_user = User(
        firebase_uid=firebase_user['uid'],
        email=user_data.email,
        username=user_data.email.split('@')[0],  # メールアドレスの@前をユーザー名として使用
        full_name=user_data.name,
        department=user_data.department,
        is_admin=user_data.role == "admin",
        has_temporary_password=True,
        temporary_password_expires_at=datetime.utcnow() + timedelta(days=7),  # 7日間有効
        is_first_login=True,
        is_active=True,
        is_verified=False
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return UserResponse(
        id=new_user.id,
        firebase_uid=new_user.firebase_uid,
        email=new_user.email,
        name=new_user.full_name,
        department=new_user.department,
        role="admin" if new_user.is_admin else "member",
        has_temporary_password=new_user.has_temporary_password,
        is_first_login=new_user.is_first_login,
        temporary_password=temporary_password,  # 仮パスワードを返す（実際の運用では安全な方法で送信）
        created_at=new_user.created_at
    )

@router.get("/users", response_model=List[UserResponse])
async def get_users(
    db: AsyncSession = Depends(get_db)
    # current_admin: User = Depends(get_current_admin_user)  # 一時的に無効化
):
    """管理者がユーザー一覧を取得"""
    users = await db.execute(select(User))
    user_list = users.scalars().all()
    
    return [
        UserResponse(
            id=user.id,
            firebase_uid=user.firebase_uid,
            email=user.email,
            name=user.full_name,
            department=user.department,
            role="admin" if user.is_admin else "member",
            has_temporary_password=user.has_temporary_password,
            is_first_login=user.is_first_login,
            created_at=user.created_at
        )
        for user in user_list
    ]

