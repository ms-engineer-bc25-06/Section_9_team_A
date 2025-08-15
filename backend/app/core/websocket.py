import json
import asyncio
from typing import Dict, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect, HTTPException, status
from fastapi.security import HTTPBearer
import structlog
from datetime import datetime, timedelta

from app.core.auth import get_current_user_from_token, verify_firebase_token
from app.models.user import User
from app.core.exceptions import AuthenticationException, PermissionException
from app.core.database import AsyncSessionLocal
from sqlalchemy import select

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

            # 1) アプリJWTでの検証
            user = await get_current_user_from_token(token)
            if not user:
                # 2) Firebase ID トークンでの検証（フォールバック）
                decoded = await verify_firebase_token(token)
                if not decoded:
                    raise AuthenticationException("Invalid token")

                firebase_uid = decoded.get("uid")
                email = decoded.get("email")
                display_name = decoded.get("name") or email

                async with AsyncSessionLocal() as db:
                    # 既存ユーザー検索（firebase_uid 優先、なければ email）
                    result = await db.execute(
                        select(User).where(
                            (User.firebase_uid == firebase_uid) if firebase_uid else (User.email == email)
                        )
                    )
                    user = result.scalar_one_or_none()

                    # 見つからない場合は作成（最小項目のみ設定）
                    if not user:
                        if not email:
                            raise AuthenticationException("Email is required")
                        user = User(
                            firebase_uid=firebase_uid,
                            email=email,
                            username=email,
                            full_name=display_name or email,
                            is_active=True,
                            is_verified=True,
                        )
                        db.add(user)
                        await db.commit()
                        await db.refresh(user)

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

            # メッセージタイプを取得
            message_type = message.get("type")

            # pingメッセージは直接処理
            if message_type == "ping":
                await manager.send_personal_message({"type": "pong"}, connection_id)
                return

            # セッションIDが必要なメッセージの処理
            session_id = message.get("session_id")
            if session_id:
                # メッセージルーターにメッセージを送信
                from app.core.message_router import message_router
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
                if message_type == "presence_update":
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
                participant_management_service,
                ParticipantRole,
            )

            # 参加者を管理システムに追加
            participant = await participant_management_service.join_session(
                session_id, user, ParticipantRole.PARTICIPANT, connection_id
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
            participants = await participant_management_service.get_session_participants(
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
            from app.services.participant_management_service import participant_management_service

            # 参加者を管理システムから削除
            await participant_management_service.leave_session(session_id, user.id)

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
            from app.services.transcription_service import realtime_transcription_manager
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

            # 参加者管理サービスに音声レベルを更新
            from app.services.participant_management_service import participant_management_service
            await participant_management_service.update_audio_level(
                session_id, user.id, audio_level.level
            )

            # 音声品質メトリクスを取得
            quality_metrics = await audio_processor.get_audio_quality_metrics(session_id)
            latest_metrics = quality_metrics[-1] if quality_metrics else None

            # バッファ統計を取得
            buffer_stats = await audio_processor.get_buffer_stats(session_id)

            # 音声レベルをブロードキャスト
            await manager.broadcast_to_session(
                {
                    "type": "audio_level",
                    "session_id": session_id,
                    "user_id": user.id,
                    "level": audio_level.level,
                    "is_speaking": audio_level.is_speaking,
                    "quality_metrics": latest_metrics.dict() if latest_metrics else None,
                    "buffer_stats": buffer_stats,
                    "timestamp": datetime.now().isoformat(),
                },
                session_id,
            )

            # 転写処理
            if audio_level.is_speaking:
                # Base64デコード
                audio_data = base64.b64decode(message.get("data"))
                timestamp = datetime.fromisoformat(message.get("timestamp"))

                # リアルタイム転写処理
                final_chunk, partial_chunk = await realtime_transcription_manager.process_audio_chunk(
                    session_id=session_id,
                    user_id=user.id,
                    audio_data=audio_data,
                    timestamp=timestamp,
                    sample_rate=message.get("sample_rate", 16000),
                )

                # 確定転写の処理
                if final_chunk:
                    await manager.broadcast_to_session(
                        {
                            "type": "transcription_final",
                            "session_id": session_id,
                            "user_id": user.id,
                            "text": final_chunk.text,
                            "confidence": final_chunk.confidence,
                            "start_time": final_chunk.start_time,
                            "end_time": final_chunk.end_time,
                            "speaker_id": final_chunk.speaker_id,
                            "speaker_confidence": final_chunk.speaker_confidence,
                            "language": final_chunk.language,
                            "quality": final_chunk.quality.value,
                            "words": final_chunk.words,
                            "timestamp": datetime.now().isoformat(),
                        },
                        session_id,
                    )

                # 部分転写の処理
                if partial_chunk:
                    await manager.broadcast_to_session(
                        {
                            "type": "transcription_partial",
                            "session_id": session_id,
                            "user_id": user.id,
                            "text": partial_chunk.text,
                            "is_final": False,
                            "confidence": partial_chunk.confidence,
                            "start_time": partial_chunk.start_time,
                            "end_time": partial_chunk.end_time,
                            "speaker_id": partial_chunk.speaker_id,
                            "language": partial_chunk.language,
                            "quality": partial_chunk.quality.value,
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
    async def handle_transcription_request(
        session_id: str, connection_id: str, user: User, message: dict
    ):
        """転写リクエスト処理"""
        try:
            from app.services.transcription_service import realtime_transcription_manager

            request_type = message.get("request_type", "stats")
            
            if request_type == "stats":
                # リアルタイム統計を取得
                stats = await realtime_transcription_manager.get_realtime_stats(session_id)
                
                if stats:
                    await manager.send_personal_message(
                        {
                            "type": "transcription_stats",
                            "session_id": session_id,
                            "stats": {
                                "total_chunks": stats.total_chunks,
                                "total_duration": stats.total_duration,
                                "average_confidence": stats.average_confidence,
                                "unique_speakers": stats.unique_speakers,
                                "languages_detected": stats.languages_detected,
                                "quality_distribution": stats.quality_distribution,
                                "error_count": stats.error_count,
                                "last_update": stats.last_update.isoformat() if stats.last_update else None,
                            },
                            "timestamp": datetime.now().isoformat(),
                        },
                        connection_id,
                    )
                else:
                    await manager.send_personal_message(
                        {
                            "type": "error",
                            "message": "No transcription stats available for this session",
                        },
                        connection_id,
                    )
                    
            elif request_type == "partial":
                # 部分転写を取得
                partial_transcriptions = await realtime_transcription_manager.get_partial_transcriptions(session_id)
                
                await manager.send_personal_message(
                    {
                        "type": "transcription_partial_list",
                        "session_id": session_id,
                        "partial_transcriptions": partial_transcriptions,
                        "timestamp": datetime.now().isoformat(),
                    },
                    connection_id,
                )
                
            elif request_type == "clear_partial":
                # 部分転写をクリア
                user_id = message.get("user_id")
                await realtime_transcription_manager.clear_partial_transcriptions(session_id, user_id)
                
                await manager.send_personal_message(
                    {
                        "type": "transcription_partial_cleared",
                        "session_id": session_id,
                        "user_id": user_id,
                        "timestamp": datetime.now().isoformat(),
                    },
                    connection_id,
                )

        except Exception as e:
            logger.error(f"Failed to handle transcription request: {e}")
            await manager.send_personal_message(
                {"type": "error", "message": "Failed to handle transcription request"},
                connection_id,
            )

    @staticmethod
    async def handle_transcription_start(
        session_id: str, connection_id: str, user: User, message: dict
    ):
        """転写開始処理"""
        try:
            from app.services.transcription_service import realtime_transcription_manager

            initial_language = message.get("language", "ja")
            
            await realtime_transcription_manager.start_session(session_id, initial_language)
            
            await manager.broadcast_to_session(
                {
                    "type": "transcription_started",
                    "session_id": session_id,
                    "user_id": user.id,
                    "language": initial_language,
                    "timestamp": datetime.now().isoformat(),
                },
                session_id,
            )

        except Exception as e:
            logger.error(f"Failed to start transcription: {e}")
            await manager.send_personal_message(
                {"type": "error", "message": "Failed to start transcription"},
                connection_id,
            )

    @staticmethod
    async def handle_transcription_stop(
        session_id: str, connection_id: str, user: User, message: dict
    ):
        """転写停止処理"""
        try:
            from app.services.transcription_service import realtime_transcription_manager

            await realtime_transcription_manager.stop_session(session_id)
            
            await manager.broadcast_to_session(
                {
                    "type": "transcription_stopped",
                    "session_id": session_id,
                    "user_id": user.id,
                    "timestamp": datetime.now().isoformat(),
                },
                session_id,
            )

        except Exception as e:
            logger.error(f"Failed to stop transcription: {e}")
            await manager.send_personal_message(
                {"type": "error", "message": "Failed to stop transcription"},
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

    @staticmethod
    async def handle_notification_request(
        session_id: str, connection_id: str, user: User, message: dict
    ):
        """通知リクエスト処理"""
        try:
            from app.services.notification_service import (
                notification_service,
                NotificationType,
                NotificationPriority,
            )

            notification_type = NotificationType(
                message.get("notification_type", "info")
            )
            title = message.get("title", "")
            content = message.get("content", "")
            priority = NotificationPriority(message.get("priority", "normal"))
            metadata = message.get("metadata", {})

            # 通知を作成・送信
            notification = await notification_service.send_session_notification(
                session_id=session_id,
                title=title,
                content=content,
                notification_type=notification_type,
                priority=priority,
                metadata=metadata,
            )

            # 送信確認を返信
            await manager.send_personal_message(
                {
                    "type": "notification_sent",
                    "notification_id": notification.id,
                    "timestamp": datetime.now().isoformat(),
                },
                connection_id,
            )

        except Exception as e:
            logger.error(f"Failed to handle notification request: {e}")
            await manager.send_personal_message(
                {"type": "error", "message": "Failed to send notification"},
                connection_id,
            )

    @staticmethod
    async def handle_announcement_request(
        session_id: str, connection_id: str, user: User, message: dict
    ):
        """アナウンスメントリクエスト処理"""
        try:
            from app.services.announcement_service import (
                announcement_service,
                AnnouncementType,
                AnnouncementPriority,
            )

            announcement_type = AnnouncementType(
                message.get("announcement_type", "general")
            )
            title = message.get("title", "")
            content = message.get("content", "")
            priority = AnnouncementPriority(message.get("priority", "normal"))
            metadata = message.get("metadata", {})
            expires_at_str = message.get("expires_at")
            expires_at = None
            if expires_at_str:
                expires_at = datetime.fromisoformat(expires_at_str)

            # アナウンスメントを作成・送信
            announcement = await announcement_service.send_session_announcement(
                session_id=session_id,
                title=title,
                content=content,
                sender=user.display_name,
                announcement_type=announcement_type,
                priority=priority,
                metadata=metadata,
                expires_at=expires_at,
            )

            # 送信確認を返信
            await manager.send_personal_message(
                {
                    "type": "announcement_sent",
                    "announcement_id": announcement.id,
                    "timestamp": datetime.now().isoformat(),
                },
                connection_id,
            )

        except Exception as e:
            logger.error(f"Failed to handle announcement request: {e}")
            await manager.send_personal_message(
                {"type": "error", "message": "Failed to send announcement"},
                connection_id,
            )

    @staticmethod
    async def handle_notification_dismiss(
        session_id: str, connection_id: str, user: User, message: dict
    ):
        """通知却下処理"""
        try:
            from app.services.notification_service import notification_service

            notification_id = message.get("notification_id")

            # 通知を却下
            success = await notification_service.mark_notification_read(
                notification_id, user.id
            )

            if success:
                await manager.send_personal_message(
                    {
                        "type": "notification_dismissed",
                        "notification_id": notification_id,
                        "timestamp": datetime.now().isoformat(),
                    },
                    connection_id,
                )
            else:
                await manager.send_personal_message(
                    {"type": "error", "message": "Failed to dismiss notification"},
                    connection_id,
                )

        except Exception as e:
            logger.error(f"Failed to handle notification dismiss: {e}")
            await manager.send_personal_message(
                {"type": "error", "message": "Failed to dismiss notification"},
                connection_id,
            )

    @staticmethod
    async def handle_announcement_dismiss(
        session_id: str, connection_id: str, user: User, message: dict
    ):
        """アナウンスメント却下処理"""
        try:
            from app.services.announcement_service import announcement_service

            announcement_id = message.get("announcement_id")

            # アナウンスメントを却下
            success = await announcement_service.dismiss_announcement(
                announcement_id, user.id
            )

            if success:
                await manager.send_personal_message(
                    {
                        "type": "announcement_dismissed",
                        "announcement_id": announcement_id,
                        "timestamp": datetime.now().isoformat(),
                    },
                    connection_id,
                )
            else:
                await manager.send_personal_message(
                    {"type": "error", "message": "Failed to dismiss announcement"},
                    connection_id,
                )

        except Exception as e:
            logger.error(f"Failed to handle announcement dismiss: {e}")
            await manager.send_personal_message(
                {"type": "error", "message": "Failed to dismiss announcement"},
                connection_id,
            )

    @staticmethod
    async def handle_get_notifications(
        session_id: str, connection_id: str, user: User, message: dict
    ):
        """通知取得処理"""
        try:
            from app.services.notification_service import notification_service

            unread_only = message.get("unread_only", False)
            limit = message.get("limit", 50)

            # ユーザーの通知を取得
            notifications = await notification_service.get_user_notifications(
                user.id, unread_only=unread_only, limit=limit
            )

            # 通知リストを送信
            notification_list = [
                {
                    "id": n.id,
                    "type": n.type.value,
                    "title": n.title,
                    "content": n.content,
                    "priority": n.priority.value,
                    "action_url": n.action_url,
                    "auto_dismiss": n.auto_dismiss,
                    "duration": n.duration,
                    "metadata": n.metadata,
                    "created_at": n.created_at.isoformat(),
                    "delivered_at": n.delivered_at.isoformat()
                    if n.delivered_at
                    else None,
                    "read_at": n.read_at.isoformat() if n.read_at else None,
                }
                for n in notifications
            ]

            await manager.send_personal_message(
                {
                    "type": "notifications_list",
                    "notifications": notification_list,
                    "timestamp": datetime.now().isoformat(),
                },
                connection_id,
            )

        except Exception as e:
            logger.error(f"Failed to handle get notifications: {e}")
            await manager.send_personal_message(
                {"type": "error", "message": "Failed to get notifications"},
                connection_id,
            )

    @staticmethod
    async def handle_get_announcements(
        session_id: str, connection_id: str, user: User, message: dict
    ):
        """アナウンスメント取得処理"""
        try:
            from app.services.announcement_service import announcement_service

            limit = message.get("limit", 50)

            # アクティブなアナウンスメントを取得
            announcements = await announcement_service.get_active_announcements(
                user_id=user.id, session_id=session_id
            )

            # アナウンスメントリストを送信
            announcement_list = [
                {
                    "id": a.id,
                    "type": a.type.value,
                    "title": a.title,
                    "content": a.content,
                    "priority": a.priority.value,
                    "sender": a.sender,
                    "action_url": a.action_url,
                    "expires_at": a.expires_at.isoformat() if a.expires_at else None,
                    "metadata": a.metadata,
                    "created_at": a.created_at.isoformat(),
                    "delivered_at": a.delivered_at.isoformat()
                    if a.delivered_at
                    else None,
                }
                for a in announcements
            ]

            await manager.send_personal_message(
                {
                    "type": "announcements_list",
                    "announcements": announcement_list,
                    "timestamp": datetime.now().isoformat(),
                },
                connection_id,
            )

        except Exception as e:
            logger.error(f"Failed to handle get announcements: {e}")
            await manager.send_personal_message(
                {"type": "error", "message": "Failed to get announcements"},
                connection_id,
            )

    @staticmethod
    async def handle_audio_quality_request(
        session_id: str, connection_id: str, user: User, message: dict
    ):
        """音声品質情報要求処理"""
        try:
            from app.services.audio_processing_service import audio_processor

            # 音声品質メトリクスを取得
            quality_metrics = await audio_processor.get_audio_quality_metrics(session_id)
            
            # バッファ統計を取得
            buffer_stats = await audio_processor.get_buffer_stats(session_id)
            
            # 音声レベル履歴を取得
            audio_levels = await audio_processor.get_session_audio_levels(session_id, user.id)

            # 音声品質情報を送信
            await manager.send_personal_message(
                {
                    "type": "audio_quality_info",
                    "session_id": session_id,
                    "user_id": user.id,
                    "quality_metrics": [
                        {
                            "snr": metrics.snr,
                            "clarity": metrics.clarity,
                            "latency": metrics.latency,
                            "packet_loss": metrics.packet_loss,
                            "jitter": metrics.jitter,
                            "timestamp": metrics.timestamp.isoformat(),
                        }
                        for metrics in quality_metrics[-10:]  # 最新10件
                    ],
                    "buffer_stats": buffer_stats,
                    "audio_levels": [
                        {
                            "level": level.level,
                            "is_speaking": level.is_speaking,
                            "rms": level.rms,
                            "peak": level.peak,
                            "timestamp": level.timestamp.isoformat(),
                        }
                        for level in audio_levels
                    ],
                },
                connection_id,
            )

        except Exception as e:
            logger.error(f"Failed to get audio quality info: {e}")
            await manager.send_personal_message(
                {"type": "error", "message": "Failed to get audio quality info"},
                connection_id,
            )

    @staticmethod
    async def handle_network_metrics_update(
        session_id: str, connection_id: str, user: User, message: dict
    ):
        """ネットワークメトリクス更新処理"""
        try:
            from app.services.audio_processing_service import audio_processor, NetworkMetrics

            # ネットワークメトリクスを作成
            network_metrics = NetworkMetrics(
                bandwidth=message.get("bandwidth", 0.0),
                latency=message.get("latency", 0.0),
                packet_loss=message.get("packet_loss", 0.0),
                jitter=message.get("jitter", 0.0),
                quality_score=message.get("quality_score", 0.5),
                timestamp=datetime.now(),
            )

            # ネットワークメトリクスを更新
            await audio_processor.update_network_metrics(session_id, network_metrics)

            logger.info(
                f"Updated network metrics for session {session_id}",
                user_id=user.id,
                bandwidth=network_metrics.bandwidth,
                latency=network_metrics.latency,
                quality_score=network_metrics.quality_score,
            )

        except Exception as e:
            logger.error(f"Failed to update network metrics: {e}")
            await manager.send_personal_message(
                {"type": "error", "message": "Failed to update network metrics"},
                connection_id,
            )

    @staticmethod
    async def handle_session_state_request(
        session_id: str, connection_id: str, user: User, message: dict
    ):
        """セッション状態リクエスト処理"""
        try:
            from app.services.session_state_service import session_state_manager

            request_type = message.get("request_type", "current")
            
            if request_type == "current":
                # 現在のセッション状態を取得
                session_state = await session_state_manager.get_session_state(session_id)
                
                if session_state:
                    await manager.send_personal_message(
                        {
                            "type": "session_state_info",
                            "session_id": session_id,
                            "state": {
                                "session_state": session_state.state.value,
                                "created_at": session_state.created_at.isoformat(),
                                "started_at": session_state.started_at.isoformat() if session_state.started_at else None,
                                "ended_at": session_state.ended_at.isoformat() if session_state.ended_at else None,
                                "duration": session_state.duration,
                                "participants_count": len(session_state.participants),
                                "recording_state": session_state.recording.state.value,
                                "transcription_active": session_state.transcription.is_active,
                                "analytics_active": session_state.analytics.is_active,
                                "last_update": session_state.last_update.isoformat(),
                            },
                            "timestamp": datetime.now().isoformat(),
                        },
                        connection_id,
                    )
                else:
                    await manager.send_personal_message(
                        {
                            "type": "error",
                            "message": "Session state not found",
                        },
                        connection_id,
                    )
                    
            elif request_type == "participants":
                # 参加者情報を取得
                participants = await session_state_manager.get_session_participants(session_id)
                
                participants_data = []
                for participant in participants:
                    participants_data.append({
                        "user_id": participant.user_id,
                        "display_name": participant.display_name,
                        "state": participant.state.value,
                        "connected_at": participant.connected_at.isoformat() if participant.connected_at else None,
                        "last_activity": participant.last_activity.isoformat() if participant.last_activity else None,
                        "is_speaking": participant.is_speaking,
                        "is_muted": participant.is_muted,
                        "audio_level": participant.audio_level,
                    })
                
                await manager.send_personal_message(
                    {
                        "type": "session_participants_info",
                        "session_id": session_id,
                        "participants": participants_data,
                        "timestamp": datetime.now().isoformat(),
                    },
                    connection_id,
                )
                
            elif request_type == "history":
                # セッション履歴を取得
                history = await session_state_manager.get_session_history(session_id)
                
                history_data = []
                for state in history:
                    history_data.append({
                        "state": state.state.value,
                        "timestamp": state.last_update.isoformat(),
                        "duration": state.duration,
                        "participants_count": len(state.participants),
                    })
                
                await manager.send_personal_message(
                    {
                        "type": "session_history_info",
                        "session_id": session_id,
                        "history": history_data,
                        "timestamp": datetime.now().isoformat(),
                    },
                    connection_id,
                )

        except Exception as e:
            logger.error(f"Failed to handle session state request: {e}")
            await manager.send_personal_message(
                {"type": "error", "message": "Failed to handle session state request"},
                connection_id,
            )

    @staticmethod
    async def handle_session_control(
        session_id: str, connection_id: str, user: User, message: dict
    ):
        """セッション制御処理"""
        try:
            from app.services.session_state_service import session_state_manager, SessionState

            action = message.get("action")
            
            if action == "start":
                # セッション開始
                session_state = await session_state_manager.start_session(session_id, user.id)
                
                await manager.broadcast_to_session(
                    {
                        "type": "session_started",
                        "session_id": session_id,
                        "user_id": user.id,
                        "state": session_state.state.value,
                        "timestamp": datetime.now().isoformat(),
                    },
                    session_id,
                )
                
            elif action == "pause":
                # セッション一時停止
                session_state = await session_state_manager.pause_session(session_id, user.id)
                
                await manager.broadcast_to_session(
                    {
                        "type": "session_paused",
                        "session_id": session_id,
                        "user_id": user.id,
                        "state": session_state.state.value,
                        "timestamp": datetime.now().isoformat(),
                    },
                    session_id,
                )
                
            elif action == "resume":
                # セッション再開
                session_state = await session_state_manager.resume_session(session_id, user.id)
                
                await manager.broadcast_to_session(
                    {
                        "type": "session_resumed",
                        "session_id": session_id,
                        "user_id": user.id,
                        "state": session_state.state.value,
                        "timestamp": datetime.now().isoformat(),
                    },
                    session_id,
                )
                
            elif action == "end":
                # セッション終了
                session_state = await session_state_manager.end_session(session_id, user.id)
                
                await manager.broadcast_to_session(
                    {
                        "type": "session_ended",
                        "session_id": session_id,
                        "user_id": user.id,
                        "state": session_state.state.value,
                        "duration": session_state.duration,
                        "timestamp": datetime.now().isoformat(),
                    },
                    session_id,
                )

        except Exception as e:
            logger.error(f"Failed to handle session control: {e}")
            await manager.send_personal_message(
                {"type": "error", "message": "Failed to handle session control"},
                connection_id,
            )

    @staticmethod
    async def handle_participant_state_update(
        session_id: str, connection_id: str, user: User, message: dict
    ):
        """参加者状態更新処理"""
        try:
            from app.services.participant_management_service import (
                participant_management_service, 
                ParticipantStatus
            )

            action = message.get("action")
            action_data = message.get("data", {})
            
            if action == "mute":
                # ミュート制御
                muted = action_data.get("muted", True)
                participant = await participant_management_service.mute_participant(
                    session_id, user.id, muted, user.id
                )
                
            elif action == "change_role":
                # 役割変更
                from app.services.participant_management_service import ParticipantRole
                new_role = ParticipantRole(action_data.get("new_role", "participant"))
                participant = await participant_management_service.change_participant_role(
                    session_id, user.id, new_role, user.id
                )
                
            elif action == "update_status":
                # ステータス更新
                new_status = ParticipantStatus(action_data.get("status", "connected"))
                participant = await participant_management_service.update_participant_status(
                    session_id, user.id, new_status, user.id
                )
                
            else:
                await manager.send_personal_message(
                    {
                        "type": "error",
                        "message": f"Invalid action: {action}",
                    },
                    connection_id,
                )
                return

            # 成功通知
            await manager.broadcast_to_session(
                {
                    "type": "participant_state_updated",
                    "session_id": session_id,
                    "user_id": user.id,
                    "action": action,
                    "data": action_data,
                    "timestamp": datetime.now().isoformat(),
                },
                session_id,
                exclude_connection=connection_id,
            )

        except Exception as e:
            logger.error(f"Failed to handle participant state update: {e}")
            await manager.send_personal_message(
                {"type": "error", "message": "Failed to handle participant state update"},
                connection_id,
            )
