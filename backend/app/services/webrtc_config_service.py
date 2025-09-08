"""
WebRTC設定管理サービス
"""
import structlog
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
import json

from app.config import settings

logger = structlog.get_logger()


class WebRTCConfigService:
    """WebRTC設定管理サービス"""
    
    def __init__(self):
        self.stun_servers = settings.WEBRTC_STUN_SERVERS
        self.turn_servers = settings.WEBRTC_TURN_SERVERS
        self.turn_username = settings.WEBRTC_TURN_USERNAME
        self.turn_credential = settings.WEBRTC_TURN_CREDENTIAL
        self.ice_candidate_pool_size = settings.WEBRTC_ICE_CANDIDATE_POOL_SIZE
        self.connection_timeout = settings.WEBRTC_CONNECTION_TIMEOUT
        self.ice_gathering_timeout = settings.WEBRTC_ICE_GATHERING_TIMEOUT
        
        # 設定の検証
        self._validate_config()
        
        logger.info("WebRTC設定サービスを初期化しました")
    
    def _validate_config(self):
        """WebRTC設定の検証"""
        if not self.stun_servers:
            logger.warning("STUNサーバーが設定されていません")
        
        if self.turn_servers and not (self.turn_username and self.turn_credential):
            logger.warning("TURNサーバーが設定されていますが、認証情報が不足しています")
        
        if self.ice_candidate_pool_size < 1:
            logger.warning("ICE candidate pool sizeが小さすぎます")
            self.ice_candidate_pool_size = 10
    
    def get_ice_servers(self) -> List[Dict[str, Any]]:
        """ICEサーバー設定を取得"""
        ice_servers = []
        
        # STUNサーバーを追加
        for stun_server in self.stun_servers:
            ice_servers.append({
                "urls": stun_server
            })
        
        # TURNサーバーを追加
        for turn_server in self.turn_servers:
            turn_config = {
                "urls": turn_server
            }
            
            if self.turn_username and self.turn_credential:
                turn_config.update({
                    "username": self.turn_username,
                    "credential": self.turn_credential
                })
            
            ice_servers.append(turn_config)
        
        logger.debug(f"ICEサーバー設定: {len(ice_servers)}個のサーバー")
        return ice_servers
    
    def get_rtc_configuration(self) -> Dict[str, Any]:
        """RTCConfiguration設定を取得"""
        return {
            "iceServers": self.get_ice_servers(),
            "iceCandidatePoolSize": self.ice_candidate_pool_size,
            "iceTransportPolicy": "all",  # 本番環境では "relay" も検討
            "bundlePolicy": "max-bundle",
            "rtcpMuxPolicy": "require",
            "sdpSemantics": "unified-plan"
        }
    
    def get_audio_constraints(self) -> Dict[str, Any]:
        """音声制約設定を取得"""
        return {
            "echoCancellation": True,
            "noiseSuppression": True,
            "autoGainControl": True,
            "sampleRate": 48000,
            "channelCount": 1,
            "latency": 0.01,  # 10ms
            "volume": 1.0
        }
    
    def get_video_constraints(self) -> Dict[str, Any]:
        """動画制約設定を取得（音声通話では使用しない）"""
        return {
            "width": {"ideal": 640, "max": 1280},
            "height": {"ideal": 480, "max": 720},
            "frameRate": {"ideal": 30, "max": 60}
        }
    
    def get_media_constraints(self, audio: bool = True, video: bool = False) -> Dict[str, Any]:
        """メディア制約設定を取得"""
        constraints = {}
        
        if audio:
            constraints["audio"] = self.get_audio_constraints()
        
        if video:
            constraints["video"] = self.get_video_constraints()
        
        return constraints
    
    def get_connection_timeout(self) -> int:
        """接続タイムアウトを取得（秒）"""
        return self.connection_timeout
    
    def get_ice_gathering_timeout(self) -> int:
        """ICE gatheringタイムアウトを取得（秒）"""
        return self.ice_gathering_timeout
    
    def is_turn_available(self) -> bool:
        """TURNサーバーが利用可能かチェック"""
        return bool(self.turn_servers and self.turn_username and self.turn_credential)
    
    def get_environment_info(self) -> Dict[str, Any]:
        """環境情報を取得"""
        return {
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "stun_servers_count": len(self.stun_servers),
            "turn_servers_count": len(self.turn_servers),
            "turn_available": self.is_turn_available(),
            "ice_candidate_pool_size": self.ice_candidate_pool_size,
            "connection_timeout": self.connection_timeout,
            "ice_gathering_timeout": self.ice_gathering_timeout
        }
    
    def update_turn_servers(self, servers: List[str], username: str = None, credential: str = None):  # pyright: ignore[reportArgumentType]
        """TURNサーバー設定を更新"""
        self.turn_servers = servers
        self.turn_username = username
        self.turn_credential = credential
        
        logger.info(f"TURNサーバー設定を更新: {len(servers)}個のサーバー")
    
    def add_stun_server(self, server: str):
        """STUNサーバーを追加"""
        if server not in self.stun_servers:
            self.stun_servers.append(server)
            logger.info(f"STUNサーバーを追加: {server}")
    
    def remove_stun_server(self, server: str):
        """STUNサーバーを削除"""
        if server in self.stun_servers:
            self.stun_servers.remove(server)
            logger.info(f"STUNサーバーを削除: {server}")
    
    def get_configuration_for_client(self) -> Dict[str, Any]:
        """クライアント用の設定を取得"""
        return {
            "rtcConfiguration": self.get_rtc_configuration(),
            "audioConstraints": self.get_audio_constraints(),
            "mediaConstraints": self.get_media_constraints(audio=True, video=False),
            "timeouts": {
                "connection": self.connection_timeout,
                "iceGathering": self.ice_gathering_timeout
            },
            "environment": self.get_environment_info()
        }


# グローバルインスタンス
webrtc_config_service = WebRTCConfigService()
