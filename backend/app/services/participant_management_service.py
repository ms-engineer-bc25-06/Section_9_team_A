from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from enum import Enum
import structlog
from dataclasses import dataclass

from app.models.user import User
from app.core.websocket import manager

logger = structlog.get_logger()


class ParticipantRole(str, Enum):
    """参加者ロール"""

    HOST = "host"  # ホスト（完全権限）
    PARTICIPANT = "participant"  # 参加者（通常権限）
    GUEST = "guest"  # ゲスト（制限権限）
    OBSERVER = "observer"  # オブザーバー（閲覧のみ）


class ParticipantStatus(str, Enum):
    """参加者状態"""

    CONNECTED = "connected"  # 接続中
    DISCONNECTED = "disconnected"  # 切断中
    MUTED = "muted"  # ミュート中
    SPEAKING = "speaking"  # 話者中
    INACTIVE = "inactive"  # 非アクティブ


@dataclass
class ParticipantInfo:
    """参加者情報"""

    user_id: int
    user: User
    session_id: str
    role: ParticipantRole
    status: ParticipantStatus
    joined_at: datetime
    last_activity: datetime
    is_muted: bool = False
    is_speaking: bool = False
    audio_level: float = 0.0
    connection_quality: float = 1.0
    permissions: Set[str] = None

    def __post_init__(self):
        if self.permissions is None:
            self.permissions = self._get_default_permissions()

    def _get_default_permissions(self) -> Set[str]:
        """デフォルト権限を取得"""
        if self.role == ParticipantRole.HOST:
            return {
                "manage_session",
                "manage_participants",
                "record_audio",
                "mute_others",
                "remove_participants",
                "change_settings",
            }
        elif self.role == ParticipantRole.PARTICIPANT:
            return {"send_audio", "send_messages", "view_participants"}
        elif self.role == ParticipantRole.GUEST:
            return {"send_audio", "view_participants"}
        else:  # OBSERVER
            return {"view_participants"}


