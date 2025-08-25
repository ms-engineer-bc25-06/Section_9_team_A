import json
import asyncio
import time
from typing import Dict, Set, Optional, Any
from fastapi import WebSocket, HTTPException, status
import structlog
from datetime import datetime, timedelta
from collections import defaultdict, deque

from app.core.auth import verify_firebase_token
from app.models.user import User
from app.core.exceptions import AuthenticationException
from app.core.database import AsyncSessionLocal
from sqlalchemy import select

logger = structlog.get_logger()


class WebSocketPerformanceMonitor:
    """WebSocketパフォーマンス監視クラス"""

    def __init__(self):
        self.connection_times = deque(maxlen=1000)  # 接続時間の履歴
        self.message_processing_times = deque(maxlen=1000)  # メッセージ処理時間の履歴
        self.error_counts = defaultdict(int)  # エラー種別別カウント
        self.message_counts = defaultdict(int)  # メッセージ種別別カウント
        self.peak_connections = 0  # ピーク接続数
        self.total_connections = 0  # 総接続数
        self.total_messages = 0  # 総メッセージ数
        self.total_errors = 0  # 総エラー数
        self.start_time = time.time()  # 監視開始時刻

    def record_connection_time(self, connection_time: float):
        """接続時間を記録"""
        self.connection_times.append(connection_time)

    def record_message_processing_time(self, processing_time: float):
        """メッセージ処理時間を記録"""
        self.message_processing_times.append(processing_time)

    def record_error(self, error_type: str):
        """エラーを記録"""
        self.error_counts[error_type] += 1
        self.total_errors += 1

    def record_message(self, message_type: str):
        """メッセージを記録"""
        self.message_counts[message_type] += 1
        self.total_messages += 1

    def record_connection_count(self, current_count: int):
        """接続数を記録"""
        self.peak_connections = max(self.peak_connections, current_count)
        self.total_connections += 1

    def get_performance_stats(self) -> Dict[str, Any]:
        """パフォーマンス統計を取得"""
        current_time = time.time()
        uptime = current_time - self.start_time

        # 接続時間の統計
        connection_times = list(self.connection_times)
        avg_connection_time = (
            sum(connection_times) / len(connection_times) if connection_times else 0
        )
        max_connection_time = max(connection_times) if connection_times else 0
        min_connection_time = min(connection_times) if connection_times else 0

        # メッセージ処理時間の統計
        processing_times = list(self.message_processing_times)
        avg_processing_time = (
            sum(processing_times) / len(processing_times) if processing_times else 0
        )
        max_processing_time = max(processing_times) if processing_times else 0
        min_processing_time = min(processing_times) if processing_times else 0

        # エラー率の計算
        error_rate = (
            (self.total_errors / self.total_messages * 100)
            if self.total_messages > 0
            else 0
        )

        # 接続率の計算
        connection_rate = (self.total_connections / uptime) if uptime > 0 else 0

        return {
            "uptime_seconds": uptime,
            "total_connections": self.total_connections,
            "peak_connections": self.peak_connections,
            "total_messages": self.total_messages,
            "total_errors": self.total_errors,
            "error_rate_percent": round(error_rate, 2),
            "connection_rate_per_second": round(connection_rate, 2),
            "connection_times": {
                "average_ms": round(avg_connection_time * 1000, 2),
                "maximum_ms": round(max_connection_time * 1000, 2),
                "minimum_ms": round(min_connection_time * 1000, 2),
                "sample_count": len(connection_times),
            },
            "message_processing_times": {
                "average_ms": round(avg_processing_time * 1000, 2),
                "maximum_ms": round(max_processing_time * 1000, 2),
                "minimum_ms": round(min_processing_time * 1000, 2),
                "sample_count": len(processing_times),
            },
            "error_breakdown": dict(self.error_counts),
            "message_breakdown": dict(self.message_counts),
        }

    def reset_stats(self):
        """統計をリセット"""
        self.connection_times.clear()
        self.message_processing_times.clear()
        self.error_counts.clear()
        self.message_counts.clear()
        self.peak_connections = 0
        self.total_connections = 0
        self.total_messages = 0
        self.total_errors = 0
        self.start_time = time.time()


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
        # パフォーマンス監視
        self.performance_monitor = WebSocketPerformanceMonitor()

    async def connect(self, websocket: WebSocket, session_id: str, user: User) -> str:
        """WebSocket接続を確立"""
        start_time = time.time()

        try:
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

            # パフォーマンス監視
            connection_time = time.time() - start_time
            self.performance_monitor.record_connection_time(connection_time)
            self.performance_monitor.record_connection_count(
                len(self.active_connections)
            )

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
                connection_time_ms=round(connection_time * 1000, 2),
            )

            return connection_id

        except Exception as e:
            # パフォーマンス監視
            self.performance_monitor.record_error("connection_failed")

            logger.error(
                "Failed to establish WebSocket connection",
                error_type=type(e).__name__,
                error_message=str(e),
                user_id=user.id,
                session_id=session_id,
            )

            # 接続に失敗した場合、WebSocketを適切に閉じる
            # 注意: websocket.accept()が呼ばれていない場合はclose()を呼べない
            try:
                if websocket.client_state.value >= 2:  # WebSocket.CONNECTING以上
                    await websocket.close(
                        code=status.WS_1011_INTERNAL_ERROR, reason="Connection failed"
                    )
            except Exception as close_error:
                logger.error(
                    f"Failed to close WebSocket after connection failure: {close_error}"
                )

            raise

    async def _check_connection_limits(self, session_id: str, user_id: int):
        """接続制限をチェック"""
        logger.info(f"接続制限チェック開始: session_id={session_id}, user_id={user_id}")

        # ユーザー別接続数チェック
        user_connections = len(self.user_connections.get(user_id, set()))
        logger.info(
            f"ユーザー接続数: {user_connections}/{self.max_connections_per_user}"
        )
        if user_connections >= self.max_connections_per_user:
            logger.warning(
                f"ユーザー接続制限超過: user_id={user_id}, connections={user_connections}"
            )
            self.performance_monitor.record_error("user_connection_limit_exceeded")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Maximum connections per user exceeded",
            )

        # セッション別接続数チェック
        session_connections = len(self.session_connections.get(session_id, set()))
        logger.info(
            f"セッション接続数: {session_connections}/{self.max_connections_per_session}"
        )
        if session_connections >= self.max_connections_per_session:
            logger.warning(
                f"セッション接続制限超過: session_id={session_id}, connections={session_connections}"
            )
            self.performance_monitor.record_error("session_connection_limit_exceeded")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Maximum connections per session exceeded",
            )

        logger.info("接続制限チェック完了: 接続可能")

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
            self.performance_monitor.record_error("disconnect_error")
            logger.error(f"Error during disconnect: {e}")

    async def send_personal_message(self, message: dict, connection_id: str):
        """特定の接続にメッセージを送信"""
        start_time = time.time()

        try:
            if connection_id in self.active_connections:
                websocket = self.active_connections[connection_id]

                # WebSocketの状態をチェック
                if websocket.client_state.value >= 3:  # WebSocket.OPEN以上
                    await websocket.send_text(json.dumps(message))

                    # パフォーマンス監視
                    processing_time = time.time() - start_time
                    self.performance_monitor.record_message_processing_time(
                        processing_time
                    )

                    logger.debug(f"Personal message sent to {connection_id}")
                else:
                    logger.warning(
                        f"WebSocket not in OPEN state for {connection_id}, state: {websocket.client_state.value}"
                    )
                    # 接続が開いていない場合は切断
                    await self.disconnect(connection_id)
            else:
                logger.warning(
                    f"Connection {connection_id} not found in active connections"
                )
        except Exception as e:
            self.performance_monitor.record_error("send_message_failed")
            logger.error(f"Failed to send personal message to {connection_id}: {e}")
            # エラーが発生した場合は接続を切断
            try:
                await self.disconnect(connection_id)
            except Exception as disconnect_error:
                logger.error(
                    f"Failed to disconnect {connection_id} after send error: {disconnect_error}"
                )

    async def broadcast_to_session(
        self, message: dict, session_id: str, exclude_connection: Optional[str] = None
    ):
        """セッション内の全接続にメッセージをブロードキャスト"""
        start_time = time.time()

        try:
            if session_id in self.session_connections:
                for connection_id in self.session_connections[session_id]:
                    if (
                        connection_id != exclude_connection
                        and connection_id in self.active_connections
                    ):
                        await self.send_personal_message(message, connection_id)

                # パフォーマンス監視
                processing_time = time.time() - start_time
                self.performance_monitor.record_message_processing_time(processing_time)

                logger.debug(f"Broadcast message sent to session {session_id}")
        except Exception as e:
            self.performance_monitor.record_error("broadcast_failed")
            logger.error(f"Failed to broadcast to session {session_id}: {e}")

    async def get_session_participants(self, session_id: str) -> list:
        """セッションの参加者一覧を取得"""
        participants = []

        try:
            # まずデータベースから参加者情報を取得
            from app.core.database import AsyncSessionLocal
            from app.services.voice_session_service import VoiceSessionService

            async with AsyncSessionLocal() as db:
                voice_session_service = VoiceSessionService(db)
                session = await voice_session_service.get_session_by_session_id(
                    session_id
                )

                if session and session.participants:
                    try:
                        # participantsフィールドをJSONとしてパース
                        participants_data = (
                            json.loads(session.participants)
                            if isinstance(session.participants, str)
                            else session.participants
                        )

                        for participant in participants_data:
                            participants.append(
                                {
                                    "id": str(participant.get("user_id")),
                                    "username": participant.get("username", "Unknown"),
                                    "display_name": participant.get(
                                        "username", "Unknown"
                                    ),
                                    "email": participant.get("email", ""),
                                    "role": participant.get(
                                        "role", "participant"
                                    ).upper(),
                                    "status": "online"
                                    if participant.get("is_active", True)
                                    else "offline",
                                    "is_active": participant.get("is_active", True),
                                    "is_muted": False,
                                    "joinedAt": participant.get(
                                        "joined_at", datetime.now().isoformat()
                                    ),
                                    "lastActivity": datetime.now().isoformat(),
                                }
                            )

                        logger.info(
                            f"Retrieved {len(participants)} participants from database for session {session_id}"
                        )
                        return participants

                    except (json.JSONDecodeError, TypeError) as e:
                        logger.error(
                            f"Failed to parse participants data for session {session_id}: {e}"
                        )

            # データベースからの取得に失敗した場合、現在のWebSocket接続から取得
            logger.warning(
                f"Falling back to WebSocket connections for session {session_id}"
            )
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

            logger.info(
                f"Total participants retrieved: {len(participants)} for session {session_id}"
            )
            return participants

        except Exception as e:
            logger.error(f"Error getting session participants for {session_id}: {e}")
            return []

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

    async def get_performance_stats(self) -> dict:
        """パフォーマンス統計を取得"""
        return self.performance_monitor.get_performance_stats()

    async def reset_performance_stats(self):
        """パフォーマンス統計をリセット"""
        self.performance_monitor.reset_stats()


