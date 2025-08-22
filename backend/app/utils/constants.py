"""
定数定義のモジュール
"""
from enum import Enum
from typing import List, Dict, Any


class UserRole(str, Enum):
    """ユーザーロール"""
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"
    GUEST = "guest"


class UserStatus(str, Enum):
    """ユーザーステータス"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class SubscriptionStatus(str, Enum):
    """サブスクリプションステータス"""
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"
    TRIAL = "trial"


class PaymentStatus(str, Enum):
    """支払いステータス"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class AnalysisType(str, Enum):
    """分析タイプ"""
    SENTIMENT = "sentiment"
    TOPIC = "topic"
    KEYWORD = "keyword"
    SUMMARY = "summary"
    ACTION_ITEMS = "action_items"
    COMPARISON = "comparison"


class AnalysisStatus(str, Enum):
    """分析ステータス"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class VoiceSessionStatus(str, Enum):
    """音声セッションステータス"""
    CREATED = "created"
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"
    ARCHIVED = "archived"


class TranscriptionStatus(str, Enum):
    """文字起こしステータス"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class PrivacyLevel(str, Enum):
    """プライバシーレベル"""
    PUBLIC = "public"
    PRIVATE = "private"
    TEAM = "team"
    ORGANIZATION = "organization"
    RESTRICTED = "restricted"


class NotificationType(str, Enum):
    """通知タイプ"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    SYSTEM = "system"


class MessagePriority(str, Enum):
    """メッセージ優先度"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class FileType(str, Enum):
    """ファイルタイプ"""
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    IMAGE = "image"
    ARCHIVE = "archive"
    OTHER = "other"


class SupportedAudioFormats(str, Enum):
    """サポートされている音声フォーマット"""
    MP3 = "mp3"
    WAV = "wav"
    M4A = "m4a"
    FLAC = "flac"
    OGG = "ogg"
    AAC = "aac"


class SupportedVideoFormats(str, Enum):
    """サポートされている動画フォーマット"""
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    WMV = "wmv"
    FLV = "flv"
    WEBM = "webm"


class SupportedDocumentFormats(str, Enum):
    """サポートされている文書フォーマット"""
    PDF = "pdf"
    DOC = "doc"
    DOCX = "docx"
    TXT = "txt"
    RTF = "rtf"
    HTML = "html"


# ファイルサイズ制限（バイト）
MAX_FILE_SIZE = {
    FileType.AUDIO: 100 * 1024 * 1024,      # 100MB
    FileType.VIDEO: 500 * 1024 * 1024,      # 500MB
    FileType.DOCUMENT: 50 * 1024 * 1024,    # 50MB
    FileType.IMAGE: 20 * 1024 * 1024,       # 20MB
    FileType.ARCHIVE: 200 * 1024 * 1024,    # 200MB
    FileType.OTHER: 100 * 1024 * 1024       # 100MB
}

# 音声品質設定
AUDIO_QUALITY_SETTINGS = {
    "low": {
        "sample_rate": 8000,
        "bit_rate": 64,
        "channels": 1
    },
    "medium": {
        "sample_rate": 16000,
        "bit_rate": 128,
        "channels": 1
    },
    "high": {
        "sample_rate": 44100,
        "bit_rate": 256,
        "channels": 2
    }
}

# セッション制限
SESSION_LIMITS = {
    "max_duration": 7200,        # 2時間（秒）
    "max_participants": 100,     # 最大参加者数
    "max_file_uploads": 50,      # 最大ファイルアップロード数
    "max_chat_messages": 1000    # 最大チャットメッセージ数
}

# レート制限
RATE_LIMITS = {
    "api_requests": 1000,        # 1分間のAPIリクエスト数
    "file_uploads": 10,          # 1分間のファイルアップロード数
    "chat_messages": 60,         # 1分間のチャットメッセージ数
    "login_attempts": 5          # 1時間のログイン試行数
}

# キャッシュ設定
CACHE_SETTINGS = {
    "default_ttl": 3600,         # デフォルトTTL（秒）
    "user_profile": 1800,        # ユーザープロフィール（30分）
    "session_data": 300,         # セッションデータ（5分）
    "analysis_results": 7200     # 分析結果（2時間）
}

# データベース設定
DATABASE_SETTINGS = {
    "max_connections": 20,
    "connection_timeout": 30,
    "query_timeout": 60,
    "max_retries": 3
}

# 外部API設定
EXTERNAL_API_SETTINGS = {
    "openai": {
        "timeout": 30,
        "max_retries": 3,
        "rate_limit": 100
    },
    "firebase": {
        "timeout": 10,
        "max_retries": 2
    },
    "stripe": {
        "timeout": 15,
        "max_retries": 3
    }
}

# セキュリティ設定
SECURITY_SETTINGS = {
    "password_min_length": 8,
    "password_require_uppercase": True,
    "password_require_lowercase": True,
    "password_require_numbers": True,
    "password_require_special": True,
    "session_timeout": 3600,     # 1時間
    "max_failed_logins": 5,
    "lockout_duration": 1800     # 30分
}

# 通知設定
NOTIFICATION_SETTINGS = {
    "email": {
        "enabled": True,
        "batch_size": 100,
        "delay": 5
    },
    "push": {
        "enabled": True,
        "batch_size": 1000,
        "delay": 1
    },
    "sms": {
        "enabled": False,
        "batch_size": 50,
        "delay": 10
    }
}

# ログ設定
LOG_SETTINGS = {
    "level": "INFO",
    "format": "json",
    "max_size": "100MB",
    "max_files": 10,
    "retention_days": 30
}

# 地域設定
LOCALE_SETTINGS = {
    "default": "ja_JP",
    "supported": ["ja_JP", "en_US", "en_GB"],
    "timezone": "Asia/Tokyo",
    "currency": "JPY"
}

# エラーメッセージ
ERROR_MESSAGES = {
    "validation": {
        "required_field": "必須フィールドです",
        "invalid_format": "形式が正しくありません",
        "too_long": "文字数が多すぎます",
        "too_short": "文字数が少なすぎます"
    },
    "authentication": {
        "invalid_credentials": "認証情報が正しくありません",
        "account_locked": "アカウントがロックされています",
        "session_expired": "セッションが期限切れです"
    },
    "authorization": {
        "insufficient_permissions": "権限が不足しています",
        "access_denied": "アクセスが拒否されました"
    },
    "resource": {
        "not_found": "リソースが見つかりません",
        "already_exists": "リソースは既に存在します",
        "deleted": "リソースは削除されました"
    }
}

# 成功メッセージ
SUCCESS_MESSAGES = {
    "created": "正常に作成されました",
    "updated": "正常に更新されました",
    "deleted": "正常に削除されました",
    "saved": "正常に保存されました",
    "uploaded": "正常にアップロードされました"
}
