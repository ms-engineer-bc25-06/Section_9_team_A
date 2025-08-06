from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class User(Base):
    """ユーザーモデル"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Firebase認証の場合はnull
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)

    # Firebase認証関連
    firebase_uid = Column(String(128), unique=True, index=True, nullable=True)

    # アカウント状態
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)

    # サブスクリプション関連
    subscription_status = Column(String(50), default="free")  # free, basic, premium
    subscription_end_date = Column(DateTime, nullable=True)

    # 使用量制限
    monthly_voice_minutes = Column(Integer, default=0)
    monthly_analysis_count = Column(Integer, default=0)

    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # リレーションシップ
    teams = relationship("TeamMember", back_populates="user")
    owned_teams = relationship("Team", back_populates="owner")
    voice_sessions = relationship("VoiceSession", back_populates="host")
    transcriptions = relationship("Transcription", back_populates="user")
    analyses = relationship("Analysis", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")
    billings = relationship("Billing", back_populates="user")
    sent_invitations = relationship("Invitation", foreign_keys="Invitation.inviter_id", back_populates="inviter")
    audit_logs = relationship("AuditLog", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"

    @property
    def is_premium_user(self) -> bool:
        """プレミアムユーザーかどうか"""
        if not self.subscription_end_date:
            return False
        return self.subscription_end_date > datetime.utcnow()

    @property
    def has_active_subscription(self) -> bool:
        """アクティブなサブスクリプションがあるかどうか"""
        return self.subscription_status in ["basic", "premium"] and self.is_premium_user
