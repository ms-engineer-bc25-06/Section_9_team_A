from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class AnalysisType(str, Enum):
    """分析タイプの列挙型"""
    PERSONALITY = "personality"  # 個性分析
    COMMUNICATION = "communication"  # コミュニケーションパターン
    BEHAVIOR = "behavior"  # 行動特性
    SENTIMENT = "sentiment"  # 感情分析
    TOPIC = "topic"  # トピック分析
    SUMMARY = "summary"  # 要約分析

class PersonalityTrait(BaseModel):
    """個性特性"""
    trait_name: str = Field(..., description="特性名")
    score: float = Field(..., ge=0.0, le=1.0, description="特性スコア（0.0-1.0）")
    confidence: float = Field(..., ge=0.0, le=1.0, description="信頼度")
    description: str = Field(..., description="特性の説明")

class CommunicationPattern(BaseModel):
    """コミュニケーションパターン"""
    pattern_type: str = Field(..., description="パターンタイプ")
    frequency: float = Field(..., ge=0.0, description="頻度")
    effectiveness: float = Field(..., ge=0.0, le=1.0, description="効果性")
    examples: List[str] = Field(default_factory=list, description="具体例")

class BehaviorScore(BaseModel):
    """行動特性スコア"""
    category: str = Field(..., description="カテゴリ")
    score: float = Field(..., ge=0.0, le=100.0, description="スコア（0-100）")
    level: str = Field(..., description="レベル（低/中/高）")
    improvement_suggestions: List[str] = Field(default_factory=list, description="改善提案")

class AnalysisResult(BaseModel):
    """分析結果の詳細"""
    analysis_type: AnalysisType
    title: str
    summary: str
    keywords: List[str] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)
    
    # 個性分析結果
    personality_traits: Optional[List[PersonalityTrait]] = None
    
    # コミュニケーションパターン結果
    communication_patterns: Optional[List[CommunicationPattern]] = None
    
    # 行動特性スコア結果
    behavior_scores: Optional[List[BehaviorScore]] = None
    
    # 感情分析結果
    sentiment_score: Optional[float] = Field(None, ge=-1.0, le=1.0)
    sentiment_label: Optional[str] = None
    
    # 統計情報
    word_count: Optional[int] = None
    sentence_count: Optional[int] = None
    speaking_time: Optional[float] = None
    
    # メタデータ
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    processing_time: Optional[float] = None

class AnalysisCreate(BaseModel):
    """分析作成リクエスト"""
    analysis_type: AnalysisType
    voice_session_id: Optional[int] = None
    transcription_id: Optional[int] = None
    content: str = Field(..., description="分析対象のテキスト内容")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="追加メタデータ")

class AnalysisUpdate(BaseModel):
    """分析更新リクエスト"""
    title: Optional[str] = None
    summary: Optional[str] = None
    keywords: Optional[List[str]] = None
    topics: Optional[List[str]] = None
    status: Optional[str] = None

class AnalysisResponse(BaseModel):
    """分析レスポンス"""
    id: int
    analysis_id: str
    analysis_type: AnalysisType
    title: Optional[str] = None
    content: str
    summary: Optional[str] = None
    keywords: Optional[List[str]] = None
    topics: Optional[List[str]] = None
    
    # 分析結果
    result: Optional[AnalysisResult] = None
    
    # 感情分析
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    
    # 統計情報
    word_count: Optional[int] = None
    sentence_count: Optional[int] = None
    speaking_time: Optional[float] = None
    
    # 処理状態
    status: str
    confidence_score: Optional[float] = None
    
    # 外部キー
    voice_session_id: Optional[int] = None
    transcription_id: Optional[int] = None
    user_id: int
    
    # タイムスタンプ
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None

class AnalysisListResponse(BaseModel):
    """分析一覧レスポンス"""
    analyses: List[AnalysisResponse]
    total_count: int
    page: int
    page_size: int

class AnalysisRequest(BaseModel):
    """分析リクエスト"""
    text_content: str = Field(..., description="分析対象のテキスト")
    analysis_types: List[AnalysisType] = Field(..., description="実行する分析タイプ")
    user_context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="ユーザーコンテキスト情報")
