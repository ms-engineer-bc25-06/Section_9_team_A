from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, asc
from sqlalchemy.orm import selectinload
import structlog

from app.models.chat_room import ChatMessage
from app.repositories.base import BaseRepository
from app.schemas.chat_room import ChatMessageQueryParams

logger = structlog.get_logger()


class ChatMessageRepository(BaseRepository[ChatMessage, Any, Any]):
    """チャットメッセージリポジトリ"""

    def __init__(self):
        super().__init__(ChatMessage)

    async def get_by_message_id(
        self, db: AsyncSession, message_id: str
    ) -> Optional[ChatMessage]:
        """メッセージIDでメッセージを取得"""
        result = await db.execute(
            select(ChatMessage).where(ChatMessage.message_id == message_id)
        )
        return result.scalar_one_or_none()

    async def get_by_chat_room(
        self, db: AsyncSession, chat_room_id: int, limit: int = 100
    ) -> List[ChatMessage]:
        """チャットルームのメッセージを取得"""
        result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.chat_room_id == chat_room_id)
            .order_by(desc(ChatMessage.created_at))
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_sender(
        self, db: AsyncSession, sender_id: int, limit: int = 100
    ) -> List[ChatMessage]:
        """送信者IDでメッセージを取得"""
        result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.sender_id == sender_id)
            .order_by(desc(ChatMessage.created_at))
            .limit(limit)
        )
        return result.scalars().all()

    async def get_multi_with_filters(
        self, db: AsyncSession, query_params: ChatMessageQueryParams
    ) -> tuple[List[ChatMessage], int]:
        """フィルター付きでメッセージ一覧を取得"""
        query = select(ChatMessage)

        # フィルター適用
        if query_params.chat_room_id:
            query = query.where(ChatMessage.chat_room_id == query_params.chat_room_id)
        
        if query_params.sender_id:
            query = query.where(ChatMessage.sender_id == query_params.sender_id)
        
        if query_params.message_type:
            query = query.where(ChatMessage.message_type == query_params.message_type)
        
        if query_params.is_edited is not None:
            query = query.where(ChatMessage.is_edited == query_params.is_edited)
        
        if query_params.is_deleted is not None:
            query = query.where(ChatMessage.is_deleted == query_params.is_deleted)

        # 総件数を取得
        count_query = select(ChatMessage.id)
        for filter_condition in query.whereclause.children:
            count_query = count_query.where(filter_condition)
        
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        # ページネーション適用
        if query_params.page and query_params.size:
            offset = (query_params.page - 1) * query_params.size
            query = query.offset(offset).limit(query_params.size)

        # ソート適用
        if query_params.sort_by:
            if query_params.sort_order == "desc":
                query = query.order_by(desc(getattr(ChatMessage, query_params.sort_by)))
            else:
                query = query.order_by(asc(getattr(ChatMessage, query_params.sort_by)))
        else:
            query = query.order_by(desc(ChatMessage.created_at))

        result = await db.execute(query)
        messages = result.scalars().all()

        return messages, total

    async def create_message(
        self, db: AsyncSession, message_data: Dict[str, Any]
    ) -> ChatMessage:
        """メッセージを作成"""
        db_message = ChatMessage(**message_data)
        db.add(db_message)
        await db.commit()
        await db.refresh(db_message)
        return db_message

    async def update_message(
        self, db: AsyncSession, message_id: str, update_data: Dict[str, Any]
    ) -> Optional[ChatMessage]:
        """メッセージを更新"""
        message = await self.get_by_message_id(db, message_id)
        if not message:
            return None
        
        for field, value in update_data.items():
            if hasattr(message, field):
                setattr(message, field, value)
        
        await db.commit()
        await db.refresh(message)
        return message

    async def delete_message(self, db: AsyncSession, message_id: str) -> bool:
        """メッセージを削除（論理削除）"""
        message = await self.get_by_message_id(db, message_id)
        if not message:
            return False
        
        message.is_deleted = True
        await db.commit()
        return True

    async def get_audio_messages(
        self, db: AsyncSession, chat_room_id: int
    ) -> List[ChatMessage]:
        """音声メッセージを取得"""
        result = await db.execute(
            select(ChatMessage)
            .where(
                and_(
                    ChatMessage.chat_room_id == chat_room_id,
                    ChatMessage.message_type == "audio",
                    ChatMessage.is_deleted == False
                )
            )
            .order_by(desc(ChatMessage.created_at))
        )
        return result.scalars().all()

    async def get_system_messages(
        self, db: AsyncSession, chat_room_id: int
    ) -> List[ChatMessage]:
        """システムメッセージを取得"""
        result = await db.execute(
            select(ChatMessage)
            .where(
                and_(
                    ChatMessage.chat_room_id == chat_room_id,
                    ChatMessage.message_type == "system",
                    ChatMessage.is_deleted == False
                )
            )
            .order_by(desc(ChatMessage.created_at))
        )
        return result.scalars().all()


# シングルトンインスタンス
chat_message_repository = ChatMessageRepository()
