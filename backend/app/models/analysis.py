# TODO: 仮Analysisテーブル（後ほど消す）
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


class Analysis(Base):
    """分析モデル"""

    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    voice_session_id = Column(Integer, ForeignKey("voice_sessions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 分析結果
    analysis_type = Column(
        String(100), nullable=False
    )  # sentiment, topic, summary, etc.
    result_data = Column(Text, nullable=True)  # JSON形式で分析結果を保存
    confidence_score = Column(Float, nullable=True)

    # 状態
    is_completed = Column(Boolean, default=False)

    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # リレーションシップ
    voice_session = relationship("VoiceSession", back_populates="analyses")
    user = relationship("User", back_populates="analyses")

    def __repr__(self):
        return f"<Analysis(id={self.id}, analysis_type='{self.analysis_type}')>"
