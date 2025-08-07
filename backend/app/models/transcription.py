from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Transcription(Base):
    """文字起こしモデル"""

    __tablename__ = "transcriptions"

    id = Column(Integer, primary_key=True, index=True)
    voice_session_id = Column(Integer, ForeignKey("voice_sessions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 文字起こし情報
    content = Column(Text, nullable=False)
    language = Column(String(10), default="ja")
    confidence_score = Column(Float, nullable=True)
    
    # 時間情報
    start_time = Column(Float, nullable=True)  # 秒単位
    end_time = Column(Float, nullable=True)    # 秒単位
    
    # メタデータ
    speaker_id = Column(String(100), nullable=True)
    speaker_name = Column(String(255), nullable=True)
    meta_data = Column(JSON, nullable=True)  # 追加のメタデータ
    
    # 状態
    is_verified = Column(Boolean, default=False)
    is_edited = Column(Boolean, default=False)
    
    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # リレーションシップ
    voice_session = relationship("VoiceSession", back_populates="transcriptions")
    user = relationship("User", back_populates="transcriptions")
    
    def __repr__(self):
        return f"<Transcription(id={self.id}, voice_session_id={self.voice_session_id}, speaker='{self.speaker_name}')>"
