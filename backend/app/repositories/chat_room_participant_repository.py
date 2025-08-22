from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, asc
from sqlalchemy.orm import selectinload
import structlog

from app.models.chat_room import ChatRoomParticipant
from app.repositories.base import BaseRepository

logger = structlog.get_logger()


class ChatRoomParticipantRepository(BaseRepository[ChatRoomParticipant, Any, Any]):
    """チャットルーム参加者リポジトリ"""

    def __init__(self):
        super().__init__(ChatRoomParticipant)

    async def get_by_room_and_user(
        self, db: AsyncSession, chat_room_id: int, user_id: int
    ) -> Optional[ChatRoomParticipant]:
        """ルームとユーザーIDで参加者を取得"""
        result = await db.execute(
            select(ChatRoomParticipant).where(
                and_(
                    ChatRoomParticipant.chat_room_id == chat_room_id,
                    ChatRoomParticipant.user_id == user_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_chat_room(
        self, db: AsyncSession, chat_room_id: int
    ) -> List[ChatRoomParticipant]:
        """チャットルームの参加者一覧を取得"""
        result = await db.execute(
            select(ChatRoomParticipant)
            .where(ChatRoomParticipant.chat_room_id == chat_room_id)
            .order_by(desc(ChatRoomParticipant.joined_at))
        )
        return result.scalars().all()

    async def get_by_user(
        self, db: AsyncSession, user_id: int
    ) -> List[ChatRoomParticipant]:
        """ユーザーが参加しているルーム一覧を取得"""
        result = await db.execute(
            select(ChatRoomParticipant)
            .where(ChatRoomParticipant.user_id == user_id)
            .order_by(desc(ChatRoomParticipant.joined_at))
        )
        return result.scalars().all()

    async def get_online_participants(
        self, db: AsyncSession, chat_room_id: int
    ) -> List[ChatRoomParticipant]:
        """オンライン参加者を取得"""
        result = await db.execute(
            select(ChatRoomParticipant)
            .where(
                and_(
                    ChatRoomParticipant.chat_room_id == chat_room_id,
                    ChatRoomParticipant.is_online == True
                )
            )
            .order_by(desc(ChatRoomParticipant.last_active_at))
        )
        return result.scalars().all()

    async def get_moderators(
        self, db: AsyncSession, chat_room_id: int
    ) -> List[ChatRoomParticipant]:
        """モデレーター一覧を取得"""
        result = await db.execute(
            select(ChatRoomParticipant)
            .where(
                and_(
                    ChatRoomParticipant.chat_room_id == chat_room_id,
                    ChatRoomParticipant.role.in_(["moderator", "admin"])
                )
            )
            .order_by(desc(ChatRoomParticipant.joined_at))
        )
        return result.scalars().all()

    async def add_participant(
        self, db: AsyncSession, participant_data: Dict[str, Any]
    ) -> ChatRoomParticipant:
        """参加者を追加"""
        db_participant = ChatRoomParticipant(**participant_data)
        db.add(db_participant)
        await db.commit()
        await db.refresh(db_participant)
        return db_participant

    async def update_participant_role(
        self, db: AsyncSession, chat_room_id: int, user_id: int, new_role: str
    ) -> Optional[ChatRoomParticipant]:
        """参加者の役割を更新"""
        participant = await self.get_by_room_and_user(db, chat_room_id, user_id)
        if not participant:
            return None
        
        participant.set_role(new_role)
        await db.commit()
        await db.refresh(participant)
        return participant

    async def update_participant_status(
        self, db: AsyncSession, chat_room_id: int, user_id: int, new_status: str
    ) -> Optional[ChatRoomParticipant]:
        """参加者のステータスを更新"""
        participant = await self.get_by_room_and_user(db, chat_room_id, user_id)
        if not participant:
            return None
        
        participant.set_status(new_status)
        await db.commit()
        await db.refresh(participant)
        return participant

    async def set_online_status(
        self, db: AsyncSession, chat_room_id: int, user_id: int, is_online: bool
    ) -> Optional[ChatRoomParticipant]:
        """オンラインステータスを設定"""
        participant = await self.get_by_room_and_user(db, chat_room_id, user_id)
        if not participant:
            return None
        
        participant.is_online = is_online
        if is_online:
            participant.update_last_active()
        
        await db.commit()
        await db.refresh(participant)
        return participant

    async def remove_participant(
        self, db: AsyncSession, chat_room_id: int, user_id: int
    ) -> bool:
        """参加者を削除"""
        participant = await self.get_by_room_and_user(db, chat_room_id, user_id)
        if not participant:
            return False
        
        await db.delete(participant)
        await db.commit()
        return True

    async def get_participant_count(self, db: AsyncSession, chat_room_id: int) -> int:
        """参加者数を取得"""
        result = await db.execute(
            select(ChatRoomParticipant.id)
            .where(ChatRoomParticipant.chat_room_id == chat_room_id)
        )
        return len(result.scalars().all())

    async def is_user_in_room(
        self, db: AsyncSession, chat_room_id: int, user_id: int
    ) -> bool:
        """ユーザーがルームに参加しているかチェック"""
        participant = await self.get_by_room_and_user(db, chat_room_id, user_id)
        return participant is not None

    async def get_user_role(
        self, db: AsyncSession, chat_room_id: int, user_id: int
    ) -> Optional[str]:
        """ユーザーの役割を取得"""
        participant = await self.get_by_room_and_user(db, chat_room_id, user_id)
        return participant.role if participant else None


# シングルトンインスタンス
chat_room_participant_repository = ChatRoomParticipantRepository()
