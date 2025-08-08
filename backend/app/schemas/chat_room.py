from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from enum import Enum

from app.schemas.common import TimestampMixin


class RoomTypeEnum(str, Enum):
    """ルームタイプ列挙"""

    CASUAL = "casual"
    BUSINESS = "business"
    STUDY = "study"


class RoomStatusEnum(str, Enum):
    """ルームステータス列挙"""

    WAITING = "waiting"
    ACTIVE = "active"
    ENDED = "ended"


class MessageTypeEnum(str, Enum):
    """メッセージタイプ列挙"""

    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    SYSTEM = "system"


class ParticipantRoleEnum(str, Enum):
    """参加者ロール列挙"""

    PARTICIPANT = "participant"
    MODERATOR = "moderator"
    ADMIN = "admin"


class ParticipantStatusEnum(str, Enum):
    """参加者ステータス列挙"""

    ACTIVE = "active"
    MUTED = "muted"
    BANNED = "banned"


# ChatRoom スキーマ
class ChatRoomBase(BaseModel):
    """チャットルーム基本スキーマ"""

    name: str = Field(..., min_length=1, max_length=255, description="ルーム名")
    description: Optional[str] = Field(None, max_length=1000, description="ルーム説明")
    is_public: bool = Field(True, description="公開設定")
    max_participants: int = Field(10, ge=1, le=100, description="最大参加者数")
    room_type: RoomTypeEnum = Field(RoomTypeEnum.CASUAL, description="ルームタイプ")


class ChatRoomCreate(ChatRoomBase):
    """チャットルーム作成スキーマ"""

    room_id: Optional[str] = Field(None, description="ルームID（自動生成）")
    team_id: Optional[int] = Field(None, description="チームID")

    @field_validator("room_id")
    def validate_room_id(cls, v):
        if v is not None and len(v) > 255:
            raise ValueError("Room ID must be 255 characters or less")
        return v


class ChatRoomUpdate(BaseModel):
    """チャットルーム更新スキーマ"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    is_public: Optional[bool] = None
    max_participants: Optional[int] = Field(None, ge=1, le=100)
    room_type: Optional[RoomTypeEnum] = None
    status: Optional[RoomStatusEnum] = None


class ChatRoomResponse(ChatRoomBase, TimestampMixin):
    """チャットルームレスポンススキーマ"""

    id: int
    room_id: str
    status: RoomStatusEnum
    current_participants: int
    total_messages: int
    total_duration: int
    created_by: int
    team_id: Optional[int]
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True


class ChatRoomDetailResponse(ChatRoomResponse):
    """チャットルーム詳細レスポンススキーマ"""

    participants: Optional[List[Dict[str, Any]]] = None
    moderators: Optional[List[Dict[str, Any]]] = None
    creator_info: Optional[Dict[str, Any]] = None


class ChatRoomListResponse(BaseModel):
    """チャットルーム一覧レスポンススキーマ"""

    rooms: List[ChatRoomResponse]
    total: int
    page: int
    size: int
    pages: int


# ChatMessage スキーマ
class ChatMessageBase(BaseModel):
    """チャットメッセージ基本スキーマ"""

    content: str = Field(
        ..., min_length=1, max_length=5000, description="メッセージ内容"
    )
    message_type: MessageTypeEnum = Field(
        MessageTypeEnum.TEXT, description="メッセージタイプ"
    )


class ChatMessageCreate(ChatMessageBase):
    """チャットメッセージ作成スキーマ"""

    message_id: Optional[str] = Field(None, description="メッセージID（自動生成）")
    audio_file_path: Optional[str] = Field(None, description="音声ファイルパス")
    audio_duration: Optional[int] = Field(None, ge=0, description="音声長（秒）")
    transcription: Optional[str] = Field(None, description="文字起こしテキスト")

    @field_validator("message_id")
    def validate_message_id(cls, v):
        if v is not None and len(v) > 255:
            raise ValueError("Message ID must be 255 characters or less")
        return v


class ChatMessageUpdate(BaseModel):
    """チャットメッセージ更新スキーマ"""

    content: Optional[str] = Field(None, min_length=1, max_length=5000)
    transcription: Optional[str] = None


class ChatMessageResponse(ChatMessageBase, TimestampMixin):
    """チャットメッセージレスポンススキーマ"""

    id: int
    message_id: str
    chat_room_id: int
    sender_id: int
    audio_file_path: Optional[str]
    audio_duration: Optional[int]
    transcription: Optional[str]
    is_edited: bool
    is_deleted: bool
    sender_info: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class ChatMessageListResponse(BaseModel):
    """チャットメッセージ一覧レスポンススキーマ"""

    messages: List[ChatMessageResponse]
    total: int
    page: int
    size: int
    pages: int


# ChatRoomParticipant スキーマ
class ChatRoomParticipantBase(BaseModel):
    """チャットルーム参加者基本スキーマ"""

    role: ParticipantRoleEnum = Field(
        ParticipantRoleEnum.PARTICIPANT, description="参加者ロール"
    )
    status: ParticipantStatusEnum = Field(
        ParticipantStatusEnum.ACTIVE, description="参加者ステータス"
    )


class ChatRoomParticipantCreate(ChatRoomParticipantBase):
    """チャットルーム参加者作成スキーマ"""

    pass


class ChatRoomParticipantUpdate(BaseModel):
    """チャットルーム参加者更新スキーマ"""

    role: Optional[ParticipantRoleEnum] = None
    status: Optional[ParticipantStatusEnum] = None
    is_online: Optional[bool] = None


class ChatRoomParticipantResponse(ChatRoomParticipantBase, TimestampMixin):
    """チャットルーム参加者レスポンススキーマ"""

    id: int
    chat_room_id: int
    user_id: int
    is_online: bool
    joined_at: datetime
    last_active_at: Optional[datetime]
    total_messages: int
    user_info: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class ChatRoomParticipantListResponse(BaseModel):
    """チャットルーム参加者一覧レスポンススキーマ"""

    participants: List[ChatRoomParticipantResponse]
    total: int
    online_count: int


# クエリパラメータ
class ChatRoomQueryParams(BaseModel):
    """チャットルームクエリパラメータ"""

    page: int = Field(1, ge=1, description="ページ番号")
    size: int = Field(10, ge=1, le=100, description="ページサイズ")
    status: Optional[RoomStatusEnum] = Field(None, description="ステータスでフィルター")
    room_type: Optional[RoomTypeEnum] = Field(
        None, description="ルームタイプでフィルター"
    )
    is_public: Optional[bool] = Field(None, description="公開設定でフィルター")
    search: Optional[str] = Field(None, description="検索キーワード")


class ChatMessageQueryParams(BaseModel):
    """チャットメッセージクエリパラメータ"""

    page: int = Field(1, ge=1, description="ページ番号")
    size: int = Field(20, ge=1, le=100, description="ページサイズ")
    message_type: Optional[MessageTypeEnum] = Field(
        None, description="メッセージタイプでフィルター"
    )


# 統計情報
class ChatRoomStats(BaseModel):
    """チャットルーム統計スキーマ"""

    total_rooms: int
    active_rooms: int
    total_messages: int
    total_participants: int
    average_messages_per_room: float
    most_active_room: Optional[Dict[str, Any]] = None
