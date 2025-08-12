from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


class TeamInteractionAnalysis(BaseModel):
    """チーム相互作用分析結果スキーマ"""
    interaction_matrix: Dict[str, Dict[str, Any]] = Field(..., description="相互作用マトリックス")
    total_interactions: int = Field(..., description="総相互作用数")
    silent_members: List[int] = Field(..., description="沈黙メンバーのユーザーIDリスト")
    communication_efficiency: float = Field(..., description="コミュニケーション効率スコア (0-100)")
    interaction_types_distribution: Dict[str, int] = Field(..., description="相互作用タイプの分布")


class TeamCompatibilityAnalysis(BaseModel):
    """チーム相性分析結果スキーマ"""
    compatibilities: List[Dict[str, Any]] = Field(..., description="メンバー間相性データ")
    team_balance_score: float = Field(..., description="チーム全体のバランススコア (0-100)")
    compatibility_matrix: Dict[int, Dict[int, float]] = Field(..., description="相性マトリックス")


class TeamCohesionAnalysis(BaseModel):
    """チーム結束力分析結果スキーマ"""
    cohesion_score: float = Field(..., description="結束力スコア (0-100)")
    common_topics: List[str] = Field(..., description="共通トピックのリスト")
    opinion_alignment: float = Field(..., description="意見の一致度 (0-100)")
    cultural_formation: float = Field(..., description="チーム文化形成度 (0-100)")
    improvement_suggestions: str = Field(..., description="改善提案")


class TeamMemberProfileCreate(BaseModel):
    """チームメンバープロファイル作成スキーマ"""
    communication_style: Optional[str] = Field(None, description="コミュニケーションスタイル")
    personality_traits: Optional[List[str]] = Field(None, description="性格特性のリスト")
    work_preferences: Optional[Dict[str, Any]] = Field(None, description="作業環境の好み")
    interaction_patterns: Optional[Dict[str, Any]] = Field(None, description="相互作用パターンの履歴")


class TeamMemberProfileUpdate(BaseModel):
    """チームメンバープロファイル更新スキーマ"""
    communication_style: Optional[str] = Field(None, description="コミュニケーションスタイル")
    personality_traits: Optional[List[str]] = Field(None, description="性格特性のリスト")
    work_preferences: Optional[Dict[str, Any]] = Field(None, description="作業環境の好み")
    interaction_patterns: Optional[Dict[str, Any]] = Field(None, description="相互作用パターンの履歴")


class TeamMemberProfileResponse(BaseModel):
    """チームメンバープロファイル応答スキーマ"""
    id: int = Field(..., description="プロファイルID")
    user_id: int = Field(..., description="ユーザーID")
    team_id: int = Field(..., description="チームID")
    communication_style: Optional[str] = Field(None, description="コミュニケーションスタイル")
    personality_traits: Optional[List[str]] = Field(None, description="性格特性のリスト")
    work_preferences: Optional[Dict[str, Any]] = Field(None, description="作業環境の好み")
    interaction_patterns: Optional[Dict[str, Any]] = Field(None, description="相互作用パターンの履歴")
    last_updated: Optional[datetime] = Field(None, description="最終更新日時")


class TeamDynamicsSummary(BaseModel):
    """チームダイナミクス総合サマリースキーマ"""
    team_id: int = Field(..., description="チームID")
    compatibility_score: float = Field(..., description="相性スコア (0-100)")
    last_updated: Optional[datetime] = Field(None, description="最終更新日時")
    recommendations: List[str] = Field(..., description="推奨事項のリスト")


class InteractionPattern(BaseModel):
    """相互作用パターンスキーマ"""
    speaker_id: int = Field(..., description="発言者ID")
    listener_id: int = Field(..., description="聴取者ID")
    interaction_type: str = Field(..., description="相互作用タイプ")
    strength: float = Field(..., description="相互作用の強度 (0-1)")
    duration: float = Field(..., description="相互作用の持続時間（秒）")


class CompatibilityScore(BaseModel):
    """相性スコアスキーマ"""
    member1_id: int = Field(..., description="メンバー1のID")
    member2_id: int = Field(..., description="メンバー2のID")
    communication_style_score: float = Field(..., description="コミュニケーションスタイル相性 (0-100)")
    personality_compatibility: float = Field(..., description="性格特性相補性 (0-100)")
    work_style_score: float = Field(..., description="作業スタイル相性 (0-100)")
    overall_compatibility: float = Field(..., description="総合相性スコア (0-100)")


class CohesionMetrics(BaseModel):
    """結束力メトリクススキーマ"""
    cohesion_score: float = Field(..., description="結束力スコア (0-100)")
    common_topics_count: int = Field(..., description="共通トピック数")
    opinion_alignment: float = Field(..., description="意見の一致度 (0-100)")
    cultural_formation: float = Field(..., description="チーム文化形成度 (0-100)")
    team_size: int = Field(..., description="チームサイズ")
    active_participants: int = Field(..., description="アクティブ参加者数")


class TeamDynamicsReport(BaseModel):
    """チームダイナミクスレポートスキーマ"""
    team_id: int = Field(..., description="チームID")
    report_date: datetime = Field(..., description="レポート作成日時")
    interaction_analysis: TeamInteractionAnalysis = Field(..., description="相互作用分析結果")
    compatibility_analysis: TeamCompatibilityAnalysis = Field(..., description="相性分析結果")
    cohesion_analysis: TeamCohesionAnalysis = Field(..., description="結束力分析結果")
    summary: TeamDynamicsSummary = Field(..., description="総合サマリー")
    recommendations: List[str] = Field(..., description="総合推奨事項")


class CommunicationStyle(BaseModel):
    """コミュニケーションスタイルスキーマ"""
    style: str = Field(..., description="スタイル名")
    description: str = Field(..., description="スタイルの説明")
    characteristics: List[str] = Field(..., description="特徴のリスト")
    compatibility_scores: Dict[str, float] = Field(..., description="他スタイルとの相性スコア")


class PersonalityTrait(BaseModel):
    """性格特性スキーマ"""
    trait: str = Field(..., description="特性名")
    category: str = Field(..., description="特性カテゴリ")
    description: str = Field(..., description="特性の説明")
    complementary_traits: List[str] = Field(..., description="相補的な特性のリスト")


class WorkPreference(BaseModel):
    """作業環境の好みスキーマ"""
    preference_type: str = Field(..., description="好みのタイプ")
    value: str = Field(..., description="好みの値")
    importance: int = Field(..., description="重要度 (1-5)")
    description: str = Field(..., description="好みの説明")
