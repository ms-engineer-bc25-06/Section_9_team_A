from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TranscriptionStatus(str, Enum):
    """文字起こしのステータス"""
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TranscriptionBase(BaseModel):
    """文字起こしの基本スキーマ"""
    content: str = Field(..., description="文字起こしの内容")
    language: str = Field(default="ja", description="言語コード")
    audio_file_path: Optional[str] = Field(None, description="音声ファイルのパス")
    audio_duration: Optional[float] = Field(None, description="音声の長さ（秒）")
    audio_format: Optional[str] = Field(None, description="音声フォーマット")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="信頼度スコア")
    speaker_count: Optional[int] = Field(default=1, ge=1, description="話者数")
    speakers: Optional[str] = Field(None, description="話者情報（JSON文字列）")
    status: TranscriptionStatus = Field(default=TranscriptionStatus.PROCESSING, description="処理ステータス")
    is_edited: bool = Field(default=False, description="編集済みかどうか")


class TranscriptionCreate(TranscriptionBase):
    """文字起こし作成用スキーマ"""
    voice_session_id: int = Field(..., description="音声セッションID")
    user_id: int = Field(..., description="ユーザーID")


class TranscriptionUpdate(BaseModel):
    """文字起こし更新用スキーマ"""
    content: Optional[str] = Field(None, description="文字起こしの内容")
    language: Optional[str] = Field(None, description="言語コード")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="信頼度スコア")
    status: Optional[TranscriptionStatus] = Field(None, description="処理ステータス")
    is_edited: Optional[bool] = Field(None, description="編集済みかどうか")
    processed_at: Optional[datetime] = Field(None, description="処理完了時刻")


class TranscriptionResponse(TranscriptionBase):
    """文字起こし応答用スキーマ"""
    id: int
    transcription_id: str
    voice_session_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True


class TranscriptionListResponse(BaseModel):
    """文字起こし一覧応答用スキーマ"""
    transcriptions: List[TranscriptionResponse]
    total: int
    page: int
    size: int


class TranscriptionFilters(BaseModel):
    """文字起こしフィルター用スキーマ"""
    voice_session_id: Optional[int] = Field(None, description="音声セッションID")
    user_id: Optional[int] = Field(None, description="ユーザーID")
    status: Optional[TranscriptionStatus] = Field(None, description="ステータス")
    language: Optional[str] = Field(None, description="言語")
    is_edited: Optional[bool] = Field(None, description="編集済みかどうか")


class TranscriptionQueryParams(BaseModel):
    """文字起こしクエリパラメータ用スキーマ"""
    page: int = Field(default=1, ge=1, description="ページ番号")
    size: int = Field(default=20, ge=1, le=100, description="ページサイズ")
    voice_session_id: Optional[int] = Field(None, description="音声セッションID")
    user_id: Optional[int] = Field(None, description="ユーザーID")
    status: Optional[TranscriptionStatus] = Field(None, description="ステータス")
    language: Optional[str] = Field(None, description="言語")
    is_edited: Optional[bool] = Field(None, description="編集済みかどうか")
