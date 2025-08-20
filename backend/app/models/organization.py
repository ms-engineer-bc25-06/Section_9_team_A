from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class Organization(Base):
    """組織モデル（チーム機能を統合）"""
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    
    # 組織設定（旧Team機能）
    is_public = Column(Boolean, default=False)
    max_members = Column(Integer, default=10)
    avatar_url = Column(String(500), nullable=True)
    
    # 課金・サブスクリプション関連
    subscription_status = Column(String(50), nullable=False, default='free')
    stripe_customer_id = Column(String(255), nullable=True, unique=True)
    stripe_subscription_id = Column(String(255), nullable=True, unique=True)
    
    # オーナー情報
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    owner = relationship("User", foreign_keys=[owner_id], back_populates="owned_organizations")
    members = relationship("OrganizationMember", back_populates="organization", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="organization", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="organization", cascade="all, delete-orphan")
    
    # 旧Team関連の機能
    voice_sessions = relationship("VoiceSession", back_populates="organization")
    chat_rooms = relationship("ChatRoom", back_populates="organization")
    shared_reports = relationship("ReportShare", back_populates="shared_with_organization")
    member_profiles = relationship("TeamMemberProfile", back_populates="organization")

    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}', slug='{self.slug}')>"
