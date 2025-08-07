from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import selectinload
import structlog

from app.repositories.base import BaseRepository
from app.models.transcription import Transcription
from app.schemas.transcription import TranscriptionCreate, TranscriptionUpdate

logger = structlog.get_logger()


class TranscriptionRepository(BaseRepository[Transcription]):
    """転写リポジトリ"""

    def __init__(self):
        super().__init__(Transcription)

    async def create(
        self, db: AsyncSession, transcription_data: TranscriptionCreate
    ) -> Transcription:
        """転写データを作成"""
        try:
            transcription = Transcription(
                voice_session_id=transcription_data.voice_session_id,
                speaker_id=transcription_data.speaker_id,
                text_content=transcription_data.text_content,
                start_time_seconds=transcription_data.start_time_seconds,
                end_time_seconds=transcription_data.end_time_seconds,
                confidence_score=transcription_data.confidence_score,
                language=transcription_data.language,
                is_final=transcription_data.is_final,
                is_processed=transcription_data.is_processed,
                word_timestamps=transcription_data.word_timestamps,
                speaker_confidence=transcription_data.speaker_confidence,
            )

            db.add(transcription)
            await db.commit()
            await db.refresh(transcription)

            logger.info(f"Created transcription: {transcription.id}")
            return transcription

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create transcription: {e}")
            raise

    async def get_by_session(
        self, db: AsyncSession, voice_session_id: int, limit: int = 100, offset: int = 0
    ) -> List[Transcription]:
        """セッションの転写データを取得"""
        try:
            query = (
                select(Transcription)
                .where(Transcription.voice_session_id == voice_session_id)
                .order_by(Transcription.start_time_seconds)
                .limit(limit)
                .offset(offset)
            )

            result = await db.execute(query)
            transcriptions = result.scalars().all()

            return transcriptions

        except Exception as e:
            logger.error(f"Failed to get transcriptions by session: {e}")
            return []

    async def get_by_speaker(
        self,
        db: AsyncSession,
        speaker_id: int,
        voice_session_id: Optional[int] = None,
        limit: int = 100,
    ) -> List[Transcription]:
        """話者の転写データを取得"""
        try:
            query = select(Transcription).where(Transcription.speaker_id == speaker_id)

            if voice_session_id:
                query = query.where(Transcription.voice_session_id == voice_session_id)

            query = query.order_by(desc(Transcription.created_at)).limit(limit)

            result = await db.execute(query)
            transcriptions = result.scalars().all()

            return transcriptions

        except Exception as e:
            logger.error(f"Failed to get transcriptions by speaker: {e}")
            return []

    async def get_final_transcriptions(
        self, db: AsyncSession, voice_session_id: int
    ) -> List[Transcription]:
        """確定転写データを取得"""
        try:
            query = (
                select(Transcription)
                .where(
                    and_(
                        Transcription.voice_session_id == voice_session_id,
                        Transcription.is_final == True,
                    )
                )
                .order_by(Transcription.start_time_seconds)
            )

            result = await db.execute(query)
            transcriptions = result.scalars().all()

            return transcriptions

        except Exception as e:
            logger.error(f"Failed to get final transcriptions: {e}")
            return []

    async def get_session_stats(
        self, db: AsyncSession, voice_session_id: int
    ) -> Dict[str, Any]:
        """セッションの統計情報を取得"""
        try:
            # 総転写数
            total_count_query = select(func.count(Transcription.id)).where(
                Transcription.voice_session_id == voice_session_id
            )
            total_count_result = await db.execute(total_count_query)
            total_count = total_count_result.scalar()

            # 総継続時間
            total_duration_query = select(
                func.sum(
                    Transcription.end_time_seconds - Transcription.start_time_seconds
                )
            ).where(Transcription.voice_session_id == voice_session_id)
            total_duration_result = await db.execute(total_duration_query)
            total_duration = total_duration_result.scalar() or 0.0

            # 平均信頼度
            avg_confidence_query = select(
                func.avg(Transcription.confidence_score)
            ).where(Transcription.voice_session_id == voice_session_id)
            avg_confidence_result = await db.execute(avg_confidence_query)
            avg_confidence = avg_confidence_result.scalar() or 0.0

            # 話者数
            unique_speakers_query = select(
                func.count(func.distinct(Transcription.speaker_id))
            ).where(Transcription.voice_session_id == voice_session_id)
            unique_speakers_result = await db.execute(unique_speakers_query)
            unique_speakers = unique_speakers_result.scalar() or 0

            return {
                "total_count": total_count,
                "total_duration": float(total_duration),
                "average_confidence": float(avg_confidence),
                "unique_speakers": unique_speakers,
            }

        except Exception as e:
            logger.error(f"Failed to get session stats: {e}")
            return {
                "total_count": 0,
                "total_duration": 0.0,
                "average_confidence": 0.0,
                "unique_speakers": 0,
            }

    async def search_transcriptions(
        self, db: AsyncSession, voice_session_id: int, search_text: str, limit: int = 50
    ) -> List[Transcription]:
        """転写テキストを検索"""
        try:
            query = (
                select(Transcription)
                .where(
                    and_(
                        Transcription.voice_session_id == voice_session_id,
                        Transcription.text_content.ilike(f"%{search_text}%"),
                    )
                )
                .order_by(Transcription.start_time_seconds)
                .limit(limit)
            )

            result = await db.execute(query)
            transcriptions = result.scalars().all()

            return transcriptions

        except Exception as e:
            logger.error(f"Failed to search transcriptions: {e}")
            return []

    async def update_transcription(
        self, db: AsyncSession, transcription_id: int, update_data: TranscriptionUpdate
    ) -> Optional[Transcription]:
        """転写データを更新"""
        try:
            transcription = await self.get_by_id(db, transcription_id)
            if not transcription:
                return None

            # 更新可能なフィールドを更新
            for field, value in update_data.dict(exclude_unset=True).items():
                setattr(transcription, field, value)

            await db.commit()
            await db.refresh(transcription)

            logger.info(f"Updated transcription: {transcription_id}")
            return transcription

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to update transcription: {e}")
            raise

    async def delete_transcription(
        self, db: AsyncSession, transcription_id: int
    ) -> bool:
        """転写データを削除"""
        try:
            transcription = await self.get_by_id(db, transcription_id)
            if not transcription:
                return False

            await db.delete(transcription)
            await db.commit()

            logger.info(f"Deleted transcription: {transcription_id}")
            return True

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to delete transcription: {e}")
            return False


# グローバルインスタンス
transcription_repository = TranscriptionRepository()
