from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base


class Transcription(Base):
    """文字起こしモデル"""

    __tablename__ = "transcriptions"

    id = Column(Integer, primary_key=True, index=True)
    
    # 文字起こし情報
    transcription_id = Column(String(255), unique=True, index=True, nullable=False)
    content = Column(Text, nullable=False)
    language = Column(String(10), default="ja")  # ja, en, etc.
    
    # 音声情報
    audio_file_path = Column(String(500), nullable=True)
    audio_duration = Column(Float, nullable=True)  # 秒単位
    audio_format = Column(String(50), nullable=True)
    
    # 文字起こし設定
    confidence_score = Column(Float, nullable=True)  # 0.0-1.0
    speaker_count = Column(Integer, default=1)
    speakers = Column(JSON, nullable=True)  # 話者情報
    
    # 処理状態
    status = Column(String(50), default="processing")  # processing, completed, failed
    is_edited = Column(Boolean, default=False)
    
    # 外部キー
    voice_session_id = Column(Integer, ForeignKey("voice_sessions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # リレーションシップ
    voice_session = relationship("VoiceSession", back_populates="transcriptions")
    user = relationship("User", back_populates="transcriptions")
    analyses = relationship("Analysis", back_populates="transcription")

    def __repr__(self):
        return f"<Transcription(id={self.id}, content='{self.content[:50]}...')>"

    @property
    def is_completed(self) -> bool:
        """文字起こしが完了しているかどうか"""
        return self.status == "completed" and self.processed_at is not None


