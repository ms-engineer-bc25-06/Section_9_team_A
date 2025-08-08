from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(String(255), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    key_topics = Column(Text, nullable=True)  # JSON形式でトピックを保存
    insights = Column(Text, nullable=True)     # JSON形式で洞察を保存
    
    # 外部キー
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    voice_session_id = Column(Integer, ForeignKey("voice_sessions.id"), nullable=True)
    
    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # リレーションシップ
    user = relationship("User", back_populates="analyses")
    voice_session = relationship("VoiceSession", back_populates="analyses")

    def __repr__(self):
        return f"<Analysis(id={self.id}, analysis_id='{self.analysis_id}')>"