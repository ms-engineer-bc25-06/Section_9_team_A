import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import WebSocket, WebSocketDisconnect

from app.core.websocket import manager, WebSocketAuth, WebSocketMessageHandler
from app.models.user import User
from app.core.exceptions import AuthenticationException
from app.schemas.websocket import WebSocketMessageValidator, ValidationError


@pytest.fixture
def mock_user():
    """テスト用ユーザーを作成"""
    user = User(
        id=1,
        username="testuser",
        email="test@example.com",
        firebase_uid="test_firebase_uid",
        is_active=True,
        display_name="Test User",
    )
    return user


@pytest.fixture
def mock_websocket():
    """テスト用WebSocketを作成"""
    websocket = AsyncMock(spec=WebSocket)
    websocket.query_params = {"token": "valid_token"}
    websocket.accept = AsyncMock()
    websocket.close = AsyncMock()
    websocket.receive_text = AsyncMock()
    websocket.send_text = AsyncMock()
    return websocket


@pytest.fixture
def mock_voice_session_service():
    """テスト用VoiceSessionServiceを作成"""
    service = AsyncMock()
    service.get_session_by_session_id = AsyncMock()
    return service


class TestWebSocketConnection:
    """WebSocket接続のテスト"""

    @pytest.mark.asyncio
    async def test_websocket_connection_success(self, mock_websocket, mock_user):
        """WebSocket接続成功のテスト"""
        with (
            patch("app.core.websocket.verify_firebase_token") as mock_verify,
            patch("app.core.websocket.AsyncSessionLocal") as mock_db_session,
            patch("app.core.websocket.VoiceSessionService") as mock_service_class,
        ):
            # モックの設定
            mock_verify.return_value = {
                "uid": "test_firebase_uid",
                "email": "test@example.com",
            }
            mock_db = AsyncMock()
            mock_db_session.return_value.__aenter__.return_value = mock_db
            mock_service = AsyncMock()
            mock_service.get_session_by_session_id.return_value = MagicMock(host_id=1)
            mock_service_class.return_value = mock_service

            # 接続テスト
            connection_id = await manager.connect(
                mock_websocket, "test-session", mock_user
            )

            assert connection_id is not None
            assert connection_id in manager.active_connections
            assert connection_id in manager.session_connections["test-session"]
            assert connection_id in manager.user_connections[1]

            # クリーンアップ
            await manager.disconnect(connection_id)

    @pytest.mark.asyncio
    async def test_websocket_connection_limits(self, mock_websocket, mock_user):
        """WebSocket接続制限のテスト"""
        # 最大接続数まで接続
        for i in range(manager.max_connections_per_user):
            connection_id = await manager.connect(
                mock_websocket, f"session-{i}", mock_user
            )
            assert connection_id is not None

        # 制限を超えた接続は失敗
        with pytest.raises(Exception):
            await manager.connect(mock_websocket, "session-limit", mock_user)

        # クリーンアップ
        for connection_id in list(manager.active_connections.keys()):
            await manager.disconnect(connection_id)

    @pytest.mark.asyncio
    async def test_websocket_connection_timeout(self, mock_websocket, mock_user):
        """WebSocket接続タイムアウトのテスト"""
        with patch("app.core.websocket.verify_firebase_token") as mock_verify:
            mock_verify.side_effect = asyncio.TimeoutError("Authentication timeout")

            with pytest.raises(asyncio.TimeoutError):
                await WebSocketAuth.authenticate_websocket(mock_websocket)

    @pytest.mark.asyncio
    async def test_websocket_connection_cleanup(self, mock_websocket, mock_user):
        """WebSocket接続クリーンアップのテスト"""
        # 接続を作成
        connection_id = await manager.connect(mock_websocket, "test-session", mock_user)

        # 非アクティブな接続としてマーク
        manager.last_heartbeat[connection_id] = (
            asyncio.get_event_loop().time() - 25 * 3600
        )  # 25時間前

        # クリーンアップ実行
        await manager.cleanup_inactive_connections()

        # 接続が削除されていることを確認
        assert connection_id not in manager.active_connections


