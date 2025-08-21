from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base


class Invitation(Base):
    """招待モデル"""

    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True, index=True)

    # 招待情報
    invitation_id = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), nullable=False, index=True)
    
    # 招待内容
    invitation_type = Column(String(50), nullable=False)  # team, project, etc.
    role = Column(String(50), default="member")  # owner, admin, member, guest
    
    # 招待状態
    status = Column(String(50), default="pending")  # pending, accepted, declined, expired
    is_active = Column(Boolean, default=True)
    
    # 招待メッセージ
    message = Column(Text, nullable=True)
    
    # 外部キー
    team_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    invited_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    invited_user = Column(Integer, ForeignKey("users.id"), nullable=True)

    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    
    # リレーションシップ（循環参照を避けるため、back_populatesは使用しない）
    team = relationship("Team")
    inviter = relationship("User", foreign_keys=[invited_by])
    invitee = relationship("User", foreign_keys=[invited_user])

    def __repr__(self):
        return f"<Invitation(id={self.id}, email='{self.email}', status='{self.status}')>"

    @property
    def is_expired(self) -> bool:
        """招待が期限切れかどうか"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    @property
    def is_accepted(self) -> bool:
        """招待が承認されたかどうか"""
        return self.status == "accepted" and self.accepted_at is not None

    @property
    def is_declined(self) -> bool:
        """招待が辞退されたかどうか"""
        return self.status == "declined"

    @property
    def is_pending(self) -> bool:
        """招待が保留中かどうか"""
        return self.status == "pending" and not self.is_expired

    @property
    def days_until_expiry(self) -> int:
        """期限までの日数"""
        if not self.expires_at:
            return -1
        delta = self.expires_at - datetime.utcnow()
        return max(0, delta.days)

    def accept_invitation(self):
        """招待を承認"""
        self.status = "accepted"
        self.accepted_at = datetime.utcnow()
        self.is_active = False

    def decline_invitation(self):
        """招待を辞退"""
        self.status = "declined"
        self.is_active = False

    def cancel_invitation(self):
        """招待をキャンセル"""
        self.status = "cancelled"
        self.is_active = False

    def extend_expiry(self, additional_days: int):
        """有効期限を延長"""
        if self.expires_at:
            self.expires_at = self.expires_at + datetime.timedelta(days=additional_days)
        else:
            self.expires_at = datetime.utcnow() + datetime.timedelta(days=additional_days)

    def get_invitation_summary(self) -> dict:
        """招待サマリーを取得"""
        return {
            "invitation_id": self.invitation_id,
            "email": self.email,
            "invitation_type": self.invitation_type,
            "role": self.role,
            "status": self.status,
            "team_id": self.team_id,
            "invited_by": self.invited_by,
            "is_active": self.is_active,
            "is_expired": self.is_expired,
            "days_until_expiry": self.days_until_expiry,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }
