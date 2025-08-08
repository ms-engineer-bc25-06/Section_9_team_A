import base64
import io
import wave
import struct
import numpy as np
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
import structlog
import asyncio
from dataclasses import dataclass
from enum import Enum

from app.core.exceptions import ValidationException
from app.schemas.websocket import AudioDataMessage

logger = structlog.get_logger()


class AudioQuality(str, Enum):
    """音声品質レベル"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"


class NetworkCondition(str, Enum):
    """ネットワーク状況"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


@dataclass
class AudioChunk:
    """音声チャンクデータ"""

    data: bytes
    sample_rate: int
    channels: int
    timestamp: datetime
    chunk_id: str
    user_id: int
    session_id: str


@dataclass
class AudioLevel:
    """音声レベル情報"""

    level: float  # 0.0 - 1.0
    is_speaking: bool
    rms: float
    peak: float
    timestamp: datetime
    user_id: Optional[int] = None


@dataclass
class AudioQualityMetrics:
    """音声品質メトリクス"""

    snr: float  # Signal-to-Noise Ratio
    clarity: float  # 音声の明瞭度
    latency: float  # 遅延時間（ms）
    packet_loss: float  # パケット損失率
    jitter: float  # ジッター
    timestamp: datetime


@dataclass
class NetworkMetrics:
    """ネットワークメトリクス"""

    bandwidth: float  # 帯域幅（kbps）
    latency: float  # 遅延（ms）
    packet_loss: float  # パケット損失率
    jitter: float  # ジッター（ms）
    quality_score: float  # 品質スコア（0-1）
    timestamp: datetime


class AudioQualityManager:
    """音声品質管理クラス"""

    def __init__(self):
        self.quality_settings = {
            AudioQuality.LOW: {
                "sample_rate": 8000,
                "channels": 1,
                "bit_depth": 16,
                "compression": "low"
            },
            AudioQuality.MEDIUM: {
                "sample_rate": 16000,
                "channels": 1,
                "bit_depth": 16,
                "compression": "medium"
            },
            AudioQuality.HIGH: {
                "sample_rate": 44100,
                "channels": 2,
                "bit_depth": 24,
                "compression": "high"
            },
            AudioQuality.ULTRA: {
                "sample_rate": 48000,
                "channels": 2,
                "bit_depth": 32,
                "compression": "lossless"
            }
        }
        
        self.current_quality = AudioQuality.MEDIUM
        self.network_metrics: Dict[str, NetworkMetrics] = {}
        self.quality_history: Dict[str, List[AudioQualityMetrics]] = {}

    def get_optimal_quality(self, network_condition: NetworkCondition) -> AudioQuality:
        """ネットワーク状況に基づいて最適な音声品質を決定"""
        if network_condition == NetworkCondition.EXCELLENT:
            return AudioQuality.ULTRA
        elif network_condition == NetworkCondition.GOOD:
            return AudioQuality.HIGH
        elif network_condition == NetworkCondition.FAIR:
            return AudioQuality.MEDIUM
        else:
            return AudioQuality.LOW

    def adjust_quality_for_network(self, session_id: str) -> AudioQuality:
        """ネットワーク状況に応じて音声品質を調整"""
        if session_id not in self.network_metrics:
            return self.current_quality

        metrics = self.network_metrics[session_id]
        
        # 品質スコアに基づいて品質を調整
        if metrics.quality_score > 0.8:
            new_quality = AudioQuality.HIGH
        elif metrics.quality_score > 0.6:
            new_quality = AudioQuality.MEDIUM
        elif metrics.quality_score > 0.4:
            new_quality = AudioQuality.LOW
        else:
            new_quality = AudioQuality.LOW

        if new_quality != self.current_quality:
            logger.info(f"Adjusting audio quality from {self.current_quality} to {new_quality}")
            self.current_quality = new_quality

        return self.current_quality

    def update_network_metrics(self, session_id: str, metrics: NetworkMetrics):
        """ネットワークメトリクスを更新"""
        self.network_metrics[session_id] = metrics

    def get_quality_settings(self, quality: AudioQuality) -> Dict[str, Any]:
        """音声品質設定を取得"""
        return self.quality_settings.get(quality, self.quality_settings[AudioQuality.MEDIUM])


