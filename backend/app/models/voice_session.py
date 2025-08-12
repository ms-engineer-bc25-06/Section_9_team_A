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

from app.models.base import Base


class VoiceSession(Base):
    """音声セッションモデル（Alembicマイグレーションに準拠）"""

    __tablename__ = "voice_sessions"

    # 基本情報
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, nullable=False)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)

    # 音声ファイル情報
    audio_file_path = Column(String(500), nullable=True)
    audio_duration = Column(Float, nullable=True)
    audio_format = Column(String(50), nullable=True)
    file_size = Column(Integer, nullable=True)

    # ステータス/可視性
    status = Column(String(50), nullable=True)
    is_public = Column(Boolean, nullable=True)
    is_analyzed = Column(Boolean, nullable=True)

    # 参加者関連
    participant_count = Column(Integer, nullable=True)
    participants = Column(Text, nullable=True)

    # 分析関連
    analysis_summary = Column(Text, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    key_topics = Column(Text, nullable=True)

    # 所有者/チーム
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)

    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)

    # リレーションシップ
    # 注意: User 側の back_populates は "voice_sessions" なので、こちらは "host" 名を維持
    # （FK 名は user_id だが、既存の User.voice_sessions と整合させるため）
    host = relationship("User", back_populates="voice_sessions", foreign_keys=[user_id])
    team = relationship("Team", back_populates="voice_sessions")
    transcriptions = relationship("Transcription", back_populates="voice_session")
    analyses = relationship("Analysis", back_populates="voice_session")
    
    # チームダイナミクス分析関連
    interactions = relationship("TeamInteraction", back_populates="session")
    cohesions = relationship("TeamCohesion", back_populates="session")

    def __repr__(self) -> str:
        return f"<VoiceSession(id={self.id}, session_id='{self.session_id}', title='{self.title}')>"
