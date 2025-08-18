from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from datetime import datetime
import uuid

from app.models.chat_room import ChatRoom, ChatMessage, ChatRoomParticipant
from app.models.user import User
from app.repositories import (
    chat_room_repository,
    chat_message_repository,
    chat_room_participant_repository,
)
from app.schemas.chat_room import (
    ChatRoomCreate,
    ChatRoomUpdate,
    ChatRoomResponse,
    ChatRoomListResponse,
    ChatRoomDetailResponse,
    ChatRoomQueryParams,
    ChatRoomStats,
    ChatMessageCreate,
    ChatMessageUpdate,
    ChatMessageResponse,
    ChatMessageListResponse,
    ChatRoomParticipantCreate,
    ChatRoomParticipantUpdate,
    ChatRoomParticipantResponse,
    ChatRoomParticipantListResponse,
    RoomStatusEnum,
    ParticipantRoleEnum,
    ParticipantStatusEnum,
)
from app.core.exceptions import (
    NotFoundException,
    ValidationException,
    PermissionException,
)

logger = structlog.get_logger()


class ChatRoomService:
    """チャットルームサービス"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.chat_room_repository = chat_room_repository
        self.chat_message_repository = chat_message_repository
        self.chat_participant_repository = chat_room_participant_repository

    async def create_room(
        self, user_id: int, room_data: ChatRoomCreate
    ) -> ChatRoomResponse:
        """チャットルームを作成"""
        try:
            # ルームIDの重複チェック
            if (
                room_data.room_id
                and await self.chat_room_repository.room_exists_by_room_id(
                    self.db, room_data.room_id
                )
            ):
                raise ValidationException("Room ID already exists")

            # ユーザー存在チェック
            user = await self._get_user_by_id(user_id)
            if not user:
                raise NotFoundException("User not found")

            # ルームIDが指定されていない場合は自動生成
            if not room_data.room_id:
                room_data.room_id = await self.generate_room_id()

            # ルーム作成
            room = await self.chat_room_repository.create(self.db, obj_in=room_data)

            # 作成者を参加者として追加
            participant_data = ChatRoomParticipantCreate(
                role=ParticipantRoleEnum.ADMIN,
                status=ParticipantStatusEnum.ACTIVE,
            )
            await self.chat_participant_repository.create(
                self.db, obj_in=participant_data
            )

            # レスポンス形式に変換
            return ChatRoomResponse.model_validate(room)

        except (ValidationException, NotFoundException):
            raise
        except Exception as e:
            logger.error(f"Failed to create chat room: {e}")
            raise ValidationException("Failed to create chat room")

    async def get_room_by_id(
        self, room_id: int, user_id: int
    ) -> ChatRoomDetailResponse:
        """チャットルーム詳細を取得"""
        try:
            room = await self.chat_room_repository.get_room_with_relations(
                self.db, room_id
            )

            if not room:
                raise NotFoundException("Chat room not found")

            # 権限チェック
            if room.created_by != user_id and not room.is_public:
                raise PermissionException("Access denied")

            # 詳細レスポンス形式に変換
            response = ChatRoomDetailResponse.model_validate(room)

            # 参加者情報を設定
            participants = await self.chat_participant_repository.get_room_participants(
                self.db, room_id
            )
            response.participants = [
                {
                    "id": p.id,
                    "user_id": p.user_id,
                    "role": p.role,
                    "status": p.status,
                    "is_online": p.is_online,
                    "joined_at": p.joined_at,
                }
                for p in participants
            ]

            return response

        except (NotFoundException, PermissionException):
            raise
        except Exception as e:
            logger.error(f"Failed to get chat room {room_id}: {e}")
            raise NotFoundException("Failed to get chat room")

    async def get_user_rooms(
        self, user_id: int, query_params: ChatRoomQueryParams
    ) -> ChatRoomListResponse:
        """ユーザーのチャットルーム一覧を取得"""
        try:
            # フィルター作成
            filters = {
                "status": query_params.status,
                "room_type": query_params.room_type,
                "is_public": query_params.is_public,
                "search": query_params.search,
            }

            # ルーム一覧取得
            rooms = await self.chat_room_repository.get_rooms_by_creator(
                self.db,
                created_by=user_id,
                skip=(query_params.page - 1) * query_params.size,
                limit=query_params.size,
                filters=filters,
            )

            # 総件数取得
            total = await self.chat_room_repository.count(
                self.db, filters={"created_by": user_id}
            )

            # レスポンス形式に変換
            room_responses = [ChatRoomResponse.model_validate(room) for room in rooms]

            return ChatRoomListResponse(
                rooms=room_responses,
                total=total,
                page=query_params.page,
                size=query_params.size,
                pages=(total + query_params.size - 1) // query_params.size,
            )

        except Exception as e:
            logger.error(f"Failed to get user rooms for user {user_id}: {e}")
            raise ValidationException("Failed to get user rooms")

    async def get_public_rooms(
        self, query_params: ChatRoomQueryParams
    ) -> ChatRoomListResponse:
        """公開チャットルーム一覧を取得"""
        try:
            # フィルター作成
            filters = {
                "status": query_params.status,
                "room_type": query_params.room_type,
                "search": query_params.search,
            }

            # 公開ルーム一覧取得
            rooms = await self.chat_room_repository.get_public_rooms(
                self.db,
                skip=(query_params.page - 1) * query_params.size,
                limit=query_params.size,
                filters=filters,
            )

            # 総件数取得
            total = await self.chat_room_repository.count(
                self.db, filters={"is_public": True}
            )

            # レスポンス形式に変換
            room_responses = [ChatRoomResponse.model_validate(room) for room in rooms]

            return ChatRoomListResponse(
                rooms=room_responses,
                total=total,
                page=query_params.page,
                size=query_params.size,
                pages=(total + query_params.size - 1) // query_params.size,
            )

        except Exception as e:
            logger.error(f"Failed to get public rooms: {e}")
            raise ValidationException("Failed to get public rooms")

    async def update_room(
        self, room_id: int, user_id: int, update_data: ChatRoomUpdate
    ) -> ChatRoomResponse:
        """チャットルームを更新"""
        try:
            # ルーム取得
            room = await self.chat_room_repository.get(self.db, room_id)
            if not room:
                raise NotFoundException("Chat room not found")

            # 権限チェック
            if room.created_by != user_id:
                raise PermissionException("Access denied")

            # 更新
            updated_room = await self.chat_room_repository.update(
                self.db, db_obj=room, obj_in=update_data
            )

            return ChatRoomResponse.model_validate(updated_room)

        except (NotFoundException, PermissionException):
            raise
        except Exception as e:
            logger.error(f"Failed to update chat room {room_id}: {e}")
            raise ValidationException("Failed to update chat room")

    async def delete_room(self, room_id: int, user_id: int) -> bool:
        """チャットルームを削除"""
        try:
            # ルーム取得
            room = await self.chat_room_repository.get(self.db, room_id)
            if not room:
                raise NotFoundException("Chat room not found")

            # 権限チェック
            if room.created_by != user_id:
                raise PermissionException("Access denied")

            # 削除
            deleted_room = await self.chat_room_repository.delete(self.db, id=room_id)

            if deleted_room:
                logger.info(f"Chat room {room_id} deleted by user {user_id}")
                return True
            else:
                return False

        except (NotFoundException, PermissionException):
            raise
        except Exception as e:
            logger.error(f"Failed to delete chat room {room_id}: {e}")
            raise ValidationException("Failed to delete chat room")

    async def join_room(
        self, room_id: int, user_id: int, participant_data: ChatRoomParticipantCreate
    ) -> ChatRoomParticipantResponse:
        """ルームに参加"""
        try:
            # ルーム取得
            room = await self.chat_room_repository.get(self.db, room_id)
            if not room:
                raise NotFoundException("Chat room not found")

            # 参加者数チェック
            if room.current_participants >= room.max_participants:
                raise ValidationException("Room is full")

            # 既に参加しているかチェック
            if await self.chat_participant_repository.is_user_in_room(
                self.db, room_id, user_id
            ):
                raise ValidationException("User is already in the room")

            # 参加者として追加
            participant = await self.chat_participant_repository.create(
                self.db, obj_in=participant_data
            )

            # 参加者数を更新
            await self.chat_room_repository.update_participant_count(
                self.db, room_id, room.current_participants + 1
            )

            return ChatRoomParticipantResponse.model_validate(participant)

        except (NotFoundException, ValidationException):
            raise
        except Exception as e:
            logger.error(f"Failed to join room {room_id} by user {user_id}: {e}")
            raise ValidationException("Failed to join room")

    async def leave_room(self, room_id: int, user_id: int) -> bool:
        """ルームから退出"""
        try:
            # ルーム取得
            room = await self.chat_room_repository.get(self.db, room_id)
            if not room:
                raise NotFoundException("Chat room not found")

            # 参加者として削除
            success = await self.chat_participant_repository.remove_user_from_room(
                self.db, room_id, user_id
            )

            if success:
                # 参加者数を更新
                await self.chat_room_repository.update_participant_count(
                    self.db, room_id, max(0, room.current_participants - 1)
                )
                logger.info(f"User {user_id} left room {room_id}")
                return True
            else:
                return False

        except NotFoundException:
            raise
        except Exception as e:
            logger.error(f"Failed to leave room {room_id} by user {user_id}: {e}")
            raise ValidationException("Failed to leave room")

    async def get_room_participants(
        self, room_id: int, user_id: int
    ) -> ChatRoomParticipantListResponse:
        """ルームの参加者一覧を取得"""
        try:
            # ルーム取得
            room = await self.chat_room_repository.get(self.db, room_id)
            if not room:
                raise NotFoundException("Chat room not found")

            # 権限チェック
            if room.created_by != user_id and not room.is_public:
                raise PermissionException("Access denied")

            # 参加者一覧取得
            participants = await self.chat_participant_repository.get_room_participants(
                self.db, room_id
            )

            # オンライン参加者数を計算
            online_count = sum(1 for p in participants if p.is_online)

            # レスポンス形式に変換
            participant_responses = [
                ChatRoomParticipantResponse.model_validate(p) for p in participants
            ]

            return ChatRoomParticipantListResponse(
                participants=participant_responses,
                total=len(participant_responses),
                online_count=online_count,
            )

        except (NotFoundException, PermissionException):
            raise
        except Exception as e:
            logger.error(f"Failed to get room participants for room {room_id}: {e}")
            raise ValidationException("Failed to get room participants")

    async def search_rooms(
        self, user_id: int, search_term: str, query_params: ChatRoomQueryParams
    ) -> ChatRoomListResponse:
        """チャットルームを検索"""
        try:
            # 検索実行
            rooms = await self.chat_room_repository.search_rooms(
                self.db,
                search_term=search_term,
                skip=(query_params.page - 1) * query_params.size,
                limit=query_params.size,
            )

            # 総件数取得（簡易版）
            total = len(rooms)

            # レスポンス形式に変換
            room_responses = [ChatRoomResponse.model_validate(room) for room in rooms]

            return ChatRoomListResponse(
                rooms=room_responses,
                total=total,
                page=query_params.page,
                size=query_params.size,
                pages=(total + query_params.size - 1) // query_params.size,
            )

        except Exception as e:
            logger.error(f"Failed to search rooms for user {user_id}: {e}")
            raise ValidationException("Failed to search rooms")

    async def get_room_stats(self, user_id: int) -> ChatRoomStats:
        """チャットルーム統計を取得"""
        try:
            # 統計情報取得
            total_rooms = await self.chat_room_repository.count(
                self.db, filters={"created_by": user_id}
            )

            active_rooms = await self.chat_room_repository.count(
                self.db, filters={"created_by": user_id, "status": "active"}
            )

            # メッセージ統計
            user_messages = await self.chat_message_repository.get_user_messages(
                self.db, user_id, limit=1000
            )
            total_messages = len(user_messages)

            # 参加者統計
            user_participations = (
                await self.chat_participant_repository.get_user_participations(
                    self.db, user_id, limit=1000
                )
            )
            total_participants = len(user_participations)

            # 平均メッセージ数
            average_messages_per_room = (
                total_messages / total_rooms if total_rooms > 0 else 0
            )

            return ChatRoomStats(
                total_rooms=total_rooms,
                active_rooms=active_rooms,
                total_messages=total_messages,
                total_participants=total_participants,
                average_messages_per_room=average_messages_per_room,
                most_active_room=None,  # TODO: 実装
            )

        except Exception as e:
            logger.error(f"Failed to get room stats for user {user_id}: {e}")
            raise ValidationException("Failed to get room stats")

    async def generate_room_id(self) -> str:
        """ユニークなルームIDを生成"""
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