class AudioBufferManager:
    """音声バッファ管理クラス"""

    def __init__(self):
        self.buffers: Dict[str, List[AudioChunk]] = {}
        self.buffer_sizes: Dict[str, int] = {}
        self.max_buffer_size = 1000  # 最大バッファサイズ
        self.target_latency_ms = 100  # 目標遅延時間

    async def add_chunk(self, session_id: str, chunk: AudioChunk):
        """音声チャンクをバッファに追加"""
        if session_id not in self.buffers:
            self.buffers[session_id] = []
            self.buffer_sizes[session_id] = 0

        # バッファに追加
        self.buffers[session_id].append(chunk)
        self.buffer_sizes[session_id] += len(chunk.data)

        # バッファサイズ制限
        await self._manage_buffer_size(session_id)

    async def get_chunks(self, session_id: str, limit: int = 10) -> List[AudioChunk]:
        """バッファから音声チャンクを取得"""
        if session_id not in self.buffers:
            return []

        return self.buffers[session_id][-limit:]

    async def clear_buffer(self, session_id: str):
        """バッファをクリア"""
        if session_id in self.buffers:
            self.buffers[session_id].clear()
            self.buffer_sizes[session_id] = 0

    async def get_buffer_stats(self, session_id: str) -> Dict[str, Any]:
        """バッファ統計を取得"""
        if session_id not in self.buffers:
            return {
                "chunk_count": 0,
                "total_size": 0,
                "average_latency": 0.0
            }

        chunks = self.buffers[session_id]
        if not chunks:
            return {
                "chunk_count": 0,
                "total_size": 0,
                "average_latency": 0.0
            }

        # 平均遅延を計算
        current_time = datetime.now()
        latencies = [
            (current_time - chunk.timestamp).total_seconds() * 1000
            for chunk in chunks
        ]
        average_latency = sum(latencies) / len(latencies)

        return {
            "chunk_count": len(chunks),
            "total_size": self.buffer_sizes[session_id],
            "average_latency": average_latency
        }

    async def _manage_buffer_size(self, session_id: str):
        """バッファサイズを管理"""
        if session_id not in self.buffers:
            return

        # 最大サイズを超えた場合、古いチャンクを削除
        while len(self.buffers[session_id]) > self.max_buffer_size:
            removed_chunk = self.buffers[session_id].pop(0)
            self.buffer_sizes[session_id] -= len(removed_chunk.data)

        # 目標遅延時間を超えた場合、古いチャンクを削除
        current_time = datetime.now()
        while self.buffers[session_id]:
            oldest_chunk = self.buffers[session_id][0]
            latency_ms = (current_time - oldest_chunk.timestamp).total_seconds() * 1000
            
            if latency_ms > self.target_latency_ms:
                removed_chunk = self.buffers[session_id].pop(0)
                self.buffer_sizes[session_id] -= len(removed_chunk.data)
            else:
                break