class TestWebSocketAuthentication:
    """WebSocket認証のテスト"""

    @pytest.mark.asyncio
    async def test_websocket_auth_success(self, mock_websocket, mock_user):
        """WebSocket認証成功のテスト"""
        with (
            patch("app.core.websocket.verify_firebase_token") as mock_verify,
            patch("app.core.websocket.AsyncSessionLocal") as mock_db_session,
        ):
            mock_verify.return_value = {
                "uid": "test_firebase_uid",
                "email": "test@example.com",
            }
            mock_db = AsyncMock()
            mock_db_session.return_value.__aenter__.return_value = mock_db
            mock_db.execute.return_value.scalar_one_or_none.return_value = mock_user

            user = await WebSocketAuth.authenticate_websocket(mock_websocket)

            assert user is not None
            assert user.id == mock_user.id
            assert user.firebase_uid == mock_user.firebase_uid

    @pytest.mark.asyncio
    async def test_websocket_auth_no_token(self, mock_websocket):
        """WebSocket認証トークンなしのテスト"""
        mock_websocket.query_params = {}

        with pytest.raises(
            AuthenticationException, match="No authentication token provided"
        ):
            await WebSocketAuth.authenticate_websocket(mock_websocket)

    @pytest.mark.asyncio
    async def test_websocket_auth_invalid_token(self, mock_websocket):
        """WebSocket認証無効トークンのテスト"""
        with patch("app.core.websocket.verify_firebase_token") as mock_verify:
            mock_verify.return_value = None

            with pytest.raises(AuthenticationException, match="Invalid Firebase token"):
                await WebSocketAuth.authenticate_websocket(mock_websocket)

    @pytest.mark.asyncio
    async def test_websocket_auth_user_not_found(self, mock_websocket):
        """WebSocket認証ユーザー未発見のテスト"""
        with (
            patch("app.core.websocket.verify_firebase_token") as mock_verify,
            patch("app.core.websocket.AsyncSessionLocal") as mock_db_session,
        ):
            mock_verify.return_value = {
                "uid": "test_firebase_uid",
                "email": "test@example.com",
            }
            mock_db = AsyncMock()
            mock_db_session.return_value.__aenter__.return_value = mock_db
            mock_db.execute.return_value.scalar_one_or_none.return_value = None

            with pytest.raises(AuthenticationException, match="User not found"):
                await WebSocketAuth.authenticate_websocket(mock_websocket)


