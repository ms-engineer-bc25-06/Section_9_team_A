from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, cast

from app.models.base import Base


class User(Base):
    """ユーザーモデル（基本的な認証機能のみ）"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Firebase認証の場合はnull
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)

    # プロフィール項目
    nickname = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    join_date = Column(Date, nullable=True)
    birth_date = Column(Date, nullable=True)
    hometown = Column(String(200), nullable=True)
    residence = Column(String(200), nullable=True)
    hobbies = Column(Text, nullable=True)
    student_activities = Column(Text, nullable=True)
    holiday_activities = Column(Text, nullable=True)
    favorite_food = Column(Text, nullable=True)
    favorite_media = Column(Text, nullable=True)
    favorite_music = Column(Text, nullable=True)
    pets_oshi = Column(Text, nullable=True)
    respected_person = Column(Text, nullable=True)
    motto = Column(Text, nullable=True)
    future_goals = Column(Text, nullable=True)

    # Firebase認証関連
    firebase_uid = Column(String(128), unique=True, index=True, nullable=True)

    # 仮パスワード管理
    has_temporary_password = Column(Boolean, default=True)  # 仮パスワード使用中フラグ
    temporary_password = Column(String(255), nullable=True)  # 仮パスワード
    temporary_password_expires_at = Column(
        DateTime(timezone=True), nullable=True
    )  # 仮パスワード有効期限
    is_first_login = Column(Boolean, default=True)  # 初回ログインフラグ
    last_password_change_at = Column(
        DateTime(timezone=True), nullable=True
    )  # 最終パスワード変更日

    # アカウント状態
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)

    # サブスクリプション関連
    subscription_status = Column(String(50), default="free")
    subscription_end_date = Column(DateTime(timezone=True), nullable=True)

    # 使用量制限
    monthly_voice_minutes = Column(Integer, default=0)
    monthly_analysis_count = Column(Integer, default=0)

    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # リレーションシップ
    organization_memberships = relationship("OrganizationMember", back_populates="user")
    owned_organizations = relationship("Organization", back_populates="owner")
    voice_sessions = relationship("VoiceSession", back_populates="host")
    # voice_session_participations = relationship(
    #     "VoiceSessionParticipant", back_populates="user"
    # )
    transcriptions = relationship("Transcription", back_populates="user")
    analyses = relationship("Analysis", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")
    billing_records = relationship("Billing", back_populates="user")
    # ChatRoom関連のリレーションシップ（一時的に無効化）
    # created_chat_rooms = relationship("ChatRoom", back_populates="creator")
    # chat_messages = relationship("ChatMessage", back_populates="sender")
    # chat_room_participations = relationship("ChatRoomParticipant", back_populates="user")

    # レポート関連（一時的に無効化）
    # reports = relationship("Report", back_populates="user")
    # shared_reports = relationship(
    #     "ReportShare",
    #     foreign_keys="ReportShare.shared_by",
    #     back_populates="shared_by_user",
    # )
    # received_reports = relationship(
    #     "ReportShare",
    #     foreign_keys="ReportShare.shared_with",
    #     back_populates="shared_with_user",
    # )
    # report_exports = relationship("ReportExport", back_populates="user")

    # チームダイナミクス分析関連
    team_profiles = relationship("OrganizationMemberProfile", back_populates="user")
    # 組織メンバーシップ関連
    organization_memberships = relationship("OrganizationMember", back_populates="user")

    # プライバシー関連
    encrypted_data = relationship("EncryptedData", back_populates="owner")
    data_access_permissions = relationship(
        "DataAccessPermission",
        foreign_keys="DataAccessPermission.user_id",
        back_populates="user",
    )
    granted_permissions = relationship(
        "DataAccessPermission",
        foreign_keys="DataAccessPermission.granted_by",
        back_populates="granter",
    )

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"

    @property
    def display_name(self) -> str:
        """表示名を取得（full_nameまたはusernameから）"""
        return self.full_name or self.username

    @property
    def is_premium_user(self) -> bool:
        """プレミアムユーザーかどうか"""
        end_date = cast(Optional[datetime], self.subscription_end_date)
        if not end_date:
            return False
        return end_date > datetime.utcnow()

    @property
    def has_active_subscription(self) -> bool:
        """アクティブなサブスクリプションがあるかどうか"""

        return self.subscription_status in ["basic", "premium"] and self.is_premium_user

    @property
    def needs_password_setup(self) -> bool:
        """パスワード設定が必要かどうか"""
        return self.is_first_login and self.has_temporary_password

    @property
    def is_temporary_password_expired(self) -> bool:
        """仮パスワードが期限切れかどうか"""
        if not self.temporary_password_expires_at:
            return False
        return self.temporary_password_expires_at < datetime.utcnow()

    def remaining_voice_minutes(self) -> int:
        """残りの音声利用時間を取得"""
        return max(0, self.monthly_voice_minutes)

    def remaining_analysis_count(self) -> int:
        """残りの分析回数を取得"""
        return max(0, self.monthly_analysis_count)
