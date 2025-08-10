import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from app.services.session_state_service import (
    SessionStateManager,
    SessionState,
    ParticipantState,
    RecordingState,
    SessionParticipant,
    SessionRecording,
    SessionTranscription,
    SessionAnalytics,
    SessionStateInfo,
    session_state_manager,
)
from app.core.websocket import WebSocketMessageHandler
from app.models.user import User


@pytest.fixture
def sample_user():
    """サンプルユーザー"""
            return User(
            id=1,
            email="test@example.com",
            username="testuser",
            full_name="テストユーザー",
            is_active=True,
        )


@pytest.fixture
def sample_user2():
    """サンプルユーザー2"""
    return User(
        id=2,
        email="test2@example.com",
        display_name="テストユーザー2",
        is_active=True,
    )


class TestSessionStateManager:
    """セッション状態管理クラスのテスト"""

    @pytest.mark.asyncio
    async def test_create_session(self, sample_user):
        """セッション作成テスト"""
        session_id = "test_session_123"
        
        session_state = await session_state_manager.create_session(session_id, sample_user)
        
        assert session_state.session_id == session_id
        assert session_state.state == SessionState.PREPARING
        assert session_id in session_state_manager.active_sessions
        assert sample_user.id in session_state.participants
        
        participant = session_state.participants[sample_user.id]
        assert participant.user_id == sample_user.id
        assert participant.display_name == sample_user.display_name
        assert participant.state == ParticipantState.CONNECTING

    @pytest.mark.asyncio
    async def test_start_session(self, sample_user):
        """セッション開始テスト"""
        session_id = "test_session_start"
        
        # セッションを作成
        await session_state_manager.create_session(session_id, sample_user)
        
        # セッションを開始
        session_state = await session_state_manager.start_session(session_id, sample_user.id)
        
        assert session_state.state == SessionState.ACTIVE
        assert session_state.started_at is not None
        assert session_state.participants[sample_user.id].state == ParticipantState.CONNECTED

    @pytest.mark.asyncio
    async def test_pause_session(self, sample_user):
        """セッション一時停止テスト"""
        session_id = "test_session_pause"
        
        # セッションを作成して開始
        await session_state_manager.create_session(session_id, sample_user)
        await session_state_manager.start_session(session_id, sample_user.id)
        
        # 録音を開始
        await session_state_manager.start_recording(session_id, sample_user.id)
        
        # セッションを一時停止
        session_state = await session_state_manager.pause_session(session_id, sample_user.id)
        
        assert session_state.state == SessionState.PAUSED
        assert session_state.recording.state == RecordingState.PAUSED

    @pytest.mark.asyncio
    async def test_resume_session(self, sample_user):
        """セッション再開テスト"""
        session_id = "test_session_resume"
        
        # セッションを作成して開始
        await session_state_manager.create_session(session_id, sample_user)
        await session_state_manager.start_session(session_id, sample_user.id)
        
        # セッションを一時停止
        await session_state_manager.pause_session(session_id, sample_user.id)
        
        # セッションを再開
        session_state = await session_state_manager.resume_session(session_id, sample_user.id)
        
        assert session_state.state == SessionState.ACTIVE

    @pytest.mark.asyncio
    async def test_end_session(self, sample_user):
        """セッション終了テスト"""
        session_id = "test_session_end"
        
        # セッションを作成して開始
        await session_state_manager.create_session(session_id, sample_user)
        await session_state_manager.start_session(session_id, sample_user.id)
        
        # 転写と分析を開始
        await session_state_manager.start_transcription(session_id)
        await session_state_manager.start_analytics(session_id)
        
        # セッションを終了
        session_state = await session_state_manager.end_session(session_id, sample_user.id)
        
        assert session_state.state == SessionState.COMPLETED
        assert session_state.ended_at is not None
        assert session_state.duration > 0
        assert not session_state.transcription.is_active
        assert not session_state.analytics.is_active

    @pytest.mark.asyncio
    async def test_add_participant(self, sample_user, sample_user2):
        """参加者追加テスト"""
        session_id = "test_session_add_participant"
        
        # セッションを作成
        await session_state_manager.create_session(session_id, sample_user)
        
        # 参加者を追加
        participant = await session_state_manager.add_participant(
            session_id, sample_user2, "connection_123"
        )
        
        assert participant.user_id == sample_user2.id
        assert participant.display_name == sample_user2.display_name
        assert participant.state == ParticipantState.CONNECTED
        assert participant.connection_id == "connection_123"
        
        # セッション状態を確認
        session_state = await session_state_manager.get_session_state(session_id)
        assert len(session_state.participants) == 2

    @pytest.mark.asyncio
    async def test_remove_participant(self, sample_user, sample_user2):
        """参加者削除テスト"""
        session_id = "test_session_remove_participant"
        
        # セッションを作成
        await session_state_manager.create_session(session_id, sample_user)
        
        # 参加者を追加
        await session_state_manager.add_participant(session_id, sample_user2, "connection_123")
        
        # 参加者を削除
        success = await session_state_manager.remove_participant(session_id, sample_user2.id)
        
        assert success is True
        
        # セッション状態を確認
        session_state = await session_state_manager.get_session_state(session_id)
        participant = session_state.participants[sample_user2.id]
        assert participant.state == ParticipantState.DISCONNECTED

    @pytest.mark.asyncio
    async def test_update_participant_state(self, sample_user):
        """参加者状態更新テスト"""
        session_id = "test_session_update_participant"
        
        # セッションを作成
        await session_state_manager.create_session(session_id, sample_user)
        
        # 参加者状態を更新
        success = await session_state_manager.update_participant_state(
            session_id, sample_user.id, ParticipantState.SPEAKING, is_speaking=True, audio_level=0.8
        )
        
        assert success is True
        
        # セッション状態を確認
        session_state = await session_state_manager.get_session_state(session_id)
        participant = session_state.participants[sample_user.id]
        assert participant.state == ParticipantState.SPEAKING
        assert participant.is_speaking is True
        assert participant.audio_level == 0.8

    @pytest.mark.asyncio
    async def test_start_recording(self, sample_user):
        """録音開始テスト"""
        session_id = "test_session_recording"
        
        # セッションを作成
        await session_state_manager.create_session(session_id, sample_user)
        
        # 録音を開始
        success = await session_state_manager.start_recording(
            session_id, sample_user.id, quality="high", format="wav"
        )
        
        assert success is True
        
        # セッション状態を確認
        session_state = await session_state_manager.get_session_state(session_id)
        assert session_state.recording.state == RecordingState.RECORDING
        assert session_state.recording.started_at is not None
        assert session_state.recording.quality == "high"
        assert session_state.recording.format == "wav"

    @pytest.mark.asyncio
    async def test_stop_recording(self, sample_user):
        """録音停止テスト"""
        session_id = "test_session_stop_recording"
        
        # セッションを作成
        await session_state_manager.create_session(session_id, sample_user)
        
        # 録音を開始
        await session_state_manager.start_recording(session_id, sample_user.id)
        
        # 録音を停止
        success = await session_state_manager.stop_recording(session_id, sample_user.id)
        
        assert success is True
        
        # セッション状態を確認
        session_state = await session_state_manager.get_session_state(session_id)
        assert session_state.recording.state == RecordingState.STOPPED

    @pytest.mark.asyncio
    async def test_start_transcription(self, sample_user):
        """転写開始テスト"""
        session_id = "test_session_transcription"
        
        # セッションを作成
        await session_state_manager.create_session(session_id, sample_user)
        
        # 転写を開始
        success = await session_state_manager.start_transcription(session_id)
        
        assert success is True
        
        # セッション状態を確認
        session_state = await session_state_manager.get_session_state(session_id)
        assert session_state.transcription.is_active is True
        assert session_state.transcription.started_at is not None

    @pytest.mark.asyncio
    async def test_update_transcription_stats(self, sample_user):
        """転写統計更新テスト"""
        session_id = "test_session_transcription_stats"
        
        # セッションを作成
        await session_state_manager.create_session(session_id, sample_user)
        
        # 転写を開始
        await session_state_manager.start_transcription(session_id)
        
        # 統計を更新
        success = await session_state_manager.update_transcription_stats(
            session_id,
            total_chunks=10,
            total_duration=30.0,
            average_confidence=0.85,
            unique_speakers=3,
            languages_detected=["ja", "en"]
        )
        
        assert success is True
        
        # セッション状態を確認
        session_state = await session_state_manager.get_session_state(session_id)
        assert session_state.transcription.total_chunks == 10
        assert session_state.transcription.total_duration == 30.0
        assert session_state.transcription.average_confidence == 0.85
        assert session_state.transcription.unique_speakers == 3
        assert "ja" in session_state.transcription.languages_detected
        assert "en" in session_state.transcription.languages_detected

    @pytest.mark.asyncio
    async def test_start_analytics(self, sample_user):
        """分析開始テスト"""
        session_id = "test_session_analytics"
        
        # セッションを作成
        await session_state_manager.create_session(session_id, sample_user)
        
        # 分析を開始
        success = await session_state_manager.start_analytics(session_id)
        
        assert success is True
        
        # セッション状態を確認
        session_state = await session_state_manager.get_session_state(session_id)
        assert session_state.analytics.is_active is True
        assert session_state.analytics.started_at is not None

    @pytest.mark.asyncio
    async def test_update_analytics_progress(self, sample_user):
        """分析進捗更新テスト"""
        session_id = "test_session_analytics_progress"
        
        # セッションを作成
        await session_state_manager.create_session(session_id, sample_user)
        
        # 分析を開始
        await session_state_manager.start_analytics(session_id)
        
        # 進捗を更新
        success = await session_state_manager.update_analytics_progress(
            session_id,
            progress_percentage=75.0,
            current_phase="analysis",
            completed_steps=["session_start", "recording", "transcription"],
            remaining_steps=["completion"]
        )
        
        assert success is True
        
        # セッション状態を確認
        session_state = await session_state_manager.get_session_state(session_id)
        assert session_state.analytics.progress_percentage == 75.0
        assert session_state.analytics.current_phase == "analysis"
        assert len(session_state.analytics.completed_steps) == 3
        assert len(session_state.analytics.remaining_steps) == 1

    @pytest.mark.asyncio
    async def test_get_session_participants(self, sample_user, sample_user2):
        """セッション参加者取得テスト"""
        session_id = "test_session_get_participants"
        
        # セッションを作成
        await session_state_manager.create_session(session_id, sample_user)
        
        # 参加者を追加
        await session_state_manager.add_participant(session_id, sample_user2, "connection_456")
        
        # 参加者を取得
        participants = await session_state_manager.get_session_participants(session_id)
        
        assert len(participants) == 2
        participant_ids = [p.user_id for p in participants]
        assert sample_user.id in participant_ids
        assert sample_user2.id in participant_ids

    @pytest.mark.asyncio
    async def test_get_session_history(self, sample_user):
        """セッション履歴取得テスト"""
        session_id = "test_session_history"
        
        # セッションを作成
        await session_state_manager.create_session(session_id, sample_user)
        
        # セッションを開始
        await session_state_manager.start_session(session_id, sample_user.id)
        
        # 履歴を取得
        history = await session_state_manager.get_session_history(session_id)
        
        assert len(history) >= 1
        assert history[0].session_id == session_id

    @pytest.mark.asyncio
    async def test_state_change_callbacks(self, sample_user):
        """状態変更コールバックテスト"""
        session_id = "test_session_callbacks"
        callback_called = False
        callback_state = None
        
        async def test_callback(session_id_param: str, new_state: SessionState):
            nonlocal callback_called, callback_state
            callback_called = True
            callback_state = new_state
        
        # セッションを作成
        await session_state_manager.create_session(session_id, sample_user)
        
        # コールバックを登録
        await session_state_manager.register_state_change_callback(session_id, test_callback)
        
        # セッションを開始（コールバックが呼ばれる）
        await session_state_manager.start_session(session_id, sample_user.id)
        
        assert callback_called is True
        assert callback_state == SessionState.ACTIVE

    @pytest.mark.asyncio
    async def test_cleanup_expired_sessions(self, sample_user):
        """期限切れセッションクリーンアップテスト"""
        session_id = "test_session_cleanup"
        
        # セッションを作成
        await session_state_manager.create_session(session_id, sample_user)
        
        # セッションを開始
        await session_state_manager.start_session(session_id, sample_user.id)
        
        # 参加者を切断状態にする
        await session_state_manager.update_participant_state(
            session_id, sample_user.id, ParticipantState.DISCONNECTED
        )
        
        # クリーンアップを実行
        await session_state_manager.cleanup_expired_sessions()
        
        # セッションが終了されていることを確認
        session_state = await session_state_manager.get_session_state(session_id)
        if session_state:
            assert session_state.state == SessionState.COMPLETED


