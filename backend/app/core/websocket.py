import json
import asyncio
from typing import Dict, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect, HTTPException, status
from fastapi.security import HTTPBearer
import structlog
from datetime import datetime, timedelta

from app.core.auth import get_current_user_from_token
from app.models.user import User
from app.core.exceptions import AuthenticationException, PermissionException

logger = structlog.get_logger()


class ConnectionManager:
    """WebSocket接続管理クラス"""

    def __init__(self):
        # アクティブな接続を管理
        self.active_connections: Dict[str, WebSocket] = {}
        # セッション別の接続を管理
        self.session_connections: Dict[str, Set[str]] = {}
        # ユーザー別の接続を管理
        self.user_connections: Dict[int, Set[str]] = {}
        # 接続情報を管理
        self.connection_info: Dict[str, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, session_id: str, user: User) -> str:
        """WebSocket接続を確立"""
        await websocket.accept()

        # 接続IDを生成
        connection_id = f"{user.id}_{session_id}_{datetime.now().timestamp()}"

        # 接続を登録
        self.active_connections[connection_id] = websocket
        self.connection_info[connection_id] = {
            "user_id": user.id,
            "session_id": session_id,
            "connected_at": datetime.now(),
            "user": user,
        }

        # セッション別接続管理
        if session_id not in self.session_connections:
            self.session_connections[session_id] = set()
        self.session_connections[session_id].add(connection_id)

        # ユーザー別接続管理
        if user.id not in self.user_connections:
            self.user_connections[user.id] = set()
        self.user_connections[user.id].add(connection_id)

        logger.info(
            f"WebSocket connected: {connection_id}",
            user_id=user.id,
            session_id=session_id,
        )

        return connection_id

    def disconnect(self, connection_id: str):
        """WebSocket接続を切断"""
        if connection_id in self.active_connections:
            # 接続情報を取得
            info = self.connection_info.get(connection_id, {})
            user_id = info.get("user_id")
            session_id = info.get("session_id")

            # 接続を削除
            del self.active_connections[connection_id]
            if connection_id in self.connection_info:
                del self.connection_info[connection_id]

            # セッション別接続から削除
            if session_id and session_id in self.session_connections:
                self.session_connections[session_id].discard(connection_id)
                if not self.session_connections[session_id]:
                    del self.session_connections[session_id]

            # ユーザー別接続から削除
            if user_id and user_id in self.user_connections:
                self.user_connections[user_id].discard(connection_id)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]

            logger.info(
                f"WebSocket disconnected: {connection_id}",
                user_id=user_id,
                session_id=session_id,
            )

    async def send_personal_message(self, message: dict, connection_id: str):
        """特定の接続にメッセージを送信"""
        if connection_id in self.active_connections:
            try:
                await self.active_connections[connection_id].send_text(
                    json.dumps(message, default=str)
                )
            except Exception as e:
                logger.error(f"Failed to send message to {connection_id}: {e}")
                self.disconnect(connection_id)

    async def broadcast_to_session(
        self, message: dict, session_id: str, exclude_connection: str = None
    ):
        """セッション内の全接続にメッセージをブロードキャスト"""
        if session_id in self.session_connections:
            for connection_id in self.session_connections[session_id]:
                if connection_id != exclude_connection:
                    await self.send_personal_message(message, connection_id)

    async def broadcast_to_user(
        self, message: dict, user_id: int, exclude_connection: str = None
    ):
        """特定ユーザーの全接続にメッセージをブロードキャスト"""
        if user_id in self.user_connections:
            for connection_id in self.user_connections[user_id]:
                if connection_id != exclude_connection:
                    await self.send_personal_message(message, connection_id)

    def get_session_participants(self, session_id: str) -> Set[int]:
        """セッションの参加者ID一覧を取得"""
        participants = set()
        if session_id in self.session_connections:
            for connection_id in self.session_connections[session_id]:
                info = self.connection_info.get(connection_id, {})
                if "user_id" in info:
                    participants.add(info["user_id"])
        return participants

    def get_user_connection_count(self, user_id: int) -> int:
        """ユーザーの接続数を取得"""
        return len(self.user_connections.get(user_id, set()))

    def get_session_connection_count(self, session_id: str) -> int:
        """セッションの接続数を取得"""
        return len(self.session_connections.get(session_id, set()))


# グローバル接続マネージャー
manager = ConnectionManager()


