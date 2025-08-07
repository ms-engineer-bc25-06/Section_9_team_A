from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class WebSocketMessageType(str, Enum):
    """WebSocketメッセージタイプ"""

    # 接続関連
    CONNECTION_ESTABLISHED = "connection_established"
    PING = "ping"
    PONG = "pong"

    # セッション関連
    JOIN_SESSION = "join_session"
    LEAVE_SESSION = "leave_session"
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    SESSION_PARTICIPANTS = "session_participants"

    # 音声関連
    AUDIO_DATA = "audio_data"
    AUDIO_START = "audio_start"
    AUDIO_STOP = "audio_stop"
    AUDIO_LEVEL = "audio_level"

    # 文字起こし関連
    TRANSCRIPTION_PARTIAL = "transcription_partial"
    TRANSCRIPTION_FINAL = "transcription_final"

    # エラー関連
    ERROR = "error"
    WARNING = "warning"


class WebSocketBaseMessage(BaseModel):
    """WebSocket基本メッセージ"""

    type: WebSocketMessageType
    timestamp: datetime = Field(default_factory=datetime.now)


class ConnectionEstablishedMessage(WebSocketBaseMessage):
    """接続確立メッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.CONNECTION_ESTABLISHED
    session_id: str
    user_id: int


class PingMessage(WebSocketBaseMessage):
    """Pingメッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.PING


class PongMessage(WebSocketBaseMessage):
    """Pongメッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.PONG


class JoinSessionMessage(WebSocketBaseMessage):
    """セッション参加メッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.JOIN_SESSION
    session_id: str


class LeaveSessionMessage(WebSocketBaseMessage):
    """セッション退出メッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.LEAVE_SESSION
    session_id: str


class UserInfo(BaseModel):
    """ユーザー情報"""

    id: int
    display_name: str
    avatar_url: Optional[str] = None


class UserJoinedMessage(WebSocketBaseMessage):
    """ユーザー参加メッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.USER_JOINED
    user: UserInfo
    session_id: str


class UserLeftMessage(WebSocketBaseMessage):
    """ユーザー退出メッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.USER_LEFT
    user: UserInfo
    session_id: str


class SessionParticipantsMessage(WebSocketBaseMessage):
    """セッション参加者一覧メッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.SESSION_PARTICIPANTS
    session_id: str
    participants: List[int]


class AudioDataMessage(WebSocketBaseMessage):
    """音声データメッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.AUDIO_DATA
    session_id: str
    user_id: int
    data: str  # Base64エンコードされた音声データ
    chunk_id: Optional[str] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None


class AudioStartMessage(WebSocketBaseMessage):
    """音声開始メッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.AUDIO_START
    session_id: str
    user_id: int


class AudioStopMessage(WebSocketBaseMessage):
    """音声停止メッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.AUDIO_STOP
    session_id: str
    user_id: int


class AudioLevelMessage(WebSocketBaseMessage):
    """音声レベルメッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.AUDIO_LEVEL
    session_id: str
    user_id: int
    level: float  # 0.0 - 1.0
    is_speaking: bool


class TranscriptionPartialMessage(WebSocketBaseMessage):
    """部分文字起こしメッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.TRANSCRIPTION_PARTIAL
    session_id: str
    user_id: int
    text: str
    is_final: bool = False
    confidence: float = Field(ge=0.0, le=1.0)
    start_time: Optional[float] = None
    end_time: Optional[float] = None


class TranscriptionFinalMessage(WebSocketBaseMessage):
    """確定文字起こしメッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.TRANSCRIPTION_FINAL
    session_id: str
    user_id: int
    text: str
    confidence: float = Field(ge=0.0, le=1.0)
    start_time: Optional[float] = None
    end_time: Optional[float] = None


class ErrorMessage(WebSocketBaseMessage):
    """エラーメッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.ERROR
    message: str
    code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class WarningMessage(WebSocketBaseMessage):
    """警告メッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.WARNING
    message: str
    code: Optional[str] = None


# メッセージ型のユニオン
WebSocketMessage = (
    ConnectionEstablishedMessage
    | PingMessage
    | PongMessage
    | JoinSessionMessage
    | LeaveSessionMessage
    | UserJoinedMessage
    | UserLeftMessage
    | SessionParticipantsMessage
    | AudioDataMessage
    | AudioStartMessage
    | AudioStopMessage
    | AudioLevelMessage
    | TranscriptionPartialMessage
    | TranscriptionFinalMessage
    | ErrorMessage
    | WarningMessage
)
