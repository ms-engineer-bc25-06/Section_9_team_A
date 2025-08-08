from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, date


class Token(BaseModel):
    """トークンスキーマ（Firebase認証用）"""

    access_token: str
    token_type: str
    user: Optional[dict] = None


class TokenData(BaseModel):
    """トークンデータスキーマ"""

    email: Optional[str] = None
    firebase_uid: Optional[str] = None


class UserBase(BaseModel):
    """ユーザーベーススキーマ"""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    # プロフィール項目
    nickname: Optional[str] = None  # ニックネーム
    department: Optional[str] = None  # 部署
    join_date: Optional[date] = None  # 入社年月
    birth_date: Optional[date] = None  # 生年月日
    hometown: Optional[str] = None  # 出身地
    residence: Optional[str] = None  # 居住地
    hobbies: Optional[str] = None  # 趣味・特技
    student_activities: Optional[str] = (
        None  # 学生時代の部活・サークル・力を入れていたこと
    )
    holiday_activities: Optional[str] = None  # 休日の過ごし方
    favorite_food: Optional[str] = None  # 好きな食べ物
    favorite_media: Optional[str] = None  # 好きな本・漫画・映画・ドラマ
    favorite_music: Optional[str] = None  # 好きな音楽・カラオケの18番
    pets_oshi: Optional[str] = None  # ペット・推し
    respected_person: Optional[str] = None  # 尊敬する人
    motto: Optional[str] = None  # 座右の銘
    future_goals: Optional[str] = None  # 将来の目標・生きてるうちにやってみたいこと


class UserCreate(UserBase):
    """ユーザー作成スキーマ（Firebase認証用）"""

    firebase_uid: str


class UserUpdate(BaseModel):
    """ユーザー更新スキーマ"""

    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    # プロフィール項目
    nickname: Optional[str] = None  # ニックネーム
    department: Optional[str] = None  # 部署
    join_date: Optional[date] = None  # 入社年月
    birth_date: Optional[date] = None  # 生年月日
    hometown: Optional[str] = None  # 出身地
    residence: Optional[str] = None  # 居住地
    hobbies: Optional[str] = None  # 趣味・特技
    student_activities: Optional[str] = (
        None  # 学生時代の部活・サークル・力を入れていたこと
    )
    holiday_activities: Optional[str] = None  # 休日の過ごし方
    favorite_food: Optional[str] = None  # 好きな食べ物
    favorite_media: Optional[str] = None  # 好きな本・漫画・映画・ドラマ
    favorite_music: Optional[str] = None  # 好きな音楽・カラオケの18番
    pets_oshi: Optional[str] = None  # ペット・推し
    respected_person: Optional[str] = None  # 尊敬する人
    motto: Optional[str] = None  # 座右の銘
    future_goals: Optional[str] = None  # 将来の目標・生きてるうちにやってみたいこと


class UserResponse(UserBase):
    """ユーザー応答スキーマ"""

    id: int
    firebase_uid: Optional[str] = None
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


class TokenVerificationResponse(BaseModel):
    """トークン検証応答スキーマ"""

    valid: bool
    user: Optional[dict] = None


class ProfileUpdateRequest(BaseModel):
    """プロフィール更新リクエストスキーマ"""

    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    nickname: Optional[str] = None
    department: Optional[str] = None
    join_date: Optional[date] = None
    birth_date: Optional[date] = None
    hometown: Optional[str] = None
    residence: Optional[str] = None
    hobbies: Optional[str] = None
    student_activities: Optional[str] = None
    holiday_activities: Optional[str] = None
    favorite_food: Optional[str] = None
    favorite_media: Optional[str] = None
    favorite_music: Optional[str] = None
    pets_oshi: Optional[str] = None
    respected_person: Optional[str] = None
    motto: Optional[str] = None
    future_goals: Optional[str] = None
