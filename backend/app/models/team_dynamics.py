from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class TeamInteraction(Base):
    """チーム相互作用パターン分析テーブル（組織メンバー間の相互作用）"""

    __tablename__ = "team_interactions"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("voice_sessions.id"), nullable=False)
    speaker_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    listener_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    interaction_type = Column(
        String(50), nullable=False
    )  # 'response', 'interruption', 'support', 'challenge'
    interaction_strength = Column(Float, default=0.0)  # 相互作用の強度 (0-1)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    duration = Column(Float, default=0.0)  # 相互作用の持続時間（秒）

    # リレーション（循環参照を避けるため、back_populatesは使用しない）
    team = relationship("Organization")
    session = relationship("VoiceSession")
    speaker = relationship("User", foreign_keys=[speaker_id])
    listener = relationship("User", foreign_keys=[listener_id])

    def __repr__(self):
        return f"<TeamInteraction(id={self.id}, type='{self.interaction_type}', strength={self.interaction_strength})>"

    @property
    def is_positive_interaction(self) -> bool:
        """ポジティブな相互作用かどうか"""
        return self.interaction_type in ["support", "response"]

    @property
    def is_negative_interaction(self) -> bool:
        """ネガティブな相互作用かどうか"""
        return self.interaction_type in ["interruption", "challenge"]

    def get_interaction_category(self) -> str:
        """相互作用のカテゴリを取得"""
        if self.interaction_strength >= 0.7:
            return "strong"
        elif self.interaction_strength >= 0.4:
            return "moderate"
        else:
            return "weak"


class TeamCompatibility(Base):
    """チーム相性スコアテーブル（組織メンバー間の相性分析）"""

    __tablename__ = "team_compatibilities"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    member1_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    member2_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    communication_style_score = Column(
        Float, default=0.0
    )  # コミュニケーションスタイル相性 (0-100)
    personality_compatibility = Column(Float, default=0.0)  # 性格特性相補性 (0-100)
    work_style_score = Column(Float, default=0.0)  # 作業スタイル相性 (0-100)
    overall_compatibility = Column(Float, default=0.0)  # 総合相性スコア (0-100)
    last_updated = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # リレーション（循環参照を避けるため、back_populatesは使用しない）
    team = relationship("Organization")
    member1 = relationship("User", foreign_keys=[member1_id])
    member2 = relationship("User", foreign_keys=[member2_id])

    def __repr__(self):
        return (
            f"<TeamCompatibility(id={self.id}, overall={self.overall_compatibility})>"
        )

    @property
    def is_high_compatibility(self) -> bool:
        """高相性かどうか"""
        return self.overall_compatibility >= 80

    @property
    def is_medium_compatibility(self) -> bool:
        """中程度の相性かどうか"""
        return 50 <= self.overall_compatibility < 80

    @property
    def is_low_compatibility(self) -> bool:
        """低相性かどうか"""
        return self.overall_compatibility < 50

    def calculate_overall_score(self):
        """総合相性スコアを計算"""
        weights = {"communication": 0.4, "personality": 0.3, "work_style": 0.3}

        self.overall_compatibility = (
            self.communication_style_score * weights["communication"]
            + self.personality_compatibility * weights["personality"]
            + self.work_style_score * weights["work_style"]
        )


class TeamCohesion(Base):
    """チーム結束力分析テーブル（組織内チームの結束力分析）"""

    __tablename__ = "team_cohesions"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("voice_sessions.id"), nullable=False)
    cohesion_score = Column(Float, default=0.0)  # 結束力スコア (0-100)
    common_topics = Column(JSON)  # 共通トピックのリスト
    opinion_alignment = Column(Float, default=0.0)  # 意見の一致度 (0-100)
    cultural_formation = Column(Float, default=0.0)  # チーム文化形成度 (0-100)
    improvement_suggestions = Column(Text)  # 改善提案
    analysis_date = Column(DateTime(timezone=True), server_default=func.now())

    # リレーション（循環参照を避けるため、back_populatesは使用しない）
    team = relationship("Organization")
    session = relationship("VoiceSession")

    def __repr__(self):
        return f"<TeamCohesion(id={self.id}, score={self.cohesion_score})>"

    @property
    def cohesion_level(self) -> str:
        """結束力レベルを取得"""
        if self.cohesion_score >= 80:
            return "excellent"
        elif self.cohesion_score >= 60:
            return "good"
        elif self.cohesion_score >= 40:
            return "fair"
        else:
            return "poor"

    @property
    def needs_improvement(self) -> bool:
        """改善が必要かどうか"""
        return self.cohesion_score < 60

    def get_improvement_priority(self) -> str:
        """改善優先度を取得"""
        if self.cohesion_score < 30:
            return "high"
        elif self.cohesion_score < 60:
            return "medium"
        else:
            return "low"


class OrganizationMemberProfile(Base):
    """組織メンバープロファイルテーブル"""

    __tablename__ = "team_member_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    communication_style = Column(
        String(50)
    )  # 'assertive', 'passive', 'collaborative', 'competitive'
    personality_traits = Column(JSON)  # 性格特性の配列
    work_preferences = Column(JSON)  # 作業環境の好み
    interaction_patterns = Column(JSON)  # 相互作用パターンの履歴
    last_updated = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # リレーション
    user = relationship("User", back_populates="team_profiles")
    team = relationship("Organization", back_populates="member_profiles")

    def __repr__(self):
        return f"<OrganizationMemberProfile(id={self.id}, user_id={self.user_id}, team_id={self.team_id})>"

    @property
    def is_assertive_communicator(self) -> bool:
        """アサーティブなコミュニケーターかどうか"""
        return self.communication_style == "assertive"

    @property
    def is_collaborative_worker(self) -> bool:
        """協調的な作業者かどうか"""
        return self.communication_style == "collaborative"

    def has_personality_trait(self, trait: str) -> bool:
        """特定の性格特性を持っているかチェック"""
        if self.personality_traits:
            return trait in self.personality_traits
        return False

    def add_interaction_pattern(self, pattern: dict):
        """相互作用パターンを追加"""
        if not self.interaction_patterns:
            self.interaction_patterns = []

        self.interaction_patterns.append(
            {**pattern, "timestamp": func.now().isoformat()}
        )

    def get_recent_interactions(self, limit: int = 10) -> list:
        """最近の相互作用パターンを取得"""
        if not self.interaction_patterns:
            return []

        # 最新のパターンを取得（タイムスタンプでソート）
        sorted_patterns = sorted(
            self.interaction_patterns,
            key=lambda x: x.get("timestamp", ""),
            reverse=True,
        )

        return sorted_patterns[:limit]
