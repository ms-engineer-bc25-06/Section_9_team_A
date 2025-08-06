from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class TeamRole(enum.Enum):
    """チームメンバーの役割"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    GUEST = "guest"


class TeamMember(Base):
    """チームメンバーモデル"""

    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # メンバー情報
    role = Column(Enum(TeamRole), default=TeamRole.MEMBER)
    is_active = Column(Boolean, default=True)
    
    # タイムスタンプ
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # リレーションシップ
    team = relationship("Team", back_populates="members")
    user = relationship("User", back_populates="teams")
    
    def __repr__(self):
        return f"<TeamMember(team_id={self.team_id}, user_id={self.user_id}, role='{self.role.value}')>"
