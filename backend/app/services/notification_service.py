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


class NotificationType(str, Enum):
    """通知タイプ"""

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    SYSTEM = "system"
    ANNOUNCEMENT = "announcement"


class NotificationPriority(str, Enum):
    """通知優先度"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Notification:
    """通知データクラス"""

    id: str
    type: NotificationType
    title: str
    content: str
    priority: NotificationPriority
    session_id: Optional[str] = None
    user_id: Optional[int] = None
    target_user_ids: Optional[List[int]] = None
    metadata: Optional[Dict[str, Any]] = None
    action_url: Optional[str] = None
    auto_dismiss: bool = True
    duration: int = 5000  # ミリ秒
    expires_at: Optional[datetime] = None
    created_at: datetime = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.id is None:
            self.id = str(uuid.uuid4())


class NotificationService:
    """通知サービス"""

    def __init__(self):
        # 通知履歴
        self.notifications: Dict[str, List[Notification]] = {}
        # セッション別通知
        self.session_notifications: Dict[str, List[Notification]] = {}
        # ユーザー別通知
        self.user_notifications: Dict[int, List[Notification]] = {}
        # 配信状態管理
        self.delivery_status: Dict[str, Dict[str, bool]] = {}

    async def create_notification(
        self,
        notification_type: NotificationType,
        title: str,
        content: str,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        session_id: Optional[str] = None,
        user_id: Optional[int] = None,
        target_user_ids: Optional[List[int]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        action_url: Optional[str] = None,
        auto_dismiss: bool = True,
        duration: int = 5000,
        expires_at: Optional[datetime] = None,
    ) -> Notification:
        """通知を作成"""
        try:
            notification = Notification(
                id=str(uuid.uuid4()),
                type=notification_type,
                title=title,
                content=content,
                priority=priority,
                session_id=session_id,
                user_id=user_id,
                target_user_ids=target_user_ids,
                metadata=metadata or {},
                action_url=action_url,
                auto_dismiss=auto_dismiss,
                duration=duration,
                expires_at=expires_at,
            )

            # 通知を保存
            await self._save_notification(notification)

            logger.info(
                f"Notification created: {notification.id}",
                type=notification_type.value,
                session_id=session_id,
                user_id=user_id,
            )

            return notification

        except Exception as e:
            logger.error(f"Failed to create notification: {e}")
            raise

    async def send_session_notification(
        self,
        session_id: str,
        title: str,
        content: str,
        notification_type: NotificationType = NotificationType.INFO,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Notification:
        """セッション内通知を送信"""
        try:
            notification = await self.create_notification(
                notification_type=notification_type,
                title=title,
                content=content,
                priority=priority,
                session_id=session_id,
                metadata=metadata,
            )

            # セッション内にブロードキャスト
            await self._broadcast_notification(notification)

            return notification

        except Exception as e:
            logger.error(f"Failed to send session notification: {e}")
            raise

    async def send_user_notification(
        self,
        user_id: int,
        title: str,
        content: str,
        notification_type: NotificationType = NotificationType.INFO,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None,
        action_url: Optional[str] = None,
    ) -> Notification:
        """ユーザー別通知を送信"""
        try:
            notification = await self.create_notification(
                notification_type=notification_type,
                title=title,
                content=content,
                priority=priority,
                user_id=user_id,
                metadata=metadata,
                action_url=action_url,
            )

            # ユーザーに配信
            await self._deliver_to_user(notification, user_id)

            return notification

        except Exception as e:
            logger.error(f"Failed to send user notification: {e}")
            raise

    async def send_broadcast_notification(
        self,
        title: str,
        content: str,
        notification_type: NotificationType = NotificationType.ANNOUNCEMENT,
        priority: NotificationPriority = NotificationPriority.HIGH,
        target_user_ids: Optional[List[int]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Notification:
        """ブロードキャスト通知を送信"""
        try:
            notification = await self.create_notification(
                notification_type=notification_type,
                title=title,
                content=content,
                priority=priority,
                target_user_ids=target_user_ids,
                metadata=metadata,
            )

            # 全ユーザーまたは指定ユーザーに配信
            if target_user_ids:
                for user_id in target_user_ids:
                    await self._deliver_to_user(notification, user_id)
            else:
                # 全アクティブユーザーに配信
                await self._broadcast_to_all_users(notification)

            return notification

        except Exception as e:
            logger.error(f"Failed to send broadcast notification: {e}")
            raise

    async def mark_notification_read(self, notification_id: str, user_id: int) -> bool:
        """通知を既読にする"""
        try:
            # 通知を検索
            notification = await self._find_notification(notification_id)
            if not notification:
                return False

            # 既読状態を更新
            notification.read_at = datetime.now()

            # 配信状態を更新
            await self._update_delivery_status(notification_id, user_id, "read")

            logger.info(
                f"Notification marked as read: {notification_id}",
                user_id=user_id,
            )

            return True

        except Exception as e:
            logger.error(f"Failed to mark notification as read: {e}")
            return False

    async def get_user_notifications(
        self, user_id: int, unread_only: bool = False, limit: int = 50
    ) -> List[Notification]:
        """ユーザーの通知を取得"""
        try:
            notifications = self.user_notifications.get(user_id, [])

            if unread_only:
                notifications = [
                    n
                    for n in notifications
                    if n.read_at is None
                    and (n.expires_at is None or n.expires_at > datetime.now())
                ]

            # 期限切れの通知を除外
            notifications = [
                n
                for n in notifications
                if n.expires_at is None or n.expires_at > datetime.now()
            ]

            # 作成日時でソート（新しい順）
            notifications.sort(key=lambda x: x.created_at, reverse=True)

            return notifications[:limit]

        except Exception as e:
            logger.error(f"Failed to get user notifications: {e}")
            return []

    async def get_session_notifications(
        self, session_id: str, limit: int = 50
    ) -> List[Notification]:
        """セッションの通知を取得"""
        try:
            notifications = self.session_notifications.get(session_id, [])

            # 期限切れの通知を除外
            notifications = [
                n
                for n in notifications
                if n.expires_at is None or n.expires_at > datetime.now()
            ]

            # 作成日時でソート（新しい順）
            notifications.sort(key=lambda x: x.created_at, reverse=True)

            return notifications[:limit]

        except Exception as e:
            logger.error(f"Failed to get session notifications: {e}")
            return []

    async def cleanup_expired_notifications(self):
        """期限切れの通知をクリーンアップ"""
        try:
            current_time = datetime.now()

            # 全通知から期限切れのものを削除
            for notification_list in self.notifications.values():
                notification_list[:] = [
                    n
                    for n in notification_list
                    if n.expires_at is None or n.expires_at > current_time
                ]

            # セッション別通知から期限切れのものを削除
            for notification_list in self.session_notifications.values():
                notification_list[:] = [
                    n
                    for n in notification_list
                    if n.expires_at is None or n.expires_at > current_time
                ]

            # ユーザー別通知から期限切れのものを削除
            for notification_list in self.user_notifications.values():
                notification_list[:] = [
                    n
                    for n in notification_list
                    if n.expires_at is None or n.expires_at > current_time
                ]

            logger.info("Expired notifications cleaned up")

        except Exception as e:
            logger.error(f"Failed to cleanup expired notifications: {e}")

    async def _save_notification(self, notification: Notification):
        """通知を保存"""
        # 全通知に追加
        if notification.id not in self.notifications:
            self.notifications[notification.id] = []
        self.notifications[notification.id].append(notification)

        # セッション別通知に追加
        if notification.session_id:
            if notification.session_id not in self.session_notifications:
                self.session_notifications[notification.session_id] = []
            self.session_notifications[notification.session_id].append(notification)

        # ユーザー別通知に追加
        if notification.user_id:
            if notification.user_id not in self.user_notifications:
                self.user_notifications[notification.user_id] = []
            self.user_notifications[notification.user_id].append(notification)

        # ターゲットユーザー別通知に追加
        if notification.target_user_ids:
            for user_id in notification.target_user_ids:
                if user_id not in self.user_notifications:
                    self.user_notifications[user_id] = []
                self.user_notifications[user_id].append(notification)

    async def _find_notification(self, notification_id: str) -> Optional[Notification]:
        """通知を検索"""
        if notification_id in self.notifications:
            for notification in self.notifications[notification_id]:
                return notification
        return None

    async def _broadcast_notification(self, notification: Notification):
        """通知をブロードキャスト"""
        if not notification.session_id:
            return

        notification_data = {
            "type": "notification",
            "notification": {
                "id": notification.id,
                "type": notification.type.value,
                "title": notification.title,
                "content": notification.content,
                "priority": notification.priority.value,
                "session_id": notification.session_id,
                "action_url": notification.action_url,
                "auto_dismiss": notification.auto_dismiss,
                "duration": notification.duration,
                "metadata": notification.metadata,
                "timestamp": notification.created_at.isoformat(),
            },
        }

        await manager.broadcast_to_session(notification_data, notification.session_id)

        # 配信状態を更新
        notification.delivered_at = datetime.now()

    async def _deliver_to_user(self, notification: Notification, user_id: int):
        """ユーザーに通知を配信"""
        notification_data = {
            "type": "notification",
            "notification": {
                "id": notification.id,
                "type": notification.type.value,
                "title": notification.title,
                "content": notification.content,
                "priority": notification.priority.value,
                "user_id": user_id,
                "action_url": notification.action_url,
                "auto_dismiss": notification.auto_dismiss,
                "duration": notification.duration,
                "metadata": notification.metadata,
                "timestamp": notification.created_at.isoformat(),
            },
        }

        await manager.broadcast_to_user(notification_data, user_id)

        # 配信状態を更新
        notification.delivered_at = datetime.now()
        await self._update_delivery_status(notification.id, user_id, "delivered")

    async def _broadcast_to_all_users(self, notification: Notification):
        """全ユーザーに通知をブロードキャスト"""
        notification_data = {
            "type": "notification",
            "notification": {
                "id": notification.id,
                "type": notification.type.value,
                "title": notification.title,
                "content": notification.content,
                "priority": notification.priority.value,
                "action_url": notification.action_url,
                "auto_dismiss": notification.auto_dismiss,
                "duration": notification.duration,
                "metadata": notification.metadata,
                "timestamp": notification.created_at.isoformat(),
            },
        }

        # 全アクティブユーザーに配信
        for user_id in manager.user_connections.keys():
            await manager.broadcast_to_user(notification_data, user_id)

        # 配信状態を更新
        notification.delivered_at = datetime.now()

    async def _update_delivery_status(
        self, notification_id: str, user_id: int, status: str
    ):
        """配信状態を更新"""
        if notification_id not in self.delivery_status:
            self.delivery_status[notification_id] = {}

        self.delivery_status[notification_id][str(user_id)] = status


# グローバルインスタンス
notification_service = NotificationService()
