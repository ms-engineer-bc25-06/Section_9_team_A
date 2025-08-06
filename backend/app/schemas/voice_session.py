from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from .common import StatusEnum, TimestampMixin, PaginationParams


class AudioFormatEnum(str, Enum):
    """音声フォーマット列挙型"""

    MP3 = "mp3"
    WAV = "wav"
    M4A = "m4a"
    FLAC = "flac"
    OGG = "ogg"


class VoiceSessionBase(BaseModel):
    """音声セッションベーススキーマ"""

    title: Optional[str] = Field(None, max_length=255, description="セッションタイトル")
    description: Optional[str] = Field(None, description="セッション説明")
    is_public: bool = Field(False, description="公開設定")
    participant_count: int = Field(1, ge=1, le=100, description="参加者数")


class VoiceSessionCreate(VoiceSessionBase):
    """音声セッション作成スキーマ"""

    session_id: str = Field(..., max_length=255, description="セッションID")

    @validator("session_id")
    def validate_session_id(cls, v):
        """セッションIDのバリデーション"""
        if not v or len(v.strip()) == 0:
            raise ValueError("session_id cannot be empty")
        return v.strip()


class VoiceSessionUpdate(BaseModel):
    """音声セッション更新スキーマ"""

    title: Optional[str] = Field(None, max_length=255, description="セッションタイトル")
    description: Optional[str] = Field(None, description="セッション説明")
    status: Optional[StatusEnum] = Field(None, description="セッション状態")
    is_public: Optional[bool] = Field(None, description="公開設定")
    is_analyzed: Optional[bool] = Field(None, description="分析完了フラグ")
    participant_count: Optional[int] = Field(None, ge=1, le=100, description="参加者数")
    participants: Optional[str] = Field(None, description="参加者情報（JSON）")
    analysis_summary: Optional[str] = Field(None, description="分析サマリー")
    sentiment_score: Optional[float] = Field(
        None, ge=-1.0, le=1.0, description="感情スコア"
    )
    key_topics: Optional[str] = Field(None, description="主要トピック（JSON）")
    started_at: Optional[datetime] = Field(None, description="開始時刻")
    ended_at: Optional[datetime] = Field(None, description="終了時刻")


class VoiceSessionAudioUpdate(BaseModel):
    """音声ファイル情報更新スキーマ"""

    audio_file_path: Optional[str] = Field(
        None, max_length=500, description="音声ファイルパス"
    )
    audio_duration: Optional[float] = Field(None, ge=0, description="音声時間（秒）")
    audio_format: Optional[AudioFormatEnum] = Field(
        None, description="音声フォーマット"
    )
    file_size: Optional[int] = Field(None, ge=0, description="ファイルサイズ（バイト）")


class VoiceSessionResponse(VoiceSessionBase, TimestampMixin):
    """音声セッション応答スキーマ"""

    id: int
    session_id: str
    audio_file_path: Optional[str] = None
    audio_duration: Optional[float] = None
    audio_format: Optional[AudioFormatEnum] = None
    file_size: Optional[int] = None
    status: StatusEnum = StatusEnum.ACTIVE
    is_analyzed: bool = False
    participants: Optional[str] = None
    analysis_summary: Optional[str] = None
    sentiment_score: Optional[float] = None
    key_topics: Optional[str] = None
    user_id: int
    team_id: Optional[int] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class VoiceSessionListResponse(BaseModel):
    """音声セッション一覧応答スキーマ"""

    sessions: List[VoiceSessionResponse]
    total: int
    page: int
    size: int
    pages: int


class VoiceSessionDetailResponse(VoiceSessionResponse):
    """音声セッション詳細応答スキーマ"""

    # 関連データを含む
    transcriptions_count: int = 0
    analyses_count: int = 0
    duration_seconds: Optional[float] = None

    @property
    def duration_seconds(self) -> Optional[float]:
        """セッションの継続時間を計算"""
        if self.started_at and self.ended_at:
            return (self.ended_at - self.started_at).total_seconds()
        return None


class VoiceSessionFilters(BaseModel):
    """音声セッションフィルタースキーマ"""

    status: Optional[StatusEnum] = Field(None, description="ステータスでフィルター")
    is_public: Optional[bool] = Field(None, description="公開設定でフィルター")
    is_analyzed: Optional[bool] = Field(None, description="分析完了でフィルター")
    date_from: Optional[datetime] = Field(None, description="開始日時（FROM）")
    date_to: Optional[datetime] = Field(None, description="開始日時（TO）")
    search: Optional[str] = Field(None, max_length=100, description="検索キーワード")


class VoiceSessionQueryParams(PaginationParams, VoiceSessionFilters):
    """音声セッションクエリパラメータ"""

    pass


class VoiceSessionStats(BaseModel):
    """音声セッション統計スキーマ"""

    total_sessions: int
    total_duration: float  # 秒
    average_duration: float  # 秒
    completed_sessions: int
    active_sessions: int
    analyzed_sessions: int
    public_sessions: int
    private_sessions: int
