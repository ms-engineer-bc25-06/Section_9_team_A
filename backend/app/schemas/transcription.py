from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal


class TranscriptionBase(BaseModel):
    """転写基本スキーマ"""

    voice_session_id: int = Field(..., description="音声セッションID")
    speaker_id: Optional[int] = Field(None, description="話者ID")
    text_content: str = Field(..., description="転写テキスト")
    start_time_seconds: Decimal = Field(..., description="開始時間（秒）")
    end_time_seconds: Decimal = Field(..., description="終了時間（秒）")
    confidence_score: Optional[Decimal] = Field(
        None, ge=0, le=1, description="信頼度（0-1）"
    )
    language: str = Field(default="ja", description="言語")
    is_final: bool = Field(default=True, description="確定転写かどうか")
    is_processed: bool = Field(default=False, description="後処理済みかどうか")
    word_timestamps: Optional[str] = Field(
        None, description="単語レベルのタイムスタンプ（JSON）"
    )
    speaker_confidence: Optional[Decimal] = Field(
        None, ge=0, le=1, description="話者識別の信頼度"
    )


class TranscriptionCreate(TranscriptionBase):
    """転写作成スキーマ"""

    pass


class TranscriptionUpdate(BaseModel):
    """転写更新スキーマ"""

    text_content: Optional[str] = Field(None, description="転写テキスト")
    confidence_score: Optional[Decimal] = Field(
        None, ge=0, le=1, description="信頼度（0-1）"
    )
    is_final: Optional[bool] = Field(None, description="確定転写かどうか")
    is_processed: Optional[bool] = Field(None, description="後処理済みかどうか")
    word_timestamps: Optional[str] = Field(
        None, description="単語レベルのタイムスタンプ（JSON）"
    )
    speaker_confidence: Optional[Decimal] = Field(
        None, ge=0, le=1, description="話者識別の信頼度"
    )


class TranscriptionResponse(TranscriptionBase):
    """転写レスポンススキーマ"""

    id: int = Field(..., description="転写ID")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: Optional[datetime] = Field(None, description="更新日時")
    processed_at: Optional[datetime] = Field(None, description="処理日時")

    # 関連データ
    speaker_name: Optional[str] = Field(None, description="話者名")
    speaker_avatar: Optional[str] = Field(None, description="話者アバター")

    class Config:
        from_attributes = True


class TranscriptionListResponse(BaseModel):
    """転写一覧レスポンススキーマ"""

    transcriptions: List[TranscriptionResponse] = Field(..., description="転写リスト")
    total: int = Field(..., description="総件数")
    has_more: bool = Field(..., description="さらにデータがあるか")


class TranscriptionStats(BaseModel):
    """転写統計スキーマ"""

    total_transcriptions: int = Field(..., description="総転写数")
    total_duration: float = Field(..., description="総継続時間（秒）")
    average_confidence: float = Field(..., description="平均信頼度")
    unique_speakers: int = Field(..., description="話者数")
    language_distribution: Dict[str, int] = Field(
        default_factory=dict, description="言語分布"
    )


class TranscriptionSearchRequest(BaseModel):
    """転写検索リクエストスキーマ"""

    voice_session_id: int = Field(..., description="音声セッションID")
    search_text: str = Field(..., description="検索テキスト")
    speaker_id: Optional[int] = Field(None, description="話者ID")
    is_final: Optional[bool] = Field(None, description="確定転写のみ")
    limit: int = Field(default=50, le=100, description="取得件数")
    offset: int = Field(default=0, ge=0, description="オフセット")


class TranscriptionExportRequest(BaseModel):
    """転写エクスポートリクエストスキーマ"""

    voice_session_id: int = Field(..., description="音声セッションID")
    format: Literal["json", "srt", "txt"] = Field(
        default="json", description="エクスポート形式"
    )
    include_partial: bool = Field(default=False, description="部分転写を含むか")
    include_metadata: bool = Field(default=True, description="メタデータを含むか")


class TranscriptionExportResponse(BaseModel):
    """転写エクスポートレスポンススキーマ"""

    format: str = Field(..., description="エクスポート形式")
    content: str = Field(..., description="エクスポート内容")
    filename: str = Field(..., description="ファイル名")
    size_bytes: int = Field(..., description="ファイルサイズ（バイト）")


class RealtimeTranscriptionChunk(BaseModel):
    """リアルタイム転写チャンクスキーマ"""

    session_id: str = Field(..., description="セッションID")
    user_id: int = Field(..., description="ユーザーID")
    text: str = Field(..., description="転写テキスト")
    is_final: bool = Field(default=False, description="確定転写かどうか")
    confidence: float = Field(..., ge=0, le=1, description="信頼度")
    start_time: Optional[float] = Field(None, description="開始時間（秒）")
    end_time: Optional[float] = Field(None, description="終了時間（秒）")
    timestamp: datetime = Field(..., description="タイムスタンプ")


class TranscriptionAnalysisRequest(BaseModel):
    """転写分析リクエストスキーマ"""

    voice_session_id: int = Field(..., description="音声セッションID")
    analysis_type: Literal["sentiment", "topics", "summary", "keywords"] = Field(
        ..., description="分析タイプ"
    )
    include_partial: bool = Field(default=False, description="部分転写を含むか")


class TranscriptionAnalysisResponse(BaseModel):
    """転写分析レスポンススキーマ"""

    analysis_type: str = Field(..., description="分析タイプ")
    result: Dict[str, Any] = Field(..., description="分析結果")
    confidence: float = Field(..., ge=0, le=1, description="分析信頼度")
    processed_at: datetime = Field(..., description="処理日時")
