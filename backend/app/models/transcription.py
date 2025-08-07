from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    Float,
    DECIMAL,
    Index,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base


class Transcription(Base):
    """転写モデル"""

    __tablename__ = "transcriptions"

    id = Column(Integer, primary_key=True, index=True)

    # 外部キー
    voice_session_id = Column(Integer, ForeignKey("voice_sessions.id"), nullable=False)
    speaker_id = Column(
        Integer, ForeignKey("users.id"), nullable=True
    )  # 話者ID（NULL可）

    # 転写内容
    text_content = Column(Text, nullable=False)
    start_time_seconds = Column(DECIMAL(10, 3), nullable=False)  # 開始時間（秒）
    end_time_seconds = Column(DECIMAL(10, 3), nullable=False)  # 終了時間（秒）
    confidence_score = Column(DECIMAL(4, 3), nullable=True)  # 信頼度（0-1）
    language = Column(String(10), default="ja")  # 言語

    # 転写状態
    is_final = Column(Boolean, default=True)  # 確定転写か部分転写か
    is_processed = Column(Boolean, default=False)  # 後処理済みか

    # メタデータ
    word_timestamps = Column(Text, nullable=True)  # 単語レベルのタイムスタンプ（JSON）
    speaker_confidence = Column(DECIMAL(4, 3), nullable=True)  # 話者識別の信頼度

    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)

    # リレーションシップ
    voice_session = relationship("VoiceSession", back_populates="transcriptions")
    speaker = relationship("User", back_populates="transcriptions")

    def __repr__(self):
        return f"<Transcription(id={self.id}, session_id={self.voice_session_id}, text='{self.text_content[:50]}...')>"

    @property
    def duration(self) -> float:
        """転写の継続時間を取得"""
        return float(self.end_time_seconds - self.start_time_seconds)

    @property
    def is_partial(self) -> bool:
        """部分転写かどうかを判定"""
        return not self.is_final


# インデックス
Index("idx_transcriptions_voice_session_id", Transcription.voice_session_id)
Index("idx_transcriptions_speaker_id", Transcription.speaker_id)
Index("idx_transcriptions_start_time", Transcription.start_time_seconds)
Index("idx_transcriptions_created_at", Transcription.created_at)
Index("idx_transcriptions_is_final", Transcription.is_final)
Index("idx_transcriptions_language", Transcription.language)
