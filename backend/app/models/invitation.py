# TODO: 仮Invitationテーブル（後ほど消す）
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Invitation(Base):
    """招待モデル"""

    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    inviter_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 招待情報
    email = Column(String(255), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    role = Column(String(50), default="member")  # owner, admin, member
    status = Column(String(50), default="pending")  # pending, accepted, expired

    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return (
            f"<Invitation(id={self.id}, email='{self.email}', status='{self.status}')>"
        )
