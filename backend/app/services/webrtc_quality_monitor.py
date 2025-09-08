"""
WebRTC接続品質監視サービス
"""
import structlog
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
import asyncio
import json
from dataclasses import dataclass, asdict
from enum import Enum

logger = structlog.get_logger()


class ConnectionQuality(Enum):
    """接続品質レベル"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    VERY_POOR = "very_poor"


@dataclass
class QualityMetrics:
    """品質メトリクス"""
    timestamp: datetime
    peer_id: str
    session_id: str
    
    # 接続品質
    connection_state: str
    ice_connection_state: str
    ice_gathering_state: str
    
    # 音声品質
    audio_level: float
    audio_quality: str
    packet_loss: float
    jitter: float
    latency: float
    
    # 統計情報
    bytes_sent: int
    bytes_received: int
    packets_sent: int
    packets_received: int
    packets_lost: int
    
    # 接続品質評価
    overall_quality: ConnectionQuality
    quality_score: float  # 0-100
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['overall_quality'] = self.overall_quality.value
        return data


class WebRTCQualityMonitor:
    """WebRTC接続品質監視サービス"""
    
    def __init__(self):
        self.metrics_history: Dict[str, List[QualityMetrics]] = {}
        self.quality_thresholds = {
            "excellent": {"min_score": 90, "max_latency": 50, "max_packet_loss": 0.01},
            "good": {"min_score": 75, "max_latency": 100, "max_packet_loss": 0.03},
            "fair": {"min_score": 60, "max_latency": 200, "max_packet_loss": 0.05},
            "poor": {"min_score": 40, "max_latency": 500, "max_packet_loss": 0.10},
        }
        self.callbacks: List[Callable[[QualityMetrics], None]] = []
        
        logger.info("WebRTC品質監視サービスを初期化しました")
    
    def add_quality_callback(self, callback: Callable[[QualityMetrics], None]):
        """品質監視コールバックを追加"""
        self.callbacks.append(callback)
    
    def remove_quality_callback(self, callback: Callable[[QualityMetrics], None]):
        """品質監視コールバックを削除"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def _calculate_quality_score(self, metrics: Dict[str, Any]) -> float:
        """品質スコアを計算（0-100）"""
        score = 100.0
        
        # レイテンシによる減点
        latency = metrics.get('latency', 0)
        if latency > 500:
            score -= 30
        elif latency > 200:
            score -= 20
        elif latency > 100:
            score -= 10
        elif latency > 50:
            score -= 5
        
        # パケットロスによる減点
        packet_loss = metrics.get('packet_loss', 0)
        if packet_loss > 0.10:
            score -= 40
        elif packet_loss > 0.05:
            score -= 25
        elif packet_loss > 0.03:
            score -= 15
        elif packet_loss > 0.01:
            score -= 5
        
        # ジッターによる減点
        jitter = metrics.get('jitter', 0)
        if jitter > 50:
            score -= 20
        elif jitter > 30:
            score -= 10
        elif jitter > 20:
            score -= 5
        
        # 接続状態による減点
        connection_state = metrics.get('connection_state', '')
        if connection_state == 'failed':
            score = 0
        elif connection_state == 'disconnected':
            score = 0
        elif connection_state == 'connecting':
            score *= 0.8
        
        return max(0, min(100, score))
    
    def _determine_quality_level(self, score: float, latency: float, packet_loss: float) -> ConnectionQuality:
        """品質レベルを決定"""
        if score >= 90 and latency <= 50 and packet_loss <= 0.01:
            return ConnectionQuality.EXCELLENT
        elif score >= 75 and latency <= 100 and packet_loss <= 0.03:
            return ConnectionQuality.GOOD
        elif score >= 60 and latency <= 200 and packet_loss <= 0.05:
            return ConnectionQuality.FAIR
        elif score >= 40 and latency <= 500 and packet_loss <= 0.10:
            return ConnectionQuality.POOR
        else:
            return ConnectionQuality.VERY_POOR
    
    def record_metrics(self, peer_id: str, session_id: str, metrics_data: Dict[str, Any]) -> QualityMetrics:
        """品質メトリクスを記録"""
        # 品質スコアを計算
        quality_score = self._calculate_quality_score(metrics_data)
        
        # 品質レベルを決定
        overall_quality = self._determine_quality_level(
            quality_score,
            metrics_data.get('latency', 0),
            metrics_data.get('packet_loss', 0)
        )
        
        # メトリクスオブジェクトを作成
        metrics = QualityMetrics(
            timestamp=datetime.utcnow(),
            peer_id=peer_id,
            session_id=session_id,
            connection_state=metrics_data.get('connection_state', 'unknown'),
            ice_connection_state=metrics_data.get('ice_connection_state', 'unknown'),
            ice_gathering_state=metrics_data.get('ice_gathering_state', 'unknown'),
            audio_level=metrics_data.get('audio_level', 0.0),
            audio_quality=metrics_data.get('audio_quality', 'unknown'),
            packet_loss=metrics_data.get('packet_loss', 0.0),
            jitter=metrics_data.get('jitter', 0.0),
            latency=metrics_data.get('latency', 0.0),
            bytes_sent=metrics_data.get('bytes_sent', 0),
            bytes_received=metrics_data.get('bytes_received', 0),
            packets_sent=metrics_data.get('packets_sent', 0),
            packets_received=metrics_data.get('packets_received', 0),
            packets_lost=metrics_data.get('packets_lost', 0),
            overall_quality=overall_quality,
            quality_score=quality_score
        )
        
        # 履歴に追加
        if peer_id not in self.metrics_history:
            self.metrics_history[peer_id] = []
        
        self.metrics_history[peer_id].append(metrics)
        
        # 履歴を保持（最新100件）
        if len(self.metrics_history[peer_id]) > 100:
            self.metrics_history[peer_id] = self.metrics_history[peer_id][-100:]
        
        # コールバックを実行
        for callback in self.callbacks:
            try:
                callback(metrics)
            except Exception as e:
                logger.error(f"品質監視コールバックエラー: {e}")
        
        logger.debug(
            f"品質メトリクス記録: peer={peer_id}, quality={overall_quality.value}, score={quality_score:.1f}"
        )
        
        return metrics
    
    def get_peer_metrics(self, peer_id: str, limit: int = 10) -> List[QualityMetrics]:
        """ピアの品質メトリクスを取得"""
        if peer_id not in self.metrics_history:
            return []
        
        return self.metrics_history[peer_id][-limit:]
    
    def get_session_metrics(self, session_id: str, limit: int = 50) -> List[QualityMetrics]:
        """セッションの品質メトリクスを取得"""
        session_metrics = []
        
        for peer_metrics in self.metrics_history.values():
            for metric in peer_metrics:
                if metric.session_id == session_id:
                    session_metrics.append(metric)
        
        # タイムスタンプでソート
        session_metrics.sort(key=lambda x: x.timestamp)
        
        return session_metrics[-limit:]
    
    def get_quality_summary(self, peer_id: str, duration_minutes: int = 5) -> Dict[str, Any]:
        """品質サマリーを取得"""
        if peer_id not in self.metrics_history:
            return {
                "peer_id": peer_id,
                "duration_minutes": duration_minutes,
                "total_samples": 0,
                "average_quality_score": 0,
                "quality_distribution": {},
                "average_latency": 0,
                "average_packet_loss": 0,
                "connection_stability": 0
            }
        
        # 指定期間のメトリクスを取得
        cutoff_time = datetime.utcnow() - timedelta(minutes=duration_minutes)
        recent_metrics = [
            m for m in self.metrics_history[peer_id]
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_metrics:
            return {
                "peer_id": peer_id,
                "duration_minutes": duration_minutes,
                "total_samples": 0,
                "average_quality_score": 0,
                "quality_distribution": {},
                "average_latency": 0,
                "average_packet_loss": 0,
                "connection_stability": 0
            }
        
        # 統計を計算
        total_samples = len(recent_metrics)
        average_quality_score = sum(m.quality_score for m in recent_metrics) / total_samples
        average_latency = sum(m.latency for m in recent_metrics) / total_samples
        average_packet_loss = sum(m.packet_loss for m in recent_metrics) / total_samples
        
        # 品質分布を計算
        quality_distribution = {}
        for quality in ConnectionQuality:
            count = sum(1 for m in recent_metrics if m.overall_quality == quality)
            quality_distribution[quality.value] = count
        
        # 接続安定性を計算（接続状態が'connected'の割合）
        connected_count = sum(1 for m in recent_metrics if m.connection_state == 'connected')
        connection_stability = (connected_count / total_samples) * 100
        
        return {
            "peer_id": peer_id,
            "duration_minutes": duration_minutes,
            "total_samples": total_samples,
            "average_quality_score": round(average_quality_score, 2),
            "quality_distribution": quality_distribution,
            "average_latency": round(average_latency, 2),
            "average_packet_loss": round(average_packet_loss, 4),
            "connection_stability": round(connection_stability, 2)
        }
    
    def get_session_quality_summary(self, session_id: str, duration_minutes: int = 5) -> Dict[str, Any]:
        """セッション全体の品質サマリーを取得"""
        session_metrics = self.get_session_metrics(session_id, limit=1000)
        
        if not session_metrics:
            return {
                "session_id": session_id,
                "duration_minutes": duration_minutes,
                "total_peers": 0,
                "total_samples": 0,
                "average_quality_score": 0,
                "quality_distribution": {},
                "average_latency": 0,
                "average_packet_loss": 0,
                "connection_stability": 0
            }
        
        # 指定期間のメトリクスを取得
        cutoff_time = datetime.utcnow() - timedelta(minutes=duration_minutes)
        recent_metrics = [m for m in session_metrics if m.timestamp >= cutoff_time]
        
        if not recent_metrics:
            return {
                "session_id": session_id,
                "duration_minutes": duration_minutes,
                "total_peers": 0,
                "total_samples": 0,
                "average_quality_score": 0,
                "quality_distribution": {},
                "average_latency": 0,
                "average_packet_loss": 0,
                "connection_stability": 0
            }
        
        # 統計を計算
        total_peers = len(set(m.peer_id for m in recent_metrics))
        total_samples = len(recent_metrics)
        average_quality_score = sum(m.quality_score for m in recent_metrics) / total_samples
        average_latency = sum(m.latency for m in recent_metrics) / total_samples
        average_packet_loss = sum(m.packet_loss for m in recent_metrics) / total_samples
        
        # 品質分布を計算
        quality_distribution = {}
        for quality in ConnectionQuality:
            count = sum(1 for m in recent_metrics if m.overall_quality == quality)
            quality_distribution[quality.value] = count
        
        # 接続安定性を計算
        connected_count = sum(1 for m in recent_metrics if m.connection_state == 'connected')
        connection_stability = (connected_count / total_samples) * 100
        
        return {
            "session_id": session_id,
            "duration_minutes": duration_minutes,
            "total_peers": total_peers,
            "total_samples": total_samples,
            "average_quality_score": round(average_quality_score, 2),
            "quality_distribution": quality_distribution,
            "average_latency": round(average_latency, 2),
            "average_packet_loss": round(average_packet_loss, 4),
            "connection_stability": round(connection_stability, 2)
        }
    
    def cleanup_old_metrics(self, hours: int = 24):
        """古いメトリクスをクリーンアップ"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        for peer_id in list(self.metrics_history.keys()):
            self.metrics_history[peer_id] = [
                m for m in self.metrics_history[peer_id]
                if m.timestamp >= cutoff_time
            ]
            
            # 空になったピアの履歴を削除
            if not self.metrics_history[peer_id]:
                del self.metrics_history[peer_id]
        
        logger.info(f"古いメトリクスをクリーンアップしました（{hours}時間以上前）")


# グローバルインスタンス
webrtc_quality_monitor = WebRTCQualityMonitor()