class TestWebSocketMessageHandler:
    """WebSocketメッセージハンドラーのテスト"""

    @pytest.mark.asyncio
    async def test_handle_join_session(self, mock_user):
        """セッション参加処理のテスト"""
        with (
            patch.object(manager, "get_session_participants") as mock_get_participants,
            patch.object(manager, "broadcast_to_session") as mock_broadcast,
        ):
            mock_get_participants.return_value = [{"id": "1", "username": "user1"}]

            await WebSocketMessageHandler.handle_join_session(
                "test-session", "connection-1", mock_user
            )

            mock_get_participants.assert_called_once_with("test-session")
            assert mock_broadcast.call_count == 2  # 参加者一覧 + 新規参加者通知

    @pytest.mark.asyncio
    async def test_handle_message_ping(self, mock_websocket, mock_user):
        """Pingメッセージ処理のテスト"""
        with patch.object(manager, "send_personal_message") as mock_send:
            message = {"type": "ping"}

            await WebSocketMessageHandler.handle_message(
                mock_websocket, message, "connection-1", mock_user
            )

            mock_send.assert_called_once()
            sent_message = mock_send.call_args[0][0]
            assert sent_message["type"] == "pong"

    @pytest.mark.asyncio
    async def test_handle_message_webrtc_signaling(self, mock_websocket, mock_user):
        """WebRTCシグナリングメッセージ処理のテスト"""
        with (
            patch.object(WebSocketMessageHandler, "_find_user_connection") as mock_find,
            patch.object(manager, "send_personal_message") as mock_send,
        ):
            mock_find.return_value = "target-connection"
            message = {"type": "offer", "to": "2", "data": "test-data"}

            await WebSocketMessageHandler.handle_message(
                mock_websocket, message, "connection-1", mock_user
            )

            mock_send.assert_called_once()
            sent_message = mock_send.call_args[0][0]
            assert sent_message["type"] == "offer"
            assert sent_message["from"] == "1"

    @pytest.mark.asyncio
    async def test_handle_message_unknown_type(self, mock_websocket, mock_user):
        """未知のメッセージタイプ処理のテスト"""
        message = {"type": "unknown_type"}

        # エラーが発生しないことを確認
        await WebSocketMessageHandler.handle_message(
            mock_websocket, message, "connection-1", mock_user
        )

    @pytest.mark.asyncio
    async def test_handle_message_missing_session_id(self, mock_websocket, mock_user):
        """セッションID不足メッセージ処理のテスト"""
        message = {"type": "join_session"}

        # エラーが発生しないことを確認
        await WebSocketMessageHandler.handle_message(
            mock_websocket, message, "connection-1", mock_user
        )


class TestWebSocketPermissions:
    """WebSocket権限チェックのテスト"""

    @pytest.mark.asyncio
    async def test_permission_check_session_host(self, mock_user):
        """セッションホスト権限チェックのテスト"""
        with patch.object(
            WebSocketMessageHandler, "_is_session_host_or_moderator"
        ) as mock_check:
            mock_check.return_value = True

            has_permission = await WebSocketMessageHandler._check_permission(
                mock_user, "test-session", "manage_session"
            )

            assert has_permission is True

    @pytest.mark.asyncio
    async def test_permission_check_not_host(self, mock_user):
        """非ホスト権限チェックのテスト"""
        with patch.object(
            WebSocketMessageHandler, "_is_session_host_or_moderator"
        ) as mock_check:
            mock_check.return_value = False

            has_permission = await WebSocketMessageHandler._check_permission(
                mock_user, "test-session", "manage_session"
            )

            assert has_permission is False

    @pytest.mark.asyncio
    async def test_participant_permission_self_operation(self, mock_user):
        """自分自身に対する操作権限のテスト"""
        has_permission = await WebSocketMessageHandler._check_participant_permission(
            mock_user, "test-session", 1, "mute_participant"
        )

        assert has_permission is True

    @pytest.mark.asyncio
    async def test_participant_permission_moderator(self, mock_user):
        """モデレーター権限のテスト"""
        with patch.object(WebSocketMessageHandler, "_check_permission") as mock_check:
            mock_check.return_value = True

            has_permission = (
                await WebSocketMessageHandler._check_participant_permission(
                    mock_user, "test-session", 2, "mute_participant"
                )
            )

            assert has_permission is True


