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
                "WebSocket connection established",
                connection_id=connection_id,
                user_id=user.id,
                session_id=session_id,
                total_connections=len(self.active_connections),
                session_connections=len(
                    self.session_connections.get(session_id, set())
                ),
                user_connections=len(self.user_connections.get(user.id, set())),
            )

            return connection_id

        except Exception as e:
            logger.error(
                "Failed to establish WebSocket connection",
                error_type=type(e).__name__,
                error_message=str(e),
                user_id=user.id,
                session_id=session_id,
            )
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

    async def disconnect(self, connection_id: str):
        """WebSocket接続を切断"""
        try:
            if connection_id in self.active_connections:
                websocket = self.active_connections[connection_id]
                await websocket.close()
                del self.active_connections[connection_id]

            # 接続情報をクリーンアップ
            if connection_id in self.connection_info:
                connection_info = self.connection_info[connection_id]
                session_id = connection_info.get("session_id")
                user_id = connection_info.get("user_id")

                # セッション別接続管理から削除
                if session_id and session_id in self.session_connections:
                    self.session_connections[session_id].discard(connection_id)
                    if not self.session_connections[session_id]:
                        del self.session_connections[session_id]

                # ユーザー別接続管理から削除
                if user_id and user_id in self.user_connections:
                    self.user_connections[user_id].discard(connection_id)
                    if not self.user_connections[user_id]:
                        del self.user_connections[user_id]

                # 接続情報を削除
                del self.connection_info[connection_id]

                # ハートビート情報を削除
                if connection_id in self.last_heartbeat:
                    del self.last_heartbeat[connection_id]

                logger.info(f"WebSocket disconnected: {connection_id}")

        except Exception as e:
            logger.error(f"Error during disconnect: {e}")

    async def send_personal_message(self, message: dict, connection_id: str):
        """特定の接続にメッセージを送信"""
        try:
            if connection_id in self.active_connections:
                websocket = self.active_connections[connection_id]
                await websocket.send_text(json.dumps(message))
                logger.debug(f"Personal message sent to {connection_id}")
        except Exception as e:
            logger.error(f"Failed to send personal message to {connection_id}: {e}")
            await self.disconnect(connection_id)

    async def broadcast_to_session(
        self, message: dict, session_id: str, exclude_connection: Optional[str] = None
    ):
        """セッション内の全接続にメッセージをブロードキャスト"""
        try:
            if session_id in self.session_connections:
                for connection_id in self.session_connections[session_id]:
                    if (
                        connection_id != exclude_connection
                        and connection_id in self.active_connections
                    ):
                        await self.send_personal_message(message, connection_id)
                logger.debug(f"Broadcast message sent to session {session_id}")
        except Exception as e:
            logger.error(f"Failed to broadcast to session {session_id}: {e}")

    async def get_session_participants(self, session_id: str) -> list:
        """セッションの参加者一覧を取得"""
        participants = []
        if session_id in self.session_connections:
            for connection_id in self.session_connections[session_id]:
                if connection_id in self.connection_info:
                    connection_info = self.connection_info[connection_id]
                    user = connection_info.get("user")
                    connected_at = connection_info.get("connected_at")
                    last_activity = connection_info.get("last_activity")

                    if user and connected_at and last_activity:
                        participants.append(
                            {
                                "id": str(user.id),
                                "username": user.username,
                                "display_name": user.display_name,
                                "email": user.email,
                                "role": "PARTICIPANT",
                                "status": "online",
                                "is_active": True,
                                "is_muted": False,
                                "joinedAt": connected_at.isoformat(),
                                "lastActivity": last_activity.isoformat(),
                            }
                        )
        return participants

    async def update_connection_activity(self, connection_id: str):
        """接続の活動時間を更新"""
        if connection_id in self.connection_info:
            self.connection_info[connection_id]["last_activity"] = datetime.now()
            self.last_heartbeat[connection_id] = datetime.now()

    async def cleanup_inactive_connections(self):
        """非アクティブな接続をクリーンアップ"""
        current_time = datetime.now()
        inactive_connections = []

        for connection_id, last_heartbeat in self.last_heartbeat.items():
            if current_time - last_heartbeat > self.connection_timeout:
                inactive_connections.append(connection_id)

        for connection_id in inactive_connections:
            logger.info(f"Cleaning up inactive connection: {connection_id}")
            await self.disconnect(connection_id)

    async def get_connection_stats(self) -> dict:
        """接続統計を取得"""
        return {
            "total_connections": len(self.active_connections),
            "total_sessions": len(self.session_connections),
            "total_users": len(self.user_connections),
            "connections_per_session": {
                session_id: len(connections)
                for session_id, connections in self.session_connections.items()
            },
            "connections_per_user": {
                user_id: len(connections)
                for user_id, connections in self.user_connections.items()
            },
        }


