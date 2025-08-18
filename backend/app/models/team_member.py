from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base


class TeamMember(Base):
    """チームメンバーモデル（基本的な機能のみ）"""

    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    
    # チームとユーザーの関連
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # メンバー情報
    role = Column(String(50), nullable=True)  # owner, admin, member
    is_active = Column(Boolean, default=True)
    
    # タイムスタンプ
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # リレーションシップ（基本的な機能のみ）
    team = relationship("Team", back_populates="members")
    user = relationship("User", back_populates="teams")

    def __repr__(self):
        return f"<TeamMember(id={self.id}, team_id={self.team_id}, user_id={self.user_id})>"
