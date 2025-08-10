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
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    invited_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    invited_user = Column(Integer, ForeignKey("users.id"), nullable=True)

    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    expires_at = Column(DateTime(timezone=True), nullable=True)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    
    # リレーションシップ
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