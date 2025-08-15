from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class TeamInteraction(Base):
    """チーム相互作用パターン分析テーブル"""
    __tablename__ = "team_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("voice_sessions.id"), nullable=False)
    speaker_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    listener_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    interaction_type = Column(String(50), nullable=False)  # 'response', 'interruption', 'support', 'challenge'
    interaction_strength = Column(Float, default=0.0)  # 相互作用の強度 (0-1)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    duration = Column(Float, default=0.0)  # 相互作用の持続時間（秒）
    
    # リレーション
    team = relationship("Team", back_populates="interactions")
    session = relationship("VoiceSession", back_populates="interactions")
    speaker = relationship("User", foreign_keys=[speaker_id])
    listener = relationship("User", foreign_keys=[listener_id])


class TeamCompatibility(Base):
    """チーム相性スコアテーブル"""
    __tablename__ = "team_compatibilities"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    member1_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    member2_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    communication_style_score = Column(Float, default=0.0)  # コミュニケーションスタイル相性 (0-100)
    personality_compatibility = Column(Float, default=0.0)  # 性格特性相補性 (0-100)
    work_style_score = Column(Float, default=0.0)  # 作業スタイル相性 (0-100)
    overall_compatibility = Column(Float, default=0.0)  # 総合相性スコア (0-100)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # リレーション
    team = relationship("Team", back_populates="compatibilities")
    member1 = relationship("User", foreign_keys=[member1_id])
    member2 = relationship("User", foreign_keys=[member2_id])


class TeamCohesion(Base):
    """チーム結束力分析テーブル"""
    __tablename__ = "team_cohesions"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("voice_sessions.id"), nullable=False)
    cohesion_score = Column(Float, default=0.0)  # 結束力スコア (0-100)
    common_topics = Column(JSON)  # 共通トピックのリスト
    opinion_alignment = Column(Float, default=0.0)  # 意見の一致度 (0-100)
    cultural_formation = Column(Float, default=0.0)  # チーム文化形成度 (0-100)
    improvement_suggestions = Column(Text)  # 改善提案
    analysis_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # リレーション
    team = relationship("Team", back_populates="cohesions")
    session = relationship("VoiceSession", back_populates="cohesions")


class TeamMemberProfile(Base):
    """チームメンバープロファイルテーブル"""
    __tablename__ = "team_member_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    communication_style = Column(String(50))  # 'assertive', 'passive', 'collaborative', 'competitive'
    personality_traits = Column(JSON)  # 性格特性の配列
    work_preferences = Column(JSON)  # 作業環境の好み
    interaction_patterns = Column(JSON)  # 相互作用パターンの履歴
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # リレーション
    user = relationship("User", back_populates="team_profiles")
    team = relationship("Team", back_populates="member_profiles")
