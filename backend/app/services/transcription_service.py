import asyncio
import structlog
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import numpy as np
from app.integrations.openai_client import openai_client
from app.models.transcription import Transcription
from app.repositories import transcription_repository
from app.schemas.transcription import TranscriptionCreate, TranscriptionResponse

logger = structlog.get_logger()


class TranscriptionQuality(str, Enum):
    """転写品質レベル"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXCELLENT = "excellent"


class SpeakerIdentification(str, Enum):
    """話者識別方法"""
    VOICE_PRINT = "voice_print"
    SPEECH_PATTERN = "speech_pattern"
    AI_ANALYSIS = "ai_analysis"


@dataclass
class TranscriptionChunk:
    """転写チャンク"""

    text: str
    start_time: float
    end_time: float
    confidence: float
    is_final: bool
    speaker_id: Optional[int] = None
    language: str = "ja"
    quality: TranscriptionQuality = TranscriptionQuality.MEDIUM
    speaker_confidence: Optional[float] = None
    words: Optional[List[Dict[str, Any]]] = None


@dataclass
class RealtimeTranscriptionStats:
    """リアルタイム転写統計"""
    
    session_id: str
    total_chunks: int = 0
    total_duration: float = 0.0
    average_confidence: float = 0.0
    unique_speakers: int = 0
    languages_detected: List[str] = None
    quality_distribution: Dict[str, int] = None
    error_count: int = 0
    last_update: datetime = None
    
    def __post_init__(self):
        if self.languages_detected is None:
            self.languages_detected = []
        if self.quality_distribution is None:
            self.quality_distribution = {quality.value: 0 for quality in TranscriptionQuality}


class RealtimeTranscriptionManager:
    """リアルタイム転写管理クラス"""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.chunk_buffers: Dict[str, List[bytes]] = {}
        self.partial_transcriptions: Dict[str, Dict[int, str]] = {}
        self.speaker_profiles: Dict[str, Dict[int, Dict[str, Any]]] = {}
        self.language_detection: Dict[str, str] = {}
        self.quality_metrics: Dict[str, List[Dict[str, Any]]] = {}
        self.stats: Dict[str, RealtimeTranscriptionStats] = {}
        
        # 設定
        self.buffer_duration = 3.0  # 3秒のバッファ
        self.min_chunk_duration = 0.5  # 最小チャンク時間
        self.max_chunk_duration = 10.0  # 最大チャンク時間
        self.partial_update_interval = 1.0  # 部分転写更新間隔
        self.speaker_confidence_threshold = 0.7  # 話者識別信頼度閾値
        
    async def start_session(self, session_id: str, initial_language: str = "ja"):
        """セッションの転写を開始"""
        self.active_sessions[session_id] = {
            "start_time": datetime.now(),
            "current_time": 0.0,
            "last_transcription": None,
            "is_active": True,
            "language": initial_language,
        }
        self.chunk_buffers[session_id] = []
        self.partial_transcriptions[session_id] = {}
        self.speaker_profiles[session_id] = {}
        self.language_detection[session_id] = initial_language
        self.quality_metrics[session_id] = []
        self.stats[session_id] = RealtimeTranscriptionStats(session_id=session_id)
        
        logger.info(f"Started realtime transcription session: {session_id}")
        
    async def stop_session(self, session_id: str):
        """セッションの転写を停止"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["is_active"] = False
        if session_id in self.chunk_buffers:
            del self.chunk_buffers[session_id]
        if session_id in self.partial_transcriptions:
            del self.partial_transcriptions[session_id]
        if session_id in self.speaker_profiles:
            del self.speaker_profiles[session_id]
        if session_id in self.language_detection:
            del self.language_detection[session_id]
        if session_id in self.quality_metrics:
            del self.quality_metrics[session_id]
        if session_id in self.stats:
            del self.stats[session_id]
            
        logger.info(f"Stopped realtime transcription session: {session_id}")

    async def process_audio_chunk(
        self,
        session_id: str,
        user_id: int,
        audio_data: bytes,
        timestamp: datetime,
        sample_rate: int = 16000,
    ) -> Tuple[Optional[TranscriptionChunk], Optional[TranscriptionChunk]]:
        """音声チャンクを処理して転写（確定と部分転写の両方を返す）"""
        try:
            if session_id not in self.active_sessions:
                return None, None
                
            session_info = self.active_sessions[session_id]
            if not session_info.get("is_active", False):
                return None, None

            # バッファに追加
            self.chunk_buffers[session_id].append(audio_data)

            # 現在時間を更新
            session_info["current_time"] = (
                timestamp - session_info["start_time"]
            ).total_seconds()

            # 部分転写を生成
            partial_chunk = await self._generate_partial_transcription(
                session_id, user_id, timestamp
            )

            # 確定転写を生成（条件を満たした場合）
            final_chunk = None
            if self._should_transcribe(session_id):
                final_chunk = await self._transcribe_buffer(session_id, user_id, timestamp)

            # 統計を更新
            await self._update_stats(session_id, final_chunk, partial_chunk)

            return final_chunk, partial_chunk

        except Exception as e:
            logger.error(f"Failed to process audio chunk for session {session_id}: {e}")
            await self._update_error_stats(session_id)
            return None, None

    async def _generate_partial_transcription(
        self, session_id: str, user_id: int, timestamp: datetime
    ) -> Optional[TranscriptionChunk]:
        """部分転写を生成"""
        try:
            buffer = self.chunk_buffers[session_id]
            if not buffer:
                return None

            # 最新のチャンクのみで部分転写
            latest_chunk = buffer[-1]
            transcription_result = await openai_client.transcribe_chunk(latest_chunk)

            if not transcription_result or not transcription_result.get("text"):
                return None

            text = transcription_result["text"].strip()
            confidence = transcription_result.get("confidence", 0.0)

            # 部分転写を保存
            self.partial_transcriptions[session_id][user_id] = text

            session_info = self.active_sessions[session_id]
            current_time = session_info["current_time"]

            return TranscriptionChunk(
                text=text,
                start_time=current_time - 0.1,
                end_time=current_time,
                confidence=confidence,
                is_final=False,
                speaker_id=user_id,
                language=self.language_detection[session_id],
                quality=self._assess_quality(confidence),
            )

        except Exception as e:
            logger.error(f"Failed to generate partial transcription: {e}")
            return None

    async def _transcribe_buffer(
        self, session_id: str, user_id: int, timestamp: datetime
    ) -> Optional[TranscriptionChunk]:
        """バッファを転写"""
        try:
            buffer = self.chunk_buffers[session_id]
            if not buffer:
                return None

            # 音声データを結合
            combined_audio = b"".join(buffer)

            # OpenAI Whisperで転写
            transcription_result = await openai_client.transcribe_audio_data(
                combined_audio
            )

            if not transcription_result or not transcription_result.get("text"):
                # バッファをクリア
                self.chunk_buffers[session_id] = []
                return None

            # 転写結果を処理
            text = transcription_result["text"].strip()
            confidence = transcription_result.get("confidence", 0.0)

            # 話者識別
            speaker_id, speaker_confidence = await self._identify_speaker(
                session_id, user_id, combined_audio
            )

            # 言語検出
            detected_language = transcription_result.get("language", "ja")
            if detected_language != self.language_detection[session_id]:
                self.language_detection[session_id] = detected_language

            # 時間情報を計算
            session_info = self.active_sessions[session_id]
            start_time = session_info["current_time"] - len(buffer) * 0.1
            end_time = session_info["current_time"]

            # バッファをクリア
            self.chunk_buffers[session_id] = []

            # 転写チャンクを作成
            chunk = TranscriptionChunk(
                text=text,
                start_time=start_time,
                end_time=end_time,
                confidence=confidence,
                is_final=True,
                speaker_id=speaker_id or user_id,
                language=detected_language,
                quality=self._assess_quality(confidence),
                speaker_confidence=speaker_confidence,
                words=transcription_result.get("words", []),
            )

            # データベースに保存
            await self._save_transcription(session_id, chunk)

            logger.info(
                f"Transcription completed for session {session_id}: {text[:50]}..."
            )
            return chunk

        except Exception as e:
            logger.error(f"Failed to transcribe buffer for session {session_id}: {e}")
            return None

    async def _identify_speaker(
        self, session_id: str, user_id: int, audio_data: bytes
    ) -> Tuple[Optional[int], Optional[float]]:
        """話者を識別"""
        try:
            # 既存の話者プロファイルを確認
            if session_id in self.speaker_profiles and user_id in self.speaker_profiles[session_id]:
                profile = self.speaker_profiles[session_id][user_id]
                confidence = profile.get("confidence", 0.0)
                
                if confidence >= self.speaker_confidence_threshold:
                    return user_id, confidence

            # 新しい話者プロファイルを作成
            # 実際の実装では、音声特徴量の分析を行う
            speaker_confidence = 0.8  # 仮の値
            
            if session_id not in self.speaker_profiles:
                self.speaker_profiles[session_id] = {}
                
            self.speaker_profiles[session_id][user_id] = {
                "confidence": speaker_confidence,
                "created_at": datetime.now(),
                "audio_samples": 1,
            }
            
            return user_id, speaker_confidence

        except Exception as e:
            logger.error(f"Failed to identify speaker: {e}")
            return None, None

    def _assess_quality(self, confidence: float) -> TranscriptionQuality:
        """転写品質を評価"""
        if confidence >= 0.9:
            return TranscriptionQuality.EXCELLENT
        elif confidence >= 0.8:
            return TranscriptionQuality.HIGH
        elif confidence >= 0.6:
            return TranscriptionQuality.MEDIUM
        else:
            return TranscriptionQuality.LOW

    async def _update_stats(
        self, 
        session_id: str, 
        final_chunk: Optional[TranscriptionChunk],
        partial_chunk: Optional[TranscriptionChunk]
    ):
        """統計を更新"""
        if session_id not in self.stats:
            return
            
        stats = self.stats[session_id]
        stats.last_update = datetime.now()
        
        if final_chunk:
            stats.total_chunks += 1
            stats.total_duration += final_chunk.end_time - final_chunk.start_time
            
            # 信頼度の平均を更新
            if stats.total_chunks == 1:
                stats.average_confidence = final_chunk.confidence
            else:
                stats.average_confidence = (
                    (stats.average_confidence * (stats.total_chunks - 1) + final_chunk.confidence)
                    / stats.total_chunks
                )
            
            # 話者数を更新
            if final_chunk.speaker_id:
                speaker_ids = set()
                for chunk in self._get_recent_chunks(session_id):
                    if chunk.speaker_id:
                        speaker_ids.add(chunk.speaker_id)
                stats.unique_speakers = len(speaker_ids)
            
            # 言語を更新
            if final_chunk.language not in stats.languages_detected:
                stats.languages_detected.append(final_chunk.language)
            
            # 品質分布を更新
            quality_key = final_chunk.quality.value
            stats.quality_distribution[quality_key] = stats.quality_distribution.get(quality_key, 0) + 1

    async def _update_error_stats(self, session_id: str):
        """エラー統計を更新"""
        if session_id in self.stats:
            self.stats[session_id].error_count += 1

    def _get_recent_chunks(self, session_id: str, limit: int = 100) -> List[TranscriptionChunk]:
        """最近の転写チャンクを取得（仮実装）"""
        # 実際の実装では、メモリまたはデータベースから取得
        return []

    def _should_transcribe(self, session_id: str) -> bool:
        """転写すべきかどうかを判定"""
        if session_id not in self.chunk_buffers:
            return False

        buffer = self.chunk_buffers[session_id]
        if not buffer:
            return False

        # バッファの合計時間を計算
        total_duration = len(buffer) * 0.1  # 100ms chunks

        # 最小時間に達しているか、最大時間を超えているか
        return (
            total_duration >= self.min_chunk_duration
            or total_duration >= self.max_chunk_duration
        )

    async def _save_transcription(self, session_id: str, chunk: TranscriptionChunk):
        """転写結果をデータベースに保存"""
        try:
            from app.core.database import get_db

            # VoiceSessionのIDを取得（仮実装）
            voice_session_id = 1  # TODO: 実際のセッションIDを取得

            transcription_data = TranscriptionCreate(
                voice_session_id=voice_session_id,
                speaker_id=chunk.speaker_id,
                text_content=chunk.text,
                start_time_seconds=chunk.start_time,
                end_time_seconds=chunk.end_time,
                confidence_score=chunk.confidence,
                language=chunk.language,
            )

            async for db in get_db():
                await transcription_repository.create(db, transcription_data)

        except Exception as e:
            logger.error(f"Failed to save transcription: {e}")

    async def get_session_transcriptions(
        self, session_id: str, limit: int = 100, offset: int = 0
    ) -> List[TranscriptionResponse]:
        """セッションの転写履歴を取得"""
        try:
            from app.core.database import get_db

            # VoiceSessionのIDを取得（仮実装）
            voice_session_id = 1  # TODO: 実際のセッションIDを取得

            async for db in get_db():
                transcriptions = await transcription_repository.get_by_session(
                    db, voice_session_id, limit, offset
                )

                return [TranscriptionResponse.from_orm(t) for t in transcriptions]

        except Exception as e:
            logger.error(f"Failed to get session transcriptions: {e}")
            return []

    async def get_realtime_transcription(
        self, session_id: str
    ) -> Optional[TranscriptionChunk]:
        """リアルタイム転写結果を取得（部分転写）"""
        try:
            if session_id not in self.chunk_buffers:
                return None

            buffer = self.chunk_buffers[session_id]
            if not buffer:
                return None

            # 最新のチャンクのみで部分転写
            latest_chunk = buffer[-1]
            transcription_result = await openai_client.transcribe_chunk(latest_chunk)

            if not transcription_result or not transcription_result.get("text"):
                return None

            text = transcription_result["text"].strip()
            confidence = transcription_result.get("confidence", 0.0)

            session_info = self.active_sessions[session_id]
            current_time = session_info["current_time"]

            return TranscriptionChunk(
                text=text,
                start_time=current_time - 0.1,
                end_time=current_time,
                confidence=confidence,
                is_final=False,
            )

        except Exception as e:
            logger.error(f"Failed to get realtime transcription: {e}")
            return None

    async def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """セッションの統計情報を取得"""
        try:
            from app.core.database import get_db

            # VoiceSessionのIDを取得（仮実装）
            voice_session_id = 1  # TODO: 実際のセッションIDを取得

            async for db in get_db():
                stats = await transcription_repository.get_session_stats(
                    db, voice_session_id
                )

                return {
                    "total_transcriptions": stats.get("total_count", 0),
                    "total_duration": stats.get("total_duration", 0.0),
                    "average_confidence": stats.get("average_confidence", 0.0),
                    "unique_speakers": stats.get("unique_speakers", 0),
                }

        except Exception as e:
            logger.error(f"Failed to get session stats: {e}")
            return {}

    async def get_realtime_stats(self, session_id: str) -> Optional[RealtimeTranscriptionStats]:
        """リアルタイム統計を取得"""
        return self.stats.get(session_id)

    async def get_partial_transcriptions(self, session_id: str) -> Dict[int, str]:
        """部分転写を取得"""
        return self.partial_transcriptions.get(session_id, {})

    async def clear_partial_transcriptions(self, session_id: str, user_id: Optional[int] = None):
        """部分転写をクリア"""
        if session_id in self.partial_transcriptions:
            if user_id is None:
                self.partial_transcriptions[session_id].clear()
            else:
                self.partial_transcriptions[session_id].pop(user_id, None)


