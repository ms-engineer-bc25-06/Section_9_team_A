from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class Team(Base):
    """チームモデル（基本的な機能のみ）"""

    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # チーム設定
    is_public = Column(Boolean, default=False)
    max_members = Column(Integer, default=10)
    
    # オーナー情報
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # リレーションシップ（基本的な機能のみ）
    owner = relationship("User", foreign_keys=[owner_id], back_populates="owned_teams")
    members = relationship("TeamMember", back_populates="team", uselist=True)
    voice_sessions = relationship("VoiceSession", back_populates="team", uselist=True)
    chat_rooms = relationship("ChatRoom", back_populates="team")
    shared_reports = relationship("ReportShare", back_populates="shared_with_team_rel")
    member_profiles = relationship("TeamMemberProfile", back_populates="team")

    def __repr__(self):
        return f"<Team(id={self.id}, name='{self.name}', owner_id={self.owner_id})>"
