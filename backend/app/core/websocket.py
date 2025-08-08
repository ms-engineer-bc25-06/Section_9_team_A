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
        # 接続制限
        self.max_connections_per_user = 3
        self.max_connections_per_session = 50
        # 接続タイムアウト
        self.connection_timeout = timedelta(hours=24)
        # ハートビート管理
        self.last_heartbeat: Dict[str, datetime] = {}

    async def connect(self, websocket: WebSocket, session_id: str, user: User) -> str:
        """WebSocket接続を確立"""
        try:
            await websocket.accept()

            # 接続制限チェック
            await self._check_connection_limits(session_id, user.id)

            # 接続IDを生成
            connection_id = f"{user.id}_{session_id}_{datetime.now().timestamp()}"

            # 接続を登録
            self.active_connections[connection_id] = websocket
            self.connection_info[connection_id] = {
                "user_id": user.id,
                "session_id": session_id,
                "connected_at": datetime.now(),
                "user": user,
                "last_activity": datetime.now(),
                "status": "connected",
            }

            # セッション別接続管理
            if session_id not in self.session_connections:
                self.session_connections[session_id] = set()
            self.session_connections[session_id].add(connection_id)

            # ユーザー別接続管理
            if user.id not in self.user_connections:
                self.user_connections[user.id] = set()
            self.user_connections[user.id].add(connection_id)

            # ハートビート初期化
            self.last_heartbeat[connection_id] = datetime.now()

            logger.info(
                f"WebSocket connected: {connection_id}",
                user_id=user.id,
                session_id=session_id,
            )

            return connection_id

        except Exception as e:
            logger.error(f"Failed to establish WebSocket connection: {e}")
            raise

    async def _check_connection_limits(self, session_id: str, user_id: int):
        """接続制限をチェック"""
        # ユーザー別接続数チェック
        user_connections = len(self.user_connections.get(user_id, set()))
        if user_connections >= self.max_connections_per_user:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Maximum connections per user exceeded",
            )

        # セッション別接続数チェック
        session_connections = len(self.session_connections.get(session_id, set()))
        if session_connections >= self.max_connections_per_session:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Maximum connections per session exceeded",
            )

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
            if connection_id in self.last_heartbeat:
                del self.last_heartbeat[connection_id]

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
                # 接続の有効性をチェック
                if not await self._is_connection_valid(connection_id):
                    self.disconnect(connection_id)
                    return

                await self.active_connections[connection_id].send_text(
                    json.dumps(message, default=str)
                )

                # 活動時間を更新
                if connection_id in self.connection_info:
                    self.connection_info[connection_id]["last_activity"] = (
                        datetime.now()
                    )

            except Exception as e:
                logger.error(f"Failed to send message to {connection_id}: {e}")
                self.disconnect(connection_id)

    async def broadcast_to_session(
        self, message: dict, session_id: str, exclude_connection: str = None
    ):
        """セッション内の全接続にメッセージをブロードキャスト"""
        if session_id in self.session_connections:
            disconnected_connections = []

            for connection_id in self.session_connections[session_id]:
                if connection_id != exclude_connection:
                    try:
                        await self.send_personal_message(message, connection_id)
                    except Exception as e:
                        logger.error(f"Failed to broadcast to {connection_id}: {e}")
                        disconnected_connections.append(connection_id)

            # 切断された接続を削除
            for connection_id in disconnected_connections:
                self.disconnect(connection_id)

    async def broadcast_to_user(
        self, message: dict, user_id: int, exclude_connection: str = None
    ):
        """特定ユーザーの全接続にメッセージをブロードキャスト"""
        if user_id in self.user_connections:
            disconnected_connections = []

            for connection_id in self.user_connections[user_id]:
                if connection_id != exclude_connection:
                    try:
                        await self.send_personal_message(message, connection_id)
                    except Exception as e:
                        logger.error(f"Failed to broadcast to {connection_id}: {e}")
                        disconnected_connections.append(connection_id)

            # 切断された接続を削除
            for connection_id in disconnected_connections:
                self.disconnect(connection_id)

    async def _is_connection_valid(self, connection_id: str) -> bool:
        """接続の有効性をチェック"""
        if connection_id not in self.connection_info:
            return False

        info = self.connection_info[connection_id]
        last_activity = info.get("last_activity")

        if last_activity and datetime.now() - last_activity > self.connection_timeout:
            logger.warning(f"Connection timeout: {connection_id}")
            return False

        return True

    async def update_heartbeat(self, connection_id: str):
        """ハートビートを更新"""
        if connection_id in self.last_heartbeat:
            self.last_heartbeat[connection_id] = datetime.now()
            if connection_id in self.connection_info:
                self.connection_info[connection_id]["last_activity"] = datetime.now()

    async def cleanup_inactive_connections(self):
        """非アクティブな接続をクリーンアップ"""
        current_time = datetime.now()
        inactive_connections = []

        for connection_id, last_heartbeat_time in self.last_heartbeat.items():
            if current_time - last_heartbeat_time > timedelta(minutes=5):
                inactive_connections.append(connection_id)

        for connection_id in inactive_connections:
            logger.info(f"Cleaning up inactive connection: {connection_id}")
            self.disconnect(connection_id)

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

    def get_connection_stats(self) -> Dict[str, Any]:
        """接続統計を取得"""
        return {
            "total_connections": len(self.active_connections),
            "total_sessions": len(self.session_connections),
            "total_users": len(self.user_connections),
            "session_connections": {
                session_id: len(connections)
                for session_id, connections in self.session_connections.items()
            },
        }


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

            # ユーザーの有効性チェック
            if not user.is_active:
                raise AuthenticationException("User account is inactive")

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
            # ハートビートを更新
            await manager.update_heartbeat(connection_id)

            # メッセージルーターを使用してメッセージを処理
            from app.core.message_router import message_router

            session_id = message.get("session_id")
            if session_id:
                # メッセージルーターにメッセージを送信
                success = await message_router.route_message(
                    message, user, session_id, connection_id
                )
                if not success:
                    await manager.send_personal_message(
                        {"type": "error", "message": "Failed to process message"},
                        connection_id,
                    )
            else:
                # セッションIDが不要なメッセージは直接処理
                message_type = message.get("type")

                if message_type == "ping":
                    await manager.send_personal_message({"type": "pong"}, connection_id)
                elif message_type == "presence_update":
                    await WebSocketMessageHandler.handle_presence_update(
                        connection_id, user, message
                    )
                else:
                    logger.warning(
                        f"Unknown message type or missing session_id: {message_type}"
                    )
                    await manager.send_personal_message(
                        {
                            "type": "error",
                            "message": f"Unknown message type or missing session_id: {message_type}",
                        },
                        connection_id,
                    )

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
            from app.services.transcription_service import transcription_service
            from app.schemas.websocket import AudioDataMessage
            import base64

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

            # 転写処理
            if audio_level.is_speaking:
                # Base64デコード
                audio_data = base64.b64decode(message.get("data"))
                timestamp = datetime.fromisoformat(message.get("timestamp"))

                # 転写処理
                transcription_chunk = await transcription_service.process_audio_chunk(
                    session_id=session_id,
                    user_id=user.id,
                    audio_data=audio_data,
                    timestamp=timestamp,
                    sample_rate=message.get("sample_rate", 16000),
                )

                if transcription_chunk:
                    # 確定転写の場合
                    if transcription_chunk.is_final:
                        await manager.broadcast_to_session(
                            {
                                "type": "transcription_final",
                                "session_id": session_id,
                                "user_id": user.id,
                                "text": transcription_chunk.text,
                                "confidence": transcription_chunk.confidence,
                                "start_time": transcription_chunk.start_time,
                                "end_time": transcription_chunk.end_time,
                                "timestamp": datetime.now().isoformat(),
                            },
                            session_id,
                        )
                    else:
                        # 部分転写の場合
                        await manager.broadcast_to_session(
                            {
                                "type": "transcription_partial",
                                "session_id": session_id,
                                "user_id": user.id,
                                "text": transcription_chunk.text,
                                "is_final": False,
                                "confidence": transcription_chunk.confidence,
                                "start_time": transcription_chunk.start_time,
                                "end_time": transcription_chunk.end_time,
                                "timestamp": datetime.now().isoformat(),
                            },
                            session_id,
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

    @staticmethod
    async def handle_presence_update(connection_id: str, user: User, message: dict):
        """プレゼンス更新処理"""
        try:
            from app.schemas.websocket import UserPresenceStatus, UserActivityStatus

            status = UserPresenceStatus(message.get("status", "online"))
            activity = UserActivityStatus(message.get("activity", "active"))
            custom_status = message.get("custom_status")

            # プレゼンス更新をブロードキャスト
            presence_message = {
                "type": "presence_update",
                "user_id": user.id,
                "status": status.value,
                "activity": activity.value,
                "custom_status": custom_status,
                "timestamp": datetime.now().isoformat(),
            }

            # 全ユーザーの接続にプレゼンス更新を送信
            await manager.broadcast_to_user(
                presence_message, user.id, exclude_connection=connection_id
            )

        except Exception as e:
            logger.error(f"Failed to handle presence update: {e}")
            await manager.send_personal_message(
                {"type": "error", "message": "Failed to update presence"}, connection_id
            )

    @staticmethod
    async def handle_typing_start(
        session_id: str, connection_id: str, user: User, message: dict
    ):
        """入力開始処理"""
        try:
            typing_message = {
                "type": "typing_start",
                "session_id": session_id,
                "user_id": user.id,
                "user_name": user.display_name,
                "timestamp": datetime.now().isoformat(),
            }

            # セッション内の他の参加者に通知
            await manager.broadcast_to_session(
                typing_message, session_id, exclude_connection=connection_id
            )

        except Exception as e:
            logger.error(f"Failed to handle typing start: {e}")

    @staticmethod
    async def handle_typing_stop(
        session_id: str, connection_id: str, user: User, message: dict
    ):
        """入力停止処理"""
        try:
            typing_message = {
                "type": "typing_stop",
                "session_id": session_id,
                "user_id": user.id,
                "timestamp": datetime.now().isoformat(),
            }

            # セッション内の他の参加者に通知
            await manager.broadcast_to_session(
                typing_message, session_id, exclude_connection=connection_id
            )

        except Exception as e:
            logger.error(f"Failed to handle typing stop: {e}")

    @staticmethod
    async def handle_file_share(
        session_id: str, connection_id: str, user: User, message: dict
    ):
        """ファイル共有処理"""
        try:
            from app.services.messaging_service import (
                messaging_service,
                MessagePriority,
            )

            file_name = message.get("file_name")
            file_size = message.get("file_size")
            file_type = message.get("file_type")
            file_url = message.get("file_url")
            description = message.get("description", "")

            # ファイル共有メッセージを作成
            file_share_content = f"ファイルを共有しました: {file_name}"
            if description:
                file_share_content += f" - {description}"

            # メッセージとして保存
            await messaging_service.send_text_message(
                session_id, user.id, file_share_content, MessagePriority.NORMAL
            )

            # ファイル共有通知をブロードキャスト
            file_share_message = {
                "type": "file_share",
                "session_id": session_id,
                "user_id": user.id,
                "user_name": user.display_name,
                "file_name": file_name,
                "file_size": file_size,
                "file_type": file_type,
                "file_url": file_url,
                "description": description,
                "timestamp": datetime.now().isoformat(),
            }

            await manager.broadcast_to_session(file_share_message, session_id)

        except Exception as e:
            logger.error(f"Failed to handle file share: {e}")
            await manager.send_personal_message(
                {"type": "error", "message": "Failed to share file"}, connection_id
            )

    @staticmethod
    async def handle_hand_raise(
        session_id: str, connection_id: str, user: User, message: dict
    ):
        """挙手処理"""
        try:
            from app.services.participant_management_service import participant_manager

            reason = message.get("reason")

            # 参加者の状態を更新
            await participant_manager.update_participant_status(
                session_id,
                user.id,
                status="speaking",  # 仮の状態
                metadata={"hand_raised": True, "reason": reason},
            )

            # 挙手通知をブロードキャスト
            hand_raise_message = {
                "type": "hand_raise",
                "session_id": session_id,
                "user_id": user.id,
                "user_name": user.display_name,
                "reason": reason,
                "timestamp": datetime.now().isoformat(),
            }

            await manager.broadcast_to_session(hand_raise_message, session_id)

        except Exception as e:
            logger.error(f"Failed to handle hand raise: {e}")
            await manager.send_personal_message(
                {"type": "error", "message": "Failed to raise hand"}, connection_id
            )

    @staticmethod
    async def handle_hand_lower(
        session_id: str, connection_id: str, user: User, message: dict
    ):
        """挙手解除処理"""
        try:
            from app.services.participant_management_service import participant_manager

            # 参加者の状態を更新
            await participant_manager.update_participant_status(
                session_id, user.id, status="connected", metadata={"hand_raised": False}
            )

            # 挙手解除通知をブロードキャスト
            hand_lower_message = {
                "type": "hand_lower",
                "session_id": session_id,
                "user_id": user.id,
                "timestamp": datetime.now().isoformat(),
            }

            await manager.broadcast_to_session(hand_lower_message, session_id)

        except Exception as e:
            logger.error(f"Failed to handle hand lower: {e}")

    @staticmethod
    async def handle_poll_create(
        session_id: str, connection_id: str, user: User, message: dict
    ):
        """投票作成処理"""
        try:
            from app.services.messaging_service import messaging_service

            poll_id = message.get("poll_id")
            question = message.get("question")
            options = message.get("options", [])
            multiple_choice = message.get("multiple_choice", False)
            anonymous = message.get("anonymous", False)
            duration = message.get("duration")

            # システムメッセージとして投票を通知
            poll_content = f"投票が作成されました: {question}"
            await messaging_service.send_system_message(session_id, poll_content)

            # 投票作成をブロードキャスト
            poll_create_message = {
                "type": "poll_create",
                "session_id": session_id,
                "poll_id": poll_id,
                "question": question,
                "options": options,
                "multiple_choice": multiple_choice,
                "anonymous": anonymous,
                "duration": duration,
                "created_by": user.id,
                "created_by_name": user.display_name,
                "timestamp": datetime.now().isoformat(),
            }

            await manager.broadcast_to_session(poll_create_message, session_id)

        except Exception as e:
            logger.error(f"Failed to handle poll create: {e}")
            await manager.send_personal_message(
                {"type": "error", "message": "Failed to create poll"}, connection_id
            )

    @staticmethod
    async def handle_poll_vote(
        session_id: str, connection_id: str, user: User, message: dict
    ):
        """投票処理"""
        try:
            poll_id = message.get("poll_id")
            option_ids = message.get("option_ids", [])

            # 投票結果を更新（実際の投票ロジックはここで実装）
            # 今回は簡単な通知のみ実装

            vote_message = {
                "type": "poll_vote",
                "session_id": session_id,
                "poll_id": poll_id,
                "user_id": user.id,
                "option_ids": option_ids,
                "timestamp": datetime.now().isoformat(),
            }

            # 投票者本人に確認を送信
            await manager.send_personal_message(
                {"type": "poll_vote_confirmed", **vote_message}, connection_id
            )

            # 匿名でない場合は他の参加者にも通知
            # （匿名投票の場合は結果のみ更新）

        except Exception as e:
            logger.error(f"Failed to handle poll vote: {e}")
            await manager.send_personal_message(
                {"type": "error", "message": "Failed to vote"}, connection_id
            )
