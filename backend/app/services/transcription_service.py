import asyncio
import structlog
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from app.integrations.openai_client import openai_client
from app.models.transcription import Transcription
from app.repositories.transcription_repository import TranscriptionRepository
from app.schemas.transcription import TranscriptionCreate, TranscriptionResponse

logger = structlog.get_logger()


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


class TranscriptionService:
    """転写サービス"""

    def __init__(self):
        self.transcription_repository = TranscriptionRepository()
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
        """音声チャンクを処理して転写"""
        try:
            # セッションの初期化
            if session_id not in self.active_sessions:
                self.active_sessions[session_id] = {
                    "start_time": timestamp,
                    "current_time": 0.0,
                    "last_transcription": None,
                }
                self.chunk_buffers[session_id] = []

            # バッファに追加
            self.chunk_buffers[session_id].append(audio_data)

            # 現在時間を更新
            session_info = self.active_sessions[session_id]
            session_info["current_time"] = (
                timestamp - session_info["start_time"]
            ).total_seconds()

            # バッファが十分な長さになったら転写
            if self._should_transcribe(session_id):
                return await self._transcribe_buffer(session_id, user_id, timestamp)

            return None

        except Exception as e:
            logger.error(f"Failed to process audio chunk for session {session_id}: {e}")
            return None

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
        self.active_sessions[session_id] = {
            "start_time": datetime.now(),
            "current_time": 0.0,
            "last_transcription": None,
        }
        self.chunk_buffers[session_id] = []
        logger.info(f"Started transcription session: {session_id}")

    async def stop_session(self, session_id: str):
        """セッションの転写を停止"""
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
