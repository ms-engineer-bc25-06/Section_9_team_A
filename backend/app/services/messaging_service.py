from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import structlog
from dataclasses import dataclass
import json

from app.core.websocket import manager
from app.models.user import User

logger = structlog.get_logger()


class MessageType(str, Enum):
    """メッセージタイプ"""

    TEXT = "text"  # テキストメッセージ
    SYSTEM = "system"  # システムメッセージ
    EMOJI = "emoji"  # 絵文字・リアクション
    NOTIFICATION = "notification"  # 通知メッセージ
    ERROR = "error"  # エラーメッセージ


class MessagePriority(str, Enum):
    """メッセージ優先度"""

    LOW = "low"  # 低優先度
    NORMAL = "normal"  # 通常優先度
    HIGH = "high"  # 高優先度
    URGENT = "urgent"  # 緊急優先度


@dataclass
class Message:
    """メッセージデータ"""

    id: str
    session_id: str
    user_id: int
    message_type: MessageType
    content: str
    timestamp: datetime
    priority: MessagePriority = MessagePriority.NORMAL
    metadata: Dict[str, Any] = None
    edited_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class MessagingService:
    """メッセージングサービス"""

    def __init__(self):
        # セッション別メッセージ履歴
        self.session_messages: Dict[str, List[Message]] = {}
        # メッセージID管理
        self.message_counter: Dict[str, int] = {}
        # メッセージ配信状態
        self.message_delivery_status: Dict[str, Dict[str, bool]] = {}

    async def send_text_message(
        self,
        session_id: str,
        user_id: int,
        content: str,
        priority: MessagePriority = MessagePriority.NORMAL,
    ) -> Message:
        """テキストメッセージを送信"""
        try:
            # メッセージを作成
            message = await self._create_message(
                session_id, user_id, MessageType.TEXT, content, priority
            )

            # メッセージを保存
            await self._save_message(message)

            # メッセージをブロードキャスト
            await self._broadcast_message(message)

            logger.info(
                f"Text message sent: {message.id} in session {session_id}",
                user_id=user_id,
                content_length=len(content),
            )

            return message

        except Exception as e:
            logger.error(f"Failed to send text message: {e}")
            raise

    async def send_system_message(
        self,
        session_id: str,
        content: str,
        priority: MessagePriority = MessagePriority.NORMAL,
    ) -> Message:
        """システムメッセージを送信"""
        try:
            # システムメッセージを作成（user_id = 0）
            message = await self._create_message(
                session_id, 0, MessageType.SYSTEM, content, priority
            )

            # メッセージを保存
            await self._save_message(message)

            # メッセージをブロードキャスト
            await self._broadcast_message(message)

            logger.info(
                f"System message sent: {message.id} in session {session_id}",
                content=content,
            )

            return message

        except Exception as e:
            logger.error(f"Failed to send system message: {e}")
            raise

    async def send_emoji_reaction(
        self, session_id: str, user_id: int, target_message_id: str, emoji: str
    ) -> Message:
        """絵文字リアクションを送信"""
        try:
            content = f"reacted with {emoji} to message {target_message_id}"

            # リアクションメッセージを作成
            message = await self._create_message(
                session_id, user_id, MessageType.EMOJI, content, MessagePriority.LOW
            )

            # メタデータにリアクション情報を追加
            message.metadata = {
                "target_message_id": target_message_id,
                "emoji": emoji,
                "reaction_type": "emoji",
            }

            # メッセージを保存
            await self._save_message(message)

            # メッセージをブロードキャスト
            await self._broadcast_message(message)

            logger.info(
                f"Emoji reaction sent: {emoji} to message {target_message_id}",
                user_id=user_id,
                session_id=session_id,
            )

            return message

        except Exception as e:
            logger.error(f"Failed to send emoji reaction: {e}")
            raise

    async def send_notification(
        self, session_id: str, content: str, notification_type: str = "info"
    ) -> Message:
        """通知メッセージを送信"""
        try:
            # 通知メッセージを作成
            message = await self._create_message(
                session_id, 0, MessageType.NOTIFICATION, content, MessagePriority.HIGH
            )

            # メタデータに通知タイプを追加
            message.metadata = {
                "notification_type": notification_type,
                "auto_dismiss": True,
            }

            # メッセージを保存
            await self._save_message(message)

            # メッセージをブロードキャスト
            await self._broadcast_message(message)

            logger.info(
                f"Notification sent: {content} in session {session_id}",
                notification_type=notification_type,
            )

            return message

        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            raise

    async def edit_message(
        self, session_id: str, message_id: str, user_id: int, new_content: str
    ) -> Optional[Message]:
        """メッセージを編集"""
        try:
            # メッセージを検索
            message = await self._find_message(session_id, message_id)
            if not message:
                raise ValueError("Message not found")

            # 権限チェック（自分のメッセージのみ編集可能）
            if message.user_id != user_id:
                raise PermissionError("Cannot edit other user's message")

            # メッセージを更新
            message.content = new_content
            message.edited_at = datetime.now()

            # 編集通知をブロードキャスト
            await self._broadcast_message_update(message)

            logger.info(
                f"Message edited: {message_id} in session {session_id}",
                user_id=user_id,
                new_content=new_content,
            )

            return message

        except Exception as e:
            logger.error(f"Failed to edit message: {e}")
            raise

    async def delete_message(
        self, session_id: str, message_id: str, user_id: int
    ) -> bool:
        """メッセージを削除"""
        try:
            # メッセージを検索
            message = await self._find_message(session_id, message_id)
            if not message:
                raise ValueError("Message not found")

            # 権限チェック（自分のメッセージのみ削除可能）
            if message.user_id != user_id:
                raise PermissionError("Cannot delete other user's message")

            # メッセージを論理削除
            message.deleted_at = datetime.now()

            # 削除通知をブロードキャスト
            await self._broadcast_message_deletion(message)

            logger.info(
                f"Message deleted: {message_id} in session {session_id}",
                user_id=user_id,
            )

            return True

        except Exception as e:
            logger.error(f"Failed to delete message: {e}")
            raise

    async def get_session_messages(
        self, session_id: str, limit: int = 50, offset: int = 0
    ) -> List[Message]:
        """セッションのメッセージ履歴を取得"""
        try:
            if session_id in self.session_messages:
                messages = self.session_messages[session_id]
                # 削除されていないメッセージのみ取得
                active_messages = [msg for msg in messages if not msg.deleted_at]
                return active_messages[offset : offset + limit]
            return []

        except Exception as e:
            logger.error(f"Failed to get session messages: {e}")
            return []

    async def search_messages(
        self, session_id: str, query: str, limit: int = 20
    ) -> List[Message]:
        """メッセージを検索"""
        try:
            if session_id not in self.session_messages:
                return []

            messages = self.session_messages[session_id]
            query_lower = query.lower()

            # 削除されていないメッセージから検索
            matching_messages = [
                msg
                for msg in messages
                if not msg.deleted_at and query_lower in msg.content.lower()
            ]

            return matching_messages[-limit:]

        except Exception as e:
            logger.error(f"Failed to search messages: {e}")
            return []

    async def _create_message(
        self,
        session_id: str,
        user_id: int,
        message_type: MessageType,
        content: str,
        priority: MessagePriority,
    ) -> Message:
        """メッセージを作成"""
        # メッセージIDを生成
        if session_id not in self.message_counter:
            self.message_counter[session_id] = 0

        self.message_counter[session_id] += 1
        message_id = f"{session_id}_{self.message_counter[session_id]}"

        return Message(
            id=message_id,
            session_id=session_id,
            user_id=user_id,
            message_type=message_type,
            content=content,
            timestamp=datetime.now(),
            priority=priority,
        )

    async def _save_message(self, message: Message):
        """メッセージを保存"""
        if message.session_id not in self.session_messages:
            self.session_messages[message.session_id] = []

        self.session_messages[message.session_id].append(message)

        # メッセージ履歴サイズ制限（最新1000件まで保持）
        if len(self.session_messages[message.session_id]) > 1000:
            self.session_messages[message.session_id] = self.session_messages[
                message.session_id
            ][-1000:]

    async def _find_message(
        self, session_id: str, message_id: str
    ) -> Optional[Message]:
        """メッセージを検索"""
        if session_id in self.session_messages:
            for message in self.session_messages[session_id]:
                if message.id == message_id:
                    return message
        return None

    async def _broadcast_message(self, message: Message):
        """メッセージをブロードキャスト"""
        message_data = {
            "type": "message",
            "message": {
                "id": message.id,
                "session_id": message.session_id,
                "user_id": message.user_id,
                "message_type": message.message_type.value,
                "content": message.content,
                "timestamp": message.timestamp.isoformat(),
                "priority": message.priority.value,
                "metadata": message.metadata or {},
            },
        }

        await manager.broadcast_to_session(message_data, message.session_id)

    async def _broadcast_message_update(self, message: Message):
        """メッセージ更新をブロードキャスト"""
        update_data = {
            "type": "message_updated",
            "message": {
                "id": message.id,
                "session_id": message.session_id,
                "content": message.content,
                "edited_at": message.edited_at.isoformat()
                if message.edited_at
                else None,
            },
        }

        await manager.broadcast_to_session(update_data, message.session_id)

    async def _broadcast_message_deletion(self, message: Message):
        """メッセージ削除をブロードキャスト"""
        deletion_data = {
            "type": "message_deleted",
            "message": {
                "id": message.id,
                "session_id": message.session_id,
                "deleted_at": message.deleted_at.isoformat()
                if message.deleted_at
                else None,
            },
        }

        await manager.broadcast_to_session(deletion_data, message.session_id)


# グローバルメッセージングサービスインスタンス
messaging_service = MessagingService()
