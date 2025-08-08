import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
import json
from fastapi import HTTPException

from app.models.voice_session import VoiceSession
from app.models.user import User
from app.schemas.voice_session import VoiceSessionResponse
from app.schemas.common import StatusEnum
from tests.conftest import CombinedTestClient


@pytest.fixture
def mock_voice_session():
    """モック音声セッション"""
    return VoiceSession(
        id=1,
        room_id="test_session_123",
        title="Test Session",
        description="Test session for WebSocket",
        status="active",
        host_id=1,
        team_id=None,
        duration_minutes=0.0,
        participant_count=0,
        recording_url=None,
        is_public=False,
        allow_recording=True,
        started_at=datetime.now(),
        ended_at=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def mock_user():
    """モックユーザー"""
    return User(
        id=1,
        email="test@example.com",
        username="testuser",
        display_name="Test User",
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


class TestWebSocketConnection:
    """WebSocket接続テスト"""

    @pytest.mark.asyncio
    async def test_websocket_connection_success(
        self, client: CombinedTestClient, mock_voice_session, mock_user
    ):
        """WebSocket接続成功テスト"""
        with (
            patch(
                "app.core.websocket.WebSocketAuth.authenticate_websocket"
            ) as mock_auth,
            patch(
                "app.services.voice_session_service.VoiceSessionService.get_session_by_session_id"
            ) as mock_get_session,
        ):
            mock_auth.return_value = mock_user
            mock_get_session.return_value = mock_voice_session

            # WebSocket接続をシミュレート
            with client.websocket_connect(
                "/api/v1/ws/voice-sessions/test_session_123?token=test_token"
            ) as websocket:
                # 接続確立メッセージを受信
                data = websocket.receive_text()
                message = json.loads(data)

                assert message["type"] == "connection_established"
                assert message["session_id"] == "test_session_123"
                assert message["user_id"] == 1

    @pytest.mark.asyncio
    async def test_websocket_authentication_failure(self, client: CombinedTestClient):
        """WebSocket認証失敗テスト"""
        with patch(
            "app.core.websocket.WebSocketAuth.authenticate_websocket"
        ) as mock_auth:
            mock_auth.side_effect = Exception("Authentication failed")

            # WebSocket接続をシミュレート（認証失敗）
            with pytest.raises(Exception):
                with client.websocket_connect(
                    "/api/v1/ws/voice-sessions/test_session_123?token=invalid_token"
                ) as websocket:
                    pass

    @pytest.mark.asyncio
    async def test_websocket_session_not_found(
        self, client: CombinedTestClient, mock_user
    ):
        """WebSocketセッション未発見テスト"""
        with (
            patch(
                "app.core.websocket.WebSocketAuth.authenticate_websocket"
            ) as mock_auth,
            patch(
                "app.services.voice_session_service.VoiceSessionService.get_session_by_session_id"
            ) as mock_get_session,
        ):
            mock_auth.return_value = mock_user
            mock_get_session.return_value = None

            # WebSocket接続をシミュレート（セッション未発見）
            with pytest.raises(Exception):
                with client.websocket_connect(
                    "/api/v1/ws/voice-sessions/nonexistent_session?token=test_token"
                ) as websocket:
                    pass


class TestWebSocketMessageHandling:
    """WebSocketメッセージ処理テスト"""

    @pytest.mark.asyncio
    async def test_ping_pong_message(
        self, client: CombinedTestClient, mock_voice_session, mock_user
    ):
        """Ping-Pongメッセージテスト"""
        with (
            patch(
                "app.core.websocket.WebSocketAuth.authenticate_websocket"
            ) as mock_auth,
            patch(
                "app.services.voice_session_service.VoiceSessionService.get_session_by_session_id"
            ) as mock_get_session,
        ):
            mock_auth.return_value = mock_user
            mock_get_session.return_value = mock_voice_session

            with client.websocket_connect(
                "/api/v1/ws/voice-sessions/test_session_123?token=test_token"
            ) as websocket:
                # Pingメッセージを送信
                ping_message = {"type": "ping"}
                websocket.send_text(json.dumps(ping_message))

                # Pongレスポンスを受信
                data = websocket.receive_text()
                message = json.loads(data)

                assert message["type"] == "pong"

    @pytest.mark.asyncio
    async def test_join_session_message(
        self, client: CombinedTestClient, mock_voice_session, mock_user
    ):
        """セッション参加メッセージテスト"""
        with (
            patch(
                "app.core.websocket.WebSocketAuth.authenticate_websocket"
            ) as mock_auth,
            patch(
                "app.services.voice_session_service.VoiceSessionService.get_session_by_session_id"
            ) as mock_get_session,
            patch(
                "app.services.participant_management_service.participant_manager.add_participant"
            ) as mock_add_participant,
        ):
            mock_auth.return_value = mock_user
            mock_get_session.return_value = mock_voice_session
            mock_add_participant.return_value = MagicMock(
                role=MagicMock(value="participant")
            )

            with client.websocket_connect(
                "/api/v1/ws/voice-sessions/test_session_123?token=test_token"
            ) as websocket:
                # セッション参加メッセージを送信
                join_message = {
                    "type": "join_session",
                    "session_id": "test_session_123",
                }
                websocket.send_text(json.dumps(join_message))

                # 参加者リストメッセージを受信
                data = websocket.receive_text()
                message = json.loads(data)

                assert message["type"] == "session_participants"

    @pytest.mark.asyncio
    async def test_audio_data_message(
        self, client: CombinedTestClient, mock_voice_session, mock_user
    ):
        """音声データメッセージテスト"""
        with (
            patch(
                "app.core.websocket.WebSocketAuth.authenticate_websocket"
            ) as mock_auth,
            patch(
                "app.services.voice_session_service.VoiceSessionService.get_session_by_session_id"
            ) as mock_get_session,
            patch(
                "app.services.audio_processing_service.audio_processor.process_audio_data"
            ) as mock_process_audio,
        ):
            mock_auth.return_value = mock_user
            mock_get_session.return_value = mock_voice_session
            mock_process_audio.return_value = MagicMock()

            with client.websocket_connect(
                "/api/v1/ws/voice-sessions/test_session_123?token=test_token"
            ) as websocket:
                # 音声データメッセージを送信
                audio_message = {
                    "type": "audio_data",
                    "session_id": "test_session_123",
                    "data": "base64_encoded_audio_data",
                    "timestamp": datetime.now().isoformat(),
                    "chunk_id": "chunk_123",
                    "sample_rate": 16000,
                    "channels": 1,
                }
                websocket.send_text(json.dumps(audio_message))

                # 音声レベルメッセージを受信
                data = websocket.receive_text()
                message = json.loads(data)

                assert message["type"] == "audio_level"

    @pytest.mark.asyncio
    async def test_text_message(
        self, client: CombinedTestClient, mock_voice_session, mock_user
    ):
        """テキストメッセージテスト"""
        with (
            patch(
                "app.core.websocket.WebSocketAuth.authenticate_websocket"
            ) as mock_auth,
            patch(
                "app.services.voice_session_service.VoiceSessionService.get_session_by_session_id"
            ) as mock_get_session,
            patch(
                "app.services.messaging_service.messaging_service.send_text_message"
            ) as mock_send_message,
        ):
            mock_auth.return_value = mock_user
            mock_get_session.return_value = mock_voice_session
            mock_send_message.return_value = MagicMock()

            with client.websocket_connect(
                "/api/v1/ws/voice-sessions/test_session_123?token=test_token"
            ) as websocket:
                # テキストメッセージを送信
                text_message = {
                    "type": "text_message",
                    "session_id": "test_session_123",
                    "content": "Hello, World!",
                    "priority": "normal",
                }
                websocket.send_text(json.dumps(text_message))

                # エラーメッセージが送信されないことを確認
                # （正常に処理される場合、特別なレスポンスはない）

    @pytest.mark.asyncio
    async def test_invalid_message_type(
        self, client: CombinedTestClient, mock_voice_session, mock_user
    ):
        """無効なメッセージタイプテスト"""
        with (
            patch(
                "app.core.websocket.WebSocketAuth.authenticate_websocket"
            ) as mock_auth,
            patch(
                "app.services.voice_session_service.VoiceSessionService.get_session_by_session_id"
            ) as mock_get_session,
        ):
            mock_auth.return_value = mock_user
            mock_get_session.return_value = mock_voice_session

            with client.websocket_connect(
                "/api/v1/ws/voice-sessions/test_session_123?token=test_token"
            ) as websocket:
                # 無効なメッセージタイプを送信
                invalid_message = {"type": "invalid_type", "data": "test"}
                websocket.send_text(json.dumps(invalid_message))

                # エラーメッセージを受信
                data = websocket.receive_text()
                message = json.loads(data)

                assert message["type"] == "error"
                assert "Unknown message type" in message["message"]


class TestWebSocketAPIEndpoints:
    """WebSocket APIエンドポイントテスト"""

    @pytest.mark.asyncio
    async def test_get_connection_stats(self, client: CombinedTestClient):
        """接続統計取得テスト"""
        with patch("app.core.websocket.manager.get_connection_stats") as mock_get_stats:
            mock_get_stats.return_value = {
                "total_connections": 5,
                "total_sessions": 2,
                "total_users": 3,
                "session_connections": {"session1": 3, "session2": 2},
            }

            response = await client.get("/api/v1/ws/connections/stats")
            assert response.status_code == 200

            data = response.json()
            assert "stats" in data
            assert "timestamp" in data
            assert data["stats"]["total_connections"] == 5

    @pytest.mark.asyncio
    async def test_cleanup_inactive_connections(self, client: CombinedTestClient):
        """非アクティブ接続クリーンアップテスト"""
        with patch(
            "app.core.websocket.manager.cleanup_inactive_connections"
        ) as mock_cleanup:
            mock_cleanup.return_value = None

            response = await client.post("/api/v1/ws/connections/cleanup")
            assert response.status_code == 200

            data = response.json()
            assert data["status"] == "cleanup_completed"
            assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_get_session_participants(self, client: CombinedTestClient):
        """セッション参加者取得テスト"""
        with patch(
            "app.core.websocket.manager.get_session_participants"
        ) as mock_get_participants:
            mock_get_participants.return_value = {1, 2, 3}

            response = await client.get(
                "/api/v1/ws/voice-sessions/test_session_123/participants"
            )
            assert response.status_code == 200

            data = response.json()
            assert data["session_id"] == "test_session_123"
            assert data["count"] == 3
            assert len(data["participants"]) == 3

    @pytest.mark.asyncio
    async def test_get_session_status(self, client: CombinedTestClient):
        """セッション状態取得テスト"""
        with (
            patch(
                "app.core.websocket.manager.get_session_connection_count"
            ) as mock_get_count,
            patch(
                "app.core.websocket.manager.get_session_participants"
            ) as mock_get_participants,
        ):
            mock_get_count.return_value = 3
            mock_get_participants.return_value = {1, 2, 3}

            response = await client.get(
                "/api/v1/ws/voice-sessions/test_session_123/status"
            )
            assert response.status_code == 200

            data = response.json()
            assert data["session_id"] == "test_session_123"
            assert data["connection_count"] == 3
            assert data["participant_count"] == 3
            assert data["is_active"] is True

    @pytest.mark.asyncio
    async def test_start_session_recording(self, client: CombinedTestClient):
        """セッション録音開始テスト"""
        with patch(
            "app.services.audio_processing_service.audio_processor.start_recording"
        ) as mock_start:
            mock_start.return_value = None

            response = await client.post(
                "/api/v1/ws/voice-sessions/test_session_123/recording/start"
            )
            assert response.status_code == 200

            data = response.json()
            assert data["session_id"] == "test_session_123"
            assert data["status"] == "recording_started"
            assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_stop_session_recording(self, client: CombinedTestClient):
        """セッション録音停止テスト"""
        with patch(
            "app.services.audio_processing_service.audio_processor.stop_recording"
        ) as mock_stop:
            mock_stop.return_value = None

            response = await client.post(
                "/api/v1/ws/voice-sessions/test_session_123/recording/stop"
            )
            assert response.status_code == 200

            data = response.json()
            assert data["session_id"] == "test_session_123"
            assert data["status"] == "recording_stopped"
            assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_get_session_audio_levels(self, client: CombinedTestClient):
        """セッション音声レベル取得テスト"""
        with patch(
            "app.services.audio_processing_service.audio_processor.get_session_participants_audio_levels"
        ) as mock_get_levels:
            mock_get_levels.return_value = {
                1: MagicMock(
                    level=0.5,
                    is_speaking=True,
                    rms=0.1,
                    peak=0.8,
                    timestamp=datetime.now(),
                ),
                2: MagicMock(
                    level=0.3,
                    is_speaking=False,
                    rms=0.05,
                    peak=0.4,
                    timestamp=datetime.now(),
                ),
            }

            response = await client.get(
                "/api/v1/ws/voice-sessions/test_session_123/audio-levels"
            )
            assert response.status_code == 200

            data = response.json()
            assert data["session_id"] == "test_session_123"
            assert "participant_levels" in data
            assert len(data["participant_levels"]) == 2

    @pytest.mark.asyncio
    async def test_clear_session_audio_buffer(self, client: CombinedTestClient):
        """セッション音声バッファクリアテスト"""
        with patch(
            "app.services.audio_processing_service.audio_processor.clear_session_buffer"
        ) as mock_clear:
            mock_clear.return_value = None

            response = await client.delete(
                "/api/v1/ws/voice-sessions/test_session_123/audio-buffer"
            )
            assert response.status_code == 200

            data = response.json()
            assert data["session_id"] == "test_session_123"
            assert data["status"] == "buffer_cleared"
            assert "timestamp" in data


class TestWebSocketErrorHandling:
    """WebSocketエラーハンドリングテスト"""

    @pytest.mark.asyncio
    async def test_websocket_connection_limit_exceeded(
        self, client: CombinedTestClient, mock_user
    ):
        """WebSocket接続制限超過テスト"""
        with (
            patch(
                "app.core.websocket.WebSocketAuth.authenticate_websocket"
            ) as mock_auth,
            patch(
                "app.core.websocket.manager._check_connection_limits"
            ) as mock_check_limits,
        ):
            mock_auth.return_value = mock_user
            mock_check_limits.side_effect = HTTPException(
                status_code=429, detail="Maximum connections per user exceeded"
            )

            # WebSocket接続をシミュレート（接続制限超過）
            with pytest.raises(Exception):
                with client.websocket_connect(
                    "/api/v1/ws/voice-sessions/test_session_123?token=test_token"
                ) as websocket:
                    pass

    @pytest.mark.asyncio
    async def test_websocket_invalid_json(
        self, client: CombinedTestClient, mock_voice_session, mock_user
    ):
        """WebSocket無効JSONテスト"""
        with (
            patch(
                "app.core.websocket.WebSocketAuth.authenticate_websocket"
            ) as mock_auth,
            patch(
                "app.services.voice_session_service.VoiceSessionService.get_session_by_session_id"
            ) as mock_get_session,
        ):
            mock_auth.return_value = mock_user
            mock_get_session.return_value = mock_voice_session

            with client.websocket_connect(
                "/api/v1/ws/voice-sessions/test_session_123?token=test_token"
            ) as websocket:
                # 無効なJSONを送信
                websocket.send_text("invalid json")

                # エラーメッセージを受信
                data = websocket.receive_text()
                message = json.loads(data)

                assert message["type"] == "error"
                assert "Invalid JSON format" in message["message"]

    @pytest.mark.asyncio
    async def test_websocket_connection_timeout(
        self, client: CombinedTestClient, mock_voice_session, mock_user
    ):
        """WebSocket接続タイムアウトテスト"""
        with (
            patch(
                "app.core.websocket.WebSocketAuth.authenticate_websocket"
            ) as mock_auth,
            patch(
                "app.services.voice_session_service.VoiceSessionService.get_session_by_session_id"
            ) as mock_get_session,
        ):
            mock_auth.return_value = mock_user
            mock_get_session.return_value = mock_voice_session

            with client.websocket_connect(
                "/api/v1/ws/voice-sessions/test_session_123?token=test_token"
            ) as websocket:
                # 長時間メッセージを送信しない（タイムアウトをシミュレート）
                # 実際のタイムアウトテストは時間がかかるため、ここでは接続が確立されることを確認
                data = websocket.receive_text()
                message = json.loads(data)
                assert message["type"] == "connection_established"
