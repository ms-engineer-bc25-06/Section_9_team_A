from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Analysis(Base):
    """分析結果モデル"""

    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    voice_session_id = Column(Integer, ForeignKey("voice_sessions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 分析情報
    analysis_type = Column(String(100), nullable=False)  # sentiment, topics, summary, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # 分析結果
    result_data = Column(JSON, nullable=False)  # 分析結果の詳細データ
    summary = Column(Text, nullable=True)       # 分析結果の要約
    
    # 統計情報
    confidence_score = Column(Float, nullable=True)
    processing_time = Column(Float, nullable=True)  # 処理時間（秒）
    
    # 状態
    status = Column(String(50), default="completed")  # pending, processing, completed, failed
    is_public = Column(Boolean, default=False)
    
    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # リレーションシップ
    voice_session = relationship("VoiceSession", back_populates="analyses")
    user = relationship("User", back_populates="analyses")
    
    def __repr__(self):
        return f"<Analysis(id={self.id}, type='{self.analysis_type}', title='{self.title}')>"