# グローバルインスタンス
manager = ConnectionManager()


class WebSocketAuth:
    """WebSocket認証クラス"""

    @staticmethod
    async def authenticate_websocket(websocket: WebSocket) -> User:
        """WebSocket接続の認証（JWTトークンとFirebaseトークンの両方に対応）"""
        try:
            # クエリパラメータからトークンを取得
            query_params = websocket.query_params
            token = query_params.get("token")

            if not token:
                logger.warning("WebSocket authentication failed: No token provided")
                raise AuthenticationException("No authentication token provided")

            logger.info(
                "WebSocket authentication started",
                token_length=len(token) if token else 0,
            )

            # まずJWTトークンとして検証を試行
            try:
                from app.core.auth import verify_token

                payload = await verify_token(token)
                if payload:
                    email = payload.get("sub")
                    if email:
                        logger.debug("JWT token verification successful", email=email)
                        # データベースからユーザーを取得
                        async with AsyncSessionLocal() as db:
                            result = await db.execute(
                                select(User).where(User.email == email)
                            )
                            user = result.scalar_one_or_none()
                            if user:
                                logger.info(
                                    "WebSocket authentication successful via JWT",
                                    user_id=user.id,
                                    email=email,
                                )
                                return user
                            else:
                                logger.warning(
                                    "JWT token valid but user not found in database",
                                    email=email,
                                )
                    else:
                        logger.warning("JWT token missing 'sub' field")
                else:
                    logger.debug("JWT token verification returned None")
            except Exception as jwt_error:
                logger.debug(
                    "JWT token verification failed",
                    error_type=type(jwt_error).__name__,
                    error_message=str(jwt_error),
                )

            # JWTトークンが無効な場合、Firebaseトークンとして検証を試行
            try:
                logger.debug("Attempting Firebase token verification")
                firebase_payload = await verify_firebase_token(token)
                if firebase_payload:
                    uid = firebase_payload.get("uid")
                    email = firebase_payload.get("email")

                    if uid and email:
                        logger.debug(
                            "Firebase token verification successful",
                            uid=uid,
                            email=email,
                        )
                        # Firebase UIDでユーザーを検索
                        async with AsyncSessionLocal() as db:
                            result = await db.execute(
                                select(User).where(User.firebase_uid == uid)
                            )
                            user = result.scalar_one_or_none()
                            if user:
                                logger.info(
                                    "WebSocket authentication successful via Firebase",
                                    user_id=user.id,
                                    firebase_uid=uid,
                                    email=email,
                                )
                                return user
                            else:
                                logger.warning(
                                    "Firebase token valid but user not found in database",
                                    firebase_uid=uid,
                                    email=email,
                                )
                    else:
                        logger.warning(
                            "Firebase token missing required fields",
                            has_uid=bool(uid),
                            has_email=bool(email),
                        )
                else:
                    logger.debug("Firebase token verification returned None")
            except Exception as firebase_error:
                logger.debug(
                    "Firebase token verification failed",
                    error_type=type(firebase_error).__name__,
                    error_message=str(firebase_error),
                )

            # どちらのトークンも無効
            logger.warning(
                "WebSocket authentication failed: All token verification methods failed"
            )
            raise AuthenticationException("Invalid authentication token")

        except Exception as e:
            logger.error(
                "WebSocket authentication failed with unexpected error",
                error_type=type(e).__name__,
                error_message=str(e),
                error_traceback=str(e.__traceback__),
            )
            raise AuthenticationException(f"Authentication failed: {str(e)}")


