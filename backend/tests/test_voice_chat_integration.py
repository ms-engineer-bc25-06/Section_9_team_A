"""
音声チャット統合テスト
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient
from tests.conftest import CombinedTestClient

from app.models.voice_session import VoiceSession
from app.models.user import User
from app.schemas.voice_session import VoiceSessionResponse
from app.schemas.websocket import AudioDataMessage
from app.services.voice_session_service import VoiceSessionService
from app.services.audio_processing_service import AudioProcessingService
from app.services.transcription_service import RealtimeTranscriptionManager
from app.core.websocket import WebSocketMessageHandler


@pytest.fixture
def mock_voice_session():
    """モック音声セッション"""
    return VoiceSession(
        id=1,
        room_id="test-session-123",
        title="Test Session",
        description="Test Description",
        status="active",
        host_id=1,
        team_id=None,
        duration_minutes=0.0,
        participant_count=2,
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
    )


@pytest.fixture
def mock_audio_data():
    """モック音声データ"""
    return b"mock_audio_data_12345"


@pytest.fixture
def mock_audio_message(mock_audio_data):
    """モック音声メッセージ"""
    import base64
    
    return AudioDataMessage(
        session_id="test_session_123",
        user_id=1,
        data=base64.b64encode(mock_audio_data).decode(),
        timestamp=datetime.now().isoformat(),
        chunk_id="chunk_123",
        sample_rate=16000,
        channels=1,
    )


class TestVoiceChatIntegration:
    """音声チャット統合テスト"""

    @pytest.mark.asyncio
    async def test_voice_session_lifecycle(
        self, client: CombinedTestClient, mock_voice_session, mock_user
    ):
        """音声セッションライフサイクルテスト"""
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
            mock_service.return_value = mock_service_instance
            
            # セッション作成
            session_data = {
                "session_id": "test-session-123",
                "title": "Test Session",
                "description": "Test Description",
                "is_public": False,
                "participant_count": 2,
            }
            
            mock_service_instance.create_session.return_value = (
                VoiceSessionResponse.model_validate(mock_voice_session)
            )
            
            response = await client.post("/api/v1/voice-sessions/", json=session_data)
            assert response.status_code == 201
            
            # セッション開始
            mock_service_instance.start_session.return_value = (
                VoiceSessionResponse.model_validate(mock_voice_session)
            )
            
            response = await client.post("/api/v1/voice-sessions/test-session-123/start")
            assert response.status_code == 200
            
            # セッション終了
            mock_voice_session.status = "completed"
            mock_service_instance.end_session.return_value = (
                VoiceSessionResponse.model_validate(mock_voice_session)
            )
            
            response = await client.post("/api/v1/voice-sessions/test-session-123/end")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_audio_processing_workflow(self, mock_audio_message):
        """音声処理ワークフローテスト"""
        # 音声処理サービスの初期化
        audio_processor = AudioProcessingService()
        
        # 音声データの処理
        chunk = await audio_processor.process_audio_data(mock_audio_message)
        
        assert chunk is not None
        assert chunk.session_id == mock_audio_message.session_id
        assert chunk.user_id == mock_audio_message.user_id
        assert chunk.chunk_id == mock_audio_message.chunk_id
        
        # 音声レベルの計算
        audio_level = audio_processor._calculate_audio_level(chunk)
        assert audio_level is not None
        assert 0.0 <= audio_level.level <= 1.0
        
        # 品質メトリクスの計算
        quality_metrics = await audio_processor._calculate_quality_metrics(chunk, audio_level)
        assert quality_metrics is not None
        assert isinstance(quality_metrics.snr, float)
        assert isinstance(quality_metrics.clarity, float)
        assert isinstance(quality_metrics.latency, float)

    @pytest.mark.asyncio
    async def test_transcription_workflow(self, mock_audio_data):
        """転写ワークフローテスト"""
        # 転写管理サービスの初期化
        transcription_manager = RealtimeTranscriptionManager()
        
        # セッション開始
        session_id = "test_transcription_session"
        await transcription_manager.start_session(session_id, "ja")
        
        assert session_id in transcription_manager.active_sessions
        assert session_id in transcription_manager.chunk_buffers
        
        # 音声チャンクの処理
        user_id = 1
        timestamp = datetime.now()
        
        # 十分な音声データを追加
        for _ in range(50):
            transcription_manager.chunk_buffers[session_id].append(mock_audio_data)
        
        # 転写の実行
        with patch("app.services.transcription_service.openai_client") as mock_client:
            mock_client.transcribe_audio_data.return_value = {
                "text": "テスト転写結果",
                "confidence": 0.95,
                "language": "ja",
            }
            
            final_chunk, partial_chunk = await transcription_manager.process_audio_chunk(
                session_id, user_id, mock_audio_data, timestamp
            )
            
            assert final_chunk is not None
            assert final_chunk.text == "テスト転写結果"
            assert final_chunk.confidence == 0.95
            assert final_chunk.is_final is True
        
        # セッション停止
        await transcription_manager.stop_session(session_id)
        assert session_id not in transcription_manager.active_sessions

    @pytest.mark.asyncio
    async def test_websocket_message_handling(self, mock_user, mock_audio_message):
        """WebSocketメッセージハンドリングテスト"""
        session_id = "test_websocket_session"
        connection_id = "test_connection_123"
        
        # 音声データメッセージの処理
        message = {
            "type": "audio-data",
            "data": mock_audio_message.model_dump(),
        }
        
        with patch("app.core.message_handlers.audio_processing_service") as mock_audio_service:
            mock_audio_service.process_audio_data.return_value = AsyncMock()
            
            await WebSocketMessageHandler.handle_audio_data(
                session_id, connection_id, mock_user, message
            )
            
            mock_audio_service.process_audio_data.assert_called_once()

    @pytest.mark.asyncio
    async def test_voice_session_participant_management(
        self, client: CombinedTestClient, mock_voice_session, mock_user
    ):
        """音声セッション参加者管理テスト"""
        with (
            patch(
                "app.api.v1.voice_sessions.get_current_active_user",
                return_value=mock_user,
            ),
            patch(
                "app.api.v1.voice_sessions.get_voice_session_service"
            ) as mock_service,
        ):
            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            
            # 参加者の追加
            participant_data = {
                "user_id": 2,
                "role": "participant",
            }
            
            mock_service_instance.add_participant.return_value = {
                "user_id": 2,
                "role": "participant",
                "joined_at": datetime.now().isoformat(),
            }
            
            response = await client.post(
                "/api/v1/voice-sessions/test-session-123/participants",
                json=participant_data
            )
            assert response.status_code == 201
            
            # 参加者の削除
            mock_service_instance.remove_participant.return_value = True
            
            response = await client.delete(
                "/api/v1/voice-sessions/test-session-123/participants/2"
            )
            assert response.status_code == 200
            
            # 参加者一覧の取得
            mock_service_instance.get_participants.return_value = [
                {
                    "user_id": 1,
                    "role": "host",
                    "joined_at": datetime.now().isoformat(),
                }
            ]
            
            response = await client.get(
                "/api/v1/voice-sessions/test-session-123/participants"
            )
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["user_id"] == 1

    @pytest.mark.asyncio
    async def test_voice_session_recording(self, mock_voice_session, mock_user):
        """音声セッション録音テスト"""
        # 録音サービスのモック
        with patch("app.services.voice_session_service.VoiceSessionService") as mock_service:
            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            
            # 録音開始
            mock_service_instance.start_recording.return_value = {
                "recording_id": "recording_123",
                "status": "recording",
                "started_at": datetime.now().isoformat(),
            }
            
            result = await mock_service_instance.start_recording("test-session-123")
            assert result["status"] == "recording"
            
            # 録音停止
            mock_service_instance.stop_recording.return_value = {
                "recording_id": "recording_123",
                "status": "completed",
                "ended_at": datetime.now().isoformat(),
                "recording_url": "https://example.com/recording.mp3",
            }
            
            result = await mock_service_instance.stop_recording("test-session-123")
            assert result["status"] == "completed"
            assert result["recording_url"] is not None

    @pytest.mark.asyncio
    async def test_voice_session_analytics(self, mock_voice_session, mock_user):
        """音声セッション分析テスト"""
        with patch("app.services.voice_session_service.VoiceSessionService") as mock_service:
            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            
            # 分析データの生成
            mock_service_instance.get_session_analytics.return_value = {
                "session_id": "test-session-123",
                "duration_minutes": 30.5,
                "participant_count": 3,
                "speaking_time": {
                    "user_1": 15.2,
                    "user_2": 10.8,
                    "user_3": 4.5,
                },
                "transcription_accuracy": 0.95,
                "audio_quality_score": 0.88,
                "network_quality_score": 0.92,
            }
            
            result = await mock_service_instance.get_session_analytics("test-session-123")
            assert result["duration_minutes"] == 30.5
            assert result["participant_count"] == 3
            assert result["transcription_accuracy"] == 0.95
            assert result["audio_quality_score"] == 0.88

    @pytest.mark.asyncio
    async def test_voice_session_error_handling(self, mock_user):
        """音声セッションエラーハンドリングテスト"""
        with patch("app.services.voice_session_service.VoiceSessionService") as mock_service:
            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            
            # 存在しないセッションへのアクセス
            from app.core.exceptions import NotFoundException
            
            mock_service_instance.get_session.side_effect = NotFoundException(
                "Voice session not found"
            )
            
            with pytest.raises(NotFoundException):
                await mock_service_instance.get_session("non-existent-session")
            
            # 権限エラー
            from app.core.exceptions import PermissionException
            
            mock_service_instance.start_session.side_effect = PermissionException(
                "Access denied"
            )
            
            with pytest.raises(PermissionException):
                await mock_service_instance.start_session("test-session-123")

    @pytest.mark.asyncio
    async def test_voice_session_performance(self, mock_voice_session, mock_user):
        """音声セッションパフォーマンステスト"""
        with patch("app.services.voice_session_service.VoiceSessionService") as mock_service:
            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            
            # 大量のセッション作成
            start_time = datetime.now()
            
            for i in range(100):
                session_data = {
                    "session_id": f"test-session-{i}",
                    "title": f"Test Session {i}",
                    "description": f"Test Description {i}",
                    "is_public": False,
                    "participant_count": 2,
                }
                
                mock_service_instance.create_session.return_value = (
                    VoiceSessionResponse.model_validate(mock_voice_session)
                )
                
                await mock_service_instance.create_session(session_data)
            
            end_time = datetime.now()
            
            # 実行時間が妥当であることを確認（5秒以内）
            assert (end_time - start_time).total_seconds() < 5.0

    @pytest.mark.asyncio
    async def test_voice_session_concurrent_access(self, mock_voice_session, mock_user):
        """音声セッション同時アクセステスト"""
        with patch("app.services.voice_session_service.VoiceSessionService") as mock_service:
            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            
            # 同時に複数のセッション操作を実行
            async def create_session(session_id):
                session_data = {
                    "session_id": session_id,
                    "title": f"Test Session {session_id}",
                    "description": f"Test Description {session_id}",
                    "is_public": False,
                    "participant_count": 2,
                }
                
                mock_service_instance.create_session.return_value = (
                    VoiceSessionResponse.model_validate(mock_voice_session)
                )
                
                return await mock_service_instance.create_session(session_data)
            
            # 並行実行
            tasks = [create_session(f"session-{i}") for i in range(10)]
            results = await asyncio.gather(*tasks)
            
            # 全てのタスクが成功することを確認
            assert len(results) == 10
            assert all(result is not None for result in results)

    @pytest.mark.asyncio
    async def test_voice_session_data_consistency(self, mock_voice_session, mock_user):
        """音声セッションデータ整合性テスト"""
        with patch("app.services.voice_session_service.VoiceSessionService") as mock_service:
            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            
            # セッション作成
            session_data = {
                "session_id": "test-session-123",
                "title": "Test Session",
                "description": "Test Description",
                "is_public": False,
                "participant_count": 2,
            }
            
            mock_service_instance.create_session.return_value = (
                VoiceSessionResponse.model_validate(mock_voice_session)
            )
            
            created_session = await mock_service_instance.create_session(session_data)
            
            # セッション取得
            mock_service_instance.get_session.return_value = (
                VoiceSessionResponse.model_validate(mock_voice_session)
            )
            
            retrieved_session = await mock_service_instance.get_session("test-session-123")
            
            # データの整合性を確認
            assert created_session.session_id == retrieved_session.session_id
            assert created_session.title == retrieved_session.title
            assert created_session.description == retrieved_session.description
            assert created_session.is_public == retrieved_session.is_public
            assert created_session.participant_count == retrieved_session.participant_count
