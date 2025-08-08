from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class VoiceSession(Base):
    """音声セッションモデル"""

    __tablename__ = "voice_sessions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # セッション情報
    room_id = Column(String(255), unique=True, nullable=False)
    status = Column(String(50), default="active")  # active, ended, archived
    
    # 参加者情報
    host_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    
    # セッション統計
    duration_minutes = Column(Float, default=0.0)
    participant_count = Column(Integer, default=0)
    recording_url = Column(String(500), nullable=True)
    
    # 設定
    is_public = Column(Boolean, default=False)
    allow_recording = Column(Boolean, default=True)
    
    # タイムスタンプ
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # リレーションシップ
    host = relationship("User", back_populates="voice_sessions")
    team = relationship("Team", back_populates="voice_sessions")
    transcriptions = relationship("Transcription", back_populates="voice_session")
    analyses = relationship("Analysis", back_populates="voice_session")
    
    def __repr__(self):
        return f"<VoiceSession(id={self.id}, title='{self.title}', room_id='{self.room_id}')>"