class WebSocketMessageHandler:
    """WebSocketメッセージハンドラークラス"""

    @staticmethod
    async def _check_permission(
        user: User, session_id: str, required_permission: str
    ) -> bool:
        """ユーザーの権限をチェック"""
        try:
            # 基本的な権限チェック
            if not user.is_active:
                logger.warning(
                    "Permission check failed: User is not active",
                    user_id=user.id,
                    session_id=session_id,
                )
                return False

            # セッション参加者の権限チェック
            if required_permission in ["manage_session", "moderate_participants"]:
                # ホストまたはモデレーター権限が必要
                # TODO: 実際の権限システムと連携
                # 現在は基本的なチェックのみ
                logger.debug(
                    "Permission check passed for session management",
                    user_id=user.id,
                    session_id=session_id,
                    permission=required_permission,
                )
                return True

            # 基本的な参加者権限
            logger.debug(
                "Basic participant permission granted",
                user_id=user.id,
                session_id=session_id,
                permission=required_permission,
            )
            return True

        except Exception as e:
            logger.error(
                "Permission check failed with error",
                error_type=type(e).__name__,
                error_message=str(e),
                user_id=user.id,
                session_id=session_id,
                permission=required_permission,
            )
            return False

    @staticmethod
    async def _check_participant_permission(
        user: User, session_id: str, target_user_id: int, action: str
    ) -> bool:
        """特定の参加者に対する操作権限をチェック"""
        try:
            # 自分自身に対する操作は許可
            if user.id == target_user_id:
                logger.debug(
                    "Self-operation permission granted",
                    user_id=user.id,
                    target_user_id=target_user_id,
                    action=action,
                )
                return True

            # 管理者権限チェック
            if await WebSocketMessageHandler._check_permission(
                user, session_id, "moderate_participants"
            ):
                logger.debug(
                    "Moderator permission granted for participant operation",
                    user_id=user.id,
                    target_user_id=target_user_id,
                    action=action,
                )
                return True

            logger.warning(
                "Insufficient permission for participant operation",
                user_id=user.id,
                target_user_id=target_user_id,
                action=action,
            )
            return False

        except Exception as e:
            logger.error(
                "Participant permission check failed",
                error_type=type(e).__name__,
                error_message=str(e),
                user_id=user.id,
                target_user_id=target_user_id,
                action=action,
            )
            return False

    @staticmethod
    async def handle_join_session(session_id: str, connection_id: str, user: User):
        """セッション参加処理"""
        try:
            # 参加者一覧を取得
            participants = await manager.get_session_participants(session_id)

            # 参加者一覧を全員に送信
            await manager.broadcast_to_session(
                {
                    "type": "session_participants",
                    "session_id": session_id,
                    "participants": participants,
                    "timestamp": datetime.now().isoformat(),
                },
                session_id,
            )

            # 新規参加者を全員に通知
            await manager.broadcast_to_session(
                {
                    "type": "participant_joined",
                    "session_id": session_id,
                    "participant": {
                        "id": str(user.id),
                        "username": user.username,
                        "display_name": user.display_name,
                        "email": user.email,
                        "role": "PARTICIPANT",
                        "status": "online",
                        "is_active": True,
                        "is_muted": False,
                        "joinedAt": datetime.now().isoformat(),
                        "lastActivity": datetime.now().isoformat(),
                    },
                    "timestamp": datetime.now().isoformat(),
                },
                session_id,
                exclude_connection=connection_id,
            )

            logger.info(f"User {user.id} joined session {session_id}")

        except Exception as e:
            logger.error(f"Failed to handle join session: {e}")

    @staticmethod
    async def handle_message(
        websocket: WebSocket, message: dict, connection_id: str, user: User
    ):
        """WebSocketメッセージの処理"""
        try:
            message_type = message.get("type")
            session_id = message.get("roomId") or message.get("session_id")

            if not session_id:
                logger.warning(
                    "Message processing failed: No session ID",
                    message=message,
                    connection_id=connection_id,
                    user_id=user.id,
                )
                return

            logger.debug(
                "Processing WebSocket message",
                message_type=message_type,
                session_id=session_id,
                connection_id=connection_id,
                user_id=user.id,
            )

            # 接続の活動時間を更新
            await manager.update_connection_activity(connection_id)

            # メッセージタイプに応じた処理
            if message_type == "ping":
                # ハートビート応答
                logger.debug("Processing ping message", connection_id=connection_id)
                await manager.send_personal_message(
                    {"type": "pong", "timestamp": datetime.now().isoformat()},
                    connection_id,
                )

            elif message_type in ["offer", "answer", "ice-candidate"]:
                # WebRTCシグナリングメッセージ
                logger.debug(
                    "Processing WebRTC signaling message",
                    message_type=message_type,
                    session_id=session_id,
                    connection_id=connection_id,
                )
                await WebSocketMessageHandler._handle_webrtc_signaling(
                    message, session_id, connection_id, user
                )

            elif message_type == "join_session":
                # セッション参加
                logger.info(
                    "User joining session",
                    user_id=user.id,
                    session_id=session_id,
                    connection_id=connection_id,
                )
                await WebSocketMessageHandler.handle_join_session(
                    session_id, connection_id, user
                )

            elif message_type == "leave_session":
                # セッション退出
                logger.info(
                    "User leaving session",
                    user_id=user.id,
                    session_id=session_id,
                    connection_id=connection_id,
                )
                await WebSocketMessageHandler._handle_leave_session(
                    session_id, connection_id, user
                )

            elif message_type == "mute_participant":
                # 参加者のミュート制御
                participant_id = message.get("participant_id")
                muted = message.get("muted", False)
                logger.info(
                    "Participant mute control",
                    user_id=user.id,
                    target_participant_id=participant_id,
                    muted=muted,
                    session_id=session_id,
                )
                await WebSocketMessageHandler._handle_mute_participant(
                    message, session_id, connection_id, user
                )

            elif message_type == "change_participant_role":
                # 参加者の役割変更
                participant_id = message.get("participant_id")
                new_role = message.get("new_role")
                logger.info(
                    "Participant role change",
                    user_id=user.id,
                    target_participant_id=participant_id,
                    new_role=new_role,
                    session_id=session_id,
                )
                await WebSocketMessageHandler._handle_change_role(
                    message, session_id, connection_id, user
                )

            elif message_type == "remove_participant":
                # 参加者の削除
                participant_id = message.get("participant_id")
                logger.info(
                    "Participant removal",
                    user_id=user.id,
                    target_participant_id=participant_id,
                    session_id=session_id,
                )
                await WebSocketMessageHandler._handle_remove_participant(
                    message, session_id, connection_id, user
                )

            else:
                logger.warning(
                    "Unknown message type received",
                    message_type=message_type,
                    session_id=session_id,
                    connection_id=connection_id,
                    user_id=user.id,
                )

        except Exception as e:
            logger.error(
                "Failed to handle WebSocket message",
                error_type=type(e).__name__,
                error_message=str(e),
                message_type=message.get("type"),
                session_id=message.get("roomId") or message.get("session_id"),
                connection_id=connection_id,
                user_id=user.id,
            )
            await manager.send_personal_message(
                {"type": "error", "message": "Failed to process message"},
                connection_id,
            )

    @staticmethod
    async def _handle_webrtc_signaling(
        message: dict, session_id: str, connection_id: str, user: User
    ):
        """WebRTCシグナリングメッセージの処理"""
        try:
            message_type = message.get("type")
            target_user_id = message.get("to")
            data = message.get("data")

            if message_type == "offer":
                # Offerを対象ユーザーに転送
                if target_user_id:
                    target_connection = (
                        await WebSocketMessageHandler._find_user_connection(
                            target_user_id, session_id
                        )
                    )
                    if target_connection:
                        await manager.send_personal_message(
                            {
                                "type": "offer",
                                "from": str(user.id),
                                "roomId": session_id,
                                "data": data,
                                "timestamp": datetime.now().isoformat(),
                            },
                            target_connection,
                        )
                        logger.info(
                            f"Offer forwarded from {user.id} to {target_user_id}"
                        )

            elif message_type == "answer":
                # Answerを対象ユーザーに転送
                if target_user_id:
                    target_connection = (
                        await WebSocketMessageHandler._find_user_connection(
                            target_user_id, session_id
                        )
                    )
                    if target_connection:
                        await manager.send_personal_message(
                            {
                                "type": "answer",
                                "from": str(user.id),
                                "roomId": session_id,
                                "data": data,
                                "timestamp": datetime.now().isoformat(),
                            },
                            target_connection,
                        )
                        logger.info(
                            f"Answer forwarded from {user.id} to {target_user_id}"
                        )

            elif message_type == "ice-candidate":
                # ICE候補を対象ユーザーに転送
                if target_user_id:
                    target_connection = (
                        await WebSocketMessageHandler._find_user_connection(
                            target_user_id, session_id
                        )
                    )
                    if target_connection:
                        await manager.send_personal_message(
                            {
                                "type": "ice-candidate",
                                "from": str(user.id),
                                "roomId": session_id,
                                "data": data,
                                "timestamp": datetime.now().isoformat(),
                            },
                            target_connection,
                        )
                        logger.info(
                            f"ICE candidate forwarded from {user.id} to {target_user_id}"
                        )

        except Exception as e:
            logger.error(f"Failed to handle WebRTC signaling: {e}")

    @staticmethod
    async def _find_user_connection(user_id: str, session_id: str) -> Optional[str]:
        """ユーザーIDとセッションIDから接続IDを検索"""
        try:
            user_id_int = int(user_id)
            if user_id_int in manager.user_connections:
                for connection_id in manager.user_connections[user_id_int]:
                    if connection_id in manager.connection_info:
                        connection_info = manager.connection_info[connection_id]
                        if connection_info.get("session_id") == session_id:
                            return connection_id
        except (ValueError, KeyError):
            pass
        return None

    @staticmethod
    async def _handle_leave_session(session_id: str, connection_id: str, user: User):
        """セッション退出処理"""
        try:
            # 参加者退出を全員に通知
            await manager.broadcast_to_session(
                {
                    "type": "participant_left",
                    "session_id": session_id,
                    "participant_id": str(user.id),
                    "timestamp": datetime.now().isoformat(),
                },
                session_id,
                exclude_connection=connection_id,
            )

            logger.info(f"User {user.id} left session {session_id}")

        except Exception as e:
            logger.error(f"Failed to handle leave session: {e}")

    @staticmethod
    async def _handle_mute_participant(
        message: dict, session_id: str, connection_id: str, user: User
    ):
        """参加者のミュート制御"""
        try:
            participant_id = message.get("participant_id")
            muted = message.get("muted", False)

            # パラメータ検証
            if participant_id is None:
                logger.warning(
                    "Missing participant_id in mute message",
                    message=message,
                    user_id=user.id,
                    session_id=session_id,
                )
                await manager.send_personal_message(
                    {"type": "error", "message": "Missing participant_id parameter"},
                    connection_id,
                )
                return

            # 権限チェック
            if not await WebSocketMessageHandler._check_participant_permission(
                user, session_id, participant_id, "mute_participant"
            ):
                logger.warning(
                    "Permission denied for mute participant operation",
                    user_id=user.id,
                    target_participant_id=participant_id,
                    session_id=session_id,
                )
                await manager.send_personal_message(
                    {
                        "type": "error",
                        "message": "Insufficient permissions for this operation",
                    },
                    connection_id,
                )
                return

            # ミュート状態変更を全員に通知
            await manager.broadcast_to_session(
                {
                    "type": "participant_state_update",
                    "session_id": session_id,
                    "participant_id": participant_id,
                    "state": "mute",
                    "data": {"is_muted": muted},
                    "timestamp": datetime.now().isoformat(),
                },
                session_id,
            )

            logger.info(
                "Participant mute operation successful",
                user_id=user.id,
                target_participant_id=participant_id,
                muted=muted,
                session_id=session_id,
            )

        except Exception as e:
            logger.error(
                "Failed to handle mute participant",
                error_type=type(e).__name__,
                error_message=str(e),
                user_id=user.id,
                target_participant_id=message.get("participant_id"),
                session_id=session_id,
            )
            await manager.send_personal_message(
                {"type": "error", "message": "Failed to process mute operation"},
                connection_id,
            )

    @staticmethod
    async def _handle_change_role(
        message: dict, session_id: str, connection_id: str, user: User
    ):
        """参加者の役割変更"""
        try:
            participant_id = message.get("participant_id")
            new_role = message.get("new_role")

            # パラメータ検証
            if participant_id is None or new_role is None:
                logger.warning(
                    "Missing required parameters in role change message",
                    message=message,
                    user_id=user.id,
                    session_id=session_id,
                )
                await manager.send_personal_message(
                    {"type": "error", "message": "Missing required parameters"},
                    connection_id,
                )
                return

            # 権限チェック（ホストのみ）
            if not await WebSocketMessageHandler._check_permission(
                user, session_id, "manage_session"
            ):
                logger.warning(
                    "Permission denied for role change operation",
                    user_id=user.id,
                    target_participant_id=participant_id,
                    session_id=session_id,
                )
                await manager.send_personal_message(
                    {
                        "type": "error",
                        "message": "Only session hosts can change participant roles",
                    },
                    connection_id,
                )
                return

            # 役割変更を全員に通知
            await manager.broadcast_to_session(
                {
                    "type": "participant_state_update",
                    "session_id": session_id,
                    "participant_id": participant_id,
                    "state": "role",
                    "data": {"role": new_role},
                    "timestamp": datetime.now().isoformat(),
                },
                session_id,
            )

            logger.info(
                "Participant role change successful",
                user_id=user.id,
                target_participant_id=participant_id,
                new_role=new_role,
                session_id=session_id,
            )

        except Exception as e:
            logger.error(
                "Failed to handle change role",
                error_type=type(e).__name__,
                error_message=str(e),
                user_id=user.id,
                target_participant_id=message.get("participant_id"),
                session_id=session_id,
            )
            await manager.send_personal_message(
                {"type": "error", "message": "Failed to process role change"},
                connection_id,
            )

    @staticmethod
    async def _handle_remove_participant(
        message: dict, session_id: str, connection_id: str, user: User
    ):
        """参加者の削除"""
        try:
            participant_id = message.get("participant_id")

            # パラメータ検証
            if participant_id is None:
                logger.warning(
                    "Missing participant_id in remove participant message",
                    message=message,
                    user_id=user.id,
                    session_id=session_id,
                )
                await manager.send_personal_message(
                    {"type": "error", "message": "Missing participant_id parameter"},
                    connection_id,
                )
                return

            # 権限チェック（ホストのみ）
            if not await WebSocketMessageHandler._check_permission(
                user, session_id, "manage_session"
            ):
                logger.warning(
                    "Permission denied for participant removal operation",
                    user_id=user.id,
                    target_participant_id=participant_id,
                    session_id=session_id,
                )
                await manager.send_personal_message(
                    {
                        "type": "error",
                        "message": "Only session hosts can remove participants",
                    },
                    connection_id,
                )
                return

            # 参加者削除を全員に通知
            await manager.broadcast_to_session(
                {
                    "type": "participant_removed",
                    "session_id": session_id,
                    "participant_id": participant_id,
                    "timestamp": datetime.now().isoformat(),
                },
                session_id,
            )

            logger.info(
                "Participant removal successful",
                user_id=user.id,
                target_participant_id=participant_id,
                session_id=session_id,
            )

        except Exception as e:
            logger.error(
                "Failed to handle remove participant",
                error_type=type(e).__name__,
                error_message=str(e),
                user_id=user.id,
                target_participant_id=message.get("participant_id"),
                session_id=session_id,
            )
            await manager.send_personal_message(
                {"type": "error", "message": "Failed to process participant removal"},
                connection_id,
            )


# 定期的なクリーンアップタスク
async def cleanup_task():
    """定期的なクリーンアップタスク"""
    while True:
        try:
            await asyncio.sleep(300)  # 5分ごと
            await manager.cleanup_inactive_connections()
        except Exception as e:
            logger.error(f"Cleanup task error: {e}")


# クリーンアップタスクの開始
async def start_cleanup_task():
    """クリーンアップタスクを開始"""
    asyncio.create_task(cleanup_task())
