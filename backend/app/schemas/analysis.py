from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AnalysisType(str, Enum):
    """分析タイプ"""
    SENTIMENT = "sentiment"      # 感情分析
    TOPIC = "topic"              # トピック分析
    SUMMARY = "summary"          # 要約
    KEYWORDS = "keywords"        # キーワード抽出
    SPEAKER = "speaker"          # 話者分析
    COMPREHENSION = "comprehension"  # 理解度分析
    ENGAGEMENT = "engagement"    # 参加度分析
    PERSONALITY = "personality"  # 個性分析
    COMMUNICATION = "communication"  # コミュニケーションパターン
    BEHAVIOR = "behavior"        # 行動特性


class AnalysisStatus(str, Enum):
    """分析のステータス"""
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SentimentLabel(str, Enum):
    """感情ラベル"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class PersonalityTrait(BaseModel):
    """個性特性"""
    trait_name: str = Field(..., description="特性名")
    score: float = Field(..., ge=0.0, le=100.0, description="スコア")
    level: str = Field(..., description="レベル")
    description: str = Field(..., description="説明")


class CommunicationPattern(BaseModel):
    """コミュニケーションパターン"""
    pattern_type: str = Field(..., description="パターンタイプ")
    frequency: float = Field(..., ge=0.0, le=1.0, description="頻度")
    effectiveness: float = Field(..., ge=0.0, le=1.0, description="効果性")
    examples: List[str] = Field(..., description="具体例")


class BehaviorScore(BaseModel):
    """行動スコア"""
    category: str = Field(..., description="カテゴリ名")
    score: float = Field(..., ge=0.0, le=100.0, description="スコア")
    level: str = Field(..., description="レベル")
    improvement_suggestions: List[str] = Field(..., description="改善提案")


class AnalysisResult(BaseModel):
    """分析結果"""
    analysis_type: AnalysisType = Field(..., description="分析タイプ")
    title: str = Field(..., description="分析タイトル")
    summary: str = Field(..., description="分析結果の要約")
    keywords: List[str] = Field(..., description="キーワード")
    topics: List[str] = Field(..., description="トピック")
    personality_traits: Optional[List[PersonalityTrait]] = Field(None, description="個性特性")
    communication_patterns: Optional[List[CommunicationPattern]] = Field(None, description="コミュニケーションパターン")
    behavior_scores: Optional[List[BehaviorScore]] = Field(None, description="行動スコア")
    word_count: Optional[int] = Field(None, description="単語数")
    sentence_count: Optional[int] = Field(None, description="文数")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="信頼度スコア")
    processing_time: Optional[float] = Field(None, description="処理時間（秒）")


class AnalysisBase(BaseModel):
    """分析の基本スキーマ"""
    analysis_type: AnalysisType = Field(..., description="分析タイプ")
    title: Optional[str] = Field(None, description="分析タイトル")
    content: str = Field(..., description="分析対象のコンテンツ")
    summary: Optional[str] = Field(None, description="分析結果の要約")
    keywords: Optional[str] = Field(None, description="キーワード（JSON文字列）")
    topics: Optional[str] = Field(None, description="トピック（JSON文字列）")
    sentiment_score: Optional[float] = Field(None, ge=-1.0, le=1.0, description="感情スコア")
    sentiment_label: Optional[SentimentLabel] = Field(None, description="感情ラベル")
    word_count: Optional[int] = Field(None, ge=0, description="単語数")
    sentence_count: Optional[int] = Field(None, ge=0, description="文数")
    speaking_time: Optional[float] = Field(None, ge=0.0, description="発話時間（秒）")
    status: AnalysisStatus = Field(default=AnalysisStatus.PROCESSING, description="処理ステータス")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="信頼度スコア")


class AnalysisCreate(AnalysisBase):
    """分析作成用スキーマ"""
    voice_session_id: Optional[int] = Field(None, description="音声セッションID")
    transcription_id: Optional[int] = Field(None, description="文字起こしID")
    user_id: int = Field(..., description="ユーザーID")


class AnalysisUpdate(BaseModel):
    """分析更新用スキーマ"""
    title: Optional[str] = Field(None, description="分析タイトル")
    summary: Optional[str] = Field(None, description="分析結果の要約")
    keywords: Optional[str] = Field(None, description="キーワード（JSON文字列）")
    topics: Optional[str] = Field(None, description="トピック（JSON文字列）")
    sentiment_score: Optional[float] = Field(None, ge=-1.0, le=1.0, description="感情スコア")
    sentiment_label: Optional[SentimentLabel] = Field(None, description="感情ラベル")
    status: Optional[AnalysisStatus] = Field(None, description="処理ステータス")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="信頼度スコア")
    processed_at: Optional[datetime] = Field(None, description="処理完了時刻")


class AnalysisResponse(AnalysisBase):
    """分析応答用スキーマ"""
    id: int
    analysis_id: str
    voice_session_id: Optional[int]
    transcription_id: Optional[int]
    user_id: int
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True


class AnalysisListResponse(BaseModel):
    """分析一覧応答用スキーマ"""
    analyses: List[AnalysisResponse]
    total: int
    page: int
    size: int


class AnalysisFilters(BaseModel):
    """分析フィルター用スキーマ"""
    analysis_type: Optional[AnalysisType] = Field(None, description="分析タイプ")
    user_id: Optional[int] = Field(None, description="ユーザーID")
    voice_session_id: Optional[int] = Field(None, description="音声セッションID")
    transcription_id: Optional[int] = Field(None, description="文字起こしID")
    status: Optional[AnalysisStatus] = Field(None, description="ステータス")
    sentiment_label: Optional[SentimentLabel] = Field(None, description="感情ラベル")


class AnalysisQueryParams(BaseModel):
    """分析クエリパラメータ用スキーマ"""
    page: int = Field(default=1, ge=1, description="ページ番号")
    size: int = Field(default=20, ge=1, le=100, description="ページサイズ")
    analysis_type: Optional[AnalysisType] = Field(None, description="分析タイプ")
    user_id: Optional[int] = Field(None, description="ユーザーID")
    voice_session_id: Optional[int] = Field(None, description="音声セッションID")
    transcription_id: Optional[int] = Field(None, description="文字起こしID")
    status: Optional[AnalysisStatus] = Field(None, description="ステータス")
    sentiment_label: Optional[SentimentLabel] = Field(None, description="感情ラベル")


class AnalysisStats(BaseModel):
    """分析統計用スキーマ"""
    total_analyses: int
    completed_analyses: int
    failed_analyses: int
    processing_analyses: int
    average_confidence: float
    sentiment_distribution: Dict[str, int]
    analysis_type_distribution: Dict[str, int]


class SentimentAnalysisRequest(BaseModel):
    """感情分析リクエスト用スキーマ"""
    text: str = Field(..., description="分析対象のテキスト")
    language: str = Field(default="ja", description="言語コード")


class SentimentAnalysisResponse(BaseModel):
    """感情分析応答用スキーマ"""
    sentiment_score: float = Field(..., ge=-1.0, le=1.0, description="感情スコア")
    sentiment_label: SentimentLabel = Field(..., description="感情ラベル")
    confidence: float = Field(..., ge=0.0, le=1.0, description="信頼度")
    positive_probability: float = Field(..., ge=0.0, le=1.0, description="ポジティブ確率")
    negative_probability: float = Field(..., ge=0.0, le=1.0, description="ネガティブ確率")
    neutral_probability: float = Field(..., ge=0.0, le=1.0, description="ニュートラル確率")


class TopicAnalysisRequest(BaseModel):
    """トピック分析リクエスト用スキーマ"""
    text: str = Field(..., description="分析対象のテキスト")
    num_topics: int = Field(default=5, ge=1, le=20, description="抽出するトピック数")
    language: str = Field(default="ja", description="言語コード")


class TopicAnalysisResponse(BaseModel):
    """トピック分析応答用スキーマ"""
    topics: List[Dict[str, Any]] = Field(..., description="トピックリスト")
    keywords: List[str] = Field(..., description="キーワードリスト")
    confidence: float = Field(..., ge=0.0, le=1.0, description="信頼度")
