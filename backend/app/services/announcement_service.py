from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import structlog
from dataclasses import dataclass
import json
import uuid

from app.core.websocket import manager
from app.models.user import User

logger = structlog.get_logger()


class AnnouncementType(str, Enum):
    """アナウンスメントタイプ"""

    GENERAL = "general"
    MAINTENANCE = "maintenance"
    UPDATE = "update"
    EMERGENCY = "emergency"
    FEATURE = "feature"
    EVENT = "event"


class AnnouncementPriority(str, Enum):
    """アナウンスメント優先度"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Announcement:
    """アナウンスメントデータクラス"""

    id: str
    type: AnnouncementType
    title: str
    content: str
    priority: AnnouncementPriority
    sender: str
    session_id: Optional[str] = None
    target_user_ids: Optional[List[int]] = None
    metadata: Optional[Dict[str, Any]] = None
    action_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime = None
    delivered_at: Optional[datetime] = None
    dismissed_by: Optional[List[int]] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.dismissed_by is None:
            self.dismissed_by = []


class AnnouncementService:
    """アナウンスメントサービス"""

    def __init__(self):
        # アナウンスメント履歴
        self.announcements: Dict[str, List[Announcement]] = {}
        # セッション別アナウンスメント
        self.session_announcements: Dict[str, List[Announcement]] = {}
        # ユーザー別アナウンスメント
        self.user_announcements: Dict[int, List[Announcement]] = {}
        # アクティブなアナウンスメント
        self.active_announcements: List[Announcement] = []
        # 配信状態管理
        self.delivery_status: Dict[str, Dict[str, bool]] = {}

    async def create_announcement(
        self,
        announcement_type: AnnouncementType,
        title: str,
        content: str,
        sender: str,
        priority: AnnouncementPriority = AnnouncementPriority.NORMAL,
        session_id: Optional[str] = None,
        target_user_ids: Optional[List[int]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        action_url: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> Announcement:
        """アナウンスメントを作成"""
        try:
            announcement = Announcement(
                id=str(uuid.uuid4()),
                type=announcement_type,
                title=title,
                content=content,
                priority=priority,
                sender=sender,
                session_id=session_id,
                target_user_ids=target_user_ids,
                metadata=metadata or {},
                action_url=action_url,
                expires_at=expires_at,
            )

            # アナウンスメントを保存
            await self._save_announcement(announcement)

            # アクティブなアナウンスメントに追加
            if not expires_at or expires_at > datetime.now():
                self.active_announcements.append(announcement)

            logger.info(
                f"Announcement created: {announcement.id}",
                type=announcement_type.value,
                session_id=session_id,
                sender=sender,
            )

            return announcement

        except Exception as e:
            logger.error(f"Failed to create announcement: {e}")
            raise

    async def send_session_announcement(
        self,
        session_id: str,
        title: str,
        content: str,
        sender: str,
        announcement_type: AnnouncementType = AnnouncementType.GENERAL,
        priority: AnnouncementPriority = AnnouncementPriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None,
        expires_at: Optional[datetime] = None,
    ) -> Announcement:
        """セッション内アナウンスメントを送信"""
        try:
            announcement = await self.create_announcement(
                announcement_type=announcement_type,
                title=title,
                content=content,
                sender=sender,
                priority=priority,
                session_id=session_id,
                metadata=metadata,
                expires_at=expires_at,
            )

            # セッション内にブロードキャスト
            await self._broadcast_announcement(announcement)

            return announcement

        except Exception as e:
            logger.error(f"Failed to send session announcement: {e}")
            raise

    async def send_global_announcement(
        self,
        title: str,
        content: str,
        sender: str,
        announcement_type: AnnouncementType = AnnouncementType.GENERAL,
        priority: AnnouncementPriority = AnnouncementPriority.NORMAL,
        target_user_ids: Optional[List[int]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        expires_at: Optional[datetime] = None,
    ) -> Announcement:
        """グローバルアナウンスメントを送信"""
        try:
            announcement = await self.create_announcement(
                announcement_type=announcement_type,
                title=title,
                content=content,
                sender=sender,
                priority=priority,
                target_user_ids=target_user_ids,
                metadata=metadata,
                expires_at=expires_at,
            )

            # 全ユーザーまたは指定ユーザーに配信
            if target_user_ids:
                for user_id in target_user_ids:
                    await self._deliver_to_user(announcement, user_id)
            else:
                # 全アクティブユーザーに配信
                await self._broadcast_to_all_users(announcement)

            return announcement

        except Exception as e:
            logger.error(f"Failed to send global announcement: {e}")
            raise

    async def dismiss_announcement(self, announcement_id: str, user_id: int) -> bool:
        """アナウンスメントを却下"""
        try:
            # アナウンスメントを検索
            announcement = await self._find_announcement(announcement_id)
            if not announcement:
                return False

            # 却下ユーザーリストに追加
            if user_id not in announcement.dismissed_by:
                announcement.dismissed_by.append(user_id)

            # 配信状態を更新
            await self._update_delivery_status(announcement_id, user_id, "dismissed")

            logger.info(
                f"Announcement dismissed: {announcement_id}",
                user_id=user_id,
            )

            return True

        except Exception as e:
            logger.error(f"Failed to dismiss announcement: {e}")
            return False

    async def get_active_announcements(
        self, user_id: Optional[int] = None, session_id: Optional[str] = None
    ) -> List[Announcement]:
        """アクティブなアナウンスメントを取得"""
        try:
            current_time = datetime.now()

            # 期限切れのアナウンスメントを除外
            active_announcements = [
                a
                for a in self.active_announcements
                if a.expires_at is None or a.expires_at > current_time
            ]

            # ユーザーが却下したアナウンスメントを除外
            if user_id:
                active_announcements = [
                    a for a in active_announcements if user_id not in a.dismissed_by
                ]

            # セッション別フィルタリング
            if session_id:
                active_announcements = [
                    a
                    for a in active_announcements
                    if a.session_id == session_id or a.session_id is None
                ]

            # 優先度でソート（高い順）
            active_announcements.sort(
                key=lambda x: (
                    x.priority.value == "urgent",
                    x.priority.value == "high",
                    x.priority.value == "normal",
                    x.priority.value == "low",
                    x.created_at,
                ),
                reverse=True,
            )

            return active_announcements

        except Exception as e:
            logger.error(f"Failed to get active announcements: {e}")
            return []

    async def get_user_announcements(
        self, user_id: int, limit: int = 50
    ) -> List[Announcement]:
        """ユーザーのアナウンスメントを取得"""
        try:
            announcements = self.user_announcements.get(user_id, [])

            # 期限切れのアナウンスメントを除外
            current_time = datetime.now()
            announcements = [
                a
                for a in announcements
                if a.expires_at is None or a.expires_at > current_time
            ]

            # 作成日時でソート（新しい順）
            announcements.sort(key=lambda x: x.created_at, reverse=True)

            return announcements[:limit]

        except Exception as e:
            logger.error(f"Failed to get user announcements: {e}")
            return []

    async def get_session_announcements(
        self, session_id: str, limit: int = 50
    ) -> List[Announcement]:
        """セッションのアナウンスメントを取得"""
        try:
            announcements = self.session_announcements.get(session_id, [])

            # 期限切れのアナウンスメントを除外
            current_time = datetime.now()
            announcements = [
                a
                for a in announcements
                if a.expires_at is None or a.expires_at > current_time
            ]

            # 作成日時でソート（新しい順）
            announcements.sort(key=lambda x: x.created_at, reverse=True)

            return announcements[:limit]

        except Exception as e:
            logger.error(f"Failed to get session announcements: {e}")
            return []

    async def cleanup_expired_announcements(self):
        """期限切れのアナウンスメントをクリーンアップ"""
        try:
            current_time = datetime.now()

            # アクティブなアナウンスメントから期限切れのものを削除
            self.active_announcements[:] = [
                a
                for a in self.active_announcements
                if a.expires_at is None or a.expires_at > current_time
            ]

            # 全アナウンスメントから期限切れのものを削除
            for announcement_list in self.announcements.values():
                announcement_list[:] = [
                    a
                    for a in announcement_list
                    if a.expires_at is None or a.expires_at > current_time
                ]

            # セッション別アナウンスメントから期限切れのものを削除
            for announcement_list in self.session_announcements.values():
                announcement_list[:] = [
                    a
                    for a in announcement_list
                    if a.expires_at is None or a.expires_at > current_time
                ]

            # ユーザー別アナウンスメントから期限切れのものを削除
            for announcement_list in self.user_announcements.values():
                announcement_list[:] = [
                    a
                    for a in announcement_list
                    if a.expires_at is None or a.expires_at > current_time
                ]

            logger.info("Expired announcements cleaned up")

        except Exception as e:
            logger.error(f"Failed to cleanup expired announcements: {e}")

    async def _save_announcement(self, announcement: Announcement):
        """アナウンスメントを保存"""
        # 全アナウンスメントに追加
        if announcement.id not in self.announcements:
            self.announcements[announcement.id] = []
        self.announcements[announcement.id].append(announcement)

        # セッション別アナウンスメントに追加
        if announcement.session_id:
            if announcement.session_id not in self.session_announcements:
                self.session_announcements[announcement.session_id] = []
            self.session_announcements[announcement.session_id].append(announcement)

        # ターゲットユーザー別アナウンスメントに追加
        if announcement.target_user_ids:
            for user_id in announcement.target_user_ids:
                if user_id not in self.user_announcements:
                    self.user_announcements[user_id] = []
                self.user_announcements[user_id].append(announcement)

    async def _find_announcement(self, announcement_id: str) -> Optional[Announcement]:
        """アナウンスメントを検索"""
        if announcement_id in self.announcements:
            for announcement in self.announcements[announcement_id]:
                return announcement
        return None

    async def _broadcast_announcement(self, announcement: Announcement):
        """アナウンスメントをブロードキャスト"""
        if not announcement.session_id:
            return

        announcement_data = {
            "type": "announcement",
            "announcement": {
                "id": announcement.id,
                "type": announcement.type.value,
                "title": announcement.title,
                "content": announcement.content,
                "priority": announcement.priority.value,
                "sender": announcement.sender,
                "session_id": announcement.session_id,
                "action_url": announcement.action_url,
                "expires_at": announcement.expires_at.isoformat()
                if announcement.expires_at
                else None,
                "metadata": announcement.metadata,
                "timestamp": announcement.created_at.isoformat(),
            },
        }

        await manager.broadcast_to_session(announcement_data, announcement.session_id)

        # 配信状態を更新
        announcement.delivered_at = datetime.now()

    async def _deliver_to_user(self, announcement: Announcement, user_id: int):
        """ユーザーにアナウンスメントを配信"""
        announcement_data = {
            "type": "announcement",
            "announcement": {
                "id": announcement.id,
                "type": announcement.type.value,
                "title": announcement.title,
                "content": announcement.content,
                "priority": announcement.priority.value,
                "sender": announcement.sender,
                "user_id": user_id,
                "action_url": announcement.action_url,
                "expires_at": announcement.expires_at.isoformat()
                if announcement.expires_at
                else None,
                "metadata": announcement.metadata,
                "timestamp": announcement.created_at.isoformat(),
            },
        }

        await manager.broadcast_to_user(announcement_data, user_id)

        # 配信状態を更新
        announcement.delivered_at = datetime.now()
        await self._update_delivery_status(announcement.id, user_id, "delivered")

    async def _broadcast_to_all_users(self, announcement: Announcement):
        """全ユーザーにアナウンスメントをブロードキャスト"""
        announcement_data = {
            "type": "announcement",
            "announcement": {
                "id": announcement.id,
                "type": announcement.type.value,
                "title": announcement.title,
                "content": announcement.content,
                "priority": announcement.priority.value,
                "sender": announcement.sender,
                "action_url": announcement.action_url,
                "expires_at": announcement.expires_at.isoformat()
                if announcement.expires_at
                else None,
                "metadata": announcement.metadata,
                "timestamp": announcement.created_at.isoformat(),
            },
        }

        # 全アクティブユーザーに配信
        for user_id in manager.user_connections.keys():
            await manager.broadcast_to_user(announcement_data, user_id)

        # 配信状態を更新
        announcement.delivered_at = datetime.now()

    async def _update_delivery_status(
        self, announcement_id: str, user_id: int, status: str
    ):
        """配信状態を更新"""
        if announcement_id not in self.delivery_status:
            self.delivery_status[announcement_id] = {}

        self.delivery_status[announcement_id][str(user_id)] = status


# グローバルインスタンス
announcement_service = AnnouncementService()
