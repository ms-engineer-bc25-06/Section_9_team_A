from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


class ComparisonType(str, Enum):
    """比較分析のタイプ"""
    SELF_IMPROVEMENT = "self_improvement"      # 自己改善（過去の自分との比較）
    ANONYMOUS_PEER = "anonymous_peer"          # 匿名化された同僚との比較
    TEAM_AGGREGATE = "team_aggregate"          # チーム集約データとの比較
    ORGANIZATION_BENCHMARK = "organization_benchmark"  # 組織ベンチマークとの比較


class ComparisonScope(str, Enum):
    """比較対象の範囲"""
    COMMUNICATION_SKILLS = "communication_skills"      # コミュニケーションスキル
    LEADERSHIP = "leadership"                          # リーダーシップ
    COLLABORATION = "collaboration"                    # 協働性
    PROBLEM_SOLVING = "problem_solving"                # 問題解決
    EMOTIONAL_INTELLIGENCE = "emotional_intelligence"  # 感情知性
    OVERALL_PERFORMANCE = "overall_performance"        # 総合的なパフォーマンス


class ComparisonRequest(BaseModel):
    """比較分析リクエスト用スキーマ"""
    comparison_type: ComparisonType = Field(..., description="比較分析のタイプ")
    comparison_scope: ComparisonScope = Field(..., description="比較対象の範囲")
    time_period: str = Field(..., description="比較対象期間（7d, 30d, 90d, 1y）")
    include_self: bool = Field(True, description="自分のデータを含めるか")
    anonymization_level: str = Field("high", description="匿名化レベル（high, medium, low）")
    
    # オプション設定
    focus_on_strengths: bool = Field(True, description="強みに焦点を当てるか")
    include_growth_suggestions: bool = Field(True, description="成長提案を含めるか")
    exclude_ranking: bool = Field(True, description="順位付けを除外するか")


class ComparisonResult(BaseModel):
    """比較分析結果用スキーマ"""
    comparison_id: str = Field(..., description="比較分析ID")
    comparison_type: ComparisonType = Field(..., description="比較分析のタイプ")
    comparison_scope: ComparisonScope = Field(..., description="比較対象の範囲")
    generated_at: datetime = Field(..., description="生成日時")
    
    # 統計情報（個人の特定を避ける）
    total_participants: int = Field(..., description="比較対象の総人数")
    confidence_level: float = Field(..., description="分析の信頼度（0.0-1.0）")
    
    # 比較結果（匿名化・集約化）
    performance_distribution: Dict[str, float] = Field(..., description="パフォーマンス分布")
    strength_areas: List[str] = Field(..., description="強みの領域")
    growth_areas: List[str] = Field(..., description="成長の領域")
    
    # 建設的な提案
    improvement_suggestions: List[str] = Field(..., description="改善提案")
    best_practices: List[str] = Field(..., description="ベストプラクティス")
    
    # 心理的安全性を保つための設定
    is_anonymous: bool = Field(True, description="匿名化されているか")
    no_individual_ranking: bool = Field(True, description="個人の順位付けは含まれていないか")


class SelfComparisonResult(BaseModel):
    """自己比較結果用スキーマ（過去の自分との比較）"""
    comparison_id: str = Field(..., description="比較分析ID")
    current_period: str = Field(..., description="現在の期間")
    previous_period: str = Field(..., description="過去の期間")
    
    # 成長の可視化
    growth_metrics: Dict[str, float] = Field(..., description="成長メトリクス")
    improvement_areas: List[str] = Field(..., description="改善された領域")
    maintained_strengths: List[str] = Field(..., description="維持されている強み")
    
    # 建設的な提案
    next_steps: List[str] = Field(..., description="次のステップ")
    goal_suggestions: List[str] = Field(..., description="目標提案")


class AnonymousPeerComparison(BaseModel):
    """匿名化された同僚比較用スキーマ"""
    comparison_id: str = Field(..., description="比較分析ID")
    
    # 集約された統計情報のみ
    peer_average: Dict[str, float] = Field(..., description="同僚の平均値")
    peer_percentile: Dict[str, float] = Field(..., description="同僚中のパーセンタイル（順位は表示しない）")
    peer_distribution: Dict[str, Dict[str, int]] = Field(..., description="同僚の分布（個人の特定を避ける）")
    
    # 建設的な比較
    relative_strengths: List[str] = Field(..., description="相対的な強み")
    learning_opportunities: List[str] = Field(..., description="学習機会")


class TeamComparisonResult(BaseModel):
    """チーム比較結果用スキーマ"""
    comparison_id: str = Field(..., description="比較分析ID")
    team_id: str = Field(..., description="チームID")
    
    # チーム全体の統計
    team_performance: Dict[str, float] = Field(..., description="チーム全体のパフォーマンス")
    team_strengths: List[str] = Field(..., description="チームの強み")
    team_improvement_areas: List[str] = Field(..., description="チームの改善領域")
    
    # 個人の位置づけ（匿名化）
    individual_position: Dict[str, str] = Field(..., description="個人の位置づけ（具体的な数値は含まない）")
    contribution_areas: List[str] = Field(..., description="貢献できる領域")


