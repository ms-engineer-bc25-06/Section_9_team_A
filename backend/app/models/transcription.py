from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Transcription(Base):
    __tablename__ = "transcriptions"

    id = Column(Integer, primary_key=True, index=True)
    transcription_id = Column(String(255), unique=True, index=True, nullable=False)
    content = Column(Text, nullable=False)
    language = Column(String(10), default="ja")
    confidence_score = Column(Float, nullable=True)
    start_time = Column(Float, nullable=True)  # 秒単位
    end_time = Column(Float, nullable=True)    # 秒単位
    
    # 外部キー
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    voice_session_id = Column(Integer, ForeignKey("voice_sessions.id"), nullable=True)
    
    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # リレーションシップ
    user = relationship("User", back_populates="transcriptions")
    voice_session = relationship("VoiceSession", back_populates="transcriptions")

    def __repr__(self):
        return f"<Transcription(id={self.id}, transcription_id='{self.transcription_id}')>"