class TestWebSocketMessageValidator:
    """WebSocketメッセージバリデーションのテスト"""

    def test_validate_message_structure_valid(self):
        """有効なメッセージ構造のテスト"""
        message = {"type": "ping"}
        is_valid, error = WebSocketMessageValidator.validate_message_structure(message)

        assert is_valid is True
        assert error is None

    def test_validate_message_structure_invalid(self):
        """無効なメッセージ構造のテスト"""
        # 辞書でない
        is_valid, error = WebSocketMessageValidator.validate_message_structure(
            "invalid"
        )
        assert is_valid is False
        assert "JSON object" in error

        # typeフィールドなし
        is_valid, error = WebSocketMessageValidator.validate_message_structure(
            {"data": "test"}
        )
        assert is_valid is False
        assert "type" in error

        # typeフィールドが文字列でない
        is_valid, error = WebSocketMessageValidator.validate_message_structure(
            {"type": 123}
        )
        assert is_valid is False
        assert "string" in error

    def test_validate_message_type_valid(self):
        """有効なメッセージタイプのテスト"""
        is_valid, error = WebSocketMessageValidator.validate_message_type("ping")
        assert is_valid is True
        assert error is None

    def test_validate_message_type_invalid(self):
        """無効なメッセージタイプのテスト"""
        is_valid, error = WebSocketMessageValidator.validate_message_type(
            "invalid_type"
        )
        assert is_valid is False
        assert "Invalid message type" in error

    def test_validate_session_id_valid(self):
        """有効なセッションIDのテスト"""
        is_valid, error = WebSocketMessageValidator.validate_session_id("room-1")
        assert is_valid is True
        assert error is None

    def test_validate_session_id_invalid(self):
        """無効なセッションIDのテスト"""
        # 空文字
        is_valid, error = WebSocketMessageValidator.validate_session_id("")
        assert is_valid is False
        assert "empty" in error

        # 無効な文字
        is_valid, error = WebSocketMessageValidator.validate_session_id("room@1")
        assert is_valid is False
        assert "invalid characters" in error

        # 長すぎる
        is_valid, error = WebSocketMessageValidator.validate_session_id("a" * 101)
        assert is_valid is False
        assert "too long" in error

    def test_validate_user_id_valid(self):
        """有効なユーザーIDのテスト"""
        # 文字列
        is_valid, error = WebSocketMessageValidator.validate_user_id("123")
        assert is_valid is True
        assert error is None

        # 整数
        is_valid, error = WebSocketMessageValidator.validate_user_id(123)
        assert is_valid is True
        assert error is None

    def test_validate_user_id_invalid(self):
        """無効なユーザーIDのテスト"""
        # 負の数
        is_valid, error = WebSocketMessageValidator.validate_user_id(-1)
        assert is_valid is False
        assert "positive" in error

        # 無効な文字列
        is_valid, error = WebSocketMessageValidator.validate_user_id("invalid")
        assert is_valid is False
        assert "integer" in error

    def test_validate_timestamp_valid(self):
        """有効なタイムスタンプのテスト"""
        is_valid, error = WebSocketMessageValidator.validate_timestamp(
            "2023-01-01T00:00:00"
        )
        assert is_valid is True
        assert error is None

    def test_validate_timestamp_invalid(self):
        """無効なタイムスタンプのテスト"""
        is_valid, error = WebSocketMessageValidator.validate_timestamp(
            "invalid-timestamp"
        )
        assert is_valid is False
        assert "Invalid timestamp format" in error

    def test_validate_audio_data_valid(self):
        """有効な音声データのテスト"""
        import base64

        valid_data = base64.b64encode(b"test audio data").decode()
        is_valid, error = WebSocketMessageValidator.validate_audio_data(valid_data)
        assert is_valid is True
        assert error is None

    def test_validate_audio_data_invalid(self):
        """無効な音声データのテスト"""
        # 空
        is_valid, error = WebSocketMessageValidator.validate_audio_data("")
        assert is_valid is False
        assert "empty" in error

        # 無効なBase64
        is_valid, error = WebSocketMessageValidator.validate_audio_data(
            "invalid-base64!"
        )
        assert is_valid is False
        assert "base64" in error

    def test_validate_message_complete(self):
        """メッセージ全体の妥当性テスト"""
        # 有効なpingメッセージ
        message = {"type": "ping"}
        is_valid, error = WebSocketMessageValidator.validate_message(message)
        assert is_valid is True
        assert error is None

        # 無効なメッセージ
        message = {"type": "invalid_type"}
        is_valid, error = WebSocketMessageValidator.validate_message(message)
        assert is_valid is False
        assert "Invalid message type" in error


