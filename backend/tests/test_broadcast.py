"""
ブロードキャスト機能のテスト
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.notification_service import (
    NotificationService,
    NotificationType,
    NotificationPriority,
    Notification,
)
from app.services.announcement_service import (
    AnnouncementService,
    AnnouncementType,
    AnnouncementPriority,
    Announcement,
)
from app.core.websocket import WebSocketMessageHandler, manager
from app.models.user import User


@pytest.fixture
def notification_service():
    """通知サービスのフィクスチャ"""
    return NotificationService()


@pytest.fixture
def announcement_service():
    """アナウンスメントサービスのフィクスチャ"""
    return AnnouncementService()


@pytest.fixture
def mock_user():
    """モックユーザー"""
    user = MagicMock(spec=User)
    user.id = 1
    user.display_name = "テストユーザー"
    user.avatar_url = "https://example.com/avatar.jpg"
    return user


@pytest.fixture
def mock_manager():
    """モックマネージャー"""
    with patch("app.services.notification_service.manager") as mock:
        mock.broadcast_to_session = AsyncMock()
        mock.broadcast_to_user = AsyncMock()
        yield mock


@pytest.fixture
def mock_announcement_manager():
    """アナウンスメントサービスのモックマネージャー"""
    with patch("app.services.announcement_service.manager") as mock:
        mock.broadcast_to_session = AsyncMock()
        mock.broadcast_to_user = AsyncMock()
        yield mock


class TestNotificationService:
    """通知サービスのテスト"""

    @pytest.mark.asyncio
    async def test_create_notification(self, notification_service):
        """通知作成テスト"""
        notification = await notification_service.create_notification(
            notification_type=NotificationType.INFO,
            title="テスト通知",
            content="テスト内容",
            priority=NotificationPriority.NORMAL,
            session_id="test_session",
        )

        assert notification.id is not None
        assert notification.type == NotificationType.INFO
        assert notification.title == "テスト通知"
        assert notification.content == "テスト内容"
        assert notification.priority == NotificationPriority.NORMAL
        assert notification.session_id == "test_session"

    @pytest.mark.asyncio
    async def test_send_session_notification(self, notification_service, mock_manager):
        """セッション通知送信テスト"""
        notification = await notification_service.send_session_notification(
            session_id="test_session",
            title="セッション通知",
            content="セッション内容",
            notification_type=NotificationType.SUCCESS,
        )

        assert notification.id is not None
        assert notification.type == NotificationType.SUCCESS
        mock_manager.broadcast_to_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_user_notification(self, notification_service, mock_manager):
        """ユーザー通知送信テスト"""
        notification = await notification_service.send_user_notification(
            user_id=1,
            title="ユーザー通知",
            content="ユーザー内容",
            notification_type=NotificationType.WARNING,
        )

        assert notification.id is not None
        assert notification.type == NotificationType.WARNING
        mock_manager.broadcast_to_user.assert_called_once()

    @pytest.mark.asyncio
    async def test_mark_notification_read(self, notification_service):
        """通知既読テスト"""
        # 通知を作成
        notification = await notification_service.create_notification(
            notification_type=NotificationType.INFO,
            title="テスト通知",
            content="テスト内容",
            user_id=1,
        )

        # 既読にする
        success = await notification_service.mark_notification_read(notification.id, 1)

        assert success is True
        assert notification.read_at is not None

    @pytest.mark.asyncio
    async def test_get_user_notifications(self, notification_service):
        """ユーザー通知取得テスト"""
        # 複数の通知を作成
        await notification_service.create_notification(
            notification_type=NotificationType.INFO,
            title="通知1",
            content="内容1",
            user_id=1,
        )
        await notification_service.create_notification(
            notification_type=NotificationType.WARNING,
            title="通知2",
            content="内容2",
            user_id=1,
        )

        notifications = await notification_service.get_user_notifications(1)

        assert len(notifications) == 2
        assert notifications[0].title == "通知2"  # 新しい順

    @pytest.mark.asyncio
    async def test_cleanup_expired_notifications(self, notification_service):
        """期限切れ通知クリーンアップテスト"""
        # 期限切れの通知を作成
        await notification_service.create_notification(
            notification_type=NotificationType.INFO,
            title="期限切れ通知",
            content="内容",
            user_id=1,
            expires_at=datetime.now() - timedelta(hours=1),
        )

        # 有効な通知を作成
        await notification_service.create_notification(
            notification_type=NotificationType.INFO,
            title="有効通知",
            content="内容",
            user_id=1,
            expires_at=datetime.now() + timedelta(hours=1),
        )

        # クリーンアップ実行
        await notification_service.cleanup_expired_notifications()

        # 期限切れの通知が削除されていることを確認
        notifications = await notification_service.get_user_notifications(1)
        assert len(notifications) == 1
        assert notifications[0].title == "有効通知"


class TestAnnouncementService:
    """アナウンスメントサービスのテスト"""

    @pytest.mark.asyncio
    async def test_create_announcement(self, announcement_service):
        """アナウンスメント作成テスト"""
        announcement = await announcement_service.create_announcement(
            announcement_type=AnnouncementType.GENERAL,
            title="テストアナウンス",
            content="テスト内容",
            sender="テスト送信者",
            priority=AnnouncementPriority.NORMAL,
            session_id="test_session",
        )

        assert announcement.id is not None
        assert announcement.type == AnnouncementType.GENERAL
        assert announcement.title == "テストアナウンス"
        assert announcement.content == "テスト内容"
        assert announcement.sender == "テスト送信者"
        assert announcement.priority == AnnouncementPriority.NORMAL
        assert announcement.session_id == "test_session"

    @pytest.mark.asyncio
    async def test_send_session_announcement(
        self, announcement_service, mock_announcement_manager
    ):
        """セッションアナウンスメント送信テスト"""
        announcement = await announcement_service.send_session_announcement(
            session_id="test_session",
            title="セッションアナウンス",
            content="セッション内容",
            sender="テスト送信者",
            announcement_type=AnnouncementType.MAINTENANCE,
        )

        assert announcement.id is not None
        assert announcement.type == AnnouncementType.MAINTENANCE
        mock_announcement_manager.broadcast_to_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_global_announcement(
        self, announcement_service, mock_announcement_manager
    ):
        """グローバルアナウンスメント送信テスト"""
        # モックマネージャーにユーザー接続を追加
        mock_announcement_manager.user_connections = {1: set(), 2: set()}

        announcement = await announcement_service.send_global_announcement(
            title="グローバルアナウンス",
            content="グローバル内容",
            sender="テスト送信者",
            announcement_type=AnnouncementType.EMERGENCY,
        )

        assert announcement.id is not None
        assert announcement.type == AnnouncementType.EMERGENCY
        mock_announcement_manager.broadcast_to_user.assert_called()

    @pytest.mark.asyncio
    async def test_dismiss_announcement(self, announcement_service):
        """アナウンスメント却下テスト"""
        # アナウンスメントを作成
        announcement = await announcement_service.create_announcement(
            announcement_type=AnnouncementType.GENERAL,
            title="テストアナウンス",
            content="テスト内容",
            sender="テスト送信者",
        )

        # 却下する
        success = await announcement_service.dismiss_announcement(announcement.id, 1)

        assert success is True
        assert 1 in announcement.dismissed_by

    @pytest.mark.asyncio
    async def test_get_active_announcements(self, announcement_service):
        """アクティブアナウンスメント取得テスト"""
        # 複数のアナウンスメントを作成
        await announcement_service.create_announcement(
            announcement_type=AnnouncementType.GENERAL,
            title="アナウンス1",
            content="内容1",
            sender="送信者1",
            priority=AnnouncementPriority.LOW,
        )
        await announcement_service.create_announcement(
            announcement_type=AnnouncementType.EMERGENCY,
            title="アナウンス2",
            content="内容2",
            sender="送信者2",
            priority=AnnouncementPriority.URGENT,
        )

        announcements = await announcement_service.get_active_announcements()

        assert len(announcements) == 2
        # 優先度の高い順にソートされていることを確認
        assert announcements[0].priority == AnnouncementPriority.URGENT

    @pytest.mark.asyncio
    async def test_cleanup_expired_announcements(self, announcement_service):
        """期限切れアナウンスメントクリーンアップテスト"""
        # 期限切れのアナウンスメントを作成
        await announcement_service.create_announcement(
            announcement_type=AnnouncementType.GENERAL,
            title="期限切れアナウンス",
            content="内容",
            sender="送信者",
            expires_at=datetime.now() - timedelta(hours=1),
        )

        # 有効なアナウンスメントを作成
        await announcement_service.create_announcement(
            announcement_type=AnnouncementType.GENERAL,
            title="有効アナウンス",
            content="内容",
            sender="送信者",
            expires_at=datetime.now() + timedelta(hours=1),
        )

        # クリーンアップ実行
        await announcement_service.cleanup_expired_announcements()

        # 期限切れのアナウンスメントが削除されていることを確認
        announcements = await announcement_service.get_active_announcements()
        assert len(announcements) == 1
        assert announcements[0].title == "有効アナウンス"


class TestWebSocketMessageHandler:
    """WebSocketメッセージハンドラーのテスト"""

    @pytest.mark.asyncio
    async def test_handle_notification_request(self, mock_user):
        """通知リクエスト処理テスト"""
        with patch("app.core.websocket.manager") as mock_manager:
            mock_manager.send_personal_message = AsyncMock()

            message = {
                "type": "notification_request",
                "title": "テスト通知",
                "content": "テスト内容",
                "notification_type": "info",
                "priority": "normal",
            }

            await WebSocketMessageHandler.handle_notification_request(
                "test_session", "test_connection", mock_user, message
            )

            mock_manager.send_personal_message.assert_called()

    @pytest.mark.asyncio
    async def test_handle_announcement_request(self, mock_user):
        """アナウンスメントリクエスト処理テスト"""
        with patch("app.core.websocket.manager") as mock_manager:
            mock_manager.send_personal_message = AsyncMock()

            message = {
                "type": "announcement_request",
                "title": "テストアナウンス",
                "content": "テスト内容",
                "announcement_type": "general",
                "priority": "normal",
            }

            await WebSocketMessageHandler.handle_announcement_request(
                "test_session", "test_connection", mock_user, message
            )

            mock_manager.send_personal_message.assert_called()

    @pytest.mark.asyncio
    async def test_handle_notification_dismiss(self, mock_user):
        """通知却下処理テスト"""
        with patch("app.core.websocket.manager") as mock_manager:
            mock_manager.send_personal_message = AsyncMock()

            message = {
                "type": "notification_dismiss",
                "notification_id": "test_notification_id",
            }

            await WebSocketMessageHandler.handle_notification_dismiss(
                "test_session", "test_connection", mock_user, message
            )

            mock_manager.send_personal_message.assert_called()

    @pytest.mark.asyncio
    async def test_handle_announcement_dismiss(self, mock_user):
        """アナウンスメント却下処理テスト"""
        with patch("app.core.websocket.manager") as mock_manager:
            mock_manager.send_personal_message = AsyncMock()

            message = {
                "type": "announcement_dismiss",
                "announcement_id": "test_announcement_id",
            }

            await WebSocketMessageHandler.handle_announcement_dismiss(
                "test_session", "test_connection", mock_user, message
            )

            mock_manager.send_personal_message.assert_called()

    @pytest.mark.asyncio
    async def test_handle_get_notifications(self, mock_user):
        """通知取得処理テスト"""
        with patch("app.core.websocket.manager") as mock_manager:
            mock_manager.send_personal_message = AsyncMock()

            message = {
                "type": "get_notifications",
                "unread_only": False,
                "limit": 10,
            }

            await WebSocketMessageHandler.handle_get_notifications(
                "test_session", "test_connection", mock_user, message
            )

            mock_manager.send_personal_message.assert_called()

    @pytest.mark.asyncio
    async def test_handle_get_announcements(self, mock_user):
        """アナウンスメント取得処理テスト"""
        with patch("app.core.websocket.manager") as mock_manager:
            mock_manager.send_personal_message = AsyncMock()

            message = {
                "type": "get_announcements",
                "limit": 10,
            }

            await WebSocketMessageHandler.handle_get_announcements(
                "test_session", "test_connection", mock_user, message
            )

            mock_manager.send_personal_message.assert_called()


class TestBroadcastIntegration:
    """ブロードキャスト統合テスト"""

    @pytest.mark.asyncio
    async def test_notification_broadcast_flow(
        self, notification_service, mock_manager
    ):
        """通知ブロードキャストフローテスト"""
        # セッション通知を送信
        notification = await notification_service.send_session_notification(
            session_id="test_session",
            title="統合テスト通知",
            content="統合テスト内容",
            notification_type=NotificationType.SUCCESS,
        )

        # ブロードキャストが呼ばれたことを確認
        mock_manager.broadcast_to_session.assert_called_once()

        # 通知データの構造を確認
        call_args = mock_manager.broadcast_to_session.call_args
        notification_data = call_args[0][0]
        assert notification_data["type"] == "notification"
        assert notification_data["notification"]["title"] == "統合テスト通知"

    @pytest.mark.asyncio
    async def test_announcement_broadcast_flow(
        self, announcement_service, mock_announcement_manager
    ):
        """アナウンスメントブロードキャストフローテスト"""
        # セッションアナウンスメントを送信
        announcement = await announcement_service.send_session_announcement(
            session_id="test_session",
            title="統合テストアナウンス",
            content="統合テスト内容",
            sender="テスト送信者",
            announcement_type=AnnouncementType.MAINTENANCE,
        )

        # ブロードキャストが呼ばれたことを確認
        mock_announcement_manager.broadcast_to_session.assert_called_once()

        # アナウンスメントデータの構造を確認
        call_args = mock_announcement_manager.broadcast_to_session.call_args
        announcement_data = call_args[0][0]
        assert announcement_data["type"] == "announcement"
        assert announcement_data["announcement"]["title"] == "統合テストアナウンス"
        assert announcement_data["announcement"]["sender"] == "テスト送信者"
