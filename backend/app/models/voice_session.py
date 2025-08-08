from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    Float,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class VoiceSession(Base):
    """音声セッションモデル"""

    __tablename__ = "voice_sessions"

    id = Column(Integer, primary_key=True, index=True)

    # セッション情報
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)

    # 音声関連
    audio_file_path = Column(String(500), nullable=True)
    audio_duration = Column(Float, nullable=True)  # 秒単位
    audio_format = Column(String(50), nullable=True)  # mp3, wav, etc.
    file_size = Column(Integer, nullable=True)  # バイト単位

    # セッション状態
    status = Column(String(50), default="active")  # active, completed, archived
    is_public = Column(Boolean, default=False)
    is_analyzed = Column(Boolean, default=False)

    # 参加者情報
    participant_count = Column(Integer, default=1)
    participants = Column(Text, nullable=True)  # JSON形式で参加者情報を保存

    # 分析結果
    analysis_summary = Column(Text, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    key_topics = Column(Text, nullable=True)  # JSON形式でトピックを保存

    # 外部キー
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)

    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)

    # リレーションシップ
    user = relationship("User", back_populates="voice_sessions")
    team = relationship("Team", back_populates="voice_sessions")
    transcriptions = relationship("Transcription", back_populates="voice_session")
    analyses = relationship("Analysis", back_populates="voice_session")

    def __repr__(self):
        return f"<VoiceSession(id={self.id}, session_id='{self.session_id}', title='{self.title}')>"

    @property
    def duration(self) -> float:
        """セッションの継続時間を計算"""
        if self.started_at and self.ended_at:
            return (self.ended_at - self.started_at).total_seconds()
        return 0.0

    @property
    def is_completed(self) -> bool:
        """セッションが完了しているかどうか"""
        return self.status == "completed" and self.ended_at is not None
