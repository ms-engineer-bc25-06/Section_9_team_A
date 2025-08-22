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
from app.integrations.firebase_client import create_firebase_user, initialize_firebase_admin
from app.api.deps import get_current_admin_user

router = APIRouter()

def generate_temporary_password(length: int = 12) -> str:
    """仮パスワードを生成（Firebase認証に安全な文字のみ）"""
    # 大文字、小文字、数字のみ（特殊文字を完全に除外）
    # 特殊文字を確実に除外するため、明示的に文字を定義
    uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    lowercase = "abcdefghijklmnopqrstuvwxyz"
    digits = "0123456789"
    
    password = ""
    
    # 最低1つの大文字、小文字、数字を含む
    password += secrets.choice(uppercase)
    password += secrets.choice(lowercase)
    password += secrets.choice(digits)
    
    # 残りの文字をランダムに生成（特殊文字なし）
    all_chars = uppercase + lowercase + digits
    for _ in range(length - 3):
        password += secrets.choice(all_chars)
    
    # パスワードをシャッフル
    password_list = list(password)
    secrets.SystemRandom().shuffle(password_list)
    return ''.join(password_list)

async def _create_user_with_temporary_password(
    user_data: UserCreate,
    db: AsyncSession
) -> UserResponse:
    """ユーザー作成の共通処理（仮パスワード付き）"""
    
    # Firebase Admin SDKを初期化（必須）
    print("🔥 Firebase Admin SDK初期化開始...")
    firebase_initialized = initialize_firebase_admin()
    print(f"🔥 Firebase初期化結果: {firebase_initialized}")
    
    if not firebase_initialized:
        print("❌ Error: Firebase Admin SDK初期化に失敗しました。")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Firebase設定エラー。Firebase Admin SDKの初期化に失敗しました。"
        )
    
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
    
    # Firebase Authでユーザーを作成
    firebase_user = None
    if firebase_initialized:
        print(f"🔥 Firebaseでユーザーを作成中: {user_data.email}")
        print(f"🔑 仮パスワード: {temporary_password}")
        firebase_user = create_firebase_user(
            email=user_data.email,
            password=temporary_password,
            display_name=user_data.name
        )
        
        if firebase_user:
            print(f"✅ Firebaseユーザー作成成功: {firebase_user['uid']}")
        else:
            print("❌ Firebaseユーザー作成失敗")
    
    # Firebaseユーザー作成が失敗した場合はエラー
    if not firebase_user:
        print("❌ Firebaseユーザー作成失敗")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Firebaseユーザーの作成に失敗しました。Firebase設定を確認してください。"
        )
    
    # PostgreSQLにユーザー情報を保存
    new_user = User(
        firebase_uid=firebase_user['uid'],
        email=user_data.email,
        username=user_data.email.split('@')[0],  # メールアドレスの@前をユーザー名として使用
        full_name=user_data.name,
        department=user_data.department,
        is_admin=user_data.role == "admin",
        has_temporary_password=True,
        temporary_password=temporary_password,  # 仮パスワードを保存
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

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
    # current_admin: User = Depends(get_current_admin_user)  # 一時的に無効化
):
    """管理者がユーザーを作成（仮パスワード付き）"""
    return await _create_user_with_temporary_password(user_data, db)

@router.post("/users/dev", response_model=UserResponse)
async def create_user_dev(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
    # 認証を無効化（開発用）
):
    """開発用：管理者がユーザーを作成（仮パスワード付き）- 認証不要"""
    return await _create_user_with_temporary_password(user_data, db)

@router.get("/users", response_model=List[UserResponse])
async def get_users(
    db: AsyncSession = Depends(get_db)
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
            temporary_password=user.temporary_password,  
            created_at=user.created_at
        )
        for user in user_list
    ]

@router.get("/users/{user_id}/temporary-password")
async def get_user_temporary_password(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """ユーザーの仮パスワードを取得（開発用）"""
    user = await db.execute(select(User).where(User.id == user_id))
    user_obj = user.scalar_one_or_none()
    
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません"
        )
    
    if not user_obj.temporary_password:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="仮パスワードが設定されていません"
        )
    
    return {
        "email": user_obj.email,
        "temporary_password": user_obj.temporary_password,
        "expires_at": user_obj.temporary_password_expires_at
    }

