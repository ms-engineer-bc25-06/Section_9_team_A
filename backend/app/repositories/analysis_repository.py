from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.repositories.base import BaseRepository
from app.models.analysis import Analysis
from app.schemas.analysis import AnalysisCreate, AnalysisUpdate, AnalysisQueryParams


class AnalysisRepository(BaseRepository[Analysis, AnalysisCreate, AnalysisUpdate]):
    """AI分析リポジトリ"""

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: AnalysisCreate,
        analysis_id: str,
    ) -> Analysis:
        """分析を作成"""
        db_obj = Analysis(
            analysis_id=analysis_id,
            analysis_type=obj_in.analysis_type,
            title=obj_in.title,
            content=obj_in.content,
            summary=obj_in.summary,
            keywords=obj_in.keywords,
            topics=obj_in.topics,
            sentiment_score=obj_in.sentiment_score,
            sentiment_label=obj_in.sentiment_label,
            word_count=obj_in.word_count,
            sentence_count=obj_in.sentence_count,
            speaking_time=obj_in.speaking_time,
            status=obj_in.status,
            confidence_score=obj_in.confidence_score,
            voice_session_id=obj_in.voice_session_id,
            transcription_id=obj_in.transcription_id,
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
        query_params: AnalysisQueryParams,
    ) -> Tuple[List[Analysis], int]:
        """分析一覧を取得"""
        # クエリの構築
        query = select(Analysis)
        count_query = select(func.count(Analysis.id))

        # フィルターの適用
        if query_params.analysis_type:
            query = query.where(Analysis.analysis_type == query_params.analysis_type)
            count_query = count_query.where(Analysis.analysis_type == query_params.analysis_type)

        if query_params.user_id:
            query = query.where(Analysis.user_id == query_params.user_id)
            count_query = count_query.where(Analysis.user_id == query_params.user_id)

        if query_params.voice_session_id:
            query = query.where(Analysis.voice_session_id == query_params.voice_session_id)
            count_query = count_query.where(Analysis.voice_session_id == query_params.voice_session_id)

        if query_params.transcription_id:
            query = query.where(Analysis.transcription_id == query_params.transcription_id)
            count_query = count_query.where(Analysis.transcription_id == query_params.transcription_id)

        if query_params.status:
            query = query.where(Analysis.status == query_params.status)
            count_query = count_query.where(Analysis.status == query_params.status)

        if query_params.sentiment_label:
            query = query.where(Analysis.sentiment_label == query_params.sentiment_label)
            count_query = count_query.where(Analysis.sentiment_label == query_params.sentiment_label)

        # 総件数を取得
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # ページネーションの適用
        offset = (query_params.page - 1) * query_params.size
        query = query.offset(offset).limit(query_params.size)

        # 結果を取得
        result = await db.execute(query)
        analyses = result.scalars().all()

        return analyses, total

    async def get_by_voice_session(
        self,
        db: AsyncSession,
        *,
        voice_session_id: int,
    ) -> List[Analysis]:
        """音声セッションIDで分析を取得"""
        query = select(Analysis).where(
            Analysis.voice_session_id == voice_session_id
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_transcription(
        self,
        db: AsyncSession,
        *,
        transcription_id: int,
    ) -> List[Analysis]:
        """文字起こしIDで分析を取得"""
        query = select(Analysis).where(
            Analysis.transcription_id == transcription_id
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_user(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        limit: int = 100,
    ) -> List[Analysis]:
        """ユーザーIDで分析を取得"""
        query = select(Analysis).where(
            Analysis.user_id == user_id
        ).order_by(Analysis.created_at.desc()).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_type(
        self,
        db: AsyncSession,
        *,
        analysis_type: str,
        limit: int = 100,
    ) -> List[Analysis]:
        """分析タイプで分析を取得"""
        query = select(Analysis).where(
            Analysis.analysis_type == analysis_type
        ).order_by(Analysis.created_at.desc()).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_sentiment_analyses(
        self,
        db: AsyncSession,
        *,
        user_id: Optional[int] = None,
        limit: int = 100,
    ) -> List[Analysis]:
        """感情分析結果を取得"""
        query = select(Analysis).where(
            Analysis.analysis_type == "sentiment"
        )
        
        if user_id:
            query = query.where(Analysis.user_id == user_id)
        
        query = query.order_by(Analysis.created_at.desc()).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()


# シングルトンインスタンス
analysis_repository = AnalysisRepository(Analysis)