class WebSocketAuth:
    """WebSocket認証クラス"""

    @staticmethod
    async def authenticate_websocket(websocket: WebSocket) -> User:
        """WebSocket接続の認証"""
        try:
            # クエリパラメータからトークンを取得
            token = websocket.query_params.get("token")
            if not token:
                raise AuthenticationException("Token is required")

            # トークンの検証
            user = await get_current_user_from_token(token)
            if not user:
                raise AuthenticationException("Invalid token")

            return user

        except Exception as e:
            logger.error(f"WebSocket authentication failed: {e}")
            raise AuthenticationException("Authentication failed")


class WebSocketMessageHandler:
    """WebSocketメッセージハンドラークラス"""

    @staticmethod
    async def handle_message(
        websocket: WebSocket, message: dict, connection_id: str, user: User
    ):
        """メッセージの処理"""
        try:
            message_type = message.get("type")

            if message_type == "ping":
                await manager.send_personal_message({"type": "pong"}, connection_id)

            elif message_type == "join_session":
                session_id = message.get("session_id")
                if session_id:
                    await WebSocketMessageHandler.handle_join_session(
                        session_id, connection_id, user
                    )

            elif message_type == "leave_session":
                session_id = message.get("session_id")
                if session_id:
                    await WebSocketMessageHandler.handle_leave_session(
                        session_id, connection_id, user
                    )

            elif message_type == "audio_data":
                session_id = message.get("session_id")
                if session_id:
                    await WebSocketMessageHandler.handle_audio_data(
                        session_id, connection_id, user, message
                    )

            elif message_type == "text_message":
                session_id = message.get("session_id")
                content = message.get("content")
                if session_id and content:
                    await WebSocketMessageHandler.handle_text_message(
                        session_id, connection_id, user, message
                    )

            elif message_type == "emoji_reaction":
                session_id = message.get("session_id")
                target_message_id = message.get("target_message_id")
                emoji = message.get("emoji")
                if session_id and target_message_id and emoji:
                    await WebSocketMessageHandler.handle_emoji_reaction(
                        session_id, connection_id, user, message
                    )

            elif message_type == "edit_message":
                session_id = message.get("session_id")
                message_id = message.get("message_id")
                new_content = message.get("new_content")
                if session_id and message_id and new_content:
                    await WebSocketMessageHandler.handle_edit_message(
                        session_id, connection_id, user, message
                    )

            elif message_type == "delete_message":
                session_id = message.get("session_id")
                message_id = message.get("message_id")
                if session_id and message_id:
                    await WebSocketMessageHandler.handle_delete_message(
                        session_id, connection_id, user, message
                    )

            else:
                logger.warning(f"Unknown message type: {message_type}")

        except Exception as e:
            logger.error(f"Failed to handle message: {e}")
            await manager.send_personal_message(
                {"type": "error", "message": "Failed to process message"}, connection_id
            )

    @staticmethod
    async def handle_join_session(session_id: str, connection_id: str, user: User):
        """セッション参加処理"""
        try:
            from app.services.participant_management_service import (
                participant_manager,
                ParticipantRole,
            )

            # 参加者を管理システムに追加
            participant = await participant_manager.add_participant(
                session_id, user, ParticipantRole.PARTICIPANT
            )

            # 参加通知をブロードキャスト
            await manager.broadcast_to_session(
                {
                    "type": "user_joined",
                    "user": {
                        "id": user.id,
                        "display_name": user.display_name,
                        "avatar_url": user.avatar_url,
                    },
                    "session_id": session_id,
                    "role": participant.role.value,
                    "timestamp": datetime.now().isoformat(),
                },
                session_id,
                exclude_connection=connection_id,
            )

            # 参加者リストを送信
            participants = await participant_manager.get_session_participants(
                session_id
            )
            participant_list = [
                {
                    "user_id": p.user_id,
                    "display_name": p.user.display_name,
                    "avatar_url": p.user.avatar_url,
                    "role": p.role.value,
                    "status": p.status.value,
                    "is_muted": p.is_muted,
                    "is_speaking": p.is_speaking,
                    "joined_at": p.joined_at.isoformat(),
                }
                for p in participants
            ]

            await manager.send_personal_message(
                {
                    "type": "session_participants",
                    "participants": participant_list,
                    "session_id": session_id,
                },
                connection_id,
            )

        except Exception as e:
            logger.error(f"Failed to handle join session: {e}")
            raise

    @staticmethod
    async def handle_leave_session(session_id: str, connection_id: str, user: User):
        """セッション退出処理"""
        try:
            from app.services.participant_management_service import participant_manager

            # 参加者を管理システムから削除
            await participant_manager.remove_participant(session_id, user.id, "left")

            # 退出通知をブロードキャスト
            await manager.broadcast_to_session(
                {
                    "type": "user_left",
                    "user": {"id": user.id, "display_name": user.display_name},
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat(),
                },
                session_id,
                exclude_connection=connection_id,
            )

        except Exception as e:
            logger.error(f"Failed to handle leave session: {e}")
            raise

    @staticmethod
    async def handle_audio_data(
        session_id: str, connection_id: str, user: User, message: dict
    ):
        """音声データ処理"""
        try:
            from app.services.audio_processing_service import audio_processor
            from app.schemas.websocket import AudioDataMessage

            # 音声データメッセージを作成
            audio_message = AudioDataMessage(
                session_id=session_id,
                user_id=user.id,
                data=message.get("data"),
                timestamp=message.get("timestamp"),
                chunk_id=message.get("chunk_id"),
                sample_rate=message.get("sample_rate"),
                channels=message.get("channels"),
            )

            # 音声データを処理
            chunk = await audio_processor.process_audio_data(audio_message)

            # 音声レベルを計算
            audio_level = audio_processor._calculate_audio_level(chunk)

            # 音声レベルメッセージを送信
            await manager.send_personal_message(
                {
                    "type": "audio_level",
                    "session_id": session_id,
                    "user_id": user.id,
                    "level": audio_level.level,
                    "is_speaking": audio_level.is_speaking,
                    "timestamp": audio_level.timestamp.isoformat(),
                },
                connection_id,
            )

            # 音声データを他の参加者に転送
            await manager.broadcast_to_session(
                {
                    "type": "audio_data",
                    "user_id": user.id,
                    "data": message.get("data"),
                    "timestamp": message.get("timestamp"),
                    "session_id": session_id,
                    "chunk_id": message.get("chunk_id"),
                    "sample_rate": message.get("sample_rate"),
                    "channels": message.get("channels"),
                },
                session_id,
                exclude_connection=connection_id,
            )

        except Exception as e:
            logger.error(f"Failed to process audio data: {e}")
            await manager.send_personal_message(
                {"type": "error", "message": "Failed to process audio data"},
                connection_id,
            )

    @staticmethod
    async def handle_text_message(
        session_id: str, connection_id: str, user: User, message: dict
    ):
        """テキストメッセージ処理"""
        try:
            from app.services.messaging_service import (
                messaging_service,
                MessagePriority,
            )

            content = message.get("content", "")
            priority = MessagePriority(message.get("priority", "normal"))

            # テキストメッセージを送信
            await messaging_service.send_text_message(
                session_id, user.id, content, priority
            )

        except Exception as e:
            logger.error(f"Failed to handle text message: {e}")
            await manager.send_personal_message(
                {"type": "error", "message": "Failed to send text message"},
                connection_id,
            )

    @staticmethod
    async def handle_emoji_reaction(
        session_id: str, connection_id: str, user: User, message: dict
    ):
        """絵文字リアクション処理"""
        try:
            from app.services.messaging_service import messaging_service

            target_message_id = message.get("target_message_id")
            emoji = message.get("emoji")

            # 絵文字リアクションを送信
            await messaging_service.send_emoji_reaction(
                session_id, user.id, target_message_id, emoji
            )

        except Exception as e:
            logger.error(f"Failed to handle emoji reaction: {e}")
            await manager.send_personal_message(
                {"type": "error", "message": "Failed to send emoji reaction"},
                connection_id,
            )

    @staticmethod
    async def handle_edit_message(
        session_id: str, connection_id: str, user: User, message: dict
    ):
        """メッセージ編集処理"""
        try:
            from app.services.messaging_service import messaging_service

            message_id = message.get("message_id")
            new_content = message.get("new_content")

            # メッセージを編集
            await messaging_service.edit_message(
                session_id, message_id, user.id, new_content
            )

        except Exception as e:
            logger.error(f"Failed to handle edit message: {e}")
            await manager.send_personal_message(
                {"type": "error", "message": "Failed to edit message"}, connection_id
            )

    @staticmethod
    async def handle_delete_message(
        session_id: str, connection_id: str, user: User, message: dict
    ):
        """メッセージ削除処理"""
        try:
            from app.services.messaging_service import messaging_service

            message_id = message.get("message_id")

            # メッセージを削除
            await messaging_service.delete_message(session_id, message_id, user.id)

        except Exception as e:
            logger.error(f"Failed to handle delete message: {e}")
            await manager.send_personal_message(
                {"type": "error", "message": "Failed to delete message"}, connection_id
            )
