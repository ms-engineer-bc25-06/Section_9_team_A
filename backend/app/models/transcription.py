# TODO: 仮Transcriptionテーブル（後ほど消す）
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

from app.core.database import Base


class Transcription(Base):
    """文字起こしモデル"""

    __tablename__ = "transcriptions"

    id = Column(Integer, primary_key=True, index=True)
    voice_session_id = Column(Integer, ForeignKey("voice_sessions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 文字起こし内容
    text = Column(Text, nullable=False)
    start_time = Column(Float, nullable=True)  # 開始時間（秒）
    end_time = Column(Float, nullable=True)  # 終了時間（秒）
    confidence = Column(Float, nullable=True)  # 信頼度

    # 状態
    is_processed = Column(Boolean, default=False)

    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # リレーションシップ
    voice_session = relationship("VoiceSession", back_populates="transcriptions")
    user = relationship("User", back_populates="transcriptions")

    def __repr__(self):
        return (
            f"<Transcription(id={self.id}, voice_session_id={self.voice_session_id})>"
        )
