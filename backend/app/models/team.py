# TODO: 仮Teamテーブル（後ほど消す）
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Team(Base):
    """チームモデル"""

    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)

    # オーナー情報
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # チーム設定
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    max_members = Column(Integer, default=10)

    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # リレーションシップ
    owner = relationship("User", back_populates="owned_teams")
    members = relationship("TeamMember", back_populates="team")
    voice_sessions = relationship("VoiceSession", back_populates="team")
    # REVIEW: Chat-room用の関係性を定義（るい）
    chat_rooms = relationship("ChatRoom", back_populates="team")
    invitations = relationship("Invitation", back_populates="team")

    def __repr__(self):
        return f"<Team(id={self.id}, name='{self.name}')>"
