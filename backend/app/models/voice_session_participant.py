from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.models.base import Base


class VoiceSessionParticipant(Base):
    """音声セッション参加者モデル"""

    __tablename__ = "voice_session_participants"

    id = Column(Integer, primary_key=True, index=True)

    # 外部キー
    voice_session_id = Column(Integer, ForeignKey("voice_sessions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 参加者情報
    role = Column(String(50), default="participant")  # host, moderator, participant
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    left_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)

    # リレーションシップ
    voice_session = relationship("VoiceSession", back_populates="participants")
    user = relationship("User", back_populates="voice_session_participations")

    def __repr__(self) -> str:
        return f"<VoiceSessionParticipant(session_id={self.voice_session_id}, user_id={self.user_id}, role='{self.role}')>"
