from typing import Optional, List, Dict, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func, desc, asc
from sqlalchemy.orm import joinedload
import structlog
from datetime import datetime

from app.models.chat_room import ChatRoom, ChatMessage, ChatRoomParticipant
from app.models.user import User
from app.models.team import Team
from app.repositories.base import BaseRepository
from app.schemas.chat_room import (
    ChatRoomCreate,
    ChatRoomUpdate,
    ChatMessageCreate,
    ChatMessageUpdate,
    ChatRoomParticipantCreate,
    ChatRoomParticipantUpdate,
    ChatRoomQueryParams,
    ChatMessageQueryParams,
)

logger = structlog.get_logger()


class ChatRoomRepository(BaseRepository[ChatRoom, ChatRoomCreate, ChatRoomUpdate]):
    """チャットルームリポジトリ"""

    def __init__(self):
        super().__init__(ChatRoom)

    async def get_by_room_id(
        self, db: AsyncSession, room_id: str
    ) -> Optional[ChatRoom]:
        """ルームIDでチャットルームを取得"""
        try:
            result = await db.execute(
                select(ChatRoom).where(ChatRoom.room_id == room_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get chat room by room_id {room_id}: {e}")
            return None

    async def get_room_with_relations(
        self, db: AsyncSession, room_id: int
    ) -> Optional[ChatRoom]:
        """関連データを含むチャットルームを取得"""
        try:
            result = await db.execute(
                select(ChatRoom)
                .options(
                    joinedload(ChatRoom.creator),
                    joinedload(ChatRoom.team),
                    joinedload(ChatRoom.messages).joinedload(ChatMessage.sender),
                )
                .where(ChatRoom.id == room_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get chat room with relations {room_id}: {e}")
            return None

    async def get_public_rooms(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[ChatRoom]:
        """公開チャットルーム一覧を取得"""
        try:
            query = select(ChatRoom).where(ChatRoom.is_public == True)

            if filters:
                query = self._apply_filters(query, filters)

            query = query.offset(skip).limit(limit).order_by(desc(ChatRoom.created_at))

            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get public chat rooms: {e}")
            return []

    async def get_rooms_by_creator(
        self,
        db: AsyncSession,
        created_by: int,
        skip: int = 0,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[ChatRoom]:
        """作成者別チャットルーム一覧を取得"""
        try:
            query = select(ChatRoom).where(ChatRoom.created_by == created_by)

            if filters:
                query = self._apply_filters(query, filters)

            query = query.offset(skip).limit(limit).order_by(desc(ChatRoom.created_at))

            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get chat rooms by creator {created_by}: {e}")
            return []

    async def get_rooms_by_team(
        self,
        db: AsyncSession,
        team_id: int,
        skip: int = 0,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[ChatRoom]:
        """チーム別チャットルーム一覧を取得"""
        try:
            query = select(ChatRoom).where(ChatRoom.team_id == team_id)

            if filters:
                query = self._apply_filters(query, filters)

            query = query.offset(skip).limit(limit).order_by(desc(ChatRoom.created_at))

            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get chat rooms by team {team_id}: {e}")
            return []

    async def search_rooms(
        self,
        db: AsyncSession,
        search_term: str,
        skip: int = 0,
        limit: int = 10,
    ) -> List[ChatRoom]:
        """チャットルームを検索"""
        try:
            query = select(ChatRoom).where(
                or_(
                    ChatRoom.name.ilike(f"%{search_term}%"),
                    ChatRoom.description.ilike(f"%{search_term}%"),
                )
            )

            query = query.offset(skip).limit(limit).order_by(desc(ChatRoom.created_at))

            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to search chat rooms: {e}")
            return []

    async def update_participant_count(
        self, db: AsyncSession, room_id: int, count: int
    ) -> Optional[ChatRoom]:
        """参加者数を更新"""
        try:
            result = await db.execute(
                update(ChatRoom)
                .where(ChatRoom.id == room_id)
                .values(current_participants=count)
                .returning(ChatRoom)
            )
            await db.commit()
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to update participant count for room {room_id}: {e}")
            await db.rollback()
            return None

    async def update_room_status(
        self, db: AsyncSession, room_id: int, status: str
    ) -> Optional[ChatRoom]:
        """ルームステータスを更新"""
        try:
            result = await db.execute(
                update(ChatRoom)
                .where(ChatRoom.id == room_id)
                .values(status=status)
                .returning(ChatRoom)
            )
            await db.commit()
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to update room status for room {room_id}: {e}")
            await db.rollback()
            return None

    async def room_exists_by_room_id(self, db: AsyncSession, room_id: str) -> bool:
        """ルームIDの存在チェック"""
        try:
            result = await db.execute(
                select(func.count(ChatRoom.id)).where(ChatRoom.room_id == room_id)
            )
            return result.scalar() > 0
        except Exception as e:
            logger.error(f"Failed to check room existence for room_id {room_id}: {e}")
            return False

    def _apply_filters(self, query, filters: Dict[str, Any]):
        """フィルターを適用"""
        if filters.get("status"):
            query = query.where(ChatRoom.status == filters["status"])

        if filters.get("room_type"):
            query = query.where(ChatRoom.room_type == filters["room_type"])

        if filters.get("is_public") is not None:
            query = query.where(ChatRoom.is_public == filters["is_public"])

        if filters.get("is_active") is not None:
            query = query.where(ChatRoom.is_active == filters["is_active"])

        if filters.get("search"):
            search_term = filters["search"]
            query = query.where(
                or_(
                    ChatRoom.name.ilike(f"%{search_term}%"),
                    ChatRoom.description.ilike(f"%{search_term}%"),
                )
            )

        return query


class ChatMessageRepository(
    BaseRepository[ChatMessage, ChatMessageCreate, ChatMessageUpdate]
):
    """チャットメッセージリポジトリ"""

    def __init__(self):
        super().__init__(ChatMessage)

    async def get_by_message_id(
        self, db: AsyncSession, message_id: str
    ) -> Optional[ChatMessage]:
        """メッセージIDでメッセージを取得"""
        try:
            result = await db.execute(
                select(ChatMessage).where(ChatMessage.message_id == message_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get message by message_id {message_id}: {e}")
            return None

    async def get_room_messages(
        self,
        db: AsyncSession,
        room_id: int,
        skip: int = 0,
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[ChatMessage]:
        """ルームのメッセージ一覧を取得"""
        try:
            query = select(ChatMessage).where(ChatMessage.chat_room_id == room_id)

            if filters:
                query = self._apply_message_filters(query, filters)

            query = (
                query.offset(skip).limit(limit).order_by(desc(ChatMessage.created_at))
            )

            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get room messages for room {room_id}: {e}")
            return []

    async def get_user_messages(
        self,
        db: AsyncSession,
        sender_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> List[ChatMessage]:
        """ユーザーのメッセージ一覧を取得"""
        try:
            query = (
                select(ChatMessage)
                .where(ChatMessage.sender_id == sender_id)
                .offset(skip)
                .limit(limit)
                .order_by(desc(ChatMessage.created_at))
            )

            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get user messages for sender {sender_id}: {e}")
            return []

    async def message_exists_by_message_id(
        self, db: AsyncSession, message_id: str
    ) -> bool:
        """メッセージIDの存在チェック"""
        try:
            result = await db.execute(
                select(func.count(ChatMessage.id)).where(
                    ChatMessage.message_id == message_id
                )
            )
            return result.scalar() > 0
        except Exception as e:
            logger.error(
                f"Failed to check message existence for message_id {message_id}: {e}"
            )
            return False

    def _apply_message_filters(self, query, filters: Dict[str, Any]):
        """メッセージフィルターを適用"""
        if filters.get("message_type"):
            query = query.where(ChatMessage.message_type == filters["message_type"])

        if filters.get("is_deleted") is not None:
            query = query.where(ChatMessage.is_deleted == filters["is_deleted"])

        if filters.get("sender_id"):
            query = query.where(ChatMessage.sender_id == filters["sender_id"])

        return query


class ChatRoomParticipantRepository(
    BaseRepository[
        ChatRoomParticipant, ChatRoomParticipantCreate, ChatRoomParticipantUpdate
    ]
):
    """チャットルーム参加者リポジトリ"""

    def __init__(self):
        super().__init__(ChatRoomParticipant)

    async def get_room_participants(
        self,
        db: AsyncSession,
        room_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> List[ChatRoomParticipant]:
        """ルームの参加者一覧を取得"""
        try:
            query = (
                select(ChatRoomParticipant)
                .where(ChatRoomParticipant.chat_room_id == room_id)
                .offset(skip)
                .limit(limit)
                .order_by(desc(ChatRoomParticipant.joined_at))
            )

            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get room participants for room {room_id}: {e}")
            return []

    async def get_user_participations(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> List[ChatRoomParticipant]:
        """ユーザーの参加ルーム一覧を取得"""
        try:
            query = (
                select(ChatRoomParticipant)
                .where(ChatRoomParticipant.user_id == user_id)
                .offset(skip)
                .limit(limit)
                .order_by(desc(ChatRoomParticipant.joined_at))
            )

            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get user participations for user {user_id}: {e}")
            return []

    async def is_user_in_room(
        self, db: AsyncSession, room_id: int, user_id: int
    ) -> bool:
        """ユーザーがルームに参加しているかチェック"""
        try:
            result = await db.execute(
                select(func.count(ChatRoomParticipant.id)).where(
                    and_(
                        ChatRoomParticipant.chat_room_id == room_id,
                        ChatRoomParticipant.user_id == user_id,
                    )
                )
            )
            return result.scalar() > 0
        except Exception as e:
            logger.error(f"Failed to check user participation: {e}")
            return False

    async def update_user_online_status(
        self, db: AsyncSession, room_id: int, user_id: int, is_online: bool
    ) -> Optional[ChatRoomParticipant]:
        """ユーザーのオンライン状態を更新"""
        try:
            result = await db.execute(
                update(ChatRoomParticipant)
                .where(
                    and_(
                        ChatRoomParticipant.chat_room_id == room_id,
                        ChatRoomParticipant.user_id == user_id,
                    )
                )
                .values(
                    is_online=is_online,
                    last_active_at=datetime.utcnow() if is_online else None,
                )
                .returning(ChatRoomParticipant)
            )
            await db.commit()
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to update user online status: {e}")
            await db.rollback()
            return None

    async def remove_user_from_room(
        self, db: AsyncSession, room_id: int, user_id: int
    ) -> bool:
        """ユーザーをルームから削除"""
        try:
            result = await db.execute(
                delete(ChatRoomParticipant).where(
                    and_(
                        ChatRoomParticipant.chat_room_id == room_id,
                        ChatRoomParticipant.user_id == user_id,
                    )
                )
            )
            await db.commit()
            return result.rowcount > 0
        except Exception as e:
            logger.error(f"Failed to remove user from room: {e}")
            await db.rollback()
            return False
