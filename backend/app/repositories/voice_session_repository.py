from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from datetime import datetime
import structlog

from app.models.voice_session import VoiceSession
from app.models.user import User
from app.schemas.voice_session import (
    VoiceSessionCreate,
    VoiceSessionUpdate,
    VoiceSessionFilters,
)
from .base import BaseRepository

logger = structlog.get_logger()


class VoiceSessionRepository(
    BaseRepository[VoiceSession, VoiceSessionCreate, VoiceSessionUpdate]
):
    """音声セッションリポジトリ"""

    def __init__(self):
        super().__init__(VoiceSession)

    async def get_by_session_id(
        self, db: AsyncSession, session_id: str
    ) -> Optional[VoiceSession]:
        """セッションIDで音声セッションを取得"""
        try:
            query = select(self.model).where(self.model.session_id == session_id)
            result = await db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting voice session by session_id {session_id}: {e}")
            raise

    async def get_by_user_id(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[VoiceSessionFilters] = None,
    ) -> List[VoiceSession]:
        """ユーザーIDで音声セッション一覧を取得"""
        try:
            query = select(self.model).where(self.model.user_id == user_id)

            # フィルター適用
            if filters:
                query = self._apply_filters(query, filters)

            query = (
                query.offset(skip).limit(limit).order_by(self.model.created_at.desc())
            )
            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting voice sessions by user_id {user_id}: {e}")
            raise

    async def get_by_team_id(
        self,
        db: AsyncSession,
        team_id: int,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[VoiceSessionFilters] = None,
    ) -> List[VoiceSession]:
        """チームIDで音声セッション一覧を取得"""
        try:
            query = select(self.model).where(self.model.team_id == team_id)

            # フィルター適用
            if filters:
                query = self._apply_filters(query, filters)

            query = (
                query.offset(skip).limit(limit).order_by(self.model.created_at.desc())
            )
            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting voice sessions by team_id {team_id}: {e}")
            raise

    async def get_public_sessions(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[VoiceSessionFilters] = None,
    ) -> List[VoiceSession]:
        """公開音声セッション一覧を取得"""
        try:
            query = select(self.model).where(self.model.is_public == True)

            # フィルター適用
            if filters:
                query = self._apply_filters(query, filters)

            query = (
                query.offset(skip).limit(limit).order_by(self.model.created_at.desc())
            )
            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting public voice sessions: {e}")
            raise

    async def search_sessions(
        self,
        db: AsyncSession,
        search_term: str,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[VoiceSession]:
        """音声セッションを検索"""
        try:
            query = select(self.model)

            # 検索条件
            search_conditions = or_(
                self.model.title.ilike(f"%{search_term}%"),
                self.model.description.ilike(f"%{search_term}%"),
                self.model.session_id.ilike(f"%{search_term}%"),
            )
            query = query.where(search_conditions)

            # ユーザーIDでフィルター
            if user_id:
                query = query.where(self.model.user_id == user_id)

            query = (
                query.offset(skip).limit(limit).order_by(self.model.created_at.desc())
            )
            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(
                f"Error searching voice sessions with term '{search_term}': {e}"
            )
            raise

    async def get_session_with_relations(
        self, db: AsyncSession, session_id: int
    ) -> Optional[VoiceSession]:
        """関連データを含む音声セッションを取得"""
        try:
            query = (
                select(self.model)
                .options(
                    selectinload(self.model.user),
                    selectinload(self.model.team),
                    selectinload(self.model.transcriptions),
                    selectinload(self.model.analyses),
                )
                .where(self.model.id == session_id)
            )
            result = await db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(
                f"Error getting voice session with relations {session_id}: {e}"
            )
            raise

    async def update_audio_info(
        self,
        db: AsyncSession,
        session_id: int,
        audio_file_path: str,
        audio_duration: float,
        audio_format: str,
        file_size: int,
    ) -> Optional[VoiceSession]:
        """音声ファイル情報を更新"""
        try:
            update_data = {
                "audio_file_path": audio_file_path,
                "audio_duration": audio_duration,
                "audio_format": audio_format,
                "file_size": file_size,
            }

            query = select(self.model).where(self.model.id == session_id)
            result = await db.execute(query)
            session = result.scalar_one_or_none()

            if session:
                for field, value in update_data.items():
                    setattr(session, field, value)

                db.add(session)
                await db.commit()
                await db.refresh(session)

            return session
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating audio info for session {session_id}: {e}")
            raise

    async def update_analysis_info(
        self,
        db: AsyncSession,
        session_id: int,
        analysis_summary: str,
        sentiment_score: float,
        key_topics: str,
    ) -> Optional[VoiceSession]:
        """分析情報を更新"""
        try:
            update_data = {
                "analysis_summary": analysis_summary,
                "sentiment_score": sentiment_score,
                "key_topics": key_topics,
                "is_analyzed": True,
            }

            query = select(self.model).where(self.model.id == session_id)
            result = await db.execute(query)
            session = result.scalar_one_or_none()

            if session:
                for field, value in update_data.items():
                    setattr(session, field, value)

                db.add(session)
                await db.commit()
                await db.refresh(session)

            return session
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating analysis info for session {session_id}: {e}")
            raise

    async def get_user_stats(self, db: AsyncSession, user_id: int) -> Dict[str, Any]:
        """ユーザーの音声セッション統計を取得"""
        try:
            # 総セッション数
            total_query = select(func.count(self.model.id)).where(
                self.model.user_id == user_id
            )
            total_result = await db.execute(total_query)
            total_sessions = total_result.scalar()

            # 完了セッション数
            completed_query = select(func.count(self.model.id)).where(
                and_(self.model.user_id == user_id, self.model.status == "completed")
            )
            completed_result = await db.execute(completed_query)
            completed_sessions = completed_result.scalar()

            # 分析済みセッション数
            analyzed_query = select(func.count(self.model.id)).where(
                and_(self.model.user_id == user_id, self.model.is_analyzed == True)
            )
            analyzed_result = await db.execute(analyzed_query)
            analyzed_sessions = analyzed_result.scalar()

            # 総音声時間
            duration_query = select(func.sum(self.model.audio_duration)).where(
                and_(
                    self.model.user_id == user_id, self.model.audio_duration.isnot(None)
                )
            )
            duration_result = await db.execute(duration_query)
            total_duration = duration_result.scalar() or 0.0

            return {
                "total_sessions": total_sessions,
                "completed_sessions": completed_sessions,
                "analyzed_sessions": analyzed_sessions,
                "total_duration": total_duration,
                "average_duration": total_duration / total_sessions
                if total_sessions > 0
                else 0.0,
            }
        except Exception as e:
            logger.error(f"Error getting user stats for user_id {user_id}: {e}")
            raise

    def _apply_filters(self, query, filters: VoiceSessionFilters):
        """フィルターを適用"""
        if filters.status:
            query = query.where(self.model.status == filters.status)

        if filters.is_public is not None:
            query = query.where(self.model.is_public == filters.is_public)

        if filters.is_analyzed is not None:
            query = query.where(self.model.is_analyzed == filters.is_analyzed)

        if filters.date_from:
            query = query.where(self.model.created_at >= filters.date_from)

        if filters.date_to:
            query = query.where(self.model.created_at <= filters.date_to)

        if filters.search:
            search_conditions = or_(
                self.model.title.ilike(f"%{filters.search}%"),
                self.model.description.ilike(f"%{filters.search}%"),
                self.model.session_id.ilike(f"%{filters.search}%"),
            )
            query = query.where(search_conditions)

        return query

    async def session_exists_by_session_id(
        self, db: AsyncSession, session_id: str
    ) -> bool:
        """セッションIDの存在確認"""
        try:
            query = select(self.model).where(self.model.session_id == session_id)
            result = await db.execute(query)
            return result.scalar_one_or_none() is not None
        except Exception as e:
            logger.error(
                f"Error checking session existence by session_id {session_id}: {e}"
            )
            raise


# グローバルインスタンス
voice_session_repository = VoiceSessionRepository()
