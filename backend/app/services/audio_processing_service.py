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

from app.core.exceptions import ValidationException
from app.schemas.websocket import AudioDataMessage

logger = structlog.get_logger()


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


class AudioProcessingService:
    """音声データ処理サービス"""

    def __init__(self):
        # 音声設定
        self.default_sample_rate = 16000
        self.default_channels = 1
        self.chunk_duration_ms = 100  # 100ms chunks
        self.speaking_threshold = 0.01  # 話者検出閾値

        # 音声バッファ
        self.audio_buffers: Dict[str, List[AudioChunk]] = {}
        self.recording_sessions: Dict[str, bool] = {}

    async def process_audio_data(self, audio_message: AudioDataMessage) -> AudioChunk:
        """音声データを処理"""
        try:
            # Base64デコード
            audio_data = self._decode_audio_data(audio_message.data)

            # 音声データの検証
            self._validate_audio_data(audio_data, audio_message)

            # 音声チャンクを作成
            chunk = AudioChunk(
                data=audio_data,
                sample_rate=audio_message.sample_rate or self.default_sample_rate,
                channels=audio_message.channels or self.default_channels,
                timestamp=datetime.fromisoformat(audio_message.timestamp),
                chunk_id=audio_message.chunk_id
                or f"chunk_{int(datetime.now().timestamp() * 1000)}",
                user_id=audio_message.user_id,
                session_id=audio_message.session_id,
            )

            # 音声レベルを計算
            audio_level = self._calculate_audio_level(chunk)

            # バッファに追加
            await self._add_to_buffer(chunk)

            # 録音中なら保存
            if self.recording_sessions.get(audio_message.session_id, False):
                await self._save_audio_chunk(chunk)

            logger.debug(
                f"Processed audio chunk: {chunk.chunk_id}",
                user_id=chunk.user_id,
                session_id=chunk.session_id,
                level=audio_level.level,
                is_speaking=audio_level.is_speaking,
            )

            return chunk

        except Exception as e:
            logger.error(f"Failed to process audio data: {e}")
            raise ValidationException("Invalid audio data")

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
            )

    async def _add_to_buffer(self, chunk: AudioChunk):
        """音声チャンクをバッファに追加"""
        session_id = chunk.session_id

        if session_id not in self.audio_buffers:
            self.audio_buffers[session_id] = []

        # バッファに追加
        self.audio_buffers[session_id].append(chunk)

        # バッファサイズ制限（最新100チャンクまで保持）
        if len(self.audio_buffers[session_id]) > 100:
            self.audio_buffers[session_id] = self.audio_buffers[session_id][-100:]

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
        if session_id not in self.audio_buffers:
            return []

        user_chunks = [
            chunk
            for chunk in self.audio_buffers[session_id]
            if chunk.user_id == user_id
        ]

        levels = []
        for chunk in user_chunks[-10:]:  # 最新10チャンク
            level = self._calculate_audio_level(chunk)
            levels.append(level)

        return levels

    async def get_session_participants_audio_levels(
        self, session_id: str
    ) -> Dict[int, AudioLevel]:
        """セッション参加者の現在の音声レベルを取得"""
        if session_id not in self.audio_buffers:
            return {}

        participant_levels = {}

        # 各参加者の最新チャンクを取得
        for chunk in self.audio_buffers[session_id][-20:]:  # 最新20チャンク
            if chunk.user_id not in participant_levels:
                level = self._calculate_audio_level(chunk)
                participant_levels[chunk.user_id] = level

        return participant_levels

    async def clear_session_buffer(self, session_id: str):
        """セッションの音声バッファをクリア"""
        if session_id in self.audio_buffers:
            del self.audio_buffers[session_id]
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
