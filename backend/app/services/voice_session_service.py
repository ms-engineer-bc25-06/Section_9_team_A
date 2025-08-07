from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from datetime import datetime
import uuid

from app.models.voice_session import VoiceSession
from app.models.user import User
from app.repositories.voice_session_repository import VoiceSessionRepository
from app.schemas.voice_session import (
    VoiceSessionCreate,
    VoiceSessionUpdate,
    VoiceSessionResponse,
    VoiceSessionListResponse,
    VoiceSessionDetailResponse,
    VoiceSessionFilters,
    VoiceSessionQueryParams,
    VoiceSessionStats,
    VoiceSessionAudioUpdate,
)
from app.core.exceptions import (
    NotFoundException,
    ValidationException,
    PermissionException,
)

logger = structlog.get_logger()


class VoiceSessionService:
    """音声セッションサービス"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = VoiceSessionRepository()

    async def create_session(
        self, user_id: int, session_data: VoiceSessionCreate
    ) -> VoiceSessionResponse:
        """音声セッションを作成"""
        try:
            # セッションIDの重複チェック
            if await self.repository.session_exists_by_session_id(
                self.db, session_data.session_id
            ):
                raise ValidationException("Session ID already exists")

            # ユーザー存在チェック
            user = await self._get_user_by_id(user_id)
            if not user:
                raise NotFoundException("User not found")

            # セッション作成
            session = await self.repository.create(self.db, obj_in=session_data)

            # レスポンス形式に変換
            return VoiceSessionResponse.model_validate(session)

        except (ValidationException, NotFoundException):
            raise
        except Exception as e:
            logger.error(f"Failed to create voice session: {e}")
            raise ValidationException("Failed to create voice session")

    async def get_session_by_id(
        self, session_id: int, user_id: int
    ) -> VoiceSessionDetailResponse:
        """音声セッション詳細を取得"""
        try:
            session = await self.repository.get_session_with_relations(
                self.db, session_id
            )

            if not session:
                raise NotFoundException("Voice session not found")

            # 権限チェック
            if session.user_id != user_id and not session.is_public:
                raise PermissionException("Access denied")

            # 詳細レスポンス形式に変換
            response = VoiceSessionDetailResponse.model_validate(session)

            # 関連データの件数を設定
            response.transcriptions_count = len(session.transcriptions)
            response.analyses_count = len(session.analyses)

            return response

        except (NotFoundException, PermissionException):
            raise
        except Exception as e:
            logger.error(f"Failed to get voice session {session_id}: {e}")
            raise NotFoundException("Failed to get voice session")

    async def get_user_sessions(
        self, user_id: int, query_params: VoiceSessionQueryParams
    ) -> VoiceSessionListResponse:
        """ユーザーの音声セッション一覧を取得"""
        try:
            # フィルター作成
            filters = VoiceSessionFilters(
                status=query_params.status,
                is_public=query_params.is_public,
                is_analyzed=query_params.is_analyzed,
                date_from=query_params.date_from,
                date_to=query_params.date_to,
                search=query_params.search,
            )

            # セッション一覧取得
            sessions = await self.repository.get_by_user_id(
                self.db,
                user_id=user_id,
                skip=(query_params.page - 1) * query_params.size,
                limit=query_params.size,
                filters=filters,
            )

            # 総件数取得
            total = await self.repository.count(self.db, filters={"user_id": user_id})

            # レスポンス形式に変換
            session_responses = [
                VoiceSessionResponse.model_validate(session) for session in sessions
            ]

            return VoiceSessionListResponse(
                sessions=session_responses,
                total=total,
                page=query_params.page,
                size=query_params.size,
                pages=(total + query_params.size - 1) // query_params.size,
            )

        except Exception as e:
            logger.error(f"Failed to get user sessions for user {user_id}: {e}")
            raise ValidationException("Failed to get user sessions")

    async def get_team_sessions(
        self, team_id: int, user_id: int, query_params: VoiceSessionQueryParams
    ) -> VoiceSessionListResponse:
        """チームの音声セッション一覧を取得"""
        try:
            # チームメンバー権限チェック（簡易版）
            # TODO: チームサービスと連携して権限チェックを実装

            # フィルター作成
            filters = VoiceSessionFilters(
                status=query_params.status,
                is_public=query_params.is_public,
                is_analyzed=query_params.is_analyzed,
                date_from=query_params.date_from,
                date_to=query_params.date_to,
                search=query_params.search,
            )

            # セッション一覧取得
            sessions = await self.repository.get_by_team_id(
                self.db,
                team_id=team_id,
                skip=(query_params.page - 1) * query_params.size,
                limit=query_params.size,
                filters=filters,
            )

            # 総件数取得
            total = await self.repository.count(self.db, filters={"team_id": team_id})

            # レスポンス形式に変換
            session_responses = [
                VoiceSessionResponse.model_validate(session) for session in sessions
            ]

            return VoiceSessionListResponse(
                sessions=session_responses,
                total=total,
                page=query_params.page,
                size=query_params.size,
                pages=(total + query_params.size - 1) // query_params.size,
            )

        except Exception as e:
            logger.error(f"Failed to get team sessions for team {team_id}: {e}")
            raise ValidationException("Failed to get team sessions")

    async def update_session(
        self, session_id: int, user_id: int, update_data: VoiceSessionUpdate
    ) -> VoiceSessionResponse:
        """音声セッションを更新"""
        try:
            # セッション取得
            session = await self.repository.get(self.db, session_id)
            if not session:
                raise NotFoundException("Voice session not found")

            # 権限チェック
            if session.user_id != user_id:
                raise PermissionException("Access denied")

            # 更新
            updated_session = await self.repository.update(
                self.db, db_obj=session, obj_in=update_data
            )

            return VoiceSessionResponse.model_validate(updated_session)

        except (NotFoundException, PermissionException):
            raise
        except Exception as e:
            logger.error(f"Failed to update voice session {session_id}: {e}")
            raise ValidationException("Failed to update voice session")

    async def update_audio_info(
        self, session_id: int, user_id: int, audio_data: VoiceSessionAudioUpdate
    ) -> VoiceSessionResponse:
        """音声ファイル情報を更新"""
        try:
            # セッション取得
            session = await self.repository.get(self.db, session_id)
            if not session:
                raise NotFoundException("Voice session not found")

            # 権限チェック
            if session.user_id != user_id:
                raise PermissionException("Access denied")

            # 音声情報更新
            updated_session = await self.repository.update_audio_info(
                self.db,
                session_id=session_id,
                audio_file_path=audio_data.audio_file_path,
                audio_duration=audio_data.audio_duration,
                audio_format=audio_data.audio_format,
                file_size=audio_data.file_size,
            )

            if not updated_session:
                raise NotFoundException("Failed to update audio info")

            return VoiceSessionResponse.model_validate(updated_session)

        except (NotFoundException, PermissionException):
            raise
        except Exception as e:
            logger.error(f"Failed to update audio info for session {session_id}: {e}")
            raise ValidationException("Failed to update audio info")

    async def update_analysis_info(
        self, session_id: int, user_id: int, analysis_data: dict
    ) -> VoiceSessionResponse:
        """分析情報を更新"""
        try:
            # セッション取得
            session = await self.repository.get(self.db, session_id)
            if not session:
                raise NotFoundException("Voice session not found")

            # 権限チェック
            if session.user_id != user_id:
                raise PermissionException("Access denied")

            # 分析情報更新
            updated_session = await self.repository.update_analysis_info(
                self.db,
                session_id=session_id,
                analysis_summary=analysis_data["analysis_summary"],
                sentiment_score=analysis_data["sentiment_score"],
                key_topics=analysis_data["key_topics"],
            )

            if not updated_session:
                raise NotFoundException("Failed to update analysis info")

            return VoiceSessionResponse.model_validate(updated_session)

        except (NotFoundException, PermissionException):
            raise
        except Exception as e:
            logger.error(
                f"Failed to update analysis info for session {session_id}: {e}"
            )
            raise ValidationException("Failed to update analysis info")

    async def delete_session(self, session_id: int, user_id: int) -> bool:
        """音声セッションを削除"""
        try:
            # セッション取得
            session = await self.repository.get(self.db, session_id)
            if not session:
                raise NotFoundException("Voice session not found")

            # 権限チェック
            if session.user_id != user_id:
                raise PermissionException("Access denied")

            # 削除
            deleted_session = await self.repository.delete(self.db, id=session_id)

            if deleted_session:
                logger.info(f"Voice session {session_id} deleted by user {user_id}")
                return True
            else:
                return False

        except (NotFoundException, PermissionException):
            raise
        except Exception as e:
            logger.error(f"Failed to delete voice session {session_id}: {e}")
            raise ValidationException("Failed to delete voice session")

    async def search_sessions(
        self, user_id: int, search_term: str, query_params: VoiceSessionQueryParams
    ) -> VoiceSessionListResponse:
        """音声セッションを検索"""
        try:
            # 検索実行
            sessions = await self.repository.search_sessions(
                self.db,
                search_term=search_term,
                user_id=user_id,
                skip=(query_params.page - 1) * query_params.size,
                limit=query_params.size,
            )

            # 総件数取得（簡易版）
            total = len(sessions)

            # レスポンス形式に変換
            session_responses = [
                VoiceSessionResponse.model_validate(session) for session in sessions
            ]

            return VoiceSessionListResponse(
                sessions=session_responses,
                total=total,
                page=query_params.page,
                size=query_params.size,
                pages=(total + query_params.size - 1) // query_params.size,
            )

        except Exception as e:
            logger.error(f"Failed to search sessions for user {user_id}: {e}")
            raise ValidationException("Failed to search sessions")

    async def get_user_stats(self, user_id: int) -> VoiceSessionStats:
        """ユーザーの音声セッション統計を取得"""
        try:
            # 統計情報取得
            stats_data = await self.repository.get_user_stats(self.db, user_id)

            # 追加統計計算
            active_sessions = await self.repository.count(
                self.db, filters={"user_id": user_id, "status": "active"}
            )

            public_sessions = await self.repository.count(
                self.db, filters={"user_id": user_id, "is_public": True}
            )

            private_sessions = await self.repository.count(
                self.db, filters={"user_id": user_id, "is_public": False}
            )

            return VoiceSessionStats(
                total_sessions=stats_data["total_sessions"],
                total_duration=stats_data["total_duration"],
                average_duration=stats_data["average_duration"],
                completed_sessions=stats_data["completed_sessions"],
                active_sessions=active_sessions,
                analyzed_sessions=stats_data["analyzed_sessions"],
                public_sessions=public_sessions,
                private_sessions=private_sessions,
            )

        except Exception as e:
            logger.error(f"Failed to get user stats for user {user_id}: {e}")
            raise ValidationException("Failed to get user stats")

    async def get_public_sessions(
        self, query_params: VoiceSessionQueryParams
    ) -> VoiceSessionListResponse:
        """公開音声セッション一覧を取得"""
        try:
            # フィルター作成
            filters = VoiceSessionFilters(
                status=query_params.status,
                is_public=query_params.is_public,
                is_analyzed=query_params.is_analyzed,
                date_from=query_params.date_from,
                date_to=query_params.date_to,
                search=query_params.search,
            )

            # 公開セッション一覧取得
            sessions = await self.repository.get_public_sessions(
                self.db,
                skip=(query_params.page - 1) * query_params.size,
                limit=query_params.size,
                filters=filters,
            )

            # 総件数取得
            total = await self.repository.count(self.db, filters={"is_public": True})

            # レスポンス形式に変換
            session_responses = [
                VoiceSessionResponse.model_validate(session) for session in sessions
            ]

            return VoiceSessionListResponse(
                sessions=session_responses,
                total=total,
                page=query_params.page,
                size=query_params.size,
                pages=(total + query_params.size - 1) // query_params.size,
            )

        except Exception as e:
            logger.error(f"Failed to get public sessions: {e}")
            raise ValidationException("Failed to get public sessions")

    async def generate_session_id(self) -> str:
        """ユニークなセッションIDを生成"""
        return str(uuid.uuid4())

    async def _get_user_by_id(self, user_id: int) -> Optional[User]:
        """ユーザーIDでユーザーを取得"""
        try:
            # TODO: ユーザーリポジトリを使用するように変更
            from sqlalchemy import select

            result = await self.db.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get user by id {user_id}: {e}")
            return None

    async def get_session_by_session_id(
        self, session_id: str
    ) -> Optional[VoiceSession]:
        """セッションIDで音声セッションを取得"""
        try:
            return await self.repository.get_by_session_id(self.db, session_id)
        except Exception as e:
            logger.error(f"Failed to get session by session_id {session_id}: {e}")
            return None

    async def start_session(
        self, session_id: str, user_id: int
    ) -> VoiceSessionResponse:
        """音声セッションを開始"""
        try:
            session = await self.get_session_by_session_id(session_id)
            if not session:
                raise NotFoundException("Voice session not found")

            # 権限チェック
            if session.user_id != user_id:
                raise PermissionException("Access denied")

            # セッション状態を更新
            update_data = VoiceSessionUpdate(status="active", started_at=datetime.now())

            updated_session = await self.repository.update(
                self.db, session.id, update_data
            )

            return VoiceSessionResponse.model_validate(updated_session)

        except (NotFoundException, PermissionException):
            raise
        except Exception as e:
            logger.error(f"Failed to start session {session_id}: {e}")
            raise ValidationException("Failed to start session")

    async def end_session(self, session_id: str, user_id: int) -> VoiceSessionResponse:
        """音声セッションを終了"""
        try:
            session = await self.get_session_by_session_id(session_id)
            if not session:
                raise NotFoundException("Voice session not found")

            # 権限チェック
            if session.user_id != user_id:
                raise PermissionException("Access denied")

            # セッション状態を更新
            update_data = VoiceSessionUpdate(
                status="completed", ended_at=datetime.now()
            )

            updated_session = await self.repository.update(
                self.db, session.id, update_data
            )

            return VoiceSessionResponse.model_validate(updated_session)

        except (NotFoundException, PermissionException):
            raise
        except Exception as e:
            logger.error(f"Failed to end session {session_id}: {e}")
            raise ValidationException("Failed to end session")
