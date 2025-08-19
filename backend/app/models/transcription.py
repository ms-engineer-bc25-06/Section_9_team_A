from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
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
    speakers = Column(Text, nullable=True)  # 話者情報（JSON文字列として保存）
    
    # 処理状態
    status = Column(String(50), default="processing")  # processing, completed, failed
    is_edited = Column(Boolean, default=False)
    
    # 外部キー
    voice_session_id = Column(Integer, ForeignKey("voice_sessions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)

    # リレーションシップ（循環参照を避けるため、back_populatesは使用しない）
    voice_session = relationship("VoiceSession")
    user = relationship("User")

    def __repr__(self):
        return f"<Transcription(id={self.id}, content='{self.content[:50]}...')>"

    @property
    def is_completed(self) -> bool:
        """文字起こしが完了しているかどうか"""
        return self.status == "completed" and self.processed_at is not None

    @property
    def is_processing(self) -> bool:
        """文字起こしが処理中かどうか"""
        return self.status == "processing"

    @property
    def is_failed(self) -> bool:
        """文字起こしが失敗しているかどうか"""
        return self.status == "failed"

    def mark_as_completed(self, processed_at: datetime = None):
        """文字起こしを完了としてマーク"""
        self.status = "completed"
        self.processed_at = processed_at or datetime.utcnow()

    def mark_as_failed(self):
        """文字起こしを失敗としてマーク"""
        self.status = "failed"

    def update_content(self, new_content: str, confidence_score: float = None):
        """文字起こし内容を更新"""
        self.content = new_content
        if confidence_score is not None:
            self.confidence_score = confidence_score
        self.is_edited = True
        self.updated_at = datetime.utcnow()
