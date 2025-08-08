from typing import Optional, List, Dict, Any, Literal
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
