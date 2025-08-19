from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.repositories.base import BaseRepository
from app.models.transcription import Transcription
from app.schemas.transcription import TranscriptionCreate, TranscriptionUpdate, TranscriptionQueryParams


class TranscriptionRepository(BaseRepository[Transcription, TranscriptionCreate, TranscriptionUpdate]):
    """文字起こしリポジトリ"""

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: TranscriptionCreate,
        transcription_id: str,
    ) -> Transcription:
        """文字起こしを作成"""
        db_obj = Transcription(
            transcription_id=transcription_id,
            content=obj_in.content,
            language=obj_in.language,
            audio_file_path=obj_in.audio_file_path,
            audio_duration=obj_in.audio_duration,
            audio_format=obj_in.audio_format,
            confidence_score=obj_in.confidence_score,
            speaker_count=obj_in.speaker_count,
            speakers=obj_in.speakers,
            status=obj_in.status,
            is_edited=obj_in.is_edited,
            voice_session_id=obj_in.voice_session_id,
            user_id=obj_in.user_id,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        query_params: TranscriptionQueryParams,
    ) -> Tuple[List[Transcription], int]:
        """文字起こし一覧を取得"""
        # クエリの構築
        query = select(Transcription)
        count_query = select(func.count(Transcription.id))

        # フィルターの適用
        if query_params.voice_session_id:
            query = query.where(Transcription.voice_session_id == query_params.voice_session_id)
            count_query = count_query.where(Transcription.voice_session_id == query_params.voice_session_id)

        if query_params.user_id:
            query = query.where(Transcription.user_id == query_params.user_id)
            count_query = count_query.where(Transcription.user_id == query_params.user_id)

        if query_params.status:
            query = query.where(Transcription.status == query_params.status)
            count_query = count_query.where(Transcription.status == query_params.status)

        if query_params.language:
            query = query.where(Transcription.language == query_params.language)
            count_query = count_query.where(Transcription.language == query_params.language)

        if query_params.is_edited is not None:
            query = query.where(Transcription.is_edited == query_params.is_edited)
            count_query = count_query.where(Transcription.is_edited == query_params.is_edited)

        # 総件数を取得
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # ページネーションの適用
        offset = (query_params.page - 1) * query_params.size
        query = query.offset(offset).limit(query_params.size)

        # 結果を取得
        result = await db.execute(query)
        transcriptions = result.scalars().all()

        return transcriptions, total

    async def get_by_voice_session(
        self,
        db: AsyncSession,
        *,
        voice_session_id: int,
    ) -> List[Transcription]:
        """音声セッションIDで文字起こしを取得"""
        query = select(Transcription).where(
            Transcription.voice_session_id == voice_session_id
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_user(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        limit: int = 100,
    ) -> List[Transcription]:
        """ユーザーIDで文字起こしを取得"""
        query = select(Transcription).where(
            Transcription.user_id == user_id
        ).order_by(Transcription.created_at.desc()).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()


# シングルトンインスタンス
transcription_repository = TranscriptionRepository(Transcription)
