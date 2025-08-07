import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from datetime import datetime

from app.models.voice_session import VoiceSession
from app.models.user import User
from app.schemas.voice_session import VoiceSessionResponse
from app.schemas.common import StatusEnum


@pytest.fixture
def mock_voice_session():
    """モック音声セッション"""
    return VoiceSession(
        id=1,
        session_id="test-session-123",
        title="Test Session",
        description="Test Description",
        status=StatusEnum.ACTIVE,
        is_public=False,
        participant_count=2,
        user_id=1,
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
        is_active=True,
    )


class TestVoiceSessionControlAPI:
    """音声セッション制御APIテスト"""

    @pytest.mark.asyncio
    async def test_start_voice_session_success(
        self, client: AsyncClient, mock_voice_session, mock_user
    ):
        """セッション開始成功テスト"""
        with (
            patch(
                "app.api.v1.voice_sessions.get_current_active_user",
                return_value=mock_user,
            ),
            patch(
                "app.api.v1.voice_sessions.get_voice_session_service"
            ) as mock_service,
        ):
            # モックサービスの設定
            mock_service_instance = AsyncMock()
            mock_service_instance.start_session.return_value = (
                VoiceSessionResponse.model_validate(mock_voice_session)
            )
            mock_service.return_value = mock_service_instance

            response = await client.post(
                "/api/v1/voice-sessions/test-session-123/start"
            )

            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == "test-session-123"
            assert data["status"] == "active"

    @pytest.mark.asyncio
    async def test_end_voice_session_success(
        self, client: AsyncClient, mock_voice_session, mock_user
    ):
        """セッション終了成功テスト"""
        with (
            patch(
                "app.api.v1.voice_sessions.get_current_active_user",
                return_value=mock_user,
            ),
            patch(
                "app.api.v1.voice_sessions.get_voice_session_service"
            ) as mock_service,
        ):
            # モックサービスの設定
            mock_service_instance = AsyncMock()
            mock_voice_session.status = StatusEnum.COMPLETED
            mock_service_instance.end_session.return_value = (
                VoiceSessionResponse.model_validate(mock_voice_session)
            )
            mock_service.return_value = mock_service_instance

            response = await client.post("/api/v1/voice-sessions/test-session-123/end")

            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == "test-session-123"
            assert data["status"] == "completed"

    @pytest.mark.asyncio
    async def test_pause_voice_session_success(
        self, client: AsyncClient, mock_voice_session, mock_user
    ):
        """セッション一時停止成功テスト"""
        with (
            patch(
                "app.api.v1.voice_sessions.get_current_active_user",
                return_value=mock_user,
            ),
            patch(
                "app.api.v1.voice_sessions.get_voice_session_service"
            ) as mock_service,
        ):
            # モックサービスの設定
            mock_service_instance = AsyncMock()
            mock_voice_session.status = StatusEnum.PAUSED
            mock_service_instance.update_session.return_value = (
                VoiceSessionResponse.model_validate(mock_voice_session)
            )
            mock_service.return_value = mock_service_instance

            response = await client.post(
                "/api/v1/voice-sessions/test-session-123/pause"
            )

            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == "test-session-123"
            assert data["status"] == "paused"

    @pytest.mark.asyncio
    async def test_resume_voice_session_success(
        self, client: AsyncClient, mock_voice_session, mock_user
    ):
        """セッション再開成功テスト"""
        with (
            patch(
                "app.api.v1.voice_sessions.get_current_active_user",
                return_value=mock_user,
            ),
            patch(
                "app.api.v1.voice_sessions.get_voice_session_service"
            ) as mock_service,
        ):
            # モックサービスの設定
            mock_service_instance = AsyncMock()
            mock_voice_session.status = StatusEnum.ACTIVE
            mock_service_instance.update_session.return_value = (
                VoiceSessionResponse.model_validate(mock_voice_session)
            )
            mock_service.return_value = mock_service_instance

            response = await client.post(
                "/api/v1/voice-sessions/test-session-123/resume"
            )

            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == "test-session-123"
            assert data["status"] == "active"

    @pytest.mark.asyncio
    async def test_start_voice_session_not_found(self, client: AsyncClient, mock_user):
        """セッション開始 - セッションが見つからない場合"""
        with (
            patch(
                "app.api.v1.voice_sessions.get_current_active_user",
                return_value=mock_user,
            ),
            patch(
                "app.api.v1.voice_sessions.get_voice_session_service"
            ) as mock_service,
        ):
            # モックサービスの設定
            mock_service_instance = AsyncMock()
            from app.core.exceptions import NotFoundException

            mock_service_instance.start_session.side_effect = NotFoundException(
                "Voice session not found"
            )
            mock_service.return_value = mock_service_instance

            response = await client.post("/api/v1/voice-sessions/non-existent/start")

            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_start_voice_session_permission_denied(
        self, client: AsyncClient, mock_user
    ):
        """セッション開始 - 権限がない場合"""
        with (
            patch(
                "app.api.v1.voice_sessions.get_current_active_user",
                return_value=mock_user,
            ),
            patch(
                "app.api.v1.voice_sessions.get_voice_session_service"
            ) as mock_service,
        ):
            # モックサービスの設定
            mock_service_instance = AsyncMock()
            from app.core.exceptions import PermissionException

            mock_service_instance.start_session.side_effect = PermissionException(
                "Access denied"
            )
            mock_service.return_value = mock_service_instance

            response = await client.post(
                "/api/v1/voice-sessions/test-session-123/start"
            )

            assert response.status_code == 403


class TestVoiceSessionCRUDAPI:
    """音声セッションCRUD APIテスト"""

    @pytest.mark.asyncio
    async def test_get_voice_sessions(
        self, client: AsyncClient, mock_voice_session, mock_user
    ):
        """音声セッション一覧取得テスト"""
        with (
            patch(
                "app.api.v1.voice_sessions.get_current_active_user",
                return_value=mock_user,
            ),
            patch(
                "app.api.v1.voice_sessions.get_voice_session_service"
            ) as mock_service,
        ):
            # モックサービスの設定
            mock_service_instance = AsyncMock()
            from app.schemas.voice_session import VoiceSessionListResponse

            mock_service_instance.get_user_sessions.return_value = (
                VoiceSessionListResponse(
                    sessions=[VoiceSessionResponse.model_validate(mock_voice_session)],
                    total=1,
                    page=1,
                    size=10,
                    pages=1,
                )
            )
            mock_service.return_value = mock_service_instance

            response = await client.get("/api/v1/voice-sessions/")

            assert response.status_code == 200
            data = response.json()
            assert len(data["sessions"]) == 1
            assert data["total"] == 1

    @pytest.mark.asyncio
    async def test_create_voice_session(
        self, client: AsyncClient, mock_voice_session, mock_user
    ):
        """音声セッション作成テスト"""
        with (
            patch(
                "app.api.v1.voice_sessions.get_current_active_user",
                return_value=mock_user,
            ),
            patch(
                "app.api.v1.voice_sessions.get_voice_session_service"
            ) as mock_service,
        ):
            # モックサービスの設定
            mock_service_instance = AsyncMock()
            mock_service_instance.create_session.return_value = (
                VoiceSessionResponse.model_validate(mock_voice_session)
            )
            mock_service.return_value = mock_service_instance

            session_data = {
                "session_id": "new-session-123",
                "title": "New Session",
                "description": "New Description",
                "is_public": False,
                "participant_count": 3,
            }

            response = await client.post("/api/v1/voice-sessions/", json=session_data)

            assert response.status_code == 201
            data = response.json()
            assert data["session_id"] == "test-session-123"
            assert data["title"] == "Test Session"
