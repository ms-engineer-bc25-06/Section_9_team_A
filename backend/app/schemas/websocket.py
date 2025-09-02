from typing import Optional, List, Dict, Any, Literal, Union
from pydantic import BaseModel, Field, validator, root_validator
from datetime import datetime
from enum import Enum
import re


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
    SESSION_STATE_REQUEST = "session_state_request"
    SESSION_CONTROL = "session_control"
    PARTICIPANT_STATE_UPDATE = "participant_state_update"
    SESSION_STATE_INFO = "session_state_info"
    SESSION_PARTICIPANTS_INFO = "session_participants_info"
    SESSION_HISTORY_INFO = "session_history_info"
    SESSION_STARTED = "session_started"
    SESSION_PAUSED = "session_paused"
    SESSION_RESUMED = "session_resumed"
    SESSION_ENDED = "session_ended"
    PARTICIPANT_STATE_UPDATED = "participant_state_updated"

    # 音声関連
    AUDIO_DATA = "audio_data"
    AUDIO_START = "audio_start"
    AUDIO_STOP = "audio_stop"
    AUDIO_LEVEL = "audio_level"
    AUDIO_QUALITY_REQUEST = "audio_quality_request"
    AUDIO_QUALITY_INFO = "audio_quality_info"
    NETWORK_METRICS_UPDATE = "network_metrics_update"

    # 文字起こし関連
    TRANSCRIPTION_PARTIAL = "transcription_partial"
    TRANSCRIPTION_FINAL = "transcription_final"
    TRANSCRIPTION_REQUEST = "transcription_request"
    TRANSCRIPTION_START = "transcription_start"
    TRANSCRIPTION_STOP = "transcription_stop"
    TRANSCRIPTION_STATS = "transcription_stats"
    TRANSCRIPTION_PARTIAL_LIST = "transcription_partial_list"
    TRANSCRIPTION_PARTIAL_CLEARED = "transcription_partial_cleared"
    TRANSCRIPTION_STARTED = "transcription_started"
    TRANSCRIPTION_STOPPED = "transcription_stopped"

    # メッセージング関連
    TEXT_MESSAGE = "text_message"
    EMOJI_REACTION = "emoji_reaction"
    EDIT_MESSAGE = "edit_message"
    DELETE_MESSAGE = "delete_message"
    MESSAGE_DELIVERED = "message_delivered"
    MESSAGE_READ = "message_read"

    # ユーザー状態関連
    TYPING_START = "typing_start"
    TYPING_STOP = "typing_stop"
    PRESENCE_UPDATE = "presence_update"
    STATUS_UPDATE = "status_update"

    # コラボレーション関連
    FILE_SHARE = "file_share"
    SCREEN_SHARE_START = "screen_share_start"
    SCREEN_SHARE_STOP = "screen_share_stop"
    HAND_RAISE = "hand_raise"
    HAND_LOWER = "hand_lower"

    # 投票関連
    POLL_CREATE = "poll_create"
    POLL_VOTE = "poll_vote"
    POLL_UPDATE = "poll_update"
    POLL_CLOSE = "poll_close"

    # システム関連
    SYSTEM_MESSAGE = "system_message"
    NOTIFICATION = "notification"
    ANNOUNCEMENT = "announcement"
    NOTIFICATION_REQUEST = "notification_request"
    ANNOUNCEMENT_REQUEST = "announcement_request"
    NOTIFICATION_DISMISS = "notification_dismiss"
    ANNOUNCEMENT_DISMISS = "announcement_dismiss"
    GET_NOTIFICATIONS = "get_notifications"
    GET_ANNOUNCEMENTS = "get_announcements"
    NOTIFICATIONS_LIST = "notifications_list"
    ANNOUNCEMENTS_LIST = "announcements_list"
    NOTIFICATION_SENT = "notification_sent"
    ANNOUNCEMENT_SENT = "announcement_sent"
    NOTIFICATION_DISMISSED = "notification_dismissed"
    ANNOUNCEMENT_DISMISSED = "announcement_dismissed"

    # エラー関連
    ERROR = "error"
    WARNING = "warning"