class TeamToTeamComparison(BaseModel):
    """チーム間比較用スキーマ"""
    comparison_id: str = Field(..., description="比較分析ID")
    source_team_id: str = Field(..., description="比較元チームID")
    target_team_id: str = Field(..., description="比較対象チームID")
    
    # チーム間の相対的な比較（順位は含まない）
    relative_performance: Dict[str, str] = Field(..., description="相対的なパフォーマンス（数値は含まない）")
    shared_strengths: List[str] = Field(..., description="両チームの共通の強み")
    complementary_areas: List[str] = Field(..., description="補完し合える領域")
    
    # 学習機会
    learning_opportunities: List[str] = Field(..., description="相互学習の機会")
    collaboration_potential: List[str] = Field(..., description="協働の可能性")


class IndustryBenchmarkComparison(BaseModel):
    """業界平均比較用スキーマ"""
    comparison_id: str = Field(..., description="比較分析ID")
    industry: str = Field(..., description="業界名")
    company_size: str = Field(..., description="企業規模")
    
    # 業界平均との比較
    industry_average: Dict[str, float] = Field(..., description="業界平均値")
    relative_position: Dict[str, str] = Field(..., description="業界内での相対的位置（数値は含まない）")
    
    # 業界のベストプラクティス
    industry_best_practices: List[str] = Field(..., description="業界のベストプラクティス")
    improvement_opportunities: List[str] = Field(..., description="業界水準に向けた改善機会")
    
    # データの信頼性
    data_source: str = Field(..., description="データソース")
    last_updated: datetime = Field(..., description="最終更新日時")
    confidence_level: float = Field(..., description="データの信頼度")


class ComparisonReport(BaseModel):
    """比較分析レポート用スキーマ"""
    report_id: str = Field(..., description="レポートID")
    comparison_id: str = Field(..., description="比較分析ID")
    generated_at: datetime = Field(..., description="生成日時")
    
    # レポートの概要
    title: str = Field(..., description="レポートタイトル")
    summary: str = Field(..., description="レポート概要")
    key_findings: List[str] = Field(..., description="主要な発見")
    
    # 詳細分析
    detailed_analysis: Dict[str, Any] = Field(..., description="詳細分析結果")
    visualizations: List[Dict[str, Any]] = Field(..., description="可視化データ")
    
    # アクションプラン
    action_items: List[str] = Field(..., description="アクション項目")
    next_steps: List[str] = Field(..., description="次のステップ")
    
    # レポート設定
    report_format: str = Field("pdf", description="レポート形式（pdf, html, json）")
    include_charts: bool = Field(True, description="チャートを含めるか")
    include_recommendations: bool = Field(True, description="推奨事項を含めるか")


class ReportGenerationRequest(BaseModel):
    """レポート生成リクエスト用スキーマ"""
    comparison_id: str = Field(..., description="比較分析ID")
    report_format: str = Field("pdf", description="レポート形式")
    include_charts: bool = Field(True, description="チャートを含めるか")
    include_recommendations: bool = Field(True, description="推奨事項を含めるか")
    custom_sections: List[str] = Field(default_factory=list, description="カスタムセクション")
    language: str = Field("ja", description="レポート言語")


class ComparisonFilters(BaseModel):
    """比較分析フィルター用スキーマ"""
    department: Optional[str] = Field(None, description="部署フィルター")
    experience_level: Optional[str] = Field(None, description="経験レベルフィルター")
    role: Optional[str] = Field(None, description="役割フィルター")
    project_type: Optional[str] = Field(None, description="プロジェクトタイプフィルター")
    
    # 心理的安全性を保つための制限
    min_group_size: int = Field(5, description="最小グループサイズ（個人の特定を避けるため）")
    max_detail_level: str = Field("aggregated", description="詳細レベル（individual, aggregated, summary）")


class ComparisonAnalytics(BaseModel):
    """比較分析の統計情報用スキーマ"""
    total_comparisons: int = Field(..., description="総比較回数")
    user_participation_rate: float = Field(..., description="ユーザー参加率")
    average_confidence: float = Field(..., description="平均信頼度")
    
    # 心理的安全性の指標
    safety_score: float = Field(..., description="心理的安全性スコア（0.0-1.0）")
    user_feedback_rating: float = Field(..., description="ユーザーフィードバック評価（0.0-1.0）")
    
    # 改善提案の効果
    improvement_adoption_rate: float = Field(..., description="改善提案の採用率")
    user_satisfaction: float = Field(..., description="ユーザー満足度")


class ComparisonPrivacySettings(BaseModel):
    """比較分析のプライバシー設定用スキーマ"""
    user_id: int = Field(..., description="ユーザーID")
    
    # 比較への参加設定
    participate_in_comparisons: bool = Field(True, description="比較分析に参加するか")
    allow_anonymous_comparison: bool = Field(True, description="匿名化された比較を許可するか")
    allow_team_comparison: bool = Field(True, description="チーム比較を許可するか")
    
    # データの可視性設定
    data_visibility_level: str = Field("aggregated", description="データの可視性レベル")
    include_in_benchmarks: bool = Field(True, description="ベンチマークに含めるか")
    
    # 通知設定
    notify_comparison_results: bool = Field(True, description="比較結果の通知を受け取るか")
    notify_improvement_suggestions: bool = Field(True, description="改善提案の通知を受け取るか")