# グローバルインスタンス
realtime_transcription_manager = RealtimeTranscriptionManager()


class TranscriptionService:
    """転写サービス（後方互換性のため残す）"""

    def __init__(self):
        self.transcription_repository = transcription_repository
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.chunk_buffers: Dict[str, List[bytes]] = {}
        self.buffer_duration = 3.0  # 3秒のバッファ
        self.min_chunk_duration = 0.5  # 最小チャンク時間
        self.max_chunk_duration = 10.0  # 最大チャンク時間

    async def process_audio_chunk(
        self,
        session_id: str,
        user_id: int,
        audio_data: bytes,
        timestamp: datetime,
        sample_rate: int = 16000,
    ) -> Optional[TranscriptionChunk]:
        """音声チャンクを処理して転写（後方互換性）"""
        final_chunk, _ = await realtime_transcription_manager.process_audio_chunk(
            session_id, user_id, audio_data, timestamp, sample_rate
        )
        return final_chunk

    def _should_transcribe(self, session_id: str) -> bool:
        """転写すべきかどうかを判定"""
        if session_id not in self.chunk_buffers:
            return False

        buffer = self.chunk_buffers[session_id]
        if not buffer:
            return False

        # バッファの合計時間を計算
        total_duration = len(buffer) * 0.1  # 100ms chunks

        # 最小時間に達しているか、最大時間を超えているか
        return (
            total_duration >= self.min_chunk_duration
            or total_duration >= self.max_chunk_duration
        )

    async def _transcribe_buffer(
        self, session_id: str, user_id: int, timestamp: datetime
    ) -> Optional[TranscriptionChunk]:
        """バッファを転写"""
        try:
            buffer = self.chunk_buffers[session_id]
            if not buffer:
                return None

            # 音声データを結合
            combined_audio = b"".join(buffer)

            # OpenAI Whisperで転写
            transcription_result = await openai_client.transcribe_audio_data(
                combined_audio
            )

            if not transcription_result or not transcription_result.get("text"):
                # バッファをクリア
                self.chunk_buffers[session_id] = []
                return None

            # 転写結果を処理
            text = transcription_result["text"].strip()
            confidence = transcription_result.get("confidence", 0.0)

            # 時間情報を計算
            session_info = self.active_sessions[session_id]
            start_time = session_info["current_time"] - len(buffer) * 0.1
            end_time = session_info["current_time"]

            # バッファをクリア
            self.chunk_buffers[session_id] = []

            # 転写チャンクを作成
            chunk = TranscriptionChunk(
                text=text,
                start_time=start_time,
                end_time=end_time,
                confidence=confidence,
                is_final=True,
                speaker_id=user_id,
            )

            # データベースに保存
            await self._save_transcription(session_id, chunk)

            logger.info(
                f"Transcription completed for session {session_id}: {text[:50]}..."
            )
            return chunk

        except Exception as e:
            logger.error(f"Failed to transcribe buffer for session {session_id}: {e}")
            return None

    async def _save_transcription(self, session_id: str, chunk: TranscriptionChunk):
        """転写結果をデータベースに保存"""
        try:
            from app.core.database import get_db

            # VoiceSessionのIDを取得（仮実装）
            voice_session_id = 1  # TODO: 実際のセッションIDを取得

            transcription_data = TranscriptionCreate(
                voice_session_id=voice_session_id,
                speaker_id=chunk.speaker_id,
                text_content=chunk.text,
                start_time_seconds=chunk.start_time,
                end_time_seconds=chunk.end_time,
                confidence_score=chunk.confidence,
                language=chunk.language,
            )

            async for db in get_db():
                await self.transcription_repository.create(db, transcription_data)

        except Exception as e:
            logger.error(f"Failed to save transcription: {e}")

    async def get_session_transcriptions(
        self, session_id: str, limit: int = 100, offset: int = 0
    ) -> List[TranscriptionResponse]:
        """セッションの転写履歴を取得"""
        try:
            from app.core.database import get_db

            # VoiceSessionのIDを取得（仮実装）
            voice_session_id = 1  # TODO: 実際のセッションIDを取得

            async for db in get_db():
                transcriptions = await self.transcription_repository.get_by_session(
                    db, voice_session_id, limit, offset
                )

                return [TranscriptionResponse.from_orm(t) for t in transcriptions]

        except Exception as e:
            logger.error(f"Failed to get session transcriptions: {e}")
            return []

    async def get_realtime_transcription(
        self, session_id: str
    ) -> Optional[TranscriptionChunk]:
        """リアルタイム転写結果を取得（部分転写）"""
        try:
            if session_id not in self.chunk_buffers:
                return None

            buffer = self.chunk_buffers[session_id]
            if not buffer:
                return None

            # 最新のチャンクのみで部分転写
            latest_chunk = buffer[-1]
            transcription_result = await openai_client.transcribe_chunk(latest_chunk)

            if not transcription_result or not transcription_result.get("text"):
                return None

            text = transcription_result["text"].strip()
            confidence = transcription_result.get("confidence", 0.0)

            session_info = self.active_sessions[session_id]
            current_time = session_info["current_time"]

            return TranscriptionChunk(
                text=text,
                start_time=current_time - 0.1,
                end_time=current_time,
                confidence=confidence,
                is_final=False,
            )

        except Exception as e:
            logger.error(f"Failed to get realtime transcription: {e}")
            return None

    async def start_session(self, session_id: str):
        """セッションの転写を開始"""
        await realtime_transcription_manager.start_session(session_id)
        self.active_sessions[session_id] = {
            "start_time": datetime.now(),
            "current_time": 0.0,
            "last_transcription": None,
        }
        self.chunk_buffers[session_id] = []
        logger.info(f"Started transcription session: {session_id}")

    async def stop_session(self, session_id: str):
        """セッションの転写を停止"""
        await realtime_transcription_manager.stop_session(session_id)
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        if session_id in self.chunk_buffers:
            del self.chunk_buffers[session_id]
        logger.info(f"Stopped transcription session: {session_id}")

    async def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """セッションの統計情報を取得"""
        try:
            from app.core.database import get_db

            # VoiceSessionのIDを取得（仮実装）
            voice_session_id = 1  # TODO: 実際のセッションIDを取得

            async for db in get_db():
                stats = await self.transcription_repository.get_session_stats(
                    db, voice_session_id
                )

                return {
                    "total_transcriptions": stats.get("total_count", 0),
                    "total_duration": stats.get("total_duration", 0.0),
                    "average_confidence": stats.get("average_confidence", 0.0),
                    "unique_speakers": stats.get("unique_speakers", 0),
                }

        except Exception as e:
            logger.error(f"Failed to get session stats: {e}")
            return {}


# グローバルインスタンス
transcription_service = TranscriptionService()
