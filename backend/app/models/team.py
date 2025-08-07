# TODO: 仮Teamテーブル（後ほど消す）
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Team(Base):
    """チームモデル"""

    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # リレーションシップ
    members = relationship("TeamMember", back_populates="team")
    voice_sessions = relationship("VoiceSession", back_populates="team")

    def __repr__(self):
        return f"<Team(id={self.id}, name='{self.name}')>"
