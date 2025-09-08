from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from datetime import datetime, timedelta
import uuid

from app.models.voice_session import VoiceSession
from app.models.user import User
from app.repositories.voice_session_repository import voice_session_repository
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
    ParticipantAddRequest,
    ParticipantListResponse,
    ParticipantUpdateRequest,
    ParticipantRoleEnum,
    RecordingStatusResponse,
    RecordingStatusEnum,
    RealtimeStatsResponse,
    SessionProgressResponse,
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
        self.repository = voice_session_repository

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

    async def update_session_by_session_id(
        self, session_id: str, user_id: int, update_data: VoiceSessionUpdate
    ) -> VoiceSessionResponse:
        """セッションID（文字列）で音声セッションを更新"""
        try:
            # セッション取得
            session = await self.repository.get_by_session_id(self.db, session_id)
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
            if not audio_data.audio_file_path:
                raise ValidationException("Audio file path is required")

            updated_session = await self.repository.update_audio_info(
                self.db,
                session_id=session_id,
                audio_file_path=audio_data.audio_file_path,
                audio_duration=audio_data.audio_duration or 0.0,
                audio_format=audio_data.audio_format.value
                if audio_data.audio_format
                else "mp3",
                file_size=audio_data.file_size or 0,
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
        self, session_id: str, user_id: int
    ) -> VoiceSessionDetailResponse:
        """セッションIDで音声セッションを取得"""
        try:
            session = await self.repository.get_by_session_id(self.db, session_id)
            if not session:
                raise NotFoundException("Voice session not found")
            
            # 権限チェック
            if session.user_id != user_id:
                raise PermissionException("Access denied")
            
            return VoiceSessionDetailResponse.model_validate(session)
        except (NotFoundException, PermissionException):
            raise
        except Exception as e:
            logger.error(f"Failed to get session by session_id {session_id}: {e}")
            raise ValidationException("Failed to get voice session")

    async def start_session(
        self, session_id: str, user_id: int
    ) -> VoiceSessionResponse:
        """音声セッションを開始"""
        try:
            session = await self.get_session_by_session_id(session_id)  # pyright: ignore[reportCallIssue]
            if not session:
                raise NotFoundException("Voice session not found")

            # 権限チェック
            if session.user_id != user_id:
                raise PermissionException("Access denied")

            # セッション状態を更新
            update_data = VoiceSessionUpdate(status="active", started_at=datetime.now())

            updated_session = await self.repository.update(
                self.db, db_obj=session, obj_in=update_data
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
            session = await self.get_session_by_session_id(session_id)  # pyright: ignore[reportCallIssue]
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
                self.db, db_obj=session, obj_in=update_data
            )

            return VoiceSessionResponse.model_validate(updated_session)

        except (NotFoundException, PermissionException):
            raise
        except Exception as e:
            logger.error(f"Failed to end session {session_id}: {e}")
            raise ValidationException("Failed to end session")

    # 参加者管理メソッド
    async def add_participant(
        self,
        session_id: str,
        user_id: int,
        participant_user_id: int,
        role: ParticipantRoleEnum,
    ) -> VoiceSessionResponse:
        """参加者を追加"""
        try:
            session = await self.get_session_by_session_id(session_id)  # pyright: ignore[reportCallIssue]
            if not session:
                raise NotFoundException("Voice session not found")

            # 権限チェック（オーナーまたはモデレーターのみ）
            if not await self._can_manage_participants(session, user_id):
                raise PermissionException("Access denied")

            # 参加者ユーザーの存在チェック
            participant_user = await self._get_user_by_id(participant_user_id)
            if not participant_user:
                raise NotFoundException("Participant user not found")

            # 参加者情報を更新
            participants = self._parse_participants(session.participants)

            # 既存の参加者かチェック
            if any(p["user_id"] == participant_user_id for p in participants):
                raise ValidationException("User is already a participant")

            # 新しい参加者を追加
            new_participant = {
                "user_id": participant_user_id,
                "username": participant_user.username,
                "email": participant_user.email,
                "role": role.value,
                "joined_at": datetime.now().isoformat(),
                "is_active": True,
            }
            participants.append(new_participant)

            # セッションを更新
            update_data = VoiceSessionUpdate(
                participants=self._serialize_participants(participants),
                participant_count=len(participants),
            )

            updated_session = await self.repository.update(
                self.db, db_obj=session, obj_in=update_data
            )

            return VoiceSessionResponse.model_validate(updated_session)

        except (NotFoundException, PermissionException, ValidationException):
            raise
        except Exception as e:
            logger.error(f"Failed to add participant to session {session_id}: {e}")
            raise ValidationException("Failed to add participant")

    async def remove_participant(
        self, session_id: str, user_id: int, participant_user_id: int
    ) -> VoiceSessionResponse:
        """参加者を削除"""
        try:
            session = await self.get_session_by_session_id(session_id)  # pyright: ignore[reportCallIssue]
            if not session:
                raise NotFoundException("Voice session not found")

            # 権限チェック（オーナーまたはモデレーターのみ）
            if not await self._can_manage_participants(session, user_id):
                raise PermissionException("Access denied")

            # 参加者情報を更新
            participants = self._parse_participants(session.participants)

            # 参加者を削除
            participants = [
                p for p in participants if p["user_id"] != participant_user_id
            ]

            # セッションを更新
            update_data = VoiceSessionUpdate(
                participants=self._serialize_participants(participants),
                participant_count=len(participants),
            )

            updated_session = await self.repository.update(
                self.db, db_obj=session, obj_in=update_data
            )

            return VoiceSessionResponse.model_validate(updated_session)

        except (NotFoundException, PermissionException):
            raise
        except Exception as e:
            logger.error(f"Failed to remove participant from session {session_id}: {e}")
            raise ValidationException("Failed to remove participant")

    async def get_participants(
        self, session_id: str, user_id: int
    ) -> ParticipantListResponse:
        """参加者一覧を取得"""
        try:
            session = await self.get_session_by_session_id(session_id)  # pyright: ignore[reportCallIssue]
            if not session:
                raise NotFoundException("Voice session not found")

            # 権限チェック（参加者またはオーナー）
            if not await self._can_view_participants(session, user_id):
                raise PermissionException("Access denied")

            participants = self._parse_participants(session.participants)

            # 参加者情報を取得
            participant_responses = []
            active_count = 0

            for participant in participants:
                user = await self._get_user_by_id(participant["user_id"])
                if user:
                    participant_responses.append(
                        {
                            "user_id": participant["user_id"],
                            "username": user.username,
                            "email": user.email,
                            "role": participant["role"],
                            "joined_at": datetime.fromisoformat(
                                participant["joined_at"]
                            ),
                            "is_active": participant["is_active"],
                        }
                    )
                    if participant["is_active"]:
                        active_count += 1

            return ParticipantListResponse(
                participants=participant_responses,
                total=len(participant_responses),
                active_count=active_count,
            )

        except (NotFoundException, PermissionException):
            raise
        except Exception as e:
            logger.error(f"Failed to get participants for session {session_id}: {e}")
            raise ValidationException("Failed to get participants")

    async def update_participant_role(
        self,
        session_id: str,
        user_id: int,
        participant_user_id: int,
        new_role: ParticipantRoleEnum,
    ) -> VoiceSessionResponse:
        """参加者の権限を更新"""
        try:
            session = await self.get_session_by_session_id(session_id)  # pyright: ignore[reportCallIssue]
            if not session:
                raise NotFoundException("Voice session not found")

            # 権限チェック（オーナーのみ）
            if session.user_id != user_id:
                raise PermissionException("Access denied")

            # 参加者情報を更新
            participants = self._parse_participants(session.participants)

            # 参加者の権限を更新
            for participant in participants:
                if participant["user_id"] == participant_user_id:
                    participant["role"] = new_role.value
                    break
            else:
                raise NotFoundException("Participant not found")

            # セッションを更新
            update_data = VoiceSessionUpdate(
                participants=self._serialize_participants(participants)
            )

            updated_session = await self.repository.update(
                self.db, db_obj=session, obj_in=update_data
            )

            return VoiceSessionResponse.model_validate(updated_session)

        except (NotFoundException, PermissionException):
            raise
        except Exception as e:
            logger.error(
                f"Failed to update participant role in session {session_id}: {e}"
            )
            raise ValidationException("Failed to update participant role")

    # ヘルパーメソッド
    def _parse_participants(self, participants_json: str) -> list:
        """参加者JSONをパース"""
        import json

        if not participants_json:
            return []
        try:
            return json.loads(participants_json)
        except json.JSONDecodeError:
            return []

    def _serialize_participants(self, participants: list) -> str:
        """参加者リストをJSONにシリアライズ"""
        import json

        return json.dumps(participants)

    async def _can_manage_participants(
        self, session: VoiceSession, user_id: int
    ) -> bool:
        """参加者管理権限があるかチェック"""
        # オーナーの場合
        if session.user_id == user_id:
            return True

        # 参加者リストから権限をチェック
        participants = self._parse_participants(session.participants)
        for participant in participants:
            if participant["user_id"] == user_id:
                return participant["role"] in ["owner", "moderator"]

        return False

    async def _can_view_participants(self, session: VoiceSession, user_id: int) -> bool:
        """参加者一覧閲覧権限があるかチェック"""
        # オーナーの場合
        if session.user_id == user_id:
            return True

        # 参加者の場合
        participants = self._parse_participants(session.participants)
        for participant in participants:
            if participant["user_id"] == user_id:
                return True

        return False

    async def _can_manage_recording(self, session: VoiceSession, user_id: int) -> bool:  # pyright: ignore[reportRedeclaration]
        """録音管理権限があるかチェック"""
        # オーナーの場合
        if session.user_id == user_id:
            return True

        # 参加者リストから権限をチェック
        participants = self._parse_participants(session.participants)
        for participant in participants:
            if participant["user_id"] == user_id:
                return participant["role"] in ["owner", "moderator"]

        return False

    async def _can_view_recording(self, session: VoiceSession, user_id: int) -> bool:  # pyright: ignore[reportRedeclaration]
        """録音状態閲覧権限があるかチェック"""
        # オーナーの場合
        if session.user_id == user_id:
            return True

        # 参加者の場合
        participants = self._parse_participants(session.participants)
        for participant in participants:
            if participant["user_id"] == user_id:
                return True

        return False

    # 録音制御メソッド
    async def start_recording(
        self, session_id: str, user_id: int, quality: str = "high", format: str = "mp3"
    ) -> RecordingStatusResponse:
        """録音を開始"""
        try:
            session_response = await self.get_session_by_session_id(session_id, user_id)
            
            # VoiceSessionDetailResponseからVoiceSessionオブジェクトを取得
            session = await self.repository.get_by_session_id(self.db, session_id)
            if not session:
                raise NotFoundException("Voice session not found")

            # 権限チェック（オーナーまたはモデレーターのみ）
            if not await self._can_manage_recording(session, user_id):
                raise PermissionException("Access denied")

            # 録音状態を更新
            recording_status = {
                "status": RecordingStatusEnum.RECORDING.value,
                "is_recording": True,
                "started_at": datetime.now().isoformat(),
                "quality": quality,
                "format": format,
                "recording_duration": 0.0,
            }

            # セッションを更新
            update_data = VoiceSessionUpdate(
                participants=self._serialize_recording_status(recording_status)
            )

            updated_session = await self.repository.update(
                self.db, db_obj=session, obj_in=update_data
            )

            return RecordingStatusResponse(
                session_id=session_id,
                status=RecordingStatusEnum.RECORDING,
                is_recording=True,
                recording_duration=0.0,
                quality=quality,
                format=format,
                started_at=datetime.now(),
            )

        except (NotFoundException, PermissionException):
            raise
        except Exception as e:
            logger.error(f"Failed to start recording for session {session_id}: {e}")
            raise ValidationException("Failed to start recording")

    async def stop_recording(
        self, session_id: str, user_id: int
    ) -> RecordingStatusResponse:
        """録音を停止"""
        try:
            session_response = await self.get_session_by_session_id(session_id, user_id)
            
            # VoiceSessionDetailResponseからVoiceSessionオブジェクトを取得
            session = await self.repository.get_by_session_id(self.db, session_id)
            if not session:
                raise NotFoundException("Voice session not found")

            # 権限チェック（オーナーまたはモデレーターのみ）
            if not await self._can_manage_recording(session, user_id):
                raise PermissionException("Access denied")

            # 録音状態を更新
            recording_status = {
                "status": RecordingStatusEnum.STOPPED.value,
                "is_recording": False,
                "stopped_at": datetime.now().isoformat(),
            }

            # セッションを更新
            update_data = VoiceSessionUpdate(
                participants=self._serialize_recording_status(recording_status)
            )

            updated_session = await self.repository.update(
                self.db, db_obj=session, obj_in=update_data
            )

            return RecordingStatusResponse(
                session_id=session_id,
                status=RecordingStatusEnum.STOPPED,
                is_recording=False,
            )

        except (NotFoundException, PermissionException):
            raise
        except Exception as e:
            logger.error(f"Failed to stop recording for session {session_id}: {e}")
            raise ValidationException("Failed to stop recording")

    async def pause_recording(
        self, session_id: str, user_id: int
    ) -> RecordingStatusResponse:
        """録音を一時停止"""
        try:
            session_response = await self.get_session_by_session_id(session_id, user_id)
            
            # VoiceSessionDetailResponseからVoiceSessionオブジェクトを取得
            session = await self.repository.get_by_session_id(self.db, session_id)
            if not session:
                raise NotFoundException("Voice session not found")

            # 権限チェック（オーナーまたはモデレーターのみ）
            if not await self._can_manage_recording(session, user_id):
                raise PermissionException("Access denied")

            # 録音状態を更新
            recording_status = {
                "status": RecordingStatusEnum.PAUSED.value,
                "is_recording": False,
                "paused_at": datetime.now().isoformat(),
            }

            # セッションを更新
            update_data = VoiceSessionUpdate(
                participants=self._serialize_recording_status(recording_status)
            )

            updated_session = await self.repository.update(
                self.db, db_obj=session, obj_in=update_data
            )

            return RecordingStatusResponse(
                session_id=session_id,
                status=RecordingStatusEnum.PAUSED,
                is_recording=False,
            )

        except (NotFoundException, PermissionException):
            raise
        except Exception as e:
            logger.error(f"Failed to pause recording for session {session_id}: {e}")
            raise ValidationException("Failed to pause recording")

    async def resume_recording(
        self, session_id: str, user_id: int
    ) -> RecordingStatusResponse:
        """録音を再開"""
        try:
            session_response = await self.get_session_by_session_id(session_id, user_id)
            
            # VoiceSessionDetailResponseからVoiceSessionオブジェクトを取得
            session = await self.repository.get_by_session_id(self.db, session_id)
            if not session:
                raise NotFoundException("Voice session not found")

            # 権限チェック（オーナーまたはモデレーターのみ）
            if not await self._can_manage_recording(session, user_id):
                raise PermissionException("Access denied")

            # 録音状態を更新
            recording_status = {
                "status": RecordingStatusEnum.RECORDING.value,
                "is_recording": True,
                "resumed_at": datetime.now().isoformat(),
            }

            # セッションを更新
            update_data = VoiceSessionUpdate(
                participants=self._serialize_recording_status(recording_status)
            )

            updated_session = await self.repository.update(
                self.db, db_obj=session, obj_in=update_data
            )

            return RecordingStatusResponse(
                session_id=session_id,
                status=RecordingStatusEnum.RECORDING,
                is_recording=True,
            )

        except (NotFoundException, PermissionException):
            raise
        except Exception as e:
            logger.error(f"Failed to resume recording for session {session_id}: {e}")
            raise ValidationException("Failed to resume recording")

    async def get_recording_status(
        self, session_id: str, user_id: int
    ) -> RecordingStatusResponse:
        """録音状態を取得"""
        try:
            session_response = await self.get_session_by_session_id(session_id, user_id)
            
            # VoiceSessionDetailResponseからVoiceSessionオブジェクトを取得
            session = await self.repository.get_by_session_id(self.db, session_id)
            if not session:
                raise NotFoundException("Voice session not found")

            # 権限チェック（参加者またはオーナー）
            if not await self._can_view_recording(session, user_id):
                raise PermissionException("Access denied")

            # 録音状態を取得
            recording_status = self._parse_recording_status(session.participants)

            return RecordingStatusResponse(
                session_id=session_id,
                status=RecordingStatusEnum(recording_status.get("status", "idle")),
                is_recording=recording_status.get("is_recording", False),
                recording_duration=recording_status.get("recording_duration", 0.0),
                file_path=recording_status.get("file_path"),
                file_size=recording_status.get("file_size"),
                quality=recording_status.get("quality"),
                format=recording_status.get("format"),
                started_at=datetime.fromisoformat(recording_status["started_at"])
                if recording_status.get("started_at")
                else None,
                error_message=recording_status.get("error_message"),
            )

        except (NotFoundException, PermissionException):
            raise
        except Exception as e:
            logger.error(
                f"Failed to get recording status for session {session_id}: {e}"
            )
            raise ValidationException("Failed to get recording status")

    # 録音制御ヘルパーメソッド
    def _parse_recording_status(self, recording_status_json: str) -> dict:
        """録音状態JSONをパース"""
        import json

        if not recording_status_json:
            return {"status": "idle", "is_recording": False}
        try:
            return json.loads(recording_status_json)
        except json.JSONDecodeError:
            return {"status": "idle", "is_recording": False}

    def _serialize_recording_status(self, recording_status: dict) -> str:
        """録音状態をJSONにシリアライズ"""
        import json

        return json.dumps(recording_status)

    async def _can_manage_recording(self, session: VoiceSession, user_id: int) -> bool:
        """録音管理権限があるかチェック"""
        # オーナーの場合
        if session.user_id == user_id:
            return True

        # 参加者リストから権限をチェック
        participants = self._parse_participants(session.participants)
        for participant in participants:
            if participant["user_id"] == user_id:
                return participant["role"] in ["owner", "moderator"]

        return False

    async def _can_view_recording(self, session: VoiceSession, user_id: int) -> bool:
        """録音状態閲覧権限があるかチェック"""
        # オーナーの場合
        if session.user_id == user_id:
            return True

        # 参加者の場合
        participants = self._parse_participants(session.participants)
        for participant in participants:
            if participant["user_id"] == user_id:
                return True

        return False

    # リアルタイム統計メソッド
    async def get_realtime_stats(
        self, session_id: str, user_id: int
    ) -> RealtimeStatsResponse:
        """リアルタイム統計を取得"""
        try:
            session = await self.get_session_by_session_id(session_id)  # pyright: ignore[reportCallIssue]
            if not session:
                raise NotFoundException("Voice session not found")

            # 権限チェック（参加者またはオーナー）
            if not await self._can_view_session(session, user_id):
                raise PermissionException("Access denied")

            # 現在の継続時間を計算
            current_duration = 0.0
            if session.started_at:
                if session.ended_at:
                    current_duration = (
                        session.ended_at - session.started_at
                    ).total_seconds()
                else:
                    current_duration = (
                        datetime.now() - session.started_at
                    ).total_seconds()

            # 参加者情報を取得
            participants = self._parse_participants(session.participants)
            active_participants = sum(
                1 for p in participants if p.get("is_active", True)
            )

            # 録音状態を取得
            recording_status = self._parse_recording_status(session.participants)
            recording_duration = recording_status.get("recording_duration", 0.0)

            # 文字起こし件数を取得
            transcription_count = (
                len(session.transcriptions) if session.transcriptions else 0
            )

            # 分析進捗を計算
            analysis_progress = 0.0
            if session.is_analyzed:
                analysis_progress = 1.0
            elif session.analyses:
                analysis_progress = min(len(session.analyses) / 3.0, 1.0)  # 仮の計算

            # 主要トピック数を取得
            key_topics_count = 0
            if session.key_topics:
                try:
                    import json

                    topics = json.loads(session.key_topics)
                    key_topics_count = len(topics) if isinstance(topics, list) else 0
                except:
                    key_topics_count = 0

            return RealtimeStatsResponse(
                session_id=session_id,
                current_duration=current_duration,
                participant_count=session.participant_count,
                active_participants=active_participants,
                recording_duration=recording_duration,
                transcription_count=transcription_count,
                analysis_progress=analysis_progress,
                sentiment_score=session.sentiment_score,
                key_topics_count=key_topics_count,
                last_activity=session.updated_at or session.created_at,
                is_live=session.status == "active",
            )

        except (NotFoundException, PermissionException):
            raise
        except Exception as e:
            logger.error(f"Failed to get realtime stats for session {session_id}: {e}")
            raise ValidationException("Failed to get realtime stats")

    async def get_session_progress(
        self, session_id: str, user_id: int
    ) -> SessionProgressResponse:
        """セッション進行状況を取得"""
        try:
            session = await self.get_session_by_session_id(session_id)  # pyright: ignore[reportCallIssue]
            if not session:
                raise NotFoundException("Voice session not found")

            # 権限チェック（参加者またはオーナー）
            if not await self._can_view_session(session, user_id):
                raise PermissionException("Access denied")

            # 進行状況を計算
            progress_percentage = 0.0
            current_phase = "preparation"
            completed_steps = []
            remaining_steps = [
                "session_start",
                "recording",
                "transcription",
                "analysis",
                "completion",
            ]

            # セッション開始済み
            if session.started_at:
                completed_steps.append("session_start")
                current_phase = "active"
                progress_percentage = 20.0

            # 録音中
            recording_status = self._parse_recording_status(session.participants)
            if recording_status.get("is_recording", False):
                completed_steps.append("recording")
                current_phase = "recording"
                progress_percentage = 40.0

            # 文字起こし完了
            if session.transcriptions and len(session.transcriptions) > 0:
                completed_steps.append("transcription")
                current_phase = "transcription"
                progress_percentage = 60.0

            # 分析完了
            if session.is_analyzed:
                completed_steps.append("analysis")
                current_phase = "analysis"
                progress_percentage = 80.0

            # セッション完了
            if session.status == "completed":
                completed_steps.append("completion")
                current_phase = "completed"
                progress_percentage = 100.0

            # 残りのステップを更新
            remaining_steps = [
                step for step in remaining_steps if step not in completed_steps
            ]

            # 推定完了時刻を計算
            estimated_completion = None
            if session.started_at and not session.ended_at:
                # 平均セッション時間を60分と仮定
                avg_session_duration = 3600  # 60分
                estimated_completion = session.started_at + timedelta(
                    seconds=avg_session_duration
                )

            # 総継続時間を計算
            total_duration = 0.0
            if session.started_at:
                if session.ended_at:
                    total_duration = (
                        session.ended_at - session.started_at
                    ).total_seconds()
                else:
                    total_duration = (
                        datetime.now() - session.started_at
                    ).total_seconds()

            # 録音状態を取得
            recording_status_enum = RecordingStatusEnum(
                recording_status.get("status", "idle")
            )

            # 分析状態を取得
            analysis_status = "not_started"
            if session.is_analyzed:
                analysis_status = "completed"
            elif session.analyses and len(session.analyses) > 0:
                analysis_status = "in_progress"
            elif session.transcriptions and len(session.transcriptions) > 0:
                analysis_status = "ready"

            return SessionProgressResponse(
                session_id=session_id,
                status=session.status,
                progress_percentage=progress_percentage,
                current_phase=current_phase,
                estimated_completion=estimated_completion,
                completed_steps=completed_steps,
                remaining_steps=remaining_steps,
                total_duration=total_duration,
                recording_status=recording_status_enum,
                analysis_status=analysis_status,
            )

        except (NotFoundException, PermissionException):
            raise
        except Exception as e:
            logger.error(
                f"Failed to get session progress for session {session_id}: {e}"
            )
            raise ValidationException("Failed to get session progress")

    async def _can_view_session(self, session: VoiceSession, user_id: int) -> bool:
        """セッション閲覧権限があるかチェック"""
        # オーナーの場合
        if session.user_id == user_id:
            return True

        # 参加者の場合
        participants = self._parse_participants(session.participants)
        for participant in participants:
            if participant["user_id"] == user_id:
                return True

        return False