class TestWebSocketErrorHandling:
    """WebSocketエラーハンドリングのテスト"""

    @pytest.mark.asyncio
    async def test_connection_error_handling(self, mock_websocket, mock_user):
        """接続エラーハンドリングのテスト"""
        with patch("app.core.websocket.verify_firebase_token") as mock_verify:
            mock_verify.side_effect = Exception("Connection failed")

            with pytest.raises(Exception):
                await WebSocketAuth.authenticate_websocket(mock_websocket)

    @pytest.mark.asyncio
    async def test_message_processing_error_handling(self, mock_websocket, mock_user):
        """メッセージ処理エラーハンドリングのテスト"""
        with patch.object(manager, "send_personal_message") as mock_send:
            mock_send.side_effect = Exception("Send failed")

            # エラーが発生してもクラッシュしないことを確認
            await WebSocketMessageHandler.handle_message(
                mock_websocket, {"type": "ping"}, "connection-1", mock_user
            )

    @pytest.mark.asyncio
    async def test_disconnect_error_handling(self, mock_websocket, mock_user):
        """切断エラーハンドリングのテスト"""
        # 接続を作成
        connection_id = await manager.connect(mock_websocket, "test-session", mock_user)

        # 切断時にエラーが発生してもクラッシュしないことを確認
        with patch.object(
            mock_websocket, "close", side_effect=Exception("Close failed")
        ):
            await manager.disconnect(connection_id)

        # 接続が適切にクリーンアップされていることを確認
        assert connection_id not in manager.active_connections


class TestWebSocketPerformance:
    """WebSocketパフォーマンスのテスト"""

    @pytest.mark.asyncio
    async def test_multiple_connections_performance(self, mock_websocket, mock_user):
        """複数接続のパフォーマンステスト"""
        import time

        start_time = time.time()

        # 複数の接続を作成
        connections = []
        for i in range(10):
            connection_id = await manager.connect(
                mock_websocket, f"session-{i}", mock_user
            )
            connections.append(connection_id)

        creation_time = time.time() - start_time

        # 接続作成が1秒以内に完了することを確認
        assert creation_time < 1.0

        # クリーンアップ
        for connection_id in connections:
            await manager.disconnect(connection_id)

    @pytest.mark.asyncio
    async def test_broadcast_performance(self, mock_websocket, mock_user):
        """ブロードキャストのパフォーマンステスト"""
        import time

        # 複数の接続を作成
        connections = []
        for i in range(5):
            connection_id = await manager.connect(
                mock_websocket, f"session-{i}", mock_user
            )
            connections.append(connection_id)

        # ブロードキャストのパフォーマンスを測定
        start_time = time.time()
        await manager.broadcast_to_session({"type": "test"}, "session-0")
        broadcast_time = time.time() - start_time

        # ブロードキャストが100ms以内に完了することを確認
        assert broadcast_time < 0.1

        # クリーンアップ
        for connection_id in connections:
            await manager.disconnect(connection_id)

    @pytest.mark.asyncio
    async def test_connection_cleanup_performance(self, mock_websocket, mock_user):
        """接続クリーンアップのパフォーマンステスト"""
        import time

        # 複数の接続を作成
        connections = []
        for i in range(20):
            connection_id = await manager.connect(
                mock_websocket, f"session-{i}", mock_user
            )
            connections.append(connection_id)

        # 非アクティブな接続としてマーク
        for connection_id in connections:
            manager.last_heartbeat[connection_id] = (
                asyncio.get_event_loop().time() - 25 * 3600
            )

        # クリーンアップのパフォーマンスを測定
        start_time = time.time()
        await manager.cleanup_inactive_connections()
        cleanup_time = time.time() - start_time

        # クリーンアップが1秒以内に完了することを確認
        assert cleanup_time < 1.0

        # すべての接続が削除されていることを確認
        assert len(manager.active_connections) == 0