class TestWebSocketSessionStateHandlers:
    """WebSocketセッション状態ハンドラーのテスト"""

    @pytest.mark.asyncio
    async def test_handle_session_state_request_current(self, sample_user):
        """セッション状態リクエスト処理テスト（現在の状態）"""
        session_id = "test_session_state_request"
        connection_id = "test_connection_123"
        
        # セッションを作成
        await session_state_manager.create_session(session_id, sample_user)
        
        message = {
            "request_type": "current",
        }
        
        # ハンドラーを実行
        await WebSocketMessageHandler.handle_session_state_request(
            session_id, connection_id, sample_user, message
        )

    @pytest.mark.asyncio
    async def test_handle_session_state_request_participants(self, sample_user, sample_user2):
        """セッション状態リクエスト処理テスト（参加者情報）"""
        session_id = "test_session_participants_request"
        connection_id = "test_connection_456"
        
        # セッションを作成
        await session_state_manager.create_session(session_id, sample_user)
        await session_state_manager.add_participant(session_id, sample_user2, "connection_789")
        
        message = {
            "request_type": "participants",
        }
        
        # ハンドラーを実行
        await WebSocketMessageHandler.handle_session_state_request(
            session_id, connection_id, sample_user, message
        )

    @pytest.mark.asyncio
    async def test_handle_session_control_start(self, sample_user):
        """セッション制御処理テスト（開始）"""
        session_id = "test_session_control_start"
        connection_id = "test_connection_101"
        
        # セッションを作成
        await session_state_manager.create_session(session_id, sample_user)
        
        message = {
            "action": "start",
        }
        
        # ハンドラーを実行
        await WebSocketMessageHandler.handle_session_control(
            session_id, connection_id, sample_user, message
        )
        
        # セッション状態を確認
        session_state = await session_state_manager.get_session_state(session_id)
        assert session_state.state == SessionState.ACTIVE

    @pytest.mark.asyncio
    async def test_handle_session_control_pause(self, sample_user):
        """セッション制御処理テスト（一時停止）"""
        session_id = "test_session_control_pause"
        connection_id = "test_connection_202"
        
        # セッションを作成して開始
        await session_state_manager.create_session(session_id, sample_user)
        await session_state_manager.start_session(session_id, sample_user.id)
        
        message = {
            "action": "pause",
        }
        
        # ハンドラーを実行
        await WebSocketMessageHandler.handle_session_control(
            session_id, connection_id, sample_user, message
        )
        
        # セッション状態を確認
        session_state = await session_state_manager.get_session_state(session_id)
        assert session_state.state == SessionState.PAUSED

    @pytest.mark.asyncio
    async def test_handle_participant_state_update(self, sample_user):
        """参加者状態更新処理テスト"""
        session_id = "test_session_participant_update"
        connection_id = "test_connection_303"
        
        # セッションを作成
        await session_state_manager.create_session(session_id, sample_user)
        
        message = {
            "state": "speaking",
            "data": {
                "is_speaking": True,
                "audio_level": 0.9
            }
        }
        
        # ハンドラーを実行
        await WebSocketMessageHandler.handle_participant_state_update(
            session_id, connection_id, sample_user, message
        )
        
        # 参加者状態を確認
        session_state = await session_state_manager.get_session_state(session_id)
        participant = session_state.participants[sample_user.id]
        assert participant.state == ParticipantState.SPEAKING
        assert participant.is_speaking is True
        assert participant.audio_level == 0.9


