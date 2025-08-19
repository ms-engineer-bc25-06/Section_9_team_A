from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field
from enum import Enum

from .common import TimestampMixin


class DifficultyLevel(str, Enum):
    """難易度レベル"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class PriorityLevel(str, Enum):
    """優先度レベル"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class GoalStatus(str, Enum):
    """目標のステータス"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"


class ImprovementStep(BaseModel):
    """改善ステップ"""
    id: Optional[int] = None
    title: str = Field(..., description="ステップのタイトル")
    description: str = Field(..., description="ステップの詳細説明")
    difficulty: DifficultyLevel = Field(..., description="難易度レベル")
    estimated_duration_days: int = Field(..., description="推定所要日数")
    priority: PriorityLevel = Field(..., description="優先度")
    resources: Optional[List[str]] = Field(default=[], description="参考リソース")
    completed: bool = Field(default=False, description="完了フラグ")
    completed_at: Optional[datetime] = Field(default=None, description="完了日時")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ImprovementStepCreate(BaseModel):
    """改善ステップ作成"""
    title: str = Field(..., description="ステップのタイトル")
    description: str = Field(..., description="ステップの詳細説明")
    difficulty: DifficultyLevel = Field(..., description="難易度レベル")
    estimated_duration_days: int = Field(..., description="推定所要日数")
    priority: PriorityLevel = Field(..., description="優先度")
    resources: Optional[List[str]] = Field(default=[], description="参考リソース")


class ImprovementStepUpdate(BaseModel):
    """改善ステップ更新"""
    title: Optional[str] = Field(None, description="ステップのタイトル")
    description: Optional[str] = Field(None, description="ステップの詳細説明")
    difficulty: Optional[DifficultyLevel] = Field(None, description="難易度レベル")
    estimated_duration_days: Optional[int] = Field(None, description="推定所要日数")
    priority: Optional[PriorityLevel] = Field(None, description="優先度")
    resources: Optional[List[str]] = Field(None, description="参考リソース")
    completed: Optional[bool] = Field(None, description="完了フラグ")


class ImprovementStepResponse(ImprovementStep):
    """改善ステップレスポンス"""
    pass


class ImprovementPlan(BaseModel):
    """改善プラン"""
    id: Optional[int] = None
    user_id: int = Field(..., description="ユーザーID")
    title: str = Field(..., description="プランのタイトル")
    description: str = Field(..., description="プランの詳細説明")
    current_skill_level: str = Field(..., description="現在のスキルレベル")
    target_skill_level: str = Field(..., description="目標スキルレベル")
    overall_difficulty: DifficultyLevel = Field(..., description="全体の難易度")
    estimated_total_duration_days: int = Field(..., description="推定総所要日数")
    steps: List[ImprovementStep] = Field(default=[], description="改善ステップ一覧")
    progress_percentage: float = Field(default=0.0, description="進捗率（%）")
    status: str = Field(default="active", description="プランのステータス")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ImprovementPlanCreate(BaseModel):
    """改善プラン作成"""
    title: str = Field(..., description="プランのタイトル")
    description: str = Field(..., description="プランの詳細説明")
    current_skill_level: str = Field(..., description="現在のスキルレベル")
    target_skill_level: str = Field(..., description="目標スキルレベル")


class ImprovementPlanUpdate(BaseModel):
    """改善プラン更新"""
    title: Optional[str] = Field(None, description="プランのタイトル")
    description: Optional[str] = Field(None, description="プランの詳細説明")
    current_skill_level: Optional[str] = Field(None, description="現在のスキルレベル")
    target_skill_level: Optional[str] = Field(None, description="目標スキルレベル")
    status: Optional[str] = Field(None, description="プランのステータス")


class ImprovementPlanResponse(ImprovementPlan):
    """改善プランレスポンス"""
    pass


class GrowthGoal(BaseModel):
    """成長目標"""
    id: Optional[int] = None
    user_id: int = Field(..., description="ユーザーID")
    title: str = Field(..., description="目標のタイトル")
    description: str = Field(..., description="目標の詳細説明")
    category: str = Field(..., description="目標のカテゴリ")
    target_date: date = Field(..., description="目標達成予定日")
    status: GoalStatus = Field(default=GoalStatus.NOT_STARTED, description="目標のステータス")
    progress_percentage: float = Field(default=0.0, description="進捗率（%）")
    milestones: Optional[List[str]] = Field(default=[], description="マイルストーン")
    notes: Optional[str] = Field(default=None, description="メモ")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class GrowthGoalCreate(BaseModel):
    """成長目標作成"""
    title: str = Field(..., description="目標のタイトル")
    description: str = Field(..., description="目標の詳細説明")
    category: str = Field(..., description="目標のカテゴリ")
    target_date: date = Field(..., description="目標達成予定日")
    milestones: Optional[List[str]] = Field(default=[], description="マイルストーン")
    notes: Optional[str] = Field(default=None, description="メモ")


class GrowthGoalUpdate(BaseModel):
    """成長目標更新"""
    title: Optional[str] = Field(None, description="目標のタイトル")
    description: Optional[str] = Field(None, description="目標の詳細説明")
    category: Optional[str] = Field(None, description="目標のカテゴリ")
    target_date: Optional[date] = Field(None, description="目標達成予定日")
    status: Optional[GoalStatus] = Field(None, description="目標のステータス")
    progress_percentage: Optional[float] = Field(None, description="進捗率（%）")
    milestones: Optional[List[str]] = Field(None, description="マイルストーン")
    notes: Optional[str] = Field(None, description="メモ")


class GrowthGoalResponse(GrowthGoal):
    """成長目標レスポンス"""
    pass


class PersonalGrowthProfile(BaseModel):
    """個人成長プロフィール"""
    id: Optional[int] = None
    user_id: int = Field(..., description="ユーザーID")
    overall_level: str = Field(..., description="全体的なレベル")
    strengths: List[str] = Field(default=[], description="強み")
    areas_for_improvement: List[str] = Field(default=[], description="改善が必要な領域")
    learning_style: str = Field(..., description="学習スタイル")
    preferred_methods: List[str] = Field(default=[], description="好ましい学習方法")
    time_availability: str = Field(..., description="学習時間の確保状況")
    motivation_level: str = Field(..., description="モチベーションレベル")
    last_assessment_date: Optional[date] = Field(default=None, description="最終評価日")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PersonalGrowthProfileResponse(PersonalGrowthProfile):
    """個人成長プロフィールレスポンス"""
    pass
