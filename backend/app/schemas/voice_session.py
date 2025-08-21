from pydantic import BaseModel, Field, field_validator
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

    @field_validator("session_id")
    def validate_session_id(cls, v):
        """セッションIDのバリデーション"""
        if v is None:
            raise ValueError("session_id cannot be empty")
        value = str(v).strip()
        if len(value) == 0:
            raise ValueError("session_id cannot be empty")
        return value


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
    session_id: str = Field(..., description="セッションID")
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
    user_id: int = Field(..., description="ユーザーID")
    team_id: Optional[int] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        populate_by_name = True

    @classmethod
    def model_validate(cls, obj):
        """VoiceSessionモデルからVoiceSessionResponseを作成"""
        if hasattr(obj, "room_id"):
            # VoiceSessionモデルの場合
            data = {
                "id": obj.id,
                "session_id": obj.room_id,  # room_idをsession_idにマッピング
                "title": obj.title,
                "description": obj.description,
                "status": obj.status,
                "is_public": obj.is_public,
                "participant_count": obj.participant_count,
                "user_id": obj.host_id,  # host_idをuser_idにマッピング
                "team_id": obj.team_id,
                "started_at": obj.started_at,
                "ended_at": obj.ended_at,
                "created_at": obj.created_at,
                "updated_at": obj.updated_at,
            }
            return cls(**data)
        return super().model_validate(obj)


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


class ParticipantRoleEnum(str, Enum):
    """参加者権限列挙型"""

    OWNER = "owner"
    MODERATOR = "moderator"
    PARTICIPANT = "participant"
    VIEWER = "viewer"


class ParticipantInfo(BaseModel):
    """参加者情報スキーマ"""

    user_id: int
    username: str
    email: str
    role: ParticipantRoleEnum = ParticipantRoleEnum.PARTICIPANT
    joined_at: datetime
    is_active: bool = True


class ParticipantAddRequest(BaseModel):
    """参加者追加リクエストスキーマ"""

    user_id: int
    role: ParticipantRoleEnum = ParticipantRoleEnum.PARTICIPANT


class ParticipantUpdateRequest(BaseModel):
    """参加者更新リクエストスキーマ"""

    role: ParticipantRoleEnum


class ParticipantResponse(BaseModel):
    """参加者応答スキーマ"""

    user_id: int
    username: str
    email: str
    role: ParticipantRoleEnum
    joined_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class ParticipantListResponse(BaseModel):
    """参加者一覧応答スキーマ"""

    participants: List[ParticipantResponse]
    total: int
    active_count: int


# 録音制御スキーマ
class RecordingStatusEnum(str, Enum):
    """録音状態列挙型"""

    IDLE = "idle"
    RECORDING = "recording"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class RecordingControlRequest(BaseModel):
    """録音制御リクエストスキーマ"""

    action: str = Field(..., description="録音アクション（start, stop, pause, resume）")
    quality: Optional[str] = Field("high", description="録音品質（low, medium, high）")
    format: Optional[str] = Field(
        "mp3", description="録音フォーマット（mp3, wav, m4a）"
    )


class RecordingStatusResponse(BaseModel):
    """録音状態応答スキーマ"""

    session_id: str
    status: RecordingStatusEnum
    is_recording: bool
    recording_duration: Optional[float] = None  # 秒
    file_path: Optional[str] = None
    file_size: Optional[int] = None  # バイト
    quality: Optional[str] = None
    format: Optional[str] = None
    started_at: Optional[datetime] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


# リアルタイム統計スキーマ
class RealtimeStatsResponse(BaseModel):
    """リアルタイム統計応答スキーマ"""

    session_id: str
    current_duration: float  # 現在の継続時間（秒）
    participant_count: int
    active_participants: int
    recording_duration: Optional[float] = None  # 録音時間（秒）
    transcription_count: int
    analysis_progress: float  # 分析進捗（0.0-1.0）
    sentiment_score: Optional[float] = None
    key_topics_count: int
    last_activity: datetime
    is_live: bool

    class Config:
        from_attributes = True


class SessionProgressResponse(BaseModel):
    """セッション進行状況応答スキーマ"""

    session_id: str
    status: StatusEnum
    progress_percentage: float  # 進行状況（0.0-100.0）
    current_phase: str  # 現在のフェーズ
    estimated_completion: Optional[datetime] = None
    completed_steps: List[str]
    remaining_steps: List[str]
    total_duration: float  # 総継続時間（秒）
    recording_status: RecordingStatusEnum
    analysis_status: str  # 分析状態

    class Config:
        from_attributes = True