# グローバルインスタンス
manager = ConnectionManager()


class WebSocketAuth:
    """WebSocket認証クラス"""

    @staticmethod
    async def authenticate_websocket(websocket: WebSocket) -> User:
        """WebSocket接続の認証（Firebase IDトークンのみ）"""
        start_time = time.time()
        logger.info("WebSocket認証処理を開始")

        # WebSocketの状態をログ出力
        logger.info(f"WebSocket状態: client_state={websocket.client_state.value}")

        try:
            # クエリパラメータからトークンを取得
            query_params = websocket.query_params
            token = query_params.get("token")

            if not token:
                logger.warning("WebSocket authentication failed: No token provided")
                manager.performance_monitor.record_error("no_token_provided")
                raise AuthenticationException("No authentication token provided")

            logger.info(
                "WebSocket authentication started",
                token_length=len(token) if token else 0,
            )

            # Firebase IDトークンの検証
            try:
                logger.info("Firebase IDトークンの検証を開始")
                firebase_payload = await verify_firebase_token(token)
                if not firebase_payload:
                    logger.warning("Firebase token verification returned None")
                    manager.performance_monitor.record_error(
                        "firebase_token_verification_failed"
                    )
                    raise AuthenticationException("Invalid Firebase token")

                uid = firebase_payload.get("uid")
                email = firebase_payload.get("email")

                if not uid or not email:
                    logger.warning(
                        "Firebase token missing required fields",
                        has_uid=bool(uid),
                        has_email=bool(email),
                    )
                    manager.performance_monitor.record_error(
                        "firebase_token_missing_fields"
                    )
                    raise AuthenticationException("Invalid token payload")

                logger.info(f"Firebaseトークン検証成功: uid={uid}, email={email}")

                # Firebase UIDでユーザーを検索
                logger.info(
                    f"データベースでユーザーを検索中: firebase_uid={uid}, email={email}"
                )
                async with AsyncSessionLocal() as db:
                    try:
                        result = await db.execute(
                            select(User).where(User.firebase_uid == uid)
                        )
                        user = result.scalar_one_or_none()

                        if not user:
                            logger.warning(
                                "Firebase token valid but user not found in database",
                                firebase_uid=uid,
                                email=email,
                            )
                            manager.performance_monitor.record_error("user_not_found")
                            raise AuthenticationException("User not found")

                        logger.info(
                            f"ユーザー検索成功: user_id={user.id}, username={user.username}"
                        )

                    except Exception as db_error:
                        logger.error(f"データベース検索エラー: {db_error}")
                        manager.performance_monitor.record_error(
                            "database_search_error"
                        )
                        raise AuthenticationException(
                            "Database error during user lookup"
                        )

                # パフォーマンス監視
                auth_time = time.time() - start_time
                manager.performance_monitor.record_connection_time(auth_time)

                logger.info(
                    "WebSocket authentication successful",
                    user_id=user.id,
                    firebase_uid=uid,
                    email=email,
                    auth_time_ms=round(auth_time * 1000, 2),
                )
                return user

            except Exception as firebase_error:
                manager.performance_monitor.record_error("firebase_verification_error")
                logger.error(
                    "Firebase token verification failed",
                    error_type=type(firebase_error).__name__,
                    error_message=str(firebase_error),
                )
                raise AuthenticationException("Invalid authentication token")

        except Exception as e:
            manager.performance_monitor.record_error("authentication_failed")
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
    async def _is_session_host_or_moderator(user: User, session_id: str) -> bool:
        """ユーザーがセッションのホストまたはモデレーターかを判定"""
        start_time = time.time()

        try:
            from app.services.voice_session_service import VoiceSessionService

            # データベースからセッション情報を取得
            async with AsyncSessionLocal() as db:
                voice_session_service = VoiceSessionService(db)
                session = await voice_session_service.get_session_by_session_id(
                    session_id
                )

                if not session:
                    logger.warning(
                        "Session not found for permission check",
                        user_id=user.id,
                        session_id=session_id,
                    )
                    manager.performance_monitor.record_error("session_not_found")
                    return False

                # セッションのホストかチェック
                if session.host_id == user.id:
                    logger.debug(
                        "User is session host",
                        user_id=user.id,
                        session_id=session_id,
                        host_id=session.host_id,
                    )
                    return True

                # TODO: モデレーター権限のチェックを追加
                # 現在はホストのみが管理権限を持つ
                logger.debug(
                    "User is not session host or moderator",
                    user_id=user.id,
                    session_id=session_id,
                    host_id=session.host_id,
                )
                return False

        except Exception as e:
            manager.performance_monitor.record_error("permission_check_failed")
            logger.error(
                "Failed to check session host or moderator status",
                error_type=type(e).__name__,
                error_message=str(e),
                user_id=user.id,
                session_id=session_id,
            )
            return False

    @staticmethod
    async def _check_permission(
        user: User, session_id: str, required_permission: str
    ) -> bool:
        """ユーザーの権限をチェック"""
        start_time = time.time()

        try:
            # 基本的な権限チェック
            if not user.is_active:
                logger.warning(
                    "Permission check failed: User is not active",
                    user_id=user.id,
                    session_id=session_id,
                )
                manager.performance_monitor.record_error("user_not_active")
                return False

            # セッション参加者の権限チェック
            if required_permission in ["manage_session", "moderate_participants"]:
                # 実際のセッション権限をチェック
                if await WebSocketMessageHandler._is_session_host_or_moderator(
                    user, session_id
                ):
                    logger.debug(
                        "Permission check passed for session management",
                        user_id=user.id,
                        session_id=session_id,
                        permission=required_permission,
                    )
                    return True
                else:
                    logger.warning(
                        "Permission denied: User is not session host or moderator",
                        user_id=user.id,
                        session_id=session_id,
                        permission=required_permission,
                    )
                    manager.performance_monitor.record_error("permission_denied")
                    return False

            # 基本的な参加者権限
            logger.debug(
                "Basic participant permission granted",
                user_id=user.id,
                session_id=session_id,
                permission=required_permission,
            )
            return True

        except Exception as e:
            manager.performance_monitor.record_error("permission_check_error")
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
        start_time = time.time()

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
            manager.performance_monitor.record_error("insufficient_permission")
            return False

        except Exception as e:
            manager.performance_monitor.record_error(
                "participant_permission_check_failed"
            )
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
        start_time = time.time()

        try:
            # 参加者一覧を取得
            participants = await manager.get_session_participants(session_id)

            if not participants:
                logger.warning(f"No participants found for session {session_id}")
                raise Exception("Failed to get session participants")

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

            # パフォーマンス監視
            processing_time = time.time() - start_time
            manager.performance_monitor.record_message_processing_time(processing_time)
            manager.performance_monitor.record_message("join_session")

            logger.info(f"User {user.id} joined session {session_id}")

        except Exception as e:
            manager.performance_monitor.record_error("join_session_failed")
            logger.error(f"Failed to handle join session: {e}")

    @staticmethod
    async def handle_message(
        websocket: WebSocket, message: dict, connection_id: str, user: User
    ):
        """WebSocketメッセージの処理"""
        start_time = time.time()
        message_type = message.get("type")

        try:
            if not message_type:
                logger.warning(
                    "Message processing failed: No message type",
                    message=message,
                    connection_id=connection_id,
                    user_id=user.id,
                )
                manager.performance_monitor.record_error("no_message_type")
                return

            session_id = message.get("roomId") or message.get("session_id")

            if not session_id:
                logger.warning(
                    "Message processing failed: No session ID",
                    message=message,
                    connection_id=connection_id,
                    user_id=user.id,
                )
                manager.performance_monitor.record_error("no_session_id")
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
                try:
                    await manager.send_personal_message(
                        {"type": "pong", "timestamp": datetime.now().isoformat()},
                        connection_id,
                    )
                except Exception as e:
                    logger.warning(
                        f"Failed to send pong response to {connection_id}: {e}"
                    )
                    # pong送信の失敗は致命的ではない

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
                manager.performance_monitor.record_error("unknown_message_type")

            # パフォーマンス監視
            processing_time = time.time() - start_time
            manager.performance_monitor.record_message_processing_time(processing_time)
            manager.performance_monitor.record_message(message_type)

        except Exception as e:
            manager.performance_monitor.record_error("message_processing_failed")
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
        start_time = time.time()

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

            # パフォーマンス監視
            processing_time = time.time() - start_time
            manager.performance_monitor.record_message_processing_time(processing_time)
            manager.performance_monitor.record_message(f"webrtc_{message_type}")

        except Exception as e:
            manager.performance_monitor.record_error("webrtc_signaling_failed")
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
        start_time = time.time()

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

            # パフォーマンス監視
            processing_time = time.time() - start_time
            manager.performance_monitor.record_message_processing_time(processing_time)
            manager.performance_monitor.record_message("leave_session")

            logger.info(f"User {user.id} left session {session_id}")

        except Exception as e:
            manager.performance_monitor.record_error("leave_session_failed")
            logger.error(f"Failed to handle leave session: {e}")

    @staticmethod
    async def _handle_mute_participant(
        message: dict, session_id: str, connection_id: str, user: User
    ):
        """参加者のミュート制御"""
        start_time = time.time()

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
                manager.performance_monitor.record_error("missing_participant_id")
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
                manager.performance_monitor.record_error("mute_permission_denied")
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

            # パフォーマンス監視
            processing_time = time.time() - start_time
            manager.performance_monitor.record_message_processing_time(processing_time)
            manager.performance_monitor.record_message("mute_participant")

            logger.info(
                "Participant mute operation successful",
                user_id=user.id,
                target_participant_id=participant_id,
                muted=muted,
                session_id=session_id,
            )

        except Exception as e:
            manager.performance_monitor.record_error("mute_participant_failed")
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
        start_time = time.time()

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
                manager.performance_monitor.record_error("missing_role_change_params")
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
                manager.performance_monitor.record_error(
                    "role_change_permission_denied"
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

            # パフォーマンス監視
            processing_time = time.time() - start_time
            manager.performance_monitor.record_message_processing_time(processing_time)
            manager.performance_monitor.record_message("change_role")

            logger.info(
                "Participant role change successful",
                user_id=user.id,
                target_participant_id=participant_id,
                new_role=new_role,
                session_id=session_id,
            )

        except Exception as e:
            manager.performance_monitor.record_error("change_role_failed")
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
        start_time = time.time()

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
                manager.performance_monitor.record_error(
                    "missing_remove_participant_id"
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
                manager.performance_monitor.record_error(
                    "remove_participant_permission_denied"
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

            # パフォーマンス監視
            processing_time = time.time() - start_time
            manager.performance_monitor.record_message_processing_time(processing_time)
            manager.performance_monitor.record_message("remove_participant")

            logger.info(
                "Participant removal successful",
                user_id=user.id,
                target_participant_id=participant_id,
                session_id=session_id,
            )

        except Exception as e:
            manager.performance_monitor.record_error("remove_participant_failed")
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
