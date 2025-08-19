import asyncio
import time
from typing import Dict, List, Optional, Set, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import structlog
from datetime import datetime, timedelta
import json
import bleach

from app.schemas.websocket import (
    WebSocketMessageType,
    MessagePriority,
    WebSocketMessage,
    WebSocketBaseMessage,
)
from app.models.user import User

logger = structlog.get_logger()


class MessageStatus(str, Enum):
    """メッセージステータス"""

    PENDING = "pending"
    PROCESSING = "processing"
    DELIVERED = "delivered"
    FAILED = "failed"
    REJECTED = "rejected"


@dataclass
class QueuedMessage:
    """キューイングされたメッセージ"""

    id: str
    message: WebSocketMessage
    priority: MessagePriority
    session_id: str
    user_id: int
    created_at: datetime
    expires_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    status: MessageStatus = MessageStatus.PENDING
    target_connections: Optional[Set[str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class MessageValidator:
    """メッセージバリデーター"""

    # 許可されるHTMLタグ
    ALLOWED_TAGS = ["b", "i", "u", "em", "strong", "code", "pre", "br"]
    ALLOWED_ATTRIBUTES = {}

    def __init__(self):
        self.max_message_size = 4096  # 4KB
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.allowed_file_types = {
            "image": ["png", "jpg", "jpeg", "gif", "webp"],
            "document": ["pdf", "doc", "docx", "txt", "md"],
            "audio": ["mp3", "wav", "ogg", "m4a"],
            "video": ["mp4", "webm", "mov"],
        }

    async def validate_message(self, message: dict, user: User) -> bool:
        """メッセージの検証"""
        try:
            # メッセージサイズチェック
            message_size = len(json.dumps(message))
            if message_size > self.max_message_size:
                logger.warning(
                    f"Message too large: {message_size} bytes", user_id=user.id
                )
                return False

            # 必須フィールドチェック
            if "type" not in message:
                logger.warning("Missing message type", user_id=user.id)
                return False

            message_type = message.get("type")

            # メッセージタイプ別の検証
            if message_type == WebSocketMessageType.TEXT_MESSAGE:
                return await self._validate_text_message(message, user)
            elif message_type == WebSocketMessageType.FILE_SHARE:
                return await self._validate_file_share(message, user)
            elif message_type == WebSocketMessageType.POLL_CREATE:
                return await self._validate_poll_create(message, user)
            elif message_type in [
                WebSocketMessageType.EMOJI_REACTION,
                WebSocketMessageType.EDIT_MESSAGE,
                WebSocketMessageType.DELETE_MESSAGE,
            ]:
                return await self._validate_message_reference(message, user)

            return True

        except Exception as e:
            logger.error(f"Message validation error: {e}", user_id=user.id)
            return False

    async def _validate_text_message(self, message: dict, user: User) -> bool:
        """テキストメッセージの検証"""
        content = message.get("content", "")

        # 空メッセージチェック
        if not content.strip():
            return False

        # 長さチェック
        if len(content) > 2000:
            logger.warning(
                f"Text message too long: {len(content)} chars", user_id=user.id
            )
            return False

        # HTMLサニタイゼーション
        cleaned_content = bleach.clean(
            content,
            tags=self.ALLOWED_TAGS,
            attributes=self.ALLOWED_ATTRIBUTES,
            strip=True,
        )

        # サニタイゼーション後に変更があった場合は警告
        if cleaned_content != content:
            logger.warning("Message content was sanitized", user_id=user.id)
            message["content"] = cleaned_content

        return True

    async def _validate_file_share(self, message: dict, user: User) -> bool:
        """ファイル共有の検証"""
        file_size = message.get("file_size", 0)
        file_type = message.get("file_type", "").lower()
        file_name = message.get("file_name", "")

        # ファイルサイズチェック
        if file_size > self.max_file_size:
            logger.warning(f"File too large: {file_size} bytes", user_id=user.id)
            return False

        # ファイル名チェック
        if not file_name or len(file_name) > 255:
            logger.warning(f"Invalid file name: {file_name}", user_id=user.id)
            return False

        # ファイルタイプチェック
        file_extension = file_name.split(".")[-1].lower() if "." in file_name else ""
        allowed_extensions = []
        for extensions in self.allowed_file_types.values():
            allowed_extensions.extend(extensions)

        if file_extension not in allowed_extensions:
            logger.warning(f"File type not allowed: {file_extension}", user_id=user.id)
            return False

        return True

    async def _validate_poll_create(self, message: dict, user: User) -> bool:
        """投票作成の検証"""
        question = message.get("question", "")
        options = message.get("options", [])

        # 質問チェック
        if not question.strip() or len(question) > 500:
            logger.warning(
                f"Invalid poll question: {len(question)} chars", user_id=user.id
            )
            return False

        # 選択肢チェック
        if len(options) < 2 or len(options) > 10:
            logger.warning(
                f"Invalid poll options count: {len(options)}", user_id=user.id
            )
            return False

        for option in options:
            if not isinstance(option, dict) or "text" not in option:
                return False
            if not option["text"].strip() or len(option["text"]) > 200:
                return False

        return True

    async def _validate_message_reference(self, message: dict, user: User) -> bool:
        """メッセージ参照の検証"""
        if message.get("type") == WebSocketMessageType.EMOJI_REACTION:
            return "target_message_id" in message and "emoji" in message
        elif message.get("type") in [
            WebSocketMessageType.EDIT_MESSAGE,
            WebSocketMessageType.DELETE_MESSAGE,
        ]:
            return "message_id" in message

        return False


class RateLimiter:
    """レート制限器"""

    def __init__(self):
        self.user_requests: Dict[int, List[float]] = {}
        self.limits = {
            MessagePriority.LOW: (10, 60),  # 10回/分
            MessagePriority.NORMAL: (30, 60),  # 30回/分
            MessagePriority.HIGH: (60, 60),  # 60回/分
            MessagePriority.URGENT: (100, 60),  # 100回/分
        }

    async def is_allowed(self, user_id: int, priority: MessagePriority) -> bool:
        """レート制限チェック"""
        current_time = time.time()

        if user_id not in self.user_requests:
            self.user_requests[user_id] = []

        # 古いリクエストを削除
        window_size = self.limits[priority][1]
        self.user_requests[user_id] = [
            req_time
            for req_time in self.user_requests[user_id]
            if current_time - req_time < window_size
        ]

        # 制限チェック
        max_requests = self.limits[priority][0]
        if len(self.user_requests[user_id]) >= max_requests:
            logger.warning(
                f"Rate limit exceeded", user_id=user_id, priority=priority.value
            )
            return False

        # リクエストを記録
        self.user_requests[user_id].append(current_time)
        return True


class MessageRouter:
    """メッセージルーター"""

    def __init__(self):
        self.message_queues: Dict[MessagePriority, asyncio.Queue] = {
            priority: asyncio.Queue() for priority in MessagePriority
        }
        self.handlers: Dict[WebSocketMessageType, Callable] = {}
        self.validator = MessageValidator()
        self.rate_limiter = RateLimiter()
        self.processing_tasks: Set[asyncio.Task] = set()
        self.message_counter = 0
        self.active_sessions: Set[str] = set()

        # 統計情報
        self.stats = {
            "messages_processed": 0,
            "messages_failed": 0,
            "messages_rejected": 0,
            "avg_processing_time": 0.0,
        }

    def register_handler(self, message_type: WebSocketMessageType, handler: Callable):
        """メッセージハンドラーの登録"""
        self.handlers[message_type] = handler
        logger.info(f"Registered handler for {message_type.value}")

    async def route_message(
        self, message: dict, user: User, session_id: str, connection_id: str
    ) -> bool:
        """メッセージのルーティング"""
        try:
            start_time = time.time()

            # メッセージの検証
            if not await self.validator.validate_message(message, user):
                self.stats["messages_rejected"] += 1
                return False

            # 優先度の決定
            priority = MessagePriority(
                message.get("priority", MessagePriority.NORMAL.value)
            )

            # レート制限チェック
            if not await self.rate_limiter.is_allowed(user.id, priority):
                self.stats["messages_rejected"] += 1
                return False

            # メッセージをキューに追加
            queued_message = QueuedMessage(
                id=self._generate_message_id(),
                message=message,
                priority=priority,
                session_id=session_id,
                user_id=user.id,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(minutes=5),
                metadata={"connection_id": connection_id},
            )

            await self.message_queues[priority].put(queued_message)

            # 処理時間の更新
            processing_time = time.time() - start_time
            self._update_processing_time(processing_time)

            return True

        except Exception as e:
            logger.error(f"Failed to route message: {e}", user_id=user.id)
            self.stats["messages_failed"] += 1
            return False

    async def start_processing(self):
        """メッセージ処理の開始"""
        logger.info("Starting message processing")

        # 各優先度キューの処理タスクを開始
        for priority in MessagePriority:
            task = asyncio.create_task(self._process_queue(priority))
            self.processing_tasks.add(task)
            task.add_done_callback(self.processing_tasks.discard)

    async def stop_processing(self):
        """メッセージ処理の停止"""
        logger.info("Stopping message processing")

        # 全ての処理タスクをキャンセル
        for task in self.processing_tasks:
            task.cancel()

        # タスクの完了を待機
        if self.processing_tasks:
            await asyncio.gather(*self.processing_tasks, return_exceptions=True)

    async def _process_queue(self, priority: MessagePriority):
        """キューの処理"""
        queue = self.message_queues[priority]

        while True:
            try:
                # メッセージを取得（優先度の高いキューから優先的に処理）
                timeout = 1.0 if priority == MessagePriority.URGENT else 5.0
                queued_message = await asyncio.wait_for(queue.get(), timeout=timeout)

                # メッセージの有効期限チェック
                if (
                    queued_message.expires_at
                    and datetime.now() > queued_message.expires_at
                ):
                    logger.warning(f"Message expired: {queued_message.id}")
                    continue

                # メッセージを処理
                await self._process_message(queued_message)

            except asyncio.TimeoutError:
                # タイムアウトは正常（高優先度キューを定期的にチェックするため）
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing queue {priority.value}: {e}")
                await asyncio.sleep(1)

    async def _process_message(self, queued_message: QueuedMessage):
        """個別メッセージの処理"""
        try:
            queued_message.status = MessageStatus.PROCESSING

            message_type = queued_message.message.get("type")

            # AI分析関連のメッセージを直接処理
            if message_type in [
                "ai_analysis_subscribe",
                "ai_analysis_unsubscribe",
                "ai_analysis_request",
                "ai_analysis_progress_request",
                "ai_analysis_cancel"
            ]:
                # WebSocketメッセージハンドラーで直接処理
                from app.core.websocket import WebSocketMessageHandler

                session_id = queued_message.message.get("session_id", "default")
                connection_id = queued_message.metadata.get("connection_id")

                if message_type == "ai_analysis_subscribe":
                    await WebSocketMessageHandler.handle_ai_analysis_subscribe(
                        session_id, connection_id, queued_message.user_id, queued_message.message
                    )
                elif message_type == "ai_analysis_unsubscribe":
                    await WebSocketMessageHandler.handle_ai_analysis_unsubscribe(
                        session_id, connection_id, queued_message.user_id, queued_message.message
                    )
                elif message_type == "ai_analysis_request":
                    await WebSocketMessageHandler.handle_ai_analysis_request(
                        session_id, connection_id, queued_message.user_id, queued_message.message
                    )
                elif message_type == "ai_analysis_progress_request":
                    await WebSocketMessageHandler.handle_ai_analysis_progress_request(
                        session_id, connection_id, queued_message.user_id, queued_message.message
                    )
                elif message_type == "ai_analysis_cancel":
                    await WebSocketMessageHandler.handle_ai_analysis_cancel(
                        session_id, connection_id, queued_message.user_id, queued_message.message
                    )

                queued_message.status = MessageStatus.DELIVERED
                self.stats["messages_processed"] += 1
                return

            # 通常のメッセージ処理
            message_type_enum = WebSocketMessageType(message_type)

            # ハンドラーの実行
            if message_type_enum in self.handlers:
                handler = self.handlers[message_type_enum]
                await handler(queued_message)
                queued_message.status = MessageStatus.DELIVERED
                self.stats["messages_processed"] += 1
            else:
                logger.warning(f"No handler for message type: {message_type}")
                queued_message.status = MessageStatus.FAILED
                self.stats["messages_failed"] += 1

        except Exception as e:
            logger.error(f"Failed to process message {queued_message.id}: {e}")
            queued_message.status = MessageStatus.FAILED
            queued_message.retry_count += 1

            # リトライ処理
            if queued_message.retry_count < queued_message.max_retries:
                await asyncio.sleep(2**queued_message.retry_count)  # 指数バックオフ
                await self.message_queues[queued_message.priority].put(queued_message)
            else:
                self.stats["messages_failed"] += 1

    def _generate_message_id(self) -> str:
        """メッセージIDの生成"""
        self.message_counter += 1
        return f"msg_{int(time.time())}_{self.message_counter}"

    def _update_processing_time(self, processing_time: float):
        """処理時間統計の更新"""
        if self.stats["avg_processing_time"] == 0:
            self.stats["avg_processing_time"] = processing_time
        else:
            self.stats["avg_processing_time"] = (
                self.stats["avg_processing_time"] * 0.9 + processing_time * 0.1
            )

    def get_stats(self) -> Dict[str, Any]:
        """統計情報の取得"""
        return {
            **self.stats,
            "queue_sizes": {
                priority.value: queue.qsize()
                for priority, queue in self.message_queues.items()
            },
            "active_sessions": len(self.active_sessions),
            "active_handlers": len(self.handlers),
        }


# グローバルメッセージルーター
message_router = MessageRouter()
