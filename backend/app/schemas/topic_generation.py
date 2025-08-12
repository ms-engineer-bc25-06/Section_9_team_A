from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class TopicCategory(str, Enum):
    """トークテーマのカテゴリ"""
    WORK = "work"
    PERSONAL = "personal"
    HOBBY = "hobby"
    CURRENT_EVENTS = "current_events"
    TECHNOLOGY = "technology"
    CULTURE = "culture"
    SPORTS = "sports"
    FOOD = "food"
    TRAVEL = "travel"
    OTHER = "other"

class TopicDifficulty(str, Enum):
    """トークテーマの難易度"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class TopicSuggestion(BaseModel):
    """個別のトークテーマ提案"""
    title: str = Field(..., description="テーマのタイトル")
    description: str = Field(..., description="テーマの詳細説明")
    category: TopicCategory = Field(..., description="テーマのカテゴリ")
    difficulty: TopicDifficulty = Field(..., description="テーマの難易度")
    estimated_duration: int = Field(..., description="推定所要時間（分）")
    conversation_starters: List[str] = Field(..., description="会話のきっかけとなる質問・話題")
    related_keywords: List[str] = Field(..., description="関連キーワード")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="提案の信頼度スコア")

class PersonalizedTopicRequest(BaseModel):
    """個別化されたトークテーマ生成リクエスト"""
    user_id: int = Field(..., description="対象ユーザーID")
    participant_ids: List[int] = Field(..., description="参加者IDのリスト")
    analysis_types: List[str] = Field(..., description="分析タイプのリスト")
    preferred_categories: Optional[List[TopicCategory]] = Field(None, description="希望するカテゴリ")
    max_duration: Optional[int] = Field(None, description="最大所要時間（分）")
    difficulty_level: Optional[TopicDifficulty] = Field(None, description="希望する難易度")

class TopicGenerationResult(BaseModel):
    """トークテーマ生成結果"""
    generation_id: str = Field(..., description="生成ID")
    user_id: int = Field(..., description="対象ユーザーID")
    participant_ids: List[int] = Field(..., description="参加者IDのリスト")
    generated_at: datetime = Field(..., description="生成日時")
    topics: List[TopicSuggestion] = Field(..., description="生成されたトピックのリスト")
    generation_reason: str = Field(..., description="生成理由の説明")
    analysis_summary: str = Field(..., description="分析結果の要約")
    total_score: float = Field(..., description="総合スコア")

class TopicGenerationRequest(BaseModel):
    """トークテーマ生成リクエスト"""
    text_content: str = Field(..., description="分析対象のテキスト内容")
    user_id: int = Field(..., description="対象ユーザーID")
    participant_ids: List[int] = Field(..., description="参加者IDのリスト")
    analysis_types: List[str] = Field(..., description="分析タイプのリスト")
    preferred_categories: Optional[List[TopicCategory]] = Field(None, description="希望するカテゴリ")
    max_duration: Optional[int] = Field(None, description="最大所要時間（分）")
    difficulty_level: Optional[TopicDifficulty] = Field(None, description="希望する難易度")

class TopicGenerationResponse(BaseModel):
    """トークテーマ生成レスポンス"""
    success: bool = Field(..., description="生成成功フラグ")
    result: Optional[TopicGenerationResult] = Field(None, description="生成結果")
    message: str = Field(..., description="メッセージ")
    error_details: Optional[str] = Field(None, description="エラー詳細")

class TopicGenerationListResponse(BaseModel):
    """トークテーマ生成結果一覧レスポンス"""
    topics: List[TopicGenerationResult] = Field(..., description="生成結果のリスト")
    total_count: int = Field(..., description="総件数")
    page: int = Field(..., description="現在のページ")
    page_size: int = Field(..., description="ページサイズ")