class TestSessionStateIntegration:
    """セッション状態統合テスト"""

    @pytest.mark.asyncio
    async def test_full_session_lifecycle(self, sample_user, sample_user2):
        """完全なセッションライフサイクルテスト"""
        session_id = "test_session_lifecycle"
        
        # 1. セッション作成
        session_state = await session_state_manager.create_session(session_id, sample_user)
        assert session_state.state == SessionState.PREPARING
        
        # 2. 参加者追加
        participant = await session_state_manager.add_participant(session_id, sample_user2, "connection_456")
        assert participant.state == ParticipantState.CONNECTED
        
        # 3. セッション開始
        session_state = await session_state_manager.start_session(session_id, sample_user.id)
        assert session_state.state == SessionState.ACTIVE
        
        # 4. 録音開始
        success = await session_state_manager.start_recording(session_id, sample_user.id)
        assert success is True
        
        # 5. 転写開始
        success = await session_state_manager.start_transcription(session_id)
        assert success is True
        
        # 6. 分析開始
        success = await session_state_manager.start_analytics(session_id)
        assert success is True
        
        # 7. 参加者状態更新
        success = await session_state_manager.update_participant_state(
            session_id, sample_user.id, ParticipantState.SPEAKING, is_speaking=True
        )
        assert success is True
        
        # 8. セッション一時停止
        session_state = await session_state_manager.pause_session(session_id, sample_user.id)
        assert session_state.state == SessionState.PAUSED
        
        # 9. セッション再開
        session_state = await session_state_manager.resume_session(session_id, sample_user.id)
        assert session_state.state == SessionState.ACTIVE
        
        # 10. セッション終了
        session_state = await session_state_manager.end_session(session_id, sample_user.id)
        assert session_state.state == SessionState.COMPLETED
        assert session_state.duration > 0

    @pytest.mark.asyncio
    async def test_error_handling(self, sample_user):
        """エラーハンドリングテスト"""
        session_id = "test_session_error"
        
        # 存在しないセッションで操作を試行
        try:
            await session_state_manager.start_session(session_id, sample_user.id)
            assert False, "Should have raised an exception"
        except ValueError:
            pass  # 期待されるエラー
        
        # 存在しない参加者で状態更新を試行
        await session_state_manager.create_session(session_id, sample_user)
        success = await session_state_manager.update_participant_state(
            session_id, 999, ParticipantState.CONNECTED
        )
        assert success is False

    @pytest.mark.asyncio
    async def test_concurrent_session_operations(self, sample_user):
        """並行セッション操作テスト"""
        session_id = "test_session_concurrent"
        
        # セッションを作成
        await session_state_manager.create_session(session_id, sample_user)
        
        # 複数の操作を並行実行
        tasks = [
            session_state_manager.start_session(session_id, sample_user.id),
            session_state_manager.start_recording(session_id, sample_user.id),
            session_state_manager.start_transcription(session_id),
            session_state_manager.update_participant_state(
                session_id, sample_user.id, ParticipantState.SPEAKING
            )
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # すべての操作が成功することを確認
        for result in results:
            assert not isinstance(result, Exception)
        
        # 最終状態を確認
        session_state = await session_state_manager.get_session_state(session_id)
        assert session_state.state == SessionState.ACTIVE
        assert session_state.recording.state == RecordingState.RECORDING
        assert session_state.transcription.is_active is True
