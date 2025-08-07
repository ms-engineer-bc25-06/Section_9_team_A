# TODO: 仮TeamMemberテーブル（後ほど消す）
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class TeamMember(Base):
    """チームメンバーモデル"""

    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    role = Column(String(50), default="member")  # owner, admin, member
    is_active = Column(Boolean, default=True)

    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # リレーションシップ
    user = relationship("User", back_populates="teams")
    team = relationship("Team", back_populates="members")

    def __repr__(self):
        return f"<TeamMember(id={self.id}, user_id={self.user_id}, team_id={self.team_id})>"
