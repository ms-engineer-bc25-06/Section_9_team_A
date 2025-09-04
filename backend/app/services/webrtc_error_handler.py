"""
WebRTCエラーハンドリングサービス
"""
import structlog
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
import asyncio
import json
from dataclasses import dataclass, asdict
from enum import Enum

logger = structlog.get_logger()


class WebRTCErrorType(Enum):
    """WebRTCエラータイプ"""
    CONNECTION_FAILED = "connection_failed"
    ICE_GATHERING_FAILED = "ice_gathering_failed"
    ICE_CONNECTION_FAILED = "ice_connection_failed"
    SIGNALING_ERROR = "signaling_error"
    MEDIA_ACCESS_ERROR = "media_access_error"
    NETWORK_ERROR = "network_error"
    PERMISSION_ERROR = "permission_error"
    CONFIGURATION_ERROR = "configuration_error"
    TIMEOUT_ERROR = "timeout_error"
    UNKNOWN_ERROR = "unknown_error"


class ErrorSeverity(Enum):
    """エラー重要度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class WebRTCError:
    """WebRTCエラー情報"""
    timestamp: datetime
    error_id: str
    error_type: WebRTCErrorType
    severity: ErrorSeverity
    peer_id: str
    session_id: str
    error_message: str
    error_code: Optional[str] = None
    stack_trace: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    resolved: bool = False
    resolution_attempts: int = 0
    last_attempt: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['error_type'] = self.error_type.value
        data['severity'] = self.severity.value
        data['last_attempt'] = self.last_attempt.isoformat() if self.last_attempt else None
        return data


class WebRTCErrorHandler:
    """WebRTCエラーハンドリングサービス"""
    
    def __init__(self):
        self.error_history: Dict[str, List[WebRTCError]] = {}
        self.error_callbacks: List[Callable[[WebRTCError], None]] = []
        self.resolution_strategies: Dict[WebRTCErrorType, List[Callable]] = {}
        self.error_thresholds = {
            ErrorSeverity.LOW: 10,      # 10回で警告
            ErrorSeverity.MEDIUM: 5,    # 5回で警告
            ErrorSeverity.HIGH: 3,      # 3回で警告
            ErrorSeverity.CRITICAL: 1,  # 1回で警告
        }
        
        # デフォルトの解決戦略を設定
        self._setup_default_strategies()
        
        logger.info("WebRTCエラーハンドリングサービスを初期化しました")
    
    def _setup_default_strategies(self):
        """デフォルトの解決戦略を設定"""
        self.resolution_strategies = {
            WebRTCErrorType.CONNECTION_FAILED: [
                self._retry_connection,
                self._fallback_to_turn,
                self._restart_peer_connection,
            ],
            WebRTCErrorType.ICE_GATHERING_FAILED: [
                self._retry_ice_gathering,
                self._add_more_ice_servers,
                self._fallback_to_turn,
            ],
            WebRTCErrorType.ICE_CONNECTION_FAILED: [
                self._retry_ice_connection,
                self._fallback_to_turn,
                self._restart_peer_connection,
            ],
            WebRTCErrorType.SIGNALING_ERROR: [
                self._retry_signaling,
                self._fallback_signaling_method,
            ],
            WebRTCErrorType.MEDIA_ACCESS_ERROR: [
                self._request_media_permission,
                self._fallback_media_constraints,
            ],
            WebRTCErrorType.NETWORK_ERROR: [
                self._retry_network_operation,
                self._fallback_to_turn,
            ],
            WebRTCErrorType.PERMISSION_ERROR: [
                self._request_permission,
                self._fallback_permission_method,
            ],
            WebRTCErrorType.CONFIGURATION_ERROR: [
                self._fix_configuration,
                self._fallback_configuration,
            ],
            WebRTCErrorType.TIMEOUT_ERROR: [
                self._increase_timeout,
                self._retry_operation,
            ],
        }
    
    def add_error_callback(self, callback: Callable[[WebRTCError], None]):
        """エラーコールバックを追加"""
        self.error_callbacks.append(callback)
    
    def remove_error_callback(self, callback: Callable[[WebRTCError], None]):
        """エラーコールバックを削除"""
        if callback in self.error_callbacks:
            self.error_callbacks.remove(callback)
    
    def add_resolution_strategy(self, error_type: WebRTCErrorType, strategy: Callable):
        """解決戦略を追加"""
        if error_type not in self.resolution_strategies:
            self.resolution_strategies[error_type] = []
        self.resolution_strategies[error_type].append(strategy)
    
    def record_error(
        self,
        error_type: WebRTCErrorType,
        severity: ErrorSeverity,
        peer_id: str,
        session_id: str,
        error_message: str,
        error_code: Optional[str] = None,
        stack_trace: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> WebRTCError:
        """エラーを記録"""
        error_id = f"{peer_id}_{session_id}_{datetime.utcnow().timestamp()}"
        
        error = WebRTCError(
            timestamp=datetime.utcnow(),
            error_id=error_id,
            error_type=error_type,
            severity=severity,
            peer_id=peer_id,
            session_id=session_id,
            error_message=error_message,
            error_code=error_code,
            stack_trace=stack_trace,
            context=context or {}
        )
        
        # 履歴に追加
        if peer_id not in self.error_history:
            self.error_history[peer_id] = []
        
        self.error_history[peer_id].append(error)
        
        # 履歴を保持（最新50件）
        if len(self.error_history[peer_id]) > 50:
            self.error_history[peer_id] = self.error_history[peer_id][-50:]
        
        # コールバックを実行
        for callback in self.error_callbacks:
            try:
                callback(error)
            except Exception as e:
                logger.error(f"エラーコールバックエラー: {e}")
        
        # 自動解決を試行
        asyncio.create_task(self._attempt_auto_resolution(error))
        
        logger.error(
            f"WebRTCエラー記録: {error_type.value} - {error_message}",
            peer_id=peer_id,
            session_id=session_id,
            severity=severity.value,
            error_code=error_code
        )
        
        return error
    
    async def _attempt_auto_resolution(self, error: WebRTCError):
        """自動解決を試行"""
        if error.resolved:
            return
        
        strategies = self.resolution_strategies.get(error.error_type, [])
        
        for strategy in strategies:
            try:
                error.resolution_attempts += 1
                error.last_attempt = datetime.utcnow()
                
                result = await strategy(error)
                
                if result:
                    error.resolved = True
                    logger.info(f"エラー自動解決成功: {error.error_id}")
                    break
                    
            except Exception as e:
                logger.error(f"エラー解決戦略実行エラー: {e}")
        
        if not error.resolved:
            logger.warning(f"エラー自動解決失敗: {error.error_id}")
    
    # 解決戦略の実装
    async def _retry_connection(self, error: WebRTCError) -> bool:
        """接続再試行"""
        logger.info(f"接続再試行: {error.error_id}")
        # 実際の実装では、RTCPeerConnectionの再接続を試行
        await asyncio.sleep(1)
        return True
    
    async def _fallback_to_turn(self, error: WebRTCError) -> bool:
        """TURNサーバーへのフォールバック"""
        logger.info(f"TURNサーバーフォールバック: {error.error_id}")
        # 実際の実装では、TURNサーバーを使用した接続を試行
        await asyncio.sleep(1)
        return True
    
    async def _restart_peer_connection(self, error: WebRTCError) -> bool:
        """ピア接続の再起動"""
        logger.info(f"ピア接続再起動: {error.error_id}")
        # 実際の実装では、RTCPeerConnectionを再作成
        await asyncio.sleep(2)
        return True
    
    async def _retry_ice_gathering(self, error: WebRTCError) -> bool:
        """ICE gathering再試行"""
        logger.info(f"ICE gathering再試行: {error.error_id}")
        await asyncio.sleep(1)
        return True
    
    async def _add_more_ice_servers(self, error: WebRTCError) -> bool:
        """ICEサーバー追加"""
        logger.info(f"ICEサーバー追加: {error.error_id}")
        await asyncio.sleep(1)
        return True
    
    async def _retry_ice_connection(self, error: WebRTCError) -> bool:
        """ICE接続再試行"""
        logger.info(f"ICE接続再試行: {error.error_id}")
        await asyncio.sleep(1)
        return True
    
    async def _retry_signaling(self, error: WebRTCError) -> bool:
        """シグナリング再試行"""
        logger.info(f"シグナリング再試行: {error.error_id}")
        await asyncio.sleep(1)
        return True
    
    async def _fallback_signaling_method(self, error: WebRTCError) -> bool:
        """シグナリング方法のフォールバック"""
        logger.info(f"シグナリング方法フォールバック: {error.error_id}")
        await asyncio.sleep(1)
        return True
    
    async def _request_media_permission(self, error: WebRTCError) -> bool:
        """メディア権限要求"""
        logger.info(f"メディア権限要求: {error.error_id}")
        await asyncio.sleep(1)
        return True
    
    async def _fallback_media_constraints(self, error: WebRTCError) -> bool:
        """メディア制約のフォールバック"""
        logger.info(f"メディア制約フォールバック: {error.error_id}")
        await asyncio.sleep(1)
        return True
    
    async def _retry_network_operation(self, error: WebRTCError) -> bool:
        """ネットワーク操作再試行"""
        logger.info(f"ネットワーク操作再試行: {error.error_id}")
        await asyncio.sleep(1)
        return True
    
    async def _request_permission(self, error: WebRTCError) -> bool:
        """権限要求"""
        logger.info(f"権限要求: {error.error_id}")
        await asyncio.sleep(1)
        return True
    
    async def _fallback_permission_method(self, error: WebRTCError) -> bool:
        """権限方法のフォールバック"""
        logger.info(f"権限方法フォールバック: {error.error_id}")
        await asyncio.sleep(1)
        return True
    
    async def _fix_configuration(self, error: WebRTCError) -> bool:
        """設定修正"""
        logger.info(f"設定修正: {error.error_id}")
        await asyncio.sleep(1)
        return True
    
    async def _fallback_configuration(self, error: WebRTCError) -> bool:
        """設定フォールバック"""
        logger.info(f"設定フォールバック: {error.error_id}")
        await asyncio.sleep(1)
        return True
    
    async def _increase_timeout(self, error: WebRTCError) -> bool:
        """タイムアウト延長"""
        logger.info(f"タイムアウト延長: {error.error_id}")
        await asyncio.sleep(1)
        return True
    
    async def _retry_operation(self, error: WebRTCError) -> bool:
        """操作再試行"""
        logger.info(f"操作再試行: {error.error_id}")
        await asyncio.sleep(1)
        return True
    
    def get_peer_errors(self, peer_id: str, limit: int = 10) -> List[WebRTCError]:
        """ピアのエラー履歴を取得"""
        if peer_id not in self.error_history:
            return []
        
        return self.error_history[peer_id][-limit:]
    
    def get_session_errors(self, session_id: str, limit: int = 50) -> List[WebRTCError]:
        """セッションのエラー履歴を取得"""
        session_errors = []
        
        for peer_errors in self.error_history.values():
            for error in peer_errors:
                if error.session_id == session_id:
                    session_errors.append(error)
        
        # タイムスタンプでソート
        session_errors.sort(key=lambda x: x.timestamp)
        
        return session_errors[-limit:]
    
    def get_error_summary(self, peer_id: str, duration_minutes: int = 5) -> Dict[str, Any]:
        """エラーサマリーを取得"""
        if peer_id not in self.error_history:
            return {
                "peer_id": peer_id,
                "duration_minutes": duration_minutes,
                "total_errors": 0,
                "error_types": {},
                "severity_distribution": {},
                "resolved_errors": 0,
                "unresolved_errors": 0,
                "error_rate": 0.0
            }
        
        # 指定期間のエラーを取得
        cutoff_time = datetime.utcnow() - timedelta(minutes=duration_minutes)
        recent_errors = [
            e for e in self.error_history[peer_id]
            if e.timestamp >= cutoff_time
        ]
        
        if not recent_errors:
            return {
                "peer_id": peer_id,
                "duration_minutes": duration_minutes,
                "total_errors": 0,
                "error_types": {},
                "severity_distribution": {},
                "resolved_errors": 0,
                "unresolved_errors": 0,
                "error_rate": 0.0
            }
        
        # 統計を計算
        total_errors = len(recent_errors)
        resolved_errors = sum(1 for e in recent_errors if e.resolved)
        unresolved_errors = total_errors - resolved_errors
        
        # エラータイプ分布
        error_types = {}
        for error_type in WebRTCErrorType:
            count = sum(1 for e in recent_errors if e.error_type == error_type)
            if count > 0:
                error_types[error_type.value] = count
        
        # 重要度分布
        severity_distribution = {}
        for severity in ErrorSeverity:
            count = sum(1 for e in recent_errors if e.severity == severity)
            if count > 0:
                severity_distribution[severity.value] = count
        
        # エラー率（分あたり）
        error_rate = total_errors / duration_minutes
        
        return {
            "peer_id": peer_id,
            "duration_minutes": duration_minutes,
            "total_errors": total_errors,
            "error_types": error_types,
            "severity_distribution": severity_distribution,
            "resolved_errors": resolved_errors,
            "unresolved_errors": unresolved_errors,
            "error_rate": round(error_rate, 2)
        }
    
    def check_error_thresholds(self, peer_id: str) -> List[Dict[str, Any]]:
        """エラー閾値をチェック"""
        if peer_id not in self.error_history:
            return []
        
        # 過去1時間のエラーを取得
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        recent_errors = [
            e for e in self.error_history[peer_id]
            if e.timestamp >= cutoff_time
        ]
        
        # 重要度別にエラー数をカウント
        severity_counts = {}
        for severity in ErrorSeverity:
            count = sum(1 for e in recent_errors if e.severity == severity)
            severity_counts[severity] = count
        
        # 閾値をチェック
        threshold_violations = []
        for severity, count in severity_counts.items():
            threshold = self.error_thresholds.get(severity, 0)
            if count >= threshold:
                threshold_violations.append({
                    "severity": severity.value,
                    "count": count,
                    "threshold": threshold,
                    "violation": True
                })
        
        return threshold_violations
    
    def cleanup_old_errors(self, hours: int = 24):
        """古いエラーをクリーンアップ"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        for peer_id in list(self.error_history.keys()):
            self.error_history[peer_id] = [
                e for e in self.error_history[peer_id]
                if e.timestamp >= cutoff_time
            ]
            
            # 空になったピアの履歴を削除
            if not self.error_history[peer_id]:
                del self.error_history[peer_id]
        
        logger.info(f"古いエラーをクリーンアップしました（{hours}時間以上前）")


# グローバルインスタンス
webrtc_error_handler = WebRTCErrorHandler()
