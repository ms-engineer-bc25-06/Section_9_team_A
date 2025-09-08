"""
WebRTC品質監視機能のテスト
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Dict, List

from app.services.webrtc_quality_monitor import (
    WebRTCQualityMonitor,
    QualityMetrics,
    NetworkCondition,
    AudioQuality,
    QualityAlert,
    QualitySuggestion,
)


@pytest.fixture
def quality_monitor():
    """WebRTC品質監視フィクスチャ"""
    return WebRTCQualityMonitor()


@pytest.fixture
def mock_peer_connections():
    """モックピア接続フィクスチャ"""
    connections = {}
    
    for i in range(3):
        connection = MagicMock()
        connection.getStats = AsyncMock()
        connection.connectionState = 'connected'
        connections[f'peer-{i}'] = connection
    
    return connections


@pytest.fixture
def mock_stats_report():
    """モック統計レポートフィクスチャ"""
    stats = [
        {
            'type': 'inbound-rtp',
            'mediaType': 'audio',
            'bytesReceived': 1000,
            'packetsReceived': 10,
            'packetsLost': 1,
            'jitter': 0.5,
            'roundTripTime': 0.1,
        },
        {
            'type': 'outbound-rtp',
            'mediaType': 'audio',
            'bytesSent': 2000,
            'packetsSent': 20,
            'packetsLost': 2,
        },
        {
            'type': 'candidate-pair',
            'state': 'succeeded',
            'currentRoundTripTime': 0.15,
            'availableOutgoingBitrate': 1000000,
        },
    ]
    
    report = MagicMock()
    report.__iter__ = lambda self: iter(stats)
    report.__getitem__ = lambda self, key: stats[key] if isinstance(key, int) else None
    
    return report


class TestWebRTCQualityMonitor:
    """WebRTC品質監視テスト"""

    @pytest.mark.asyncio
    async def test_initialization(self, quality_monitor):
        """初期化テスト"""
        assert quality_monitor.is_monitoring is False
        assert quality_monitor.quality_metrics == {}
        assert quality_monitor.alerts == []
        assert quality_monitor.suggestions == []
        assert quality_monitor.monitoring_interval == 5.0

    @pytest.mark.asyncio
    async def test_start_monitoring(self, quality_monitor, mock_peer_connections):
        """監視開始テスト"""
        await quality_monitor.start_monitoring(mock_peer_connections)
        
        assert quality_monitor.is_monitoring is True
        assert quality_monitor.peer_connections == mock_peer_connections

    @pytest.mark.asyncio
    async def test_stop_monitoring(self, quality_monitor, mock_peer_connections):
        """監視停止テスト"""
        await quality_monitor.start_monitoring(mock_peer_connections)
        assert quality_monitor.is_monitoring is True
        
        await quality_monitor.stop_monitoring()
        assert quality_monitor.is_monitoring is False

    @pytest.mark.asyncio
    async def test_collect_stats(self, quality_monitor, mock_peer_connections, mock_stats_report):
        """統計収集テスト"""
        # モックの統計レポートを設定
        for connection in mock_peer_connections.values():
            connection.getStats.return_value = mock_stats_report
        
        await quality_monitor.start_monitoring(mock_peer_connections)
        
        # 統計を収集
        stats = await quality_monitor.collect_stats()
        
        assert len(stats) == len(mock_peer_connections)
        assert all('peer_id' in stat for stat in stats)
        assert all('audio_level' in stat for stat in stats)
        assert all('latency' in stat for stat in stats)
        assert all('packet_loss' in stat for stat in stats)
        assert all('jitter' in stat for stat in stats)
        assert all('bandwidth' in stat for stat in stats)

    @pytest.mark.asyncio
    async def test_calculate_quality_score(self, quality_monitor):
        """品質スコア計算テスト"""
        metrics = QualityMetrics(
            audio_level=0.8,
            latency=50.0,
            packet_loss=0.01,
            jitter=5.0,
            bandwidth=1000000.0,
            timestamp=datetime.now()
        )
        
        score = quality_monitor.calculate_quality_score(metrics)
        
        assert 0.0 <= score <= 1.0
        assert isinstance(score, float)

    @pytest.mark.asyncio
    async def test_assess_network_condition(self, quality_monitor):
        """ネットワーク状況評価テスト"""
        # 良好なネットワーク状況
        good_metrics = QualityMetrics(
            audio_level=0.8,
            latency=50.0,
            packet_loss=0.001,
            jitter=2.0,
            bandwidth=2000000.0,
            timestamp=datetime.now()
        )
        
        condition = quality_monitor.assess_network_condition(good_metrics)
        assert condition == NetworkCondition.EXCELLENT
        
        # 悪いネットワーク状況
        poor_metrics = QualityMetrics(
            audio_level=0.2,
            latency=500.0,
            packet_loss=0.1,
            jitter=50.0,
            bandwidth=100000.0,
            timestamp=datetime.now()
        )
        
        condition = quality_monitor.assess_network_condition(poor_metrics)
        assert condition == NetworkCondition.POOR

    @pytest.mark.asyncio
    async def test_generate_quality_alerts(self, quality_monitor):
        """品質アラート生成テスト"""
        # 低品質のメトリクス
        poor_metrics = QualityMetrics(
            audio_level=0.1,
            latency=1000.0,
            packet_loss=0.2,
            jitter=100.0,
            bandwidth=50000.0,
            timestamp=datetime.now()
        )
        
        alerts = quality_monitor.generate_quality_alerts('peer-1', poor_metrics)
        
        assert len(alerts) > 0
        assert all(isinstance(alert, QualityAlert) for alert in alerts)
        assert any(alert.type == 'warning' for alert in alerts)

    @pytest.mark.asyncio
    async def test_generate_quality_suggestions(self, quality_monitor):
        """品質改善提案生成テスト"""
        # 低品質のメトリクス
        poor_metrics = QualityMetrics(
            audio_level=0.1,
            latency=1000.0,
            packet_loss=0.2,
            jitter=100.0,
            bandwidth=50000.0,
            timestamp=datetime.now()
        )
        
        suggestions = quality_monitor.generate_quality_suggestions('peer-1', poor_metrics)
        
        assert len(suggestions) > 0
        assert all(isinstance(suggestion, QualitySuggestion) for suggestion in suggestions)
        assert any(suggestion.type == 'suggestion' for suggestion in suggestions)

    @pytest.mark.asyncio
    async def test_update_quality_metrics(self, quality_monitor):
        """品質メトリクス更新テスト"""
        peer_id = 'peer-1'
        metrics = QualityMetrics(
            audio_level=0.8,
            latency=50.0,
            packet_loss=0.01,
            jitter=5.0,
            bandwidth=1000000.0,
            timestamp=datetime.now()
        )
        
        await quality_monitor.update_quality_metrics(peer_id, metrics)
        
        assert peer_id in quality_monitor.quality_metrics
        assert quality_monitor.quality_metrics[peer_id] == metrics

    @pytest.mark.asyncio
    async def test_get_quality_summary(self, quality_monitor):
        """品質サマリー取得テスト"""
        # 複数のピアのメトリクスを設定
        for i in range(3):
            peer_id = f'peer-{i}'
            metrics = QualityMetrics(
                audio_level=0.8,
                latency=50.0 + i * 10,
                packet_loss=0.01,
                jitter=5.0,
                bandwidth=1000000.0,
                timestamp=datetime.now()
            )
            await quality_monitor.update_quality_metrics(peer_id, metrics)
        
        summary = await quality_monitor.get_quality_summary()
        
        assert 'total_peers' in summary
        assert 'average_latency' in summary
        assert 'average_packet_loss' in summary
        assert 'average_jitter' in summary
        assert 'average_bandwidth' in summary
        assert 'overall_quality' in summary
        assert summary['total_peers'] == 3

    @pytest.mark.asyncio
    async def test_quality_trend_analysis(self, quality_monitor):
        """品質トレンド分析テスト"""
        peer_id = 'peer-1'
        
        # 時系列でメトリクスを追加
        base_time = datetime.now()
        for i in range(10):
            metrics = QualityMetrics(
                audio_level=0.8 - i * 0.05,  # 徐々に低下
                latency=50.0 + i * 10,       # 徐々に増加
                packet_loss=0.01 + i * 0.005, # 徐々に増加
                jitter=5.0 + i * 2,          # 徐々に増加
                bandwidth=1000000.0 - i * 50000, # 徐々に減少
                timestamp=base_time + timedelta(seconds=i * 5)
            )
            await quality_monitor.update_quality_metrics(peer_id, metrics)
        
        trend = await quality_monitor.analyze_quality_trend(peer_id)
        
        assert 'trend_direction' in trend
        assert 'trend_strength' in trend
        assert 'predicted_quality' in trend
        assert trend['trend_direction'] == 'declining'

    @pytest.mark.asyncio
    async def test_quality_threshold_monitoring(self, quality_monitor):
        """品質閾値監視テスト"""
        peer_id = 'peer-1'
        
        # 閾値を設定
        quality_monitor.set_quality_thresholds({
            'latency': 100.0,
            'packet_loss': 0.05,
            'jitter': 20.0,
            'bandwidth': 500000.0,
        })
        
        # 閾値を超えるメトリクス
        poor_metrics = QualityMetrics(
            audio_level=0.8,
            latency=200.0,  # 閾値超過
            packet_loss=0.1,  # 閾値超過
            jitter=30.0,    # 閾値超過
            bandwidth=300000.0,  # 閾値未満
            timestamp=datetime.now()
        )
        
        await quality_monitor.update_quality_metrics(peer_id, poor_metrics)
        
        violations = await quality_monitor.check_quality_thresholds(peer_id)
        
        assert len(violations) > 0
        assert any(violation['metric'] == 'latency' for violation in violations)
        assert any(violation['metric'] == 'packet_loss' for violation in violations)
        assert any(violation['metric'] == 'jitter' for violation in violations)

    @pytest.mark.asyncio
    async def test_quality_metrics_history(self, quality_monitor):
        """品質メトリクス履歴テスト"""
        peer_id = 'peer-1'
        
        # 複数のメトリクスを追加
        for i in range(5):
            metrics = QualityMetrics(
                audio_level=0.8,
                latency=50.0 + i * 10,
                packet_loss=0.01,
                jitter=5.0,
                bandwidth=1000000.0,
                timestamp=datetime.now() + timedelta(seconds=i * 10)
            )
            await quality_monitor.update_quality_metrics(peer_id, metrics)
        
        history = await quality_monitor.get_quality_history(peer_id, limit=3)
        
        assert len(history) == 3
        assert all(isinstance(metric, QualityMetrics) for metric in history)

    @pytest.mark.asyncio
    async def test_quality_metrics_cleanup(self, quality_monitor):
        """品質メトリクスクリーンアップテスト"""
        peer_id = 'peer-1'
        
        # メトリクスを追加
        metrics = QualityMetrics(
            audio_level=0.8,
            latency=50.0,
            packet_loss=0.01,
            jitter=5.0,
            bandwidth=1000000.0,
            timestamp=datetime.now()
        )
        await quality_monitor.update_quality_metrics(peer_id, metrics)
        
        assert peer_id in quality_monitor.quality_metrics
        
        # クリーンアップ
        await quality_monitor.cleanup_old_metrics(peer_id)
        
        # メトリクスが保持されていることを確認（最近のデータなので）
        assert peer_id in quality_monitor.quality_metrics

    @pytest.mark.asyncio
    async def test_quality_monitoring_integration(self, quality_monitor, mock_peer_connections, mock_stats_report):
        """品質監視統合テスト"""
        # モックの統計レポートを設定
        for connection in mock_peer_connections.values():
            connection.getStats.return_value = mock_stats_report
        
        # 監視を開始
        await quality_monitor.start_monitoring(mock_peer_connections)
        
        # 統計を収集
        stats = await quality_monitor.collect_stats()
        
        # 品質メトリクスを更新
        for stat in stats:
            await quality_monitor.update_quality_metrics(stat['peer_id'], QualityMetrics(
                audio_level=stat['audio_level'],
                latency=stat['latency'],
                packet_loss=stat['packet_loss'],
                jitter=stat['jitter'],
                bandwidth=stat['bandwidth'],
                timestamp=datetime.now()
            ))
        
        # 品質サマリーを取得
        summary = await quality_monitor.get_quality_summary()
        
        assert summary['total_peers'] == len(mock_peer_connections)
        assert summary['overall_quality'] in ['excellent', 'good', 'fair', 'poor']
        
        # 監視を停止
        await quality_monitor.stop_monitoring()
        assert quality_monitor.is_monitoring is False

    @pytest.mark.asyncio
    async def test_error_handling(self, quality_monitor, mock_peer_connections):
        """エラーハンドリングテスト"""
        # 統計取得でエラーが発生する接続を設定
        error_connection = MagicMock()
        error_connection.getStats = AsyncMock(side_effect=Exception("Connection error"))
        error_connection.connectionState = 'failed'
        
        mock_peer_connections['error-peer'] = error_connection
        
        await quality_monitor.start_monitoring(mock_peer_connections)
        
        # エラーが発生してもクラッシュしないことを確認
        stats = await quality_monitor.collect_stats()
        
        # エラーが発生したピアは除外される
        assert len(stats) == len(mock_peer_connections) - 1
        assert not any(stat['peer_id'] == 'error-peer' for stat in stats)

    @pytest.mark.asyncio
    async def test_quality_monitoring_performance(self, quality_monitor, mock_peer_connections, mock_stats_report):
        """品質監視パフォーマンステスト"""
        # 大量のピア接続をシミュレート
        large_peer_connections = {}
        for i in range(100):
            connection = MagicMock()
            connection.getStats = AsyncMock(return_value=mock_stats_report)
            connection.connectionState = 'connected'
            large_peer_connections[f'peer-{i}'] = connection
        
        await quality_monitor.start_monitoring(large_peer_connections)
        
        # 統計収集の実行時間を測定
        import time
        start_time = time.time()
        stats = await quality_monitor.collect_stats()
        end_time = time.time()
        
        # 実行時間が妥当であることを確認（5秒以内）
        assert end_time - start_time < 5.0
        assert len(stats) == 100
        
        await quality_monitor.stop_monitoring()
