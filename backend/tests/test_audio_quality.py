"""
音声品質管理機能のテスト
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
import numpy as np

from app.services.audio_processing_service import (
    AudioProcessingService,
    AudioQualityManager,
    AudioBufferManager,
    AudioQuality,
    NetworkCondition,
    AudioQualityMetrics,
    NetworkMetrics,
    AudioChunk,
    AudioLevel,
)
from app.schemas.websocket import AudioDataMessage


@pytest.fixture
def audio_processor():
    """音声処理サービスフィクスチャ"""
    return AudioProcessingService()


@pytest.fixture
def quality_manager():
    """音声品質管理フィクスチャ"""
    return AudioQualityManager()


@pytest.fixture
def buffer_manager():
    """音声バッファ管理フィクスチャ"""
    return AudioBufferManager()


@pytest.fixture
def mock_audio_data():
    """モック音声データ"""
    # 1秒間の16kHzモノラル音声データ（16-bit）
    sample_rate = 16000
    duration = 1.0
    samples = int(sample_rate * duration)
    
    # 正弦波を生成（440Hz）
    t = np.linspace(0, duration, samples, False)
    audio_data = np.sin(2 * np.pi * 440 * t) * 0.5
    
    # 16-bit整数に変換
    audio_data = (audio_data * 32767).astype(np.int16)
    
    return audio_data.tobytes()


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


class TestAudioQualityManager:
    """音声品質管理テスト"""

    @pytest.mark.asyncio
    async def test_get_optimal_quality(self, quality_manager):
        """最適な音声品質の決定テスト"""
        # ネットワーク状況に応じた品質決定
        assert quality_manager.get_optimal_quality(NetworkCondition.EXCELLENT) == AudioQuality.ULTRA
        assert quality_manager.get_optimal_quality(NetworkCondition.GOOD) == AudioQuality.HIGH
        assert quality_manager.get_optimal_quality(NetworkCondition.FAIR) == AudioQuality.MEDIUM
        assert quality_manager.get_optimal_quality(NetworkCondition.POOR) == AudioQuality.LOW

    @pytest.mark.asyncio
    async def test_adjust_quality_for_network(self, quality_manager):
        """ネットワーク状況に応じた品質調整テスト"""
        session_id = "test_session_123"
        
        # ネットワークメトリクスを設定
        network_metrics = NetworkMetrics(
            bandwidth=1000.0,
            latency=50.0,
            packet_loss=0.01,
            jitter=5.0,
            quality_score=0.9,
            timestamp=datetime.now(),
        )
        
        quality_manager.update_network_metrics(session_id, network_metrics)
        
        # 品質調整
        adjusted_quality = quality_manager.adjust_quality_for_network(session_id)
        assert adjusted_quality == AudioQuality.HIGH

    @pytest.mark.asyncio
    async def test_get_quality_settings(self, quality_manager):
        """音声品質設定取得テスト"""
        settings = quality_manager.get_quality_settings(AudioQuality.HIGH)
        
        assert settings["sample_rate"] == 44100
        assert settings["channels"] == 2
        assert settings["bit_depth"] == 24
        assert settings["compression"] == "high"

    @pytest.mark.asyncio
    async def test_quality_adjustment_logging(self, quality_manager):
        """品質調整のログ出力テスト"""
        session_id = "test_session_123"
        
        # 高品質スコアで品質を上げる
        network_metrics = NetworkMetrics(
            bandwidth=2000.0,
            latency=20.0,
            packet_loss=0.001,
            jitter=2.0,
            quality_score=0.95,
            timestamp=datetime.now(),
        )
        
        quality_manager.update_network_metrics(session_id, network_metrics)
        quality_manager.adjust_quality_for_network(session_id)
        
        # 品質が変更されたことを確認
        assert quality_manager.current_quality == AudioQuality.HIGH


class TestAudioBufferManager:
    """音声バッファ管理テスト"""

    @pytest.mark.asyncio
    async def test_add_chunk(self, buffer_manager):
        """音声チャンク追加テスト"""
        session_id = "test_session_123"
        chunk = AudioChunk(
            data=b"test_audio_data",
            sample_rate=16000,
            channels=1,
            timestamp=datetime.now(),
            chunk_id="chunk_123",
            user_id=1,
            session_id=session_id,
        )
        
        await buffer_manager.add_chunk(session_id, chunk)
        
        # バッファに追加されたことを確認
        assert session_id in buffer_manager.buffers
        assert len(buffer_manager.buffers[session_id]) == 1
        assert buffer_manager.buffer_sizes[session_id] == len(chunk.data)

    @pytest.mark.asyncio
    async def test_get_chunks(self, buffer_manager):
        """音声チャンク取得テスト"""
        session_id = "test_session_123"
        
        # 複数のチャンクを追加
        for i in range(5):
            chunk = AudioChunk(
                data=f"test_audio_data_{i}".encode(),
                sample_rate=16000,
                channels=1,
                timestamp=datetime.now(),
                chunk_id=f"chunk_{i}",
                user_id=1,
                session_id=session_id,
            )
            await buffer_manager.add_chunk(session_id, chunk)
        
        # 最新3チャンクを取得
        chunks = await buffer_manager.get_chunks(session_id, limit=3)
        assert len(chunks) == 3
        assert chunks[-1].chunk_id == "chunk_4"

    @pytest.mark.asyncio
    async def test_buffer_size_management(self, buffer_manager):
        """バッファサイズ管理テスト"""
        session_id = "test_session_123"
        
        # 最大サイズを超えるチャンクを追加
        for i in range(buffer_manager.max_buffer_size + 10):
            chunk = AudioChunk(
                data=f"test_audio_data_{i}".encode(),
                sample_rate=16000,
                channels=1,
                timestamp=datetime.now(),
                chunk_id=f"chunk_{i}",
                user_id=1,
                session_id=session_id,
            )
            await buffer_manager.add_chunk(session_id, chunk)
        
        # バッファサイズが制限されていることを確認
        assert len(buffer_manager.buffers[session_id]) <= buffer_manager.max_buffer_size

    @pytest.mark.asyncio
    async def test_get_buffer_stats(self, buffer_manager):
        """バッファ統計取得テスト"""
        session_id = "test_session_123"
        
        # チャンクを追加
        chunk = AudioChunk(
            data=b"test_audio_data",
            sample_rate=16000,
            channels=1,
            timestamp=datetime.now(),
            chunk_id="chunk_123",
            user_id=1,
            session_id=session_id,
        )
        
        await buffer_manager.add_chunk(session_id, chunk)
        
        # 統計を取得
        stats = await buffer_manager.get_buffer_stats(session_id)
        
        assert stats["chunk_count"] == 1
        assert stats["total_size"] == len(chunk.data)
        assert "average_latency" in stats

    @pytest.mark.asyncio
    async def test_clear_buffer(self, buffer_manager):
        """バッファクリアテスト"""
        session_id = "test_session_123"
        
        # チャンクを追加
        chunk = AudioChunk(
            data=b"test_audio_data",
            sample_rate=16000,
            channels=1,
            timestamp=datetime.now(),
            chunk_id="chunk_123",
            user_id=1,
            session_id=session_id,
        )
        
        await buffer_manager.add_chunk(session_id, chunk)
        assert len(buffer_manager.buffers[session_id]) == 1
        
        # バッファをクリア
        await buffer_manager.clear_buffer(session_id)
        assert len(buffer_manager.buffers[session_id]) == 0
        assert buffer_manager.buffer_sizes[session_id] == 0


class TestAudioProcessingService:
    """音声処理サービステスト"""

    @pytest.mark.asyncio
    async def test_process_audio_data(self, audio_processor, mock_audio_message):
        """音声データ処理テスト"""
        chunk = await audio_processor.process_audio_data(mock_audio_message)
        
        assert chunk.session_id == mock_audio_message.session_id
        assert chunk.user_id == mock_audio_message.user_id
        assert chunk.chunk_id == mock_audio_message.chunk_id
        assert chunk.sample_rate == mock_audio_message.sample_rate
        assert chunk.channels == mock_audio_message.channels

    @pytest.mark.asyncio
    async def test_calculate_audio_level(self, audio_processor, mock_audio_data):
        """音声レベル計算テスト"""
        chunk = AudioChunk(
            data=mock_audio_data,
            sample_rate=16000,
            channels=1,
            timestamp=datetime.now(),
            chunk_id="chunk_123",
            user_id=1,
            session_id="test_session_123",
        )
        
        audio_level = audio_processor._calculate_audio_level(chunk)
        
        assert isinstance(audio_level, AudioLevel)
        assert 0.0 <= audio_level.level <= 1.0
        assert audio_level.is_speaking in [True, False]  # bool型のチェック
        assert audio_level.rms >= 0.0
        assert audio_level.peak >= 0.0
        assert audio_level.user_id == chunk.user_id

    @pytest.mark.asyncio
    async def test_quality_metrics_calculation(self, audio_processor, mock_audio_data):
        """音声品質メトリクス計算テスト"""
        chunk = AudioChunk(
            data=mock_audio_data,
            sample_rate=16000,
            channels=1,
            timestamp=datetime.now(),
            chunk_id="chunk_123",
            user_id=1,
            session_id="test_session_123",
        )
        
        audio_level = audio_processor._calculate_audio_level(chunk)
        quality_metrics = await audio_processor._calculate_quality_metrics(chunk, audio_level)
        
        assert isinstance(quality_metrics, AudioQualityMetrics)
        assert isinstance(quality_metrics.snr, float)
        assert isinstance(quality_metrics.clarity, float)
        assert isinstance(quality_metrics.latency, float)
        assert isinstance(quality_metrics.packet_loss, float)
        assert isinstance(quality_metrics.jitter, float)

    @pytest.mark.asyncio
    async def test_audio_level_history(self, audio_processor, mock_audio_message):
        """音声レベル履歴テスト"""
        # 音声データを処理
        chunk = await audio_processor.process_audio_data(mock_audio_message)
        
        # 音声レベル履歴を取得
        audio_levels = await audio_processor.get_session_audio_levels(
            mock_audio_message.session_id, mock_audio_message.user_id
        )
        
        # 履歴が更新されていることを確認
        assert len(audio_processor.audio_level_history[mock_audio_message.session_id]) > 0

    @pytest.mark.asyncio
    async def test_network_metrics_update(self, audio_processor):
        """ネットワークメトリクス更新テスト"""
        session_id = "test_session_123"
        
        network_metrics = NetworkMetrics(
            bandwidth=1000.0,
            latency=50.0,
            packet_loss=0.01,
            jitter=5.0,
            quality_score=0.8,
            timestamp=datetime.now(),
        )
        
        await audio_processor.update_network_metrics(session_id, network_metrics)
        
        # ネットワークメトリクスが更新されていることを確認
        assert session_id in audio_processor.quality_manager.network_metrics

    @pytest.mark.asyncio
    async def test_audio_quality_metrics_retrieval(self, audio_processor, mock_audio_message):
        """音声品質メトリクス取得テスト"""
        # 音声データを処理
        await audio_processor.process_audio_data(mock_audio_message)
        
        # 品質メトリクスを取得
        quality_metrics = await audio_processor.get_audio_quality_metrics(
            mock_audio_message.session_id
        )
        
        # メトリクスが取得できることを確認
        assert isinstance(quality_metrics, list)

    @pytest.mark.asyncio
    async def test_buffer_stats_retrieval(self, audio_processor, mock_audio_message):
        """バッファ統計取得テスト"""
        # 音声データを処理
        await audio_processor.process_audio_data(mock_audio_message)
        
        # バッファ統計を取得
        buffer_stats = await audio_processor.get_buffer_stats(mock_audio_message.session_id)
        
        # 統計が取得できることを確認
        assert isinstance(buffer_stats, dict)
        assert "chunk_count" in buffer_stats
        assert "total_size" in buffer_stats
        assert "average_latency" in buffer_stats

    @pytest.mark.asyncio
    async def test_audio_format_conversion(self, audio_processor, mock_audio_data):
        """音声フォーマット変換テスト"""
        # RAW → WAV変換
        wav_data = audio_processor.convert_audio_format(
            mock_audio_data, "raw", "wav", sample_rate=16000
        )
        
        assert isinstance(wav_data, bytes)
        assert len(wav_data) > len(mock_audio_data)  # WAVヘッダーが追加される

    @pytest.mark.asyncio
    async def test_session_buffer_clear(self, audio_processor, mock_audio_message):
        """セッションバッファクリアテスト"""
        # 音声データを処理
        await audio_processor.process_audio_data(mock_audio_message)
        
        # バッファをクリア
        await audio_processor.clear_session_buffer(mock_audio_message.session_id)
        
        # バッファがクリアされていることを確認
        buffer_stats = await audio_processor.get_buffer_stats(mock_audio_message.session_id)
        assert buffer_stats["chunk_count"] == 0
        assert buffer_stats["total_size"] == 0


class TestAudioQualityIntegration:
    """音声品質統合テスト"""

    @pytest.mark.asyncio
    async def test_quality_adjustment_flow(self, audio_processor):
        """品質調整フローテスト"""
        session_id = "test_session_123"
        
        # ネットワークメトリクスを更新
        network_metrics = NetworkMetrics(
            bandwidth=500.0,
            latency=100.0,
            packet_loss=0.05,
            jitter=10.0,
            quality_score=0.3,
            timestamp=datetime.now(),
        )
        
        await audio_processor.update_network_metrics(session_id, network_metrics)
        
        # 品質が低品質に調整されることを確認
        optimal_quality = audio_processor.quality_manager.adjust_quality_for_network(session_id)
        assert optimal_quality == AudioQuality.LOW

    @pytest.mark.asyncio
    async def test_audio_processing_with_quality(self, audio_processor, mock_audio_message):
        """品質を考慮した音声処理テスト"""
        # ネットワークメトリクスを設定
        network_metrics = NetworkMetrics(
            bandwidth=2000.0,
            latency=20.0,
            packet_loss=0.001,
            jitter=2.0,
            quality_score=0.95,
            timestamp=datetime.now(),
        )
        
        await audio_processor.update_network_metrics(
            mock_audio_message.session_id, network_metrics
        )
        
        # 音声データを処理
        chunk = await audio_processor.process_audio_data(mock_audio_message)
        
        # 品質に応じた処理が行われていることを確認
        assert chunk is not None
        assert chunk.session_id == mock_audio_message.session_id

    @pytest.mark.asyncio
    async def test_quality_metrics_history(self, audio_processor, mock_audio_message):
        """品質メトリクス履歴テスト"""
        # 複数回音声データを処理
        for i in range(5):
            message = AudioDataMessage(
                session_id=mock_audio_message.session_id,
                user_id=mock_audio_message.user_id,
                data=mock_audio_message.data,
                timestamp=datetime.now().isoformat(),
                chunk_id=f"chunk_{i}",
                sample_rate=mock_audio_message.sample_rate,
                channels=mock_audio_message.channels,
            )
            
            await audio_processor.process_audio_data(message)
        
        # 品質メトリクス履歴を取得
        quality_metrics = await audio_processor.get_audio_quality_metrics(
            mock_audio_message.session_id
        )
        
        # 履歴が蓄積されていることを確認
        assert len(quality_metrics) > 0
        assert len(quality_metrics) <= 100  # 履歴サイズ制限
