from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ParticipantInfoResponse(BaseModel):
    """参加者情報レスポンス"""
    user_id: int = Field(..., description="ユーザーID")
    display_name: str = Field(..., description="表示名")
    email: str = Field(..., description="メールアドレス")
    role: str = Field(..., description="役割")
    status: str = Field(..., description="ステータス")
    joined_at: datetime = Field(..., description="参加時刻")
    last_activity: datetime = Field(..., description="最終活動時刻")
    is_speaking: bool = Field(..., description="発言中かどうか")
    audio_level: float = Field(..., description="音声レベル")
    speak_time_session: float = Field(..., description="セッション内発言時間")
    messages_sent: int = Field(..., description="送信メッセージ数")


class ParticipantListResponse(BaseModel):
    """参加者一覧レスポンス"""
    session_id: str = Field(..., description="セッションID")
    participants: List[ParticipantInfoResponse] = Field(..., description="参加者一覧")
    total_count: int = Field(..., description="総参加者数")
    connected_count: int = Field(..., description="接続中参加者数")
    speaking_count: int = Field(..., description="発言中参加者数")
    muted_count: int = Field(..., description="ミュート中参加者数")


class ParticipantUpdateRequest(BaseModel):
    """参加者更新リクエスト"""
    status: str = Field(..., description="新しいステータス")


class ParticipantRoleUpdateRequest(BaseModel):
    """参加者役割更新リクエスト"""
    new_role: str = Field(..., description="新しい役割")


class ParticipantMuteRequest(BaseModel):
    """参加者ミュートリクエスト"""
    muted: bool = Field(..., description="ミュート状態")


class ParticipantStatsResponse(BaseModel):
    """参加者統計レスポンス"""
    user_id: int = Field(..., description="ユーザーID")
    display_name: str = Field(..., description="表示名")
    role: str = Field(..., description="役割")
    joined_at: datetime = Field(..., description="参加時刻")
    last_activity: datetime = Field(..., description="最終活動時刻")
    speak_time_total: float = Field(..., description="総発言時間")
    speak_time_session: float = Field(..., description="セッション内発言時間")
    messages_sent: int = Field(..., description="送信メッセージ数")
    current_audio_level: float = Field(..., description="現在の音声レベル")
    is_speaking: bool = Field(..., description="発言中かどうか")
    quality_metrics: Dict[str, Any] = Field(default_factory=dict, description="品質メトリクス")


class SessionStatsResponse(BaseModel):
    """セッション統計レスポンス"""
    session_id: str = Field(..., description="セッションID")
    total_participants: int = Field(..., description="総参加者数")
    connected_participants: int = Field(..., description="接続中参加者数")
    speaking_participants: int = Field(..., description="発言中参加者数")
    muted_participants: int = Field(..., description="ミュート中参加者数")
    total_speak_time: float = Field(..., description="総発言時間")
    session_duration: float = Field(..., description="セッション継続時間")


class ParticipantActionRequest(BaseModel):
    """参加者アクションリクエスト"""
    action: str = Field(..., description="実行するアクション")
    action_data: Optional[Dict[str, Any]] = Field(default=None, description="アクションに必要なデータ")


class ParticipantActionResponse(BaseModel):
    """参加者アクションレスポンス"""
    action: str = Field(..., description="実行されたアクション")
    target_user_id: int = Field(..., description="対象ユーザーID")
    success: bool = Field(..., description="成功したかどうか")
    message: str = Field(..., description="結果メッセージ")
    participant_info: Optional[ParticipantInfoResponse] = Field(default=None, description="更新後の参加者情報")


class ParticipantJoinRequest(BaseModel):
    """参加者参加リクエスト"""
    session_id: str = Field(..., description="セッションID")
    role: str = Field(default="participant", description="参加する役割")


class ParticipantLeaveRequest(BaseModel):
    """参加者退出リクエスト"""
    session_id: str = Field(..., description="セッションID")
    reason: Optional[str] = Field(default=None, description="退出理由")


class AudioLevelUpdate(BaseModel):
    """音声レベル更新"""
    user_id: int = Field(..., description="ユーザーID")
    audio_level: float = Field(..., description="音声レベル")
    timestamp: datetime = Field(..., description="更新時刻")


class ParticipantActivityLog(BaseModel):
    """参加者活動ログ"""
    user_id: int = Field(..., description="ユーザーID")
    activity_type: str = Field(..., description="活動タイプ")
    timestamp: datetime = Field(..., description="活動時刻")
    details: Dict[str, Any] = Field(default_factory=dict, description="活動詳細")


class SessionParticipantSummary(BaseModel):
    """セッション参加者サマリー"""
    session_id: str = Field(..., description="セッションID")
    host_user_id: int = Field(..., description="ホストユーザーID")
    moderator_count: int = Field(..., description="モデレーター数")
    participant_count: int = Field(..., description="参加者数")
    observer_count: int = Field(..., description="オブザーバー数")
    total_connected: int = Field(..., description="総接続数")
    session_start_time: datetime = Field(..., description="セッション開始時刻")
    current_duration: float = Field(..., description="現在の継続時間")