class WebSocketMessageValidator:
    """WebSocketメッセージのバリデーションクラス"""

    @staticmethod
    def validate_message_structure(
        message: Dict[str, Any],
    ) -> tuple[bool, Optional[str]]:
        """メッセージの基本構造を検証"""
        if not isinstance(message, dict):
            return False, "Message must be a JSON object"

        if "type" not in message:
            return False, "Message must contain 'type' field"

        if not isinstance(message["type"], str):
            return False, "Message type must be a string"

        return True, None

    @staticmethod
    def validate_message_type(message_type: str) -> tuple[bool, Optional[str]]:
        """メッセージタイプの妥当性を検証"""
        try:
            WebSocketMessageType(message_type)
            return True, None
        except ValueError:
            return False, f"Invalid message type: {message_type}"

    @staticmethod
    def validate_required_fields(
        message: Dict[str, Any], required_fields: List[str]
    ) -> tuple[bool, Optional[str]]:
        """必須フィールドの存在を検証"""
        missing_fields = []
        for field in required_fields:
            if field not in message:
                missing_fields.append(field)

        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"

        return True, None

    @staticmethod
    def validate_field_types(
        message: Dict[str, Any], field_types: Dict[str, type]
    ) -> tuple[bool, Optional[str]]:
        """フィールドの型を検証"""
        for field, expected_type in field_types.items():
            if field in message:
                if not isinstance(message[field], expected_type):
                    return (
                        False,
                        f"Field '{field}' must be of type {expected_type.__name__}",
                    )

        return True, None

    @staticmethod
    def validate_session_id(session_id: str) -> tuple[bool, Optional[str]]:
        """セッションIDの形式を検証"""
        if not session_id:
            return False, "Session ID cannot be empty"

        # UUID形式または英数字ハイフンの組み合わせを許可
        if not re.match(r"^[a-zA-Z0-9\-_]+$", session_id):
            return False, "Session ID contains invalid characters"

        if len(session_id) > 100:
            return False, "Session ID too long (max 100 characters)"

        return True, None

    @staticmethod
    def validate_user_id(user_id: Union[str, int]) -> tuple[bool, Optional[str]]:
        """ユーザーIDの妥当性を検証"""
        if isinstance(user_id, str):
            try:
                user_id_int = int(user_id)
                if user_id_int <= 0:
                    return False, "User ID must be positive"
            except ValueError:
                return False, "User ID must be a valid integer"
        elif isinstance(user_id, int):
            if user_id <= 0:
                return False, "User ID must be positive"
        else:
            return False, "User ID must be string or integer"

        return True, None

    @staticmethod
    def validate_timestamp(timestamp: str) -> tuple[bool, Optional[str]]:
        """タイムスタンプの形式を検証"""
        try:
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            return True, None
        except ValueError:
            return False, "Invalid timestamp format"

    @staticmethod
    def validate_audio_data(audio_data: str) -> tuple[bool, Optional[str]]:
        """音声データの妥当性を検証"""
        if not audio_data:
            return False, "Audio data cannot be empty"

        # Base64エンコードされたデータかチェック
        try:
            import base64

            base64.b64decode(audio_data)
        except Exception:
            return False, "Audio data must be valid base64 encoded"

        if len(audio_data) > 1024 * 1024:  # 1MB制限
            return False, "Audio data too large (max 1MB)"

        return True, None

    @staticmethod
    def validate_message(message: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """メッセージ全体の妥当性を検証"""
        # 基本構造の検証
        is_valid, error = WebSocketMessageValidator.validate_message_structure(message)
        if not is_valid:
            return False, error

        # メッセージタイプの検証
        is_valid, error = WebSocketMessageValidator.validate_message_type(
            message["type"]
        )
        if not is_valid:
            return False, error

        # メッセージタイプ別の詳細検証
        message_type = message["type"]

        if message_type in [
            WebSocketMessageType.JOIN_SESSION,
            WebSocketMessageType.LEAVE_SESSION,
        ]:
            # セッション関連メッセージの検証
            required_fields = ["roomId", "session_id"]
            is_valid, error = WebSocketMessageValidator.validate_required_fields(
                message, required_fields
            )
            if not is_valid:
                return False, error

            # セッションIDの検証
            session_id = message.get("roomId") or message.get("session_id")
            if session_id:
                is_valid, error = WebSocketMessageValidator.validate_session_id(
                    session_id
                )
                if not is_valid:
                    return False, error

        elif message_type in [WebSocketMessageType.AUDIO_DATA]:
            # 音声データメッセージの検証
            required_fields = ["data", "session_id"]
            is_valid, error = WebSocketMessageValidator.validate_required_fields(
                message, required_fields
            )
            if not is_valid:
                return False, error

            # 音声データの検証
            if "data" in message:
                is_valid, error = WebSocketMessageValidator.validate_audio_data(
                    message["data"]
                )
                if not is_valid:
                    return False, error

        elif message_type in [WebSocketMessageType.PING, WebSocketMessageType.PONG]:
            # ハートビートメッセージの検証
            if "timestamp" in message:
                is_valid, error = WebSocketMessageValidator.validate_timestamp(
                    message["timestamp"]
                )
                if not is_valid:
                    return False, error

        return True, None


class ValidationError(Exception):
    """バリデーションエラー"""

    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


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


class SessionStateRequestMessage(WebSocketBaseMessage):
    """セッション状態リクエストメッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.SESSION_STATE_REQUEST
    session_id: str
    request_type: str = "current"  # current, participants, history


class SessionControlMessage(WebSocketBaseMessage):
    """セッション制御メッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.SESSION_CONTROL
    session_id: str
    action: str  # start, pause, resume, end


class ParticipantStateUpdateMessage(WebSocketBaseMessage):
    """参加者状態更新メッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.PARTICIPANT_STATE_UPDATE
    session_id: str
    state: str  # connecting, connected, speaking, listening, muted, disconnected
    data: Optional[Dict[str, Any]] = None


class SessionStateInfoMessage(WebSocketBaseMessage):
    """セッション状態情報メッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.SESSION_STATE_INFO
    session_id: str
    state: Dict[str, Any]


class SessionParticipantsInfoMessage(WebSocketBaseMessage):
    """セッション参加者情報メッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.SESSION_PARTICIPANTS_INFO
    session_id: str
    participants: List[Dict[str, Any]]


class SessionHistoryInfoMessage(WebSocketBaseMessage):
    """セッション履歴情報メッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.SESSION_HISTORY_INFO
    session_id: str
    history: List[Dict[str, Any]]


class SessionStartedMessage(WebSocketBaseMessage):
    """セッション開始メッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.SESSION_STARTED
    session_id: str
    user_id: int
    state: str
    timestamp: datetime = Field(default_factory=datetime.now)


class SessionPausedMessage(WebSocketBaseMessage):
    """セッション一時停止メッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.SESSION_PAUSED
    session_id: str
    user_id: int
    state: str
    timestamp: datetime = Field(default_factory=datetime.now)


class SessionResumedMessage(WebSocketBaseMessage):
    """セッション再開メッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.SESSION_RESUMED
    session_id: str
    user_id: int
    state: str
    timestamp: datetime = Field(default_factory=datetime.now)


class SessionEndedMessage(WebSocketBaseMessage):
    """セッション終了メッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.SESSION_ENDED
    session_id: str
    user_id: int
    state: str
    duration: float
    timestamp: datetime = Field(default_factory=datetime.now)


class ParticipantStateUpdatedMessage(WebSocketBaseMessage):
    """参加者状態更新通知メッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.PARTICIPANT_STATE_UPDATED
    session_id: str
    user_id: int
    state: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


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
    speaker_id: Optional[int] = None
    speaker_confidence: Optional[float] = None
    language: str = "ja"
    quality: str = "medium"
    words: Optional[List[Dict[str, Any]]] = None


class TranscriptionRequestMessage(WebSocketBaseMessage):
    """転写リクエストメッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.TRANSCRIPTION_REQUEST
    session_id: str
    request_type: str = "stats"  # stats, partial, clear_partial
    user_id: Optional[int] = None


class TranscriptionStartMessage(WebSocketBaseMessage):
    """転写開始メッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.TRANSCRIPTION_START
    session_id: str
    language: str = "ja"


class TranscriptionStopMessage(WebSocketBaseMessage):
    """転写停止メッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.TRANSCRIPTION_STOP
    session_id: str


class TranscriptionStatsMessage(WebSocketBaseMessage):
    """転写統計メッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.TRANSCRIPTION_STATS
    session_id: str
    stats: Dict[str, Any]


class TranscriptionPartialListMessage(WebSocketBaseMessage):
    """部分転写リストメッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.TRANSCRIPTION_PARTIAL_LIST
    session_id: str
    partial_transcriptions: Dict[int, str]


class TranscriptionPartialClearedMessage(WebSocketBaseMessage):
    """部分転写クリアメッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.TRANSCRIPTION_PARTIAL_CLEARED
    session_id: str
    user_id: Optional[int] = None


class TranscriptionStartedMessage(WebSocketBaseMessage):
    """転写開始確認メッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.TRANSCRIPTION_STARTED
    session_id: str
    user_id: int
    language: str


class TranscriptionStoppedMessage(WebSocketBaseMessage):
    """転写停止確認メッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.TRANSCRIPTION_STOPPED
    session_id: str
    user_id: int


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


# メッセージ優先度
class MessagePriority(str, Enum):
    """メッセージ優先度"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


# ユーザー状態
class UserPresenceStatus(str, Enum):
    """ユーザー状態"""

    ONLINE = "online"
    AWAY = "away"
    BUSY = "busy"
    OFFLINE = "offline"


class UserActivityStatus(str, Enum):
    """ユーザー活動状態"""

    ACTIVE = "active"
    IDLE = "idle"
    TYPING = "typing"
    SPEAKING = "speaking"
    LISTENING = "listening"


# メッセージングメッセージ
class TextMessageMessage(WebSocketBaseMessage):
    """テキストメッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.TEXT_MESSAGE
    session_id: str
    content: str
    priority: MessagePriority = MessagePriority.NORMAL
    reply_to: Optional[str] = None  # 返信先メッセージID


class EmojiReactionMessage(WebSocketBaseMessage):
    """絵文字リアクション"""

    type: WebSocketMessageType = WebSocketMessageType.EMOJI_REACTION
    session_id: str
    target_message_id: str
    emoji: str
    action: Literal["add", "remove"]


class EditMessageMessage(WebSocketBaseMessage):
    """メッセージ編集"""

    type: WebSocketMessageType = WebSocketMessageType.EDIT_MESSAGE
    session_id: str
    message_id: str
    new_content: str


class DeleteMessageMessage(WebSocketBaseMessage):
    """メッセージ削除"""

    type: WebSocketMessageType = WebSocketMessageType.DELETE_MESSAGE
    session_id: str
    message_id: str


class MessageDeliveredMessage(WebSocketBaseMessage):
    """メッセージ配信確認"""

    type: WebSocketMessageType = WebSocketMessageType.MESSAGE_DELIVERED
    session_id: str
    message_id: str
    user_id: int


class MessageReadMessage(WebSocketBaseMessage):
    """メッセージ既読確認"""

    type: WebSocketMessageType = WebSocketMessageType.MESSAGE_READ
    session_id: str
    message_id: str
    user_id: int


# ユーザー状態メッセージ
class TypingStartMessage(WebSocketBaseMessage):
    """入力開始"""

    type: WebSocketMessageType = WebSocketMessageType.TYPING_START
    session_id: str
    user_id: int


class TypingStopMessage(WebSocketBaseMessage):
    """入力停止"""

    type: WebSocketMessageType = WebSocketMessageType.TYPING_STOP
    session_id: str
    user_id: int


class PresenceUpdateMessage(WebSocketBaseMessage):
    """プレゼンス更新"""

    type: WebSocketMessageType = WebSocketMessageType.PRESENCE_UPDATE
    user_id: int
    status: UserPresenceStatus
    activity: UserActivityStatus = UserActivityStatus.ACTIVE
    custom_status: Optional[str] = None


class StatusUpdateMessage(WebSocketBaseMessage):
    """ステータス更新"""

    type: WebSocketMessageType = WebSocketMessageType.STATUS_UPDATE
    session_id: str
    user_id: int
    status: Dict[str, Any]


# コラボレーションメッセージ
class FileShareMessage(WebSocketBaseMessage):
    """ファイル共有"""

    type: WebSocketMessageType = WebSocketMessageType.FILE_SHARE
    session_id: str
    file_name: str
    file_size: int
    file_type: str
    file_url: Optional[str] = None
    description: Optional[str] = None


class ScreenShareStartMessage(WebSocketBaseMessage):
    """画面共有開始"""

    type: WebSocketMessageType = WebSocketMessageType.SCREEN_SHARE_START
    session_id: str
    user_id: int
    stream_id: str
    quality: str = "high"


class ScreenShareStopMessage(WebSocketBaseMessage):
    """画面共有停止"""

    type: WebSocketMessageType = WebSocketMessageType.SCREEN_SHARE_STOP
    session_id: str
    user_id: int
    stream_id: str


class HandRaiseMessage(WebSocketBaseMessage):
    """挙手"""

    type: WebSocketMessageType = WebSocketMessageType.HAND_RAISE
    session_id: str
    user_id: int
    reason: Optional[str] = None


class HandLowerMessage(WebSocketBaseMessage):
    """挙手解除"""

    type: WebSocketMessageType = WebSocketMessageType.HAND_LOWER
    session_id: str
    user_id: int


# 投票メッセージ
class PollOption(BaseModel):
    """投票選択肢"""

    id: str
    text: str
    votes: int = 0


class PollCreateMessage(WebSocketBaseMessage):
    """投票作成"""

    type: WebSocketMessageType = WebSocketMessageType.POLL_CREATE
    session_id: str
    poll_id: str
    question: str
    options: List[PollOption]
    multiple_choice: bool = False
    anonymous: bool = False
    duration: Optional[int] = None  # 秒


class PollVoteMessage(WebSocketBaseMessage):
    """投票"""

    type: WebSocketMessageType = WebSocketMessageType.POLL_VOTE
    session_id: str
    poll_id: str
    option_ids: List[str]
    user_id: int


class PollUpdateMessage(WebSocketBaseMessage):
    """投票結果更新"""

    type: WebSocketMessageType = WebSocketMessageType.POLL_UPDATE
    session_id: str
    poll_id: str
    options: List[PollOption]
    total_votes: int


class PollCloseMessage(WebSocketBaseMessage):
    """投票終了"""

    type: WebSocketMessageType = WebSocketMessageType.POLL_CLOSE
    session_id: str
    poll_id: str
    final_results: List[PollOption]


# システムメッセージ
class SystemMessage(WebSocketBaseMessage):
    """システムメッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.SYSTEM_MESSAGE
    session_id: str
    content: str
    priority: MessagePriority = MessagePriority.NORMAL
    metadata: Optional[Dict[str, Any]] = None


class NotificationMessage(WebSocketBaseMessage):
    """通知メッセージ"""

    type: WebSocketMessageType = WebSocketMessageType.NOTIFICATION
    session_id: Optional[str] = None
    user_id: Optional[int] = None
    title: str
    content: str
    notification_type: str = "info"  # info, warning, error, success
    action_url: Optional[str] = None
    auto_dismiss: bool = True
    duration: int = 5000  # ミリ秒


class AnnouncementMessage(WebSocketBaseMessage):
    """アナウンス"""

    type: WebSocketMessageType = WebSocketMessageType.ANNOUNCEMENT
    session_id: Optional[str] = None
    title: str
    content: str
    priority: MessagePriority = MessagePriority.HIGH
    sender: str
    expires_at: Optional[datetime] = None


class NotificationRequestMessage(WebSocketBaseMessage):
    """通知リクエスト"""

    type: WebSocketMessageType = WebSocketMessageType.NOTIFICATION_REQUEST
    session_id: str
    title: str
    content: str
    notification_type: str = "info"
    priority: MessagePriority = MessagePriority.NORMAL
    metadata: Optional[Dict[str, Any]] = None


class AnnouncementRequestMessage(WebSocketBaseMessage):
    """アナウンスメントリクエスト"""

    type: WebSocketMessageType = WebSocketMessageType.ANNOUNCEMENT_REQUEST
    session_id: str
    title: str
    content: str
    announcement_type: str = "general"
    priority: MessagePriority = MessagePriority.NORMAL
    metadata: Optional[Dict[str, Any]] = None
    expires_at: Optional[str] = None


class NotificationDismissMessage(WebSocketBaseMessage):
    """通知却下"""

    type: WebSocketMessageType = WebSocketMessageType.NOTIFICATION_DISMISS
    notification_id: str


class AnnouncementDismissMessage(WebSocketBaseMessage):
    """アナウンスメント却下"""

    type: WebSocketMessageType = WebSocketMessageType.ANNOUNCEMENT_DISMISS
    announcement_id: str


class GetNotificationsMessage(WebSocketBaseMessage):
    """通知取得"""

    type: WebSocketMessageType = WebSocketMessageType.GET_NOTIFICATIONS
    unread_only: bool = False
    limit: int = 50


class GetAnnouncementsMessage(WebSocketBaseMessage):
    """アナウンスメント取得"""

    type: WebSocketMessageType = WebSocketMessageType.GET_ANNOUNCEMENTS
    limit: int = 50


class NotificationsListMessage(WebSocketBaseMessage):
    """通知リスト"""

    type: WebSocketMessageType = WebSocketMessageType.NOTIFICATIONS_LIST
    notifications: List[Dict[str, Any]]


class AnnouncementsListMessage(WebSocketBaseMessage):
    """アナウンスメントリスト"""

    type: WebSocketMessageType = WebSocketMessageType.ANNOUNCEMENTS_LIST
    announcements: List[Dict[str, Any]]


class NotificationSentMessage(WebSocketBaseMessage):
    """通知送信確認"""

    type: WebSocketMessageType = WebSocketMessageType.NOTIFICATION_SENT
    notification_id: str


class AnnouncementSentMessage(WebSocketBaseMessage):
    """アナウンスメント送信確認"""

    type: WebSocketMessageType = WebSocketMessageType.ANNOUNCEMENT_SENT
    announcement_id: str


class NotificationDismissedMessage(WebSocketBaseMessage):
    """通知却下確認"""

    type: WebSocketMessageType = WebSocketMessageType.NOTIFICATION_DISMISSED
    notification_id: str


class AnnouncementDismissedMessage(WebSocketBaseMessage):
    """アナウンスメント却下確認"""

    type: WebSocketMessageType = WebSocketMessageType.ANNOUNCEMENT_DISMISSED
    announcement_id: str


class AudioQualityRequestMessage(WebSocketBaseMessage):
    """音声品質情報要求"""

    type: WebSocketMessageType = WebSocketMessageType.AUDIO_QUALITY_REQUEST
    session_id: str


class AudioQualityInfoMessage(WebSocketBaseMessage):
    """音声品質情報"""

    type: WebSocketMessageType = WebSocketMessageType.AUDIO_QUALITY_INFO
    session_id: str
    user_id: int
    quality_metrics: List[Dict[str, Any]]
    buffer_stats: Dict[str, Any]
    audio_levels: List[Dict[str, Any]]


class NetworkMetricsUpdateMessage(WebSocketBaseMessage):
    """ネットワークメトリクス更新"""

    type: WebSocketMessageType = WebSocketMessageType.NETWORK_METRICS_UPDATE
    session_id: str
    bandwidth: float
    latency: float
    packet_loss: float
    jitter: float
    quality_score: float


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
    | SessionStateRequestMessage
    | SessionControlMessage
    | ParticipantStateUpdateMessage
    | SessionStateInfoMessage
    | SessionParticipantsInfoMessage
    | SessionHistoryInfoMessage
    | SessionStartedMessage
    | SessionPausedMessage
    | SessionResumedMessage
    | SessionEndedMessage
    | ParticipantStateUpdatedMessage
    | AudioDataMessage
    | AudioStartMessage
    | AudioStopMessage
    | AudioLevelMessage
    | TranscriptionPartialMessage
    | TranscriptionFinalMessage
    | TranscriptionRequestMessage
    | TranscriptionStartMessage
    | TranscriptionStopMessage
    | TranscriptionStatsMessage
    | TranscriptionPartialListMessage
    | TranscriptionPartialClearedMessage
    | TranscriptionStartedMessage
    | TranscriptionStoppedMessage
    | TextMessageMessage
    | EmojiReactionMessage
    | EditMessageMessage
    | DeleteMessageMessage
    | MessageDeliveredMessage
    | MessageReadMessage
    | TypingStartMessage
    | TypingStopMessage
    | PresenceUpdateMessage
    | StatusUpdateMessage
    | FileShareMessage
    | ScreenShareStartMessage
    | ScreenShareStopMessage
    | HandRaiseMessage
    | HandLowerMessage
    | PollCreateMessage
    | PollVoteMessage
    | PollUpdateMessage
    | PollCloseMessage
    | SystemMessage
    | NotificationMessage
    | AnnouncementMessage
    | NotificationRequestMessage
    | AnnouncementRequestMessage
    | NotificationDismissMessage
    | AnnouncementDismissMessage
    | GetNotificationsMessage
    | GetAnnouncementsMessage
    | NotificationsListMessage
    | AnnouncementsListMessage
    | NotificationSentMessage
    | AnnouncementSentMessage
    | NotificationDismissedMessage
    | AnnouncementDismissedMessage
    | ErrorMessage
    | WarningMessage
)
