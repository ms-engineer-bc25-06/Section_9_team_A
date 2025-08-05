from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class Token(BaseModel):
    """トークンスキーマ"""

    access_token: str
    token_type: str
    user: Optional[dict] = None


class TokenData(BaseModel):
    """トークンデータスキーマ"""

    email: Optional[str] = None


class UserBase(BaseModel):
    """ユーザーベーススキーマ"""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None


class UserCreate(UserBase):
    """ユーザー作成スキーマ"""

    password: str = Field(..., min_length=8)
    firebase_uid: Optional[str] = None


class UserLogin(BaseModel):
    """ユーザーログインスキーマ"""

    email: EmailStr
    password: str


class UserRegister(UserCreate):
    """ユーザー登録スキーマ"""

    confirm_password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """ユーザー更新スキーマ"""

    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None


class UserResponse(UserBase):
    """ユーザー応答スキーマ"""

    id: int
    is_active: bool
    is_verified: bool
    is_premium: bool
    subscription_status: str
    subscription_end_date: Optional[datetime] = None
    monthly_voice_minutes: int
    monthly_analysis_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FirebaseAuthRequest(BaseModel):
    """Firebase認証リクエストスキーマ"""

    id_token: str


class PasswordResetRequest(BaseModel):
    """パスワードリセットリクエストスキーマ"""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """パスワードリセット確認スキーマ"""

    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)


class EmailVerificationRequest(BaseModel):
    """メール認証リクエストスキーマ"""

    email: EmailStr


class EmailVerificationConfirm(BaseModel):
    """メール認証確認スキーマ"""

    token: str
