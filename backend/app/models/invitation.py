from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class InvitationStatus(enum.Enum):
    """招待の状態"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"


class Invitation(Base):
    """招待モデル"""

    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    inviter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 招待情報
    email = Column(String(255), nullable=False)
    role = Column(String(50), default="member")  # owner, admin, member, guest
    message = Column(Text, nullable=True)
    
    # 招待状態
    status = Column(Enum(InvitationStatus), default=InvitationStatus.PENDING)
    token = Column(String(255), unique=True, nullable=False)
    
    # 期限
    expires_at = Column(DateTime(timezone=True), nullable=False)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    
    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # リレーションシップ
    team = relationship("Team", back_populates="invitations")
    inviter = relationship("User", foreign_keys=[inviter_id], back_populates="sent_invitations")
    
    def __repr__(self):
        return f"<Invitation(id={self.id}, team_id={self.team_id}, email='{self.email}', status='{self.status.value}')>"
