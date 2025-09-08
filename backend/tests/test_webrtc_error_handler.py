"""
WebRTCエラーハンドリング機能のテスト
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Dict, List

from app.services.webrtc_error_handler import (
    WebRTCErrorHandler,
    ErrorType,
    ErrorLevel,
    ErrorRecord,
    RecoveryStrategy,
    ErrorPattern,
    ErrorStatistics,
)


@pytest.fixture
def error_handler():
    """WebRTCエラーハンドラーフィクスチャ"""
    return WebRTCErrorHandler()


@pytest.fixture
def mock_error():
    """モックエラーフィクスチャ"""
    return Exception("Test WebRTC error")


@pytest.fixture
def mock_peer_connection():
    """モックピア接続フィクスチャ"""
    connection = MagicMock()
    connection.connectionState = 'connected'
    connection.close = MagicMock()
    connection.restart = MagicMock()
    return connection


class TestWebRTCErrorHandler:
    """WebRTCエラーハンドラーテスト"""

    @pytest.mark.asyncio
    async def test_initialization(self, error_handler):
        """初期化テスト"""
        assert error_handler.error_records == []
        assert error_handler.recovery_attempts == {}
        assert error_handler.error_patterns == {}
        assert error_handler.is_recovering == {}
        assert error_handler.max_recovery_attempts == 3
        assert error_handler.recovery_timeout == 30.0

    @pytest.mark.asyncio
    async def test_record_error(self, error_handler, mock_error):
        """エラー記録テスト"""
        peer_id = 'peer-1'
        error_type = ErrorType.CONNECTION_FAILURE
        error_level = ErrorLevel.CRITICAL
        
        await error_handler.record_error(
            peer_id=peer_id,
            error=mock_error,
            error_type=error_type,
            error_level=error_level
        )
        
        assert len(error_handler.error_records) == 1
        record = error_handler.error_records[0]
        assert record.peer_id == peer_id
        assert record.error == mock_error
        assert record.error_type == error_type
        assert record.error_level == error_level
        assert record.timestamp is not None

    @pytest.mark.asyncio
    async def test_get_errors_by_peer(self, error_handler, mock_error):
        """ピア別エラー取得テスト"""
        peer_id = 'peer-1'
        
        # 複数のエラーを記録
        for i in range(3):
            await error_handler.record_error(
                peer_id=peer_id,
                error=Exception(f"Error {i}"),
                error_type=ErrorType.CONNECTION_FAILURE,
                error_level=ErrorLevel.CRITICAL
            )
        
        # 別のピアのエラーも記録
        await error_handler.record_error(
            peer_id='peer-2',
            error=Exception("Other peer error"),
            error_type=ErrorType.AUDIO_FAILURE,
            error_level=ErrorLevel.WARNING
        )
        
        peer_errors = await error_handler.get_errors_by_peer(peer_id)
        
        assert len(peer_errors) == 3
        assert all(error.peer_id == peer_id for error in peer_errors)

    @pytest.mark.asyncio
    async def test_get_errors_by_type(self, error_handler, mock_error):
        """エラータイプ別取得テスト"""
        # 異なるタイプのエラーを記録
        await error_handler.record_error(
            peer_id='peer-1',
            error=Exception("Connection error"),
            error_type=ErrorType.CONNECTION_FAILURE,
            error_level=ErrorLevel.CRITICAL
        )
        
        await error_handler.record_error(
            peer_id='peer-2',
            error=Exception("Audio error"),
            error_type=ErrorType.AUDIO_FAILURE,
            error_level=ErrorLevel.WARNING
        )
        
        connection_errors = await error_handler.get_errors_by_type(ErrorType.CONNECTION_FAILURE)
        audio_errors = await error_handler.get_errors_by_type(ErrorType.AUDIO_FAILURE)
        
        assert len(connection_errors) == 1
        assert len(audio_errors) == 1
        assert connection_errors[0].error_type == ErrorType.CONNECTION_FAILURE
        assert audio_errors[0].error_type == ErrorType.AUDIO_FAILURE

    @pytest.mark.asyncio
    async def test_get_errors_by_level(self, error_handler, mock_error):
        """エラーレベル別取得テスト"""
        # 異なるレベルのエラーを記録
        await error_handler.record_error(
            peer_id='peer-1',
            error=Exception("Critical error"),
            error_type=ErrorType.CONNECTION_FAILURE,
            error_level=ErrorLevel.CRITICAL
        )
        
        await error_handler.record_error(
            peer_id='peer-2',
            error=Exception("Warning error"),
            error_type=ErrorType.AUDIO_FAILURE,
            error_level=ErrorLevel.WARNING
        )
        
        critical_errors = await error_handler.get_errors_by_level(ErrorLevel.CRITICAL)
        warning_errors = await error_handler.get_errors_by_level(ErrorLevel.WARNING)
        
        assert len(critical_errors) == 1
        assert len(warning_errors) == 1
        assert critical_errors[0].error_level == ErrorLevel.CRITICAL
        assert warning_errors[0].error_level == ErrorLevel.WARNING

    @pytest.mark.asyncio
    async def test_start_recovery(self, error_handler, mock_peer_connection):
        """回復処理開始テスト"""
        peer_id = 'peer-1'
        strategy = RecoveryStrategy.RECONNECT
        
        await error_handler.start_recovery(peer_id, strategy, mock_peer_connection)
        
        assert peer_id in error_handler.is_recovering
        assert error_handler.is_recovering[peer_id] is True
        assert peer_id in error_handler.recovery_attempts
        assert error_handler.recovery_attempts[peer_id] == 1

    @pytest.mark.asyncio
    async def test_complete_recovery(self, error_handler, mock_peer_connection):
        """回復処理完了テスト"""
        peer_id = 'peer-1'
        strategy = RecoveryStrategy.RECONNECT
        
        # 回復処理を開始
        await error_handler.start_recovery(peer_id, strategy, mock_peer_connection)
        assert error_handler.is_recovering[peer_id] is True
        
        # 回復処理を完了
        await error_handler.complete_recovery(peer_id)
        
        assert error_handler.is_recovering[peer_id] is False
        assert peer_id not in error_handler.recovery_attempts

    @pytest.mark.asyncio
    async def test_fail_recovery(self, error_handler, mock_peer_connection):
        """回復処理失敗テスト"""
        peer_id = 'peer-1'
        strategy = RecoveryStrategy.RECONNECT
        
        # 回復処理を開始
        await error_handler.start_recovery(peer_id, strategy, mock_peer_connection)
        assert error_handler.is_recovering[peer_id] is True
        
        # 回復処理を失敗
        recovery_error = Exception("Recovery failed")
        await error_handler.fail_recovery(peer_id, recovery_error)
        
        assert error_handler.is_recovering[peer_id] is False
        assert error_handler.recovery_attempts[peer_id] == 1

    @pytest.mark.asyncio
    async def test_max_recovery_attempts(self, error_handler, mock_peer_connection):
        """最大回復試行回数テスト"""
        peer_id = 'peer-1'
        strategy = RecoveryStrategy.RECONNECT
        
        # 最大試行回数まで回復を試行
        for i in range(error_handler.max_recovery_attempts):
            await error_handler.start_recovery(peer_id, strategy, mock_peer_connection)
            await error_handler.fail_recovery(peer_id, Exception(f"Recovery attempt {i+1} failed"))
        
        assert error_handler.recovery_attempts[peer_id] == error_handler.max_recovery_attempts
        
        # 追加の回復試行は無視される
        await error_handler.start_recovery(peer_id, strategy, mock_peer_connection)
        assert error_handler.recovery_attempts[peer_id] == error_handler.max_recovery_attempts

    @pytest.mark.asyncio
    async def test_detect_error_patterns(self, error_handler, mock_error):
        """エラーパターン検出テスト"""
        peer_id = 'peer-1'
        
        # 同じタイプのエラーを複数回記録
        for i in range(5):
            await error_handler.record_error(
                peer_id=peer_id,
                error=Exception(f"Connection error {i}"),
                error_type=ErrorType.CONNECTION_FAILURE,
                error_level=ErrorLevel.CRITICAL
            )
        
        patterns = await error_handler.detect_error_patterns(peer_id)
        
        assert len(patterns) > 0
        assert any(pattern.error_type == ErrorType.CONNECTION_FAILURE for pattern in patterns)

    @pytest.mark.asyncio
    async def test_get_error_statistics(self, error_handler, mock_error):
        """エラー統計取得テスト"""
        # 複数のエラーを記録
        for i in range(10):
            await error_handler.record_error(
                peer_id=f'peer-{i % 3}',  # 3つのピアに分散
                error=Exception(f"Error {i}"),
                error_type=ErrorType.CONNECTION_FAILURE if i % 2 == 0 else ErrorType.AUDIO_FAILURE,
                error_level=ErrorLevel.CRITICAL if i % 3 == 0 else ErrorLevel.WARNING
            )
        
        stats = await error_handler.get_error_statistics()
        
        assert stats.total_errors == 10
        assert stats.errors_by_peer['peer-0'] == 4  # 0, 3, 6, 9
        assert stats.errors_by_peer['peer-1'] == 3  # 1, 4, 7
        assert stats.errors_by_peer['peer-2'] == 3  # 2, 5, 8
        assert stats.errors_by_type[ErrorType.CONNECTION_FAILURE] == 5
        assert stats.errors_by_type[ErrorType.AUDIO_FAILURE] == 5
        assert stats.errors_by_level[ErrorLevel.CRITICAL] == 4
        assert stats.errors_by_level[ErrorLevel.WARNING] == 6

    @pytest.mark.asyncio
    async def test_clear_old_errors(self, error_handler, mock_error):
        """古いエラークリーンアップテスト"""
        # 古いエラーを記録
        old_time = datetime.now() - timedelta(hours=2)
        with patch('app.services.webrtc_error_handler.datetime') as mock_datetime:
            mock_datetime.now.return_value = old_time
            await error_handler.record_error(
                peer_id='peer-1',
                error=Exception("Old error"),
                error_type=ErrorType.CONNECTION_FAILURE,
                error_level=ErrorLevel.CRITICAL
            )
        
        # 新しいエラーを記録
        await error_handler.record_error(
            peer_id='peer-1',
            error=Exception("New error"),
            error_type=ErrorType.AUDIO_FAILURE,
            error_level=ErrorLevel.WARNING
        )
        
        assert len(error_handler.error_records) == 2
        
        # 古いエラーをクリーンアップ
        await error_handler.clear_old_errors(hours=1)
        
        assert len(error_handler.error_records) == 1
        assert error_handler.error_records[0].error_type == ErrorType.AUDIO_FAILURE

    @pytest.mark.asyncio
    async def test_recovery_strategy_selection(self, error_handler, mock_peer_connection):
        """回復戦略選択テスト"""
        peer_id = 'peer-1'
        
        # 接続エラーの場合
        await error_handler.record_error(
            peer_id=peer_id,
            error=Exception("Connection failed"),
            error_type=ErrorType.CONNECTION_FAILURE,
            error_level=ErrorLevel.CRITICAL
        )
        
        strategy = await error_handler.select_recovery_strategy(peer_id)
        assert strategy == RecoveryStrategy.RECONNECT
        
        # 音声エラーの場合
        await error_handler.record_error(
            peer_id=peer_id,
            error=Exception("Audio failed"),
            error_type=ErrorType.AUDIO_FAILURE,
            error_level=ErrorLevel.WARNING
        )
        
        strategy = await error_handler.select_recovery_strategy(peer_id)
        assert strategy == RecoveryStrategy.RESTART_AUDIO

    @pytest.mark.asyncio
    async def test_error_aggregation(self, error_handler, mock_error):
        """エラー集約テスト"""
        peer_id = 'peer-1'
        
        # 同じエラーを複数回記録
        for i in range(3):
            await error_handler.record_error(
                peer_id=peer_id,
                error=Exception("Same error"),
                error_type=ErrorType.CONNECTION_FAILURE,
                error_level=ErrorLevel.CRITICAL
            )
        
        aggregated_errors = await error_handler.get_aggregated_errors(peer_id)
        
        assert len(aggregated_errors) == 1
        assert aggregated_errors[0].count == 3
        assert aggregated_errors[0].error_type == ErrorType.CONNECTION_FAILURE

    @pytest.mark.asyncio
    async def test_error_handling_integration(self, error_handler, mock_peer_connection):
        """エラーハンドリング統合テスト"""
        peer_id = 'peer-1'
        
        # エラーを記録
        await error_handler.record_error(
            peer_id=peer_id,
            error=Exception("Test error"),
            error_type=ErrorType.CONNECTION_FAILURE,
            error_level=ErrorLevel.CRITICAL
        )
        
        # 回復戦略を選択
        strategy = await error_handler.select_recovery_strategy(peer_id)
        assert strategy == RecoveryStrategy.RECONNECT
        
        # 回復処理を開始
        await error_handler.start_recovery(peer_id, strategy, mock_peer_connection)
        assert error_handler.is_recovering[peer_id] is True
        
        # 回復処理を完了
        await error_handler.complete_recovery(peer_id)
        assert error_handler.is_recovering[peer_id] is False
        
        # エラー統計を取得
        stats = await error_handler.get_error_statistics()
        assert stats.total_errors == 1
        assert stats.errors_by_peer[peer_id] == 1

    @pytest.mark.asyncio
    async def test_error_handler_cleanup(self, error_handler, mock_error):
        """エラーハンドラークリーンアップテスト"""
        # エラーを記録
        await error_handler.record_error(
            peer_id='peer-1',
            error=Exception("Test error"),
            error_type=ErrorType.CONNECTION_FAILURE,
            error_level=ErrorLevel.CRITICAL
        )
        
        # 回復処理を開始
        await error_handler.start_recovery('peer-1', RecoveryStrategy.RECONNECT, mock_peer_connection)
        
        assert len(error_handler.error_records) == 1
        assert error_handler.is_recovering['peer-1'] is True
        
        # クリーンアップ
        await error_handler.cleanup()
        
        assert len(error_handler.error_records) == 0
        assert error_handler.is_recovering == {}
        assert error_handler.recovery_attempts == {}

    @pytest.mark.asyncio
    async def test_error_handler_performance(self, error_handler, mock_error):
        """エラーハンドラーパフォーマンステスト"""
        # 大量のエラーを記録
        start_time = datetime.now()
        
        for i in range(1000):
            await error_handler.record_error(
                peer_id=f'peer-{i % 10}',
                error=Exception(f"Error {i}"),
                error_type=ErrorType.CONNECTION_FAILURE if i % 2 == 0 else ErrorType.AUDIO_FAILURE,
                error_level=ErrorLevel.CRITICAL if i % 3 == 0 else ErrorLevel.WARNING
            )
        
        end_time = datetime.now()
        
        # 実行時間が妥当であることを確認（1秒以内）
        assert (end_time - start_time).total_seconds() < 1.0
        
        # 統計取得のパフォーマンス
        start_time = datetime.now()
        stats = await error_handler.get_error_statistics()
        end_time = datetime.now()
        
        assert (end_time - start_time).total_seconds() < 0.1
        assert stats.total_errors == 1000