class ParticipantManagementService:
    """参加者管理サービス"""

    def __init__(self):
        # セッション別参加者管理
        self.session_participants: Dict[str, Dict[int, ParticipantInfo]] = {}
        # 参加者の活動履歴
        self.participant_activity: Dict[str, List[Dict]] = {}
        # 参加者の統計情報
        self.participant_stats: Dict[str, Dict[int, Dict]] = {}

    async def add_participant(
        self,
        session_id: str,
        user: User,
        role: ParticipantRole = ParticipantRole.PARTICIPANT,
    ) -> ParticipantInfo:
        """参加者を追加"""
        try:
            if session_id not in self.session_participants:
                self.session_participants[session_id] = {}
                self.participant_activity[session_id] = []
                self.participant_stats[session_id] = {}

            # 参加者情報を作成
            participant = ParticipantInfo(
                user_id=user.id,
                user=user,
                session_id=session_id,
                role=role,
                status=ParticipantStatus.CONNECTED,
                joined_at=datetime.now(),
                last_activity=datetime.now(),
            )

            # 参加者を登録
            self.session_participants[session_id][user.id] = participant

            # 統計情報を初期化
            self.participant_stats[session_id][user.id] = {
                "total_speaking_time": 0,
                "message_count": 0,
                "audio_chunks_sent": 0,
                "connection_drops": 0,
            }

            # 活動履歴を記録
            self._log_activity(
                session_id,
                user.id,
                "joined",
                {"role": role.value, "timestamp": datetime.now().isoformat()},
            )

            logger.info(
                f"Participant added: {user.display_name} to session {session_id}",
                user_id=user.id,
                session_id=session_id,
                role=role.value,
            )

            return participant

        except Exception as e:
            logger.error(f"Failed to add participant: {e}")
            raise

    async def remove_participant(
        self, session_id: str, user_id: int, reason: str = "left"
    ):
        """参加者を削除"""
        try:
            if (
                session_id in self.session_participants
                and user_id in self.session_participants[session_id]
            ):
                participant = self.session_participants[session_id][user_id]

                # 活動履歴を記録
                self._log_activity(
                    session_id,
                    user_id,
                    "left",
                    {
                        "reason": reason,
                        "duration": (
                            datetime.now() - participant.joined_at
                        ).total_seconds(),
                        "timestamp": datetime.now().isoformat(),
                    },
                )

                # 参加者を削除
                del self.session_participants[session_id][user_id]

                # セッションが空になった場合の処理
                if not self.session_participants[session_id]:
                    await self._cleanup_session(session_id)

                logger.info(
                    f"Participant removed: {participant.user.display_name} from session {session_id}",
                    user_id=user_id,
                    session_id=session_id,
                    reason=reason,
                )

        except Exception as e:
            logger.error(f"Failed to remove participant: {e}")
            raise

    async def update_participant_status(
        self, session_id: str, user_id: int, status: ParticipantStatus, **kwargs
    ):
        """参加者状態を更新"""
        try:
            if (
                session_id in self.session_participants
                and user_id in self.session_participants[session_id]
            ):
                participant = self.session_participants[session_id][user_id]
                old_status = participant.status

                # 状態を更新
                participant.status = status
                participant.last_activity = datetime.now()

                # 追加情報を更新
                for key, value in kwargs.items():
                    if hasattr(participant, key):
                        setattr(participant, key, value)

                # 活動履歴を記録
                self._log_activity(
                    session_id,
                    user_id,
                    "status_changed",
                    {
                        "old_status": old_status.value,
                        "new_status": status.value,
                        "timestamp": datetime.now().isoformat(),
                    },
                )

                logger.debug(
                    f"Participant status updated: {user_id} in session {session_id}",
                    old_status=old_status.value,
                    new_status=status.value,
                )

        except Exception as e:
            logger.error(f"Failed to update participant status: {e}")
            raise

    async def change_participant_role(
        self, session_id: str, user_id: int, new_role: ParticipantRole, changed_by: int
    ):
        """参加者ロールを変更"""
        try:
            if (
                session_id in self.session_participants
                and user_id in self.session_participants[session_id]
            ):
                participant = self.session_participants[session_id][user_id]
                old_role = participant.role

                # 権限チェック
                if not await self._can_change_role(session_id, changed_by, user_id):
                    raise PermissionError("Insufficient permissions to change role")

                # ロールを変更
                participant.role = new_role
                participant.permissions = participant._get_default_permissions()

                # 活動履歴を記録
                self._log_activity(
                    session_id,
                    user_id,
                    "role_changed",
                    {
                        "old_role": old_role.value,
                        "new_role": new_role.value,
                        "changed_by": changed_by,
                        "timestamp": datetime.now().isoformat(),
                    },
                )

                logger.info(
                    f"Participant role changed: {user_id} in session {session_id}",
                    old_role=old_role.value,
                    new_role=new_role.value,
                    changed_by=changed_by,
                )

        except Exception as e:
            logger.error(f"Failed to change participant role: {e}")
            raise

    async def mute_participant(
        self, session_id: str, user_id: int, muted_by: int, mute: bool = True
    ):
        """参加者をミュート/アンミュート"""
        try:
            if (
                session_id in self.session_participants
                and user_id in self.session_participants[session_id]
            ):
                participant = self.session_participants[session_id][user_id]

                # 権限チェック
                if not await self._can_mute_participant(session_id, muted_by, user_id):
                    raise PermissionError(
                        "Insufficient permissions to mute participant"
                    )

                # ミュート状態を変更
                participant.is_muted = mute
                participant.status = (
                    ParticipantStatus.MUTED if mute else ParticipantStatus.CONNECTED
                )

                # 活動履歴を記録
                self._log_activity(
                    session_id,
                    user_id,
                    "mute_changed",
                    {
                        "muted": mute,
                        "muted_by": muted_by,
                        "timestamp": datetime.now().isoformat(),
                    },
                )

                logger.info(
                    f"Participant mute changed: {user_id} in session {session_id}",
                    muted=mute,
                    muted_by=muted_by,
                )

        except Exception as e:
            logger.error(f"Failed to mute participant: {e}")
            raise

    async def get_session_participants(self, session_id: str) -> List[ParticipantInfo]:
        """セッションの参加者一覧を取得"""
        if session_id in self.session_participants:
            return list(self.session_participants[session_id].values())
        return []

    async def get_participant(
        self, session_id: str, user_id: int
    ) -> Optional[ParticipantInfo]:
        """特定の参加者情報を取得"""
        if (
            session_id in self.session_participants
            and user_id in self.session_participants[session_id]
        ):
            return self.session_participants[session_id][user_id]
        return None

    async def get_participant_stats(self, session_id: str, user_id: int) -> Dict:
        """参加者の統計情報を取得"""
        if (
            session_id in self.participant_stats
            and user_id in self.participant_stats[session_id]
        ):
            return self.participant_stats[session_id][user_id]
        return {}

    async def get_participant_activity(
        self, session_id: str, user_id: int, limit: int = 50
    ) -> List[Dict]:
        """参加者の活動履歴を取得"""
        if session_id in self.participant_activity:
            user_activities = [
                activity
                for activity in self.participant_activity[session_id]
                if activity.get("user_id") == user_id
            ]
            return user_activities[-limit:]
        return []

    async def check_permission(
        self, session_id: str, user_id: int, permission: str
    ) -> bool:
        """権限チェック"""
        participant = await self.get_participant(session_id, user_id)
        if participant:
            return permission in participant.permissions
        return False

    async def _can_change_role(
        self, session_id: str, changed_by: int, target_user_id: int
    ) -> bool:
        """ロール変更権限チェック"""
        # 自分自身のロール変更は可能
        if changed_by == target_user_id:
            return True

        # ホストのみが他の参加者のロールを変更可能
        changer = await self.get_participant(session_id, changed_by)
        return changer and changer.role == ParticipantRole.HOST

    async def _can_mute_participant(
        self, session_id: str, muted_by: int, target_user_id: int
    ) -> bool:
        """ミュート権限チェック"""
        # 自分自身のミュートは可能
        if muted_by == target_user_id:
            return True

        # ホストと参加者は他の参加者をミュート可能
        muter = await self.get_participant(session_id, muted_by)
        target = await self.get_participant(session_id, target_user_id)

        if not muter or not target:
            return False

        # ホストは誰でもミュート可能
        if muter.role == ParticipantRole.HOST:
            return True

        # 参加者はゲストとオブザーバーをミュート可能
        if muter.role == ParticipantRole.PARTICIPANT:
            return target.role in [ParticipantRole.GUEST, ParticipantRole.OBSERVER]

        return False

    def _log_activity(
        self, session_id: str, user_id: int, activity_type: str, details: Dict
    ):
        """活動履歴を記録"""
        if session_id not in self.participant_activity:
            self.participant_activity[session_id] = []

        activity = {
            "user_id": user_id,
            "activity_type": activity_type,
            "timestamp": datetime.now().isoformat(),
            **details,
        }

        self.participant_activity[session_id].append(activity)

        # 履歴サイズ制限（最新1000件まで保持）
        if len(self.participant_activity[session_id]) > 1000:
            self.participant_activity[session_id] = self.participant_activity[
                session_id
            ][-1000:]

    async def _cleanup_session(self, session_id: str):
        """セッションのクリーンアップ"""
        try:
            if session_id in self.session_participants:
                del self.session_participants[session_id]
            if session_id in self.participant_activity:
                del self.participant_activity[session_id]
            if session_id in self.participant_stats:
                del self.participant_stats[session_id]

            logger.info(f"Session cleaned up: {session_id}")

        except Exception as e:
            logger.error(f"Failed to cleanup session: {e}")


# グローバル参加者管理サービスインスタンス
participant_manager = ParticipantManagementService()
