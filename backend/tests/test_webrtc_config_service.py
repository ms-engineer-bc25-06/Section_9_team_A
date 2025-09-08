"""
WebRTC設定サービス機能のテスト
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Dict, List, Optional

from app.services.webrtc_config_service import (
    WebRTCConfigService,
    WebRTCConfig,
    ICE Server,
    AudioConfig,
    VideoConfig,
    NetworkConfig,
    ConfigValidationError,
    ConfigUpdateError,
)


@pytest.fixture
def config_service():
    """WebRTC設定サービスフィクスチャ"""
    return WebRTCConfigService()


@pytest.fixture
def mock_ice_servers():
    """モックICEサーバーフィクスチャ"""
    return [
        ICE Server(
            urls=['stun:stun.l.google.com:19302'],
            username=None,
            credential=None
        ),
        ICE Server(
            urls=['turn:turn.example.com:3478'],
            username='test_user',
            credential='test_password'
        ),
    ]


@pytest.fixture
def mock_audio_config():
    """モック音声設定フィクスチャ"""
    return AudioConfig(
        sample_rate=48000,
        channels=2,
        bit_depth=16,
        echo_cancellation=True,
        noise_suppression=True,
        auto_gain_control=True,
        volume_control=True,
        mute_detection=True,
    )


@pytest.fixture
def mock_video_config():
    """モック動画設定フィクスチャ"""
    return VideoConfig(
        width=1280,
        height=720,
        frame_rate=30,
        bitrate=1000000,
        codec='VP8',
        quality='high',
        resolution_adaptation=True,
        bandwidth_adaptation=True,
    )


@pytest.fixture
def mock_network_config():
    """モックネットワーク設定フィクスチャ"""
    return NetworkConfig(
        ice_candidate_pool_size=10,
        ice_transport_policy='all',
        bundle_policy='balanced',
        rtcp_mux_policy='require',
        connection_timeout=30,
        keepalive_interval=30,
        max_retry_attempts=3,
        retry_delay=5,
    )


@pytest.fixture
def mock_webrtc_config(mock_ice_servers, mock_audio_config, mock_video_config, mock_network_config):
    """モックWebRTC設定フィクスチャ"""
    return WebRTCConfig(
        ice_servers=mock_ice_servers,
        audio_config=mock_audio_config,
        video_config=mock_video_config,
        network_config=mock_network_config,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


class TestWebRTCConfigService:
    """WebRTC設定サービステスト"""

    @pytest.mark.asyncio
    async def test_initialization(self, config_service):
        """初期化テスト"""
        assert config_service.default_config is not None
        assert config_service.config_cache == {}
        assert config_service.cache_ttl == 300  # 5分
        assert config_service.max_cache_size == 1000

    @pytest.mark.asyncio
    async def test_get_default_config(self, config_service):
        """デフォルト設定取得テスト"""
        config = await config_service.get_default_config()
        
        assert isinstance(config, WebRTCConfig)
        assert len(config.ice_servers) > 0
        assert config.audio_config is not None
        assert config.video_config is not None
        assert config.network_config is not None

    @pytest.mark.asyncio
    async def test_get_config_by_room(self, config_service, mock_webrtc_config):
        """ルーム別設定取得テスト"""
        room_id = 'test-room-123'
        
        # 設定を保存
        await config_service.save_config(room_id, mock_webrtc_config)
        
        # 設定を取得
        config = await config_service.get_config_by_room(room_id)
        
        assert config is not None
        assert config.ice_servers == mock_webrtc_config.ice_servers
        assert config.audio_config == mock_webrtc_config.audio_config
        assert config.video_config == mock_webrtc_config.video_config
        assert config.network_config == mock_webrtc_config.network_config

    @pytest.mark.asyncio
    async def test_get_config_by_user(self, config_service, mock_webrtc_config):
        """ユーザー別設定取得テスト"""
        user_id = 123
        
        # 設定を保存
        await config_service.save_user_config(user_id, mock_webrtc_config)
        
        # 設定を取得
        config = await config_service.get_config_by_user(user_id)
        
        assert config is not None
        assert config.ice_servers == mock_webrtc_config.ice_servers
        assert config.audio_config == mock_webrtc_config.audio_config
        assert config.video_config == mock_webrtc_config.video_config
        assert config.network_config == mock_webrtc_config.network_config

    @pytest.mark.asyncio
    async def test_save_config(self, config_service, mock_webrtc_config):
        """設定保存テスト"""
        room_id = 'test-room-456'
        
        # 設定を保存
        await config_service.save_config(room_id, mock_webrtc_config)
        
        # 設定が保存されていることを確認
        assert room_id in config_service.config_cache
        assert config_service.config_cache[room_id]['config'] == mock_webrtc_config

    @pytest.mark.asyncio
    async def test_update_config(self, config_service, mock_webrtc_config):
        """設定更新テスト"""
        room_id = 'test-room-789'
        
        # 初期設定を保存
        await config_service.save_config(room_id, mock_webrtc_config)
        
        # 設定を更新
        updated_config = mock_webrtc_config.copy()
        updated_config.audio_config.sample_rate = 44100
        updated_config.audio_config.channels = 1
        
        await config_service.update_config(room_id, updated_config)
        
        # 更新された設定を取得
        config = await config_service.get_config_by_room(room_id)
        
        assert config.audio_config.sample_rate == 44100
        assert config.audio_config.channels == 1
        assert config.updated_at > mock_webrtc_config.updated_at

    @pytest.mark.asyncio
    async def test_delete_config(self, config_service, mock_webrtc_config):
        """設定削除テスト"""
        room_id = 'test-room-delete'
        
        # 設定を保存
        await config_service.save_config(room_id, mock_webrtc_config)
        assert room_id in config_service.config_cache
        
        # 設定を削除
        await config_service.delete_config(room_id)
        
        # 設定が削除されていることを確認
        assert room_id not in config_service.config_cache

    @pytest.mark.asyncio
    async def test_validate_config(self, config_service, mock_webrtc_config):
        """設定検証テスト"""
        # 有効な設定
        is_valid = await config_service.validate_config(mock_webrtc_config)
        assert is_valid is True
        
        # 無効な設定（ICEサーバーが空）
        invalid_config = mock_webrtc_config.copy()
        invalid_config.ice_servers = []
        
        is_valid = await config_service.validate_config(invalid_config)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_validate_config_raises_error(self, config_service):
        """設定検証エラーテスト"""
        # 無効な設定でエラーが発生することを確認
        invalid_config = WebRTCConfig(
            ice_servers=[],  # 空のICEサーバー
            audio_config=None,  # 音声設定がNone
            video_config=None,  # 動画設定がNone
            network_config=None,  # ネットワーク設定がNone
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        
        with pytest.raises(ConfigValidationError):
            await config_service.validate_config(invalid_config, raise_on_error=True)

    @pytest.mark.asyncio
    async def test_merge_configs(self, config_service, mock_webrtc_config):
        """設定マージテスト"""
        # ベース設定
        base_config = mock_webrtc_config.copy()
        
        # オーバーライド設定
        override_config = WebRTCConfig(
            ice_servers=None,  # 変更なし
            audio_config=AudioConfig(
                sample_rate=44100,  # 変更
                channels=1,  # 変更
                bit_depth=16,
                echo_cancellation=True,
                noise_suppression=True,
                auto_gain_control=True,
                volume_control=True,
                mute_detection=True,
            ),
            video_config=None,  # 変更なし
            network_config=None,  # 変更なし
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        
        # 設定をマージ
        merged_config = await config_service.merge_configs(base_config, override_config)
        
        # マージ結果を確認
        assert merged_config.ice_servers == base_config.ice_servers
        assert merged_config.audio_config.sample_rate == 44100
        assert merged_config.audio_config.channels == 1
        assert merged_config.video_config == base_config.video_config
        assert merged_config.network_config == base_config.network_config

    @pytest.mark.asyncio
    async def test_get_optimized_config(self, config_service, mock_webrtc_config):
        """最適化設定取得テスト"""
        room_id = 'test-room-optimized'
        
        # 設定を保存
        await config_service.save_config(room_id, mock_webrtc_config)
        
        # ネットワーク状況をシミュレート
        network_conditions = {
            'bandwidth': 1000000,  # 1Mbps
            'latency': 100,  # 100ms
            'packet_loss': 0.01,  # 1%
            'jitter': 10,  # 10ms
        }
        
        # 最適化された設定を取得
        optimized_config = await config_service.get_optimized_config(
            room_id, network_conditions
        )
        
        assert optimized_config is not None
        assert optimized_config.audio_config.sample_rate <= mock_webrtc_config.audio_config.sample_rate
        assert optimized_config.video_config.bitrate <= mock_webrtc_config.video_config.bitrate

    @pytest.mark.asyncio
    async def test_config_caching(self, config_service, mock_webrtc_config):
        """設定キャッシュテスト"""
        room_id = 'test-room-cache'
        
        # 設定を保存
        await config_service.save_config(room_id, mock_webrtc_config)
        
        # キャッシュから設定を取得
        config1 = await config_service.get_config_by_room(room_id)
        config2 = await config_service.get_config_by_room(room_id)
        
        # 同じオブジェクトが返されることを確認（キャッシュされている）
        assert config1 is config2

    @pytest.mark.asyncio
    async def test_config_cache_expiration(self, config_service, mock_webrtc_config):
        """設定キャッシュ期限切れテスト"""
        room_id = 'test-room-expire'
        
        # 設定を保存
        await config_service.save_config(room_id, mock_webrtc_config)
        
        # キャッシュの有効期限を短く設定
        config_service.cache_ttl = 0.1  # 0.1秒
        
        # 設定を取得
        config1 = await config_service.get_config_by_room(room_id)
        assert config1 is not None
        
        # キャッシュ期限切れまで待機
        await asyncio.sleep(0.2)
        
        # 設定を再取得（キャッシュが期限切れ）
        config2 = await config_service.get_config_by_room(room_id)
        assert config2 is not None
        assert config2 is not config1  # 新しいオブジェクトが返される

    @pytest.mark.asyncio
    async def test_config_cache_size_limit(self, config_service, mock_webrtc_config):
        """設定キャッシュサイズ制限テスト"""
        # キャッシュサイズを小さく設定
        config_service.max_cache_size = 2
        
        # 複数の設定を保存
        for i in range(5):
            room_id = f'test-room-{i}'
            await config_service.save_config(room_id, mock_webrtc_config)
        
        # キャッシュサイズが制限内であることを確認
        assert len(config_service.config_cache) <= config_service.max_cache_size

    @pytest.mark.asyncio
    async def test_get_config_statistics(self, config_service, mock_webrtc_config):
        """設定統計取得テスト"""
        # 複数の設定を保存
        for i in range(10):
            room_id = f'test-room-{i}'
            await config_service.save_config(room_id, mock_webrtc_config)
        
        # 統計を取得
        stats = await config_service.get_config_statistics()
        
        assert stats['total_configs'] == 10
        assert stats['cache_size'] == 10
        assert stats['cache_hit_rate'] >= 0
        assert stats['cache_miss_rate'] >= 0

    @pytest.mark.asyncio
    async def test_config_backup_and_restore(self, config_service, mock_webrtc_config):
        """設定バックアップ・復元テスト"""
        room_id = 'test-room-backup'
        
        # 設定を保存
        await config_service.save_config(room_id, mock_webrtc_config)
        
        # バックアップを作成
        backup = await config_service.create_backup()
        
        assert 'configs' in backup
        assert room_id in backup['configs']
        
        # 設定を削除
        await config_service.delete_config(room_id)
        assert room_id not in config_service.config_cache
        
        # バックアップから復元
        await config_service.restore_from_backup(backup)
        
        # 設定が復元されていることを確認
        restored_config = await config_service.get_config_by_room(room_id)
        assert restored_config is not None
        assert restored_config.ice_servers == mock_webrtc_config.ice_servers

    @pytest.mark.asyncio
    async def test_config_export_and_import(self, config_service, mock_webrtc_config):
        """設定エクスポート・インポートテスト"""
        room_id = 'test-room-export'
        
        # 設定を保存
        await config_service.save_config(room_id, mock_webrtc_config)
        
        # 設定をエクスポート
        exported_data = await config_service.export_config(room_id)
        
        assert 'ice_servers' in exported_data
        assert 'audio_config' in exported_data
        assert 'video_config' in exported_data
        assert 'network_config' in exported_data
        
        # 設定を削除
        await config_service.delete_config(room_id)
        
        # エクスポートしたデータから設定をインポート
        new_room_id = 'test-room-import'
        await config_service.import_config(new_room_id, exported_data)
        
        # 設定がインポートされていることを確認
        imported_config = await config_service.get_config_by_room(new_room_id)
        assert imported_config is not None
        assert imported_config.ice_servers == mock_webrtc_config.ice_servers

    @pytest.mark.asyncio
    async def test_config_service_cleanup(self, config_service, mock_webrtc_config):
        """設定サービスクリーンアップテスト"""
        # 複数の設定を保存
        for i in range(5):
            room_id = f'test-room-{i}'
            await config_service.save_config(room_id, mock_webrtc_config)
        
        assert len(config_service.config_cache) == 5
        
        # クリーンアップ
        await config_service.cleanup()
        
        assert len(config_service.config_cache) == 0

    @pytest.mark.asyncio
    async def test_config_service_performance(self, config_service, mock_webrtc_config):
        """設定サービスパフォーマンステスト"""
        # 大量の設定を保存
        start_time = datetime.now()
        
        for i in range(1000):
            room_id = f'test-room-{i}'
            await config_service.save_config(room_id, mock_webrtc_config)
        
        end_time = datetime.now()
        
        # 実行時間が妥当であることを確認（1秒以内）
        assert (end_time - start_time).total_seconds() < 1.0
        
        # 設定取得のパフォーマンス
        start_time = datetime.now()
        config = await config_service.get_config_by_room('test-room-500')
        end_time = datetime.now()
        
        assert (end_time - start_time).total_seconds() < 0.1
        assert config is not None
