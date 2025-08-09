from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base


class Analysis(Base):
    """分析結果モデル"""

    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    
    # 分析情報
    analysis_id = Column(String(255), unique=True, index=True, nullable=False)
    analysis_type = Column(String(50), nullable=False)  # sentiment, topic, summary, etc.
    title = Column(String(255), nullable=True)
    
    # 分析結果
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    keywords = Column(JSON, nullable=True)  # キーワードリスト
    topics = Column(JSON, nullable=True)  # トピックリスト
    
    # 感情分析
    sentiment_score = Column(Float, nullable=True)  # -1.0 to 1.0
    sentiment_label = Column(String(50), nullable=True)  # positive, negative, neutral
    
    # 統計情報
    word_count = Column(Integer, nullable=True)
    sentence_count = Column(Integer, nullable=True)
    speaking_time = Column(Float, nullable=True)  # 秒単位
    
    # 処理状態
    status = Column(String(50), default="processing")  # processing, completed, failed
    confidence_score = Column(Float, nullable=True)  # 0.0-1.0
    
    # 外部キー
    voice_session_id = Column(Integer, ForeignKey("voice_sessions.id"), nullable=True)
    transcription_id = Column(Integer, ForeignKey("transcriptions.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # リレーションシップ
    voice_session = relationship("VoiceSession", back_populates="analyses")
    transcription = relationship("Transcription", back_populates="analyses")
    user = relationship("User", back_populates="analyses")

    def __repr__(self):
        return f"<Analysis(id={self.id}, type='{self.analysis_type}', title='{self.title}')>"

    @property
    def is_completed(self) -> bool:
        """分析が完了しているかどうか"""
        return self.status == "completed" and self.processed_at is not None