class AudioProcessingService:
    """音声データ処理サービス"""

    def __init__(self):
        # 音声設定
        self.default_sample_rate = 16000
        self.default_channels = 1
        self.chunk_duration_ms = 100  # 100ms chunks
        self.speaking_threshold = 0.01  # 話者検出閾値

        # 音声品質管理
        self.quality_manager = AudioQualityManager()
        
        # 音声バッファ管理
        self.buffer_manager = AudioBufferManager()
        
        # 録音セッション
        self.recording_sessions: Dict[str, bool] = {}
        
        # 音声レベル履歴
        self.audio_level_history: Dict[str, List[AudioLevel]] = {}

    async def process_audio_data(self, audio_message: AudioDataMessage) -> AudioChunk:
        """音声データを処理"""
        try:
            # Base64デコード
            audio_data = self._decode_audio_data(audio_message.data)

            # 音声データの検証
            self._validate_audio_data(audio_data, audio_message)

            # 音声品質を調整
            optimal_quality = self.quality_manager.adjust_quality_for_network(
                audio_message.session_id
            )
            
            # 音声データを品質に応じて処理
            processed_audio_data = await self._process_audio_for_quality(
                audio_data, optimal_quality
            )

            # 音声チャンクを作成
            chunk = AudioChunk(
                data=processed_audio_data,
                sample_rate=audio_message.sample_rate or self.default_sample_rate,
                channels=audio_message.channels or self.default_channels,
                timestamp=audio_message.timestamp if isinstance(audio_message.timestamp, datetime) else datetime.fromisoformat(audio_message.timestamp),
                chunk_id=audio_message.chunk_id
                or f"chunk_{int(datetime.now().timestamp() * 1000)}",
                user_id=audio_message.user_id,
                session_id=audio_message.session_id,
            )

            # 音声レベルを計算
            audio_level = self._calculate_audio_level(chunk)

            # 音声品質メトリクスを計算
            quality_metrics = await self._calculate_quality_metrics(chunk, audio_level)

            # バッファに追加
            await self.buffer_manager.add_chunk(chunk.session_id, chunk)

            # 音声レベル履歴を更新
            await self._update_audio_level_history(chunk.session_id, audio_level)

            # 録音中なら保存
            if self.recording_sessions.get(audio_message.session_id, False):
                await self._save_audio_chunk(chunk)

            logger.debug(
                f"Processed audio chunk: {chunk.chunk_id}",
                user_id=chunk.user_id,
                session_id=chunk.session_id,
                level=audio_level.level,
                is_speaking=audio_level.is_speaking,
                quality=optimal_quality.value,
            )

            return chunk

        except Exception as e:
            logger.error(f"Failed to process audio data: {e}")
            raise ValidationException("Invalid audio data")

    async def _process_audio_for_quality(
        self, audio_data: bytes, quality: AudioQuality
    ) -> bytes:
        """音声品質に応じて音声データを処理"""
        try:
            settings = self.quality_manager.get_quality_settings(quality)
            
            # サンプルレート変換（簡易実装）
            if settings["sample_rate"] != self.default_sample_rate:
                # 実際の実装ではlibrosa等を使用
                logger.debug(f"Sample rate conversion: {self.default_sample_rate} -> {settings['sample_rate']}")
            
            # チャンネル数変換
            if settings["channels"] == 1 and self.default_channels == 2:
                # ステレオからモノラルに変換
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                mono_array = audio_array[::2]  # 左チャンネルのみ
                audio_data = mono_array.tobytes()
            
            return audio_data

        except Exception as e:
            logger.error(f"Failed to process audio for quality: {e}")
            return audio_data

    async def _calculate_quality_metrics(
        self, chunk: AudioChunk, audio_level: AudioLevel
    ) -> AudioQualityMetrics:
        """音声品質メトリクスを計算"""
        try:
            # SNR（Signal-to-Noise Ratio）の簡易計算
            audio_array = np.frombuffer(chunk.data, dtype=np.int16)
            signal_power = np.mean(audio_array**2)
            noise_power = np.var(audio_array) * 0.1  # 簡易ノイズ推定
            snr = 10 * np.log10(signal_power / (noise_power + 1e-10))

            # 明瞭度の計算（簡易）
            clarity = min(1.0, audio_level.rms * 5)

            # 遅延時間（現在時刻とチャンク時刻の差）
            latency = (datetime.now() - chunk.timestamp).total_seconds() * 1000

            # パケット損失率（簡易推定）
            packet_loss = 0.0  # 実際の実装では統計から計算

            # ジッター（簡易）
            jitter = 0.0  # 実際の実装では統計から計算

            metrics = AudioQualityMetrics(
                snr=snr,
                clarity=clarity,
                latency=latency,
                packet_loss=packet_loss,
                jitter=jitter,
                timestamp=datetime.now()
            )

            # 品質履歴に追加
            session_id = chunk.session_id
            if session_id not in self.quality_manager.quality_history:
                self.quality_manager.quality_history[session_id] = []
            
            self.quality_manager.quality_history[session_id].append(metrics)
            
            # 履歴サイズ制限
            if len(self.quality_manager.quality_history[session_id]) > 100:
                self.quality_manager.quality_history[session_id] = \
                    self.quality_manager.quality_history[session_id][-100:]

            return metrics

        except Exception as e:
            logger.error(f"Failed to calculate quality metrics: {e}")
            return AudioQualityMetrics(
                snr=0.0,
                clarity=0.0,
                latency=0.0,
                packet_loss=0.0,
                jitter=0.0,
                timestamp=datetime.now()
            )

    async def _update_audio_level_history(self, session_id: str, audio_level: AudioLevel):
        """音声レベル履歴を更新"""
        if session_id not in self.audio_level_history:
            self.audio_level_history[session_id] = []
        
        self.audio_level_history[session_id].append(audio_level)
        
        # 履歴サイズ制限（最新100件）
        if len(self.audio_level_history[session_id]) > 100:
            self.audio_level_history[session_id] = \
                self.audio_level_history[session_id][-100:]

    def _decode_audio_data(self, base64_data: str) -> bytes:
        """Base64エンコードされた音声データをデコード"""
        try:
            return base64.b64decode(base64_data)
        except Exception as e:
            logger.error(f"Failed to decode base64 audio data: {e}")
            raise ValidationException("Invalid base64 audio data")

    def _validate_audio_data(self, audio_data: bytes, message: AudioDataMessage):
        """音声データの検証"""
        if not audio_data:
            raise ValidationException("Empty audio data")

        # データサイズのチェック
        if len(audio_data) > 1024 * 1024:  # 1MB制限
            raise ValidationException("Audio data too large")

        # 音声フォーマットの検証（簡易）
        if len(audio_data) < 44:  # WAVヘッダー最小サイズ
            logger.warning("Audio data may not be in valid format")

    def _calculate_audio_level(self, chunk: AudioChunk) -> AudioLevel:
        """音声レベルを計算"""
        try:
            # バイトデータを数値配列に変換
            if chunk.channels == 1:
                # モノラル
                audio_array = np.frombuffer(chunk.data, dtype=np.int16)
            else:
                # ステレオ（左チャンネルのみ使用）
                audio_array = np.frombuffer(chunk.data, dtype=np.int16)[::2]

            # 正規化（-1.0 から 1.0）
            audio_normalized = audio_array.astype(np.float32) / 32768.0

            # RMS（二乗平均平方根）を計算
            rms = np.sqrt(np.mean(audio_normalized**2))

            # ピーク値を計算
            peak = np.max(np.abs(audio_normalized))

            # 音声レベル（0.0 - 1.0）
            level = min(1.0, rms * 10)  # スケーリング

            # 話者検出
            is_speaking = rms > self.speaking_threshold

            return AudioLevel(
                level=level,
                is_speaking=is_speaking,
                rms=rms,
                peak=peak,
                timestamp=chunk.timestamp,
                user_id=chunk.user_id,
            )

        except Exception as e:
            logger.error(f"Failed to calculate audio level: {e}")
            # デフォルト値を返す
            return AudioLevel(
                level=0.0,
                is_speaking=False,
                rms=0.0,
                peak=0.0,
                timestamp=chunk.timestamp,
                user_id=chunk.user_id,
            )

    async def _save_audio_chunk(self, chunk: AudioChunk):
        """音声チャンクをファイルに保存"""
        try:
            # セッション別ディレクトリを作成
            import os
            from app.config import settings

            session_dir = f"recordings/{chunk.session_id}"
            os.makedirs(session_dir, exist_ok=True)

            # ファイル名を生成
            timestamp_str = chunk.timestamp.strftime("%Y%m%d_%H%M%S")
            filename = f"{session_dir}/audio_{chunk.user_id}_{timestamp_str}_{chunk.chunk_id}.wav"

            # WAVファイルとして保存
            with wave.open(filename, "wb") as wav_file:
                wav_file.setnchannels(chunk.channels)
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(chunk.sample_rate)
                wav_file.writeframes(chunk.data)

            logger.debug(f"Saved audio chunk: {filename}")

        except Exception as e:
            logger.error(f"Failed to save audio chunk: {e}")

    async def start_recording(self, session_id: str):
        """セッションの録音を開始"""
        self.recording_sessions[session_id] = True
        logger.info(f"Started recording for session: {session_id}")

    async def stop_recording(self, session_id: str):
        """セッションの録音を停止"""
        self.recording_sessions[session_id] = False
        logger.info(f"Stopped recording for session: {session_id}")

    async def get_session_audio_levels(
        self, session_id: str, user_id: int
    ) -> List[AudioLevel]:
        """セッションの音声レベル履歴を取得"""
        if session_id not in self.audio_level_history:
            return []

        return [
            level for level in self.audio_level_history[session_id]
            if level.user_id == user_id
        ][-10:]  # 最新10件

    async def get_session_participants_audio_levels(
        self, session_id: str
    ) -> Dict[int, AudioLevel]:
        """セッション参加者の現在の音声レベルを取得"""
        if session_id not in self.audio_level_history:
            return {}

        participant_levels = {}
        
        # 最新の音声レベルを取得
        for level in self.audio_level_history[session_id][-20:]:  # 最新20件
            if level.user_id is not None:
                participant_levels[level.user_id] = level

        return participant_levels

    async def get_audio_quality_metrics(self, session_id: str) -> List[AudioQualityMetrics]:
        """音声品質メトリクスを取得"""
        return self.quality_manager.quality_history.get(session_id, [])

    async def get_buffer_stats(self, session_id: str) -> Dict[str, Any]:
        """バッファ統計を取得"""
        return await self.buffer_manager.get_buffer_stats(session_id)

    async def update_network_metrics(self, session_id: str, metrics: NetworkMetrics):
        """ネットワークメトリクスを更新"""
        self.quality_manager.update_network_metrics(session_id, metrics)

    async def clear_session_buffer(self, session_id: str):
        """セッションの音声バッファをクリア"""
        await self.buffer_manager.clear_buffer(session_id)
        if session_id in self.audio_level_history:
            self.audio_level_history[session_id].clear()
        logger.info(f"Cleared audio buffer for session: {session_id}")

    def convert_audio_format(
        self,
        audio_data: bytes,
        from_format: str,
        to_format: str,
        sample_rate: int = 16000,
    ) -> bytes:
        """音声フォーマット変換"""
        try:
            if from_format == "raw" and to_format == "wav":
                # RAW → WAV変換
                return self._raw_to_wav(audio_data, sample_rate)
            elif from_format == "wav" and to_format == "raw":
                # WAV → RAW変換
                return self._wav_to_raw(audio_data)
            else:
                logger.warning(
                    f"Unsupported format conversion: {from_format} → {to_format}"
                )
                return audio_data

        except Exception as e:
            logger.error(f"Failed to convert audio format: {e}")
            return audio_data

    def _raw_to_wav(self, raw_data: bytes, sample_rate: int) -> bytes:
        """RAW音声データをWAV形式に変換"""
        with io.BytesIO() as wav_buffer:
            with wave.open(wav_buffer, "wb") as wav_file:
                wav_file.setnchannels(1)  # モノラル
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(raw_data)
            return wav_buffer.getvalue()

    def _wav_to_raw(self, wav_data: bytes) -> bytes:
        """WAV音声データをRAW形式に変換"""
        with io.BytesIO(wav_data) as wav_buffer:
            with wave.open(wav_buffer, "rb") as wav_file:
                return wav_file.readframes(wav_file.getnframes())


# グローバル音声処理サービスインスタンス
audio_processor = AudioProcessingService()
