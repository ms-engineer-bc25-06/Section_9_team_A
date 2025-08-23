import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, status
import structlog
from datetime import datetime

from app.core.websocket import manager, WebSocketAuth, WebSocketMessageHandler
from app.services.voice_session_service import VoiceSessionService
from app.core.exceptions import AuthenticationException

router = APIRouter()
logger = structlog.get_logger()

# WebSocket接続のタイムアウト設定
WEBSOCKET_CONNECTION_TIMEOUT = 30.0  # 30秒
WEBSOCKET_AUTH_TIMEOUT = 10.0  # 認証タイムアウト10秒
WEBSOCKET_SESSION_CHECK_TIMEOUT = 5.0  # セッション確認タイムアウト5秒


@router.websocket("/voice-sessions/{session_id}")
async def websocket_voice_session(websocket: WebSocket, session_id: str):
    """音声セッション用WebSocketエンドポイント"""
    try:
        # 接続全体のタイムアウト設定
        connection_task = asyncio.create_task(
            _handle_voice_session_connection(websocket, session_id)
        )

        try:
            await asyncio.wait_for(
                connection_task, timeout=WEBSOCKET_CONNECTION_TIMEOUT
            )
        except asyncio.TimeoutError:
            logger.error(f"WebSocket connection timeout for session {session_id}")
            await websocket.close(
                code=status.WS_1011_INTERNAL_ERROR, reason="Connection timeout"
            )
            return

    except Exception as e:
        logger.error(f"Unexpected error in voice session WebSocket: {e}")
        await websocket.close(
            code=status.WS_1011_INTERNAL_ERROR, reason="Internal server error"
        )


async def _handle_voice_session_connection(websocket: WebSocket, session_id: str):
    """音声セッション接続の実際の処理"""
    connection_id = None
    connection_established = False

    try:
        # 認証（タイムアウト付き）
        try:
            user = await asyncio.wait_for(
                WebSocketAuth.authenticate_websocket(websocket),
                timeout=WEBSOCKET_AUTH_TIMEOUT,
            )
            logger.info(f"WebSocket authentication successful for user {user.id}")
        except asyncio.TimeoutError:
            logger.warning(f"WebSocket authentication timeout for session {session_id}")
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION, reason="Authentication timeout"
            )
            return
        except AuthenticationException as e:
            logger.warning(f"Authentication failed: {e}")
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION, reason="Authentication failed"
            )
            return

        # セッション存在確認（タイムアウト付き）
        try:
            # データベースセッションを適切に管理
            from app.core.database import AsyncSessionLocal

            async with AsyncSessionLocal() as db:
                voice_session_service = VoiceSessionService(db)
                session = await asyncio.wait_for(
                    voice_session_service.get_session_by_session_id(session_id),
                    timeout=WEBSOCKET_SESSION_CHECK_TIMEOUT,
                )
                if not session:
                    logger.warning(f"Session not found: {session_id}")
                    await websocket.close(
                        code=status.WS_1008_POLICY_VIOLATION, reason="Session not found"
                    )
                    return
        except asyncio.TimeoutError:
            logger.warning(f"Session check timeout for session {session_id}")
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION, reason="Session check timeout"
            )
            return
        except Exception as e:
            logger.error(f"Session check failed: {e}")
            await websocket.close(
                code=status.WS_1011_INTERNAL_ERROR, reason="Session check failed"
            )
            return

        # 接続を確立
        try:
            connection_id = await manager.connect(websocket, session_id, user)
            connection_established = True
            logger.info(
                f"WebSocket connection established: {connection_id} for session {session_id}"
            )
        except Exception as e:
            logger.error(f"Failed to establish connection: {e}")
            await websocket.close(
                code=status.WS_1011_INTERNAL_ERROR,
                reason="Connection establishment failed",
            )
            return

        # 接続成功通知
        try:
            await manager.send_personal_message(
                {
                    "type": "connection_established",
                    "session_id": session_id,
                    "user_id": user.id,
                    "timestamp": manager.connection_info[connection_id][
                        "connected_at"
                    ].isoformat(),
                },
                connection_id,
            )
        except Exception as e:
            logger.error(f"Failed to send connection established message: {e}")
            # 接続成功通知の失敗は致命的ではないが、ログに記録
            # 接続自体は継続する

        # セッション参加通知
        try:
            await WebSocketMessageHandler.handle_join_session(
                session_id, connection_id, user
            )
        except Exception as e:
            logger.error(f"Failed to handle join session: {e}")
            # クライアントにエラーを通知
            await manager.send_personal_message(
                {"type": "error", "message": "Failed to join session"}, connection_id
            )
            # エラーが発生した場合は接続を切断
            await websocket.close(
                code=status.WS_1011_INTERNAL_ERROR, reason="Session join failed"
            )
            return

        # メッセージ受信ループ
        while True:
            try:
                # メッセージを受信
                data = await websocket.receive_text()
                message = json.loads(data)

                # メッセージを処理
                await WebSocketMessageHandler.handle_message(
                    websocket, message, connection_id, user
                )

            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected: {connection_id}")
                break
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received from {connection_id}")
                await manager.send_personal_message(
                    {"type": "error", "message": "Invalid JSON format"}, connection_id
                )
            except Exception as e:
                logger.error(f"Error processing message from {connection_id}: {e}")
                try:
                    await manager.send_personal_message(
                        {"type": "error", "message": "Internal server error"},
                        connection_id,
                    )
                except Exception as send_error:
                    logger.error(
                        f"Failed to send error message to {connection_id}: {send_error}"
                    )
                    # エラーメッセージの送信に失敗した場合は接続を切断
                    break

    except Exception as e:
        logger.error(f"Error in voice session connection handler: {e}")
        await websocket.close(
            code=status.WS_1011_INTERNAL_ERROR, reason="Internal server error"
        )
    finally:
        # 接続を適切に切断（接続が確立されている場合のみ）
        if connection_id and connection_established:
            try:
                await manager.disconnect(connection_id)
                logger.info(f"WebSocket connection properly closed: {connection_id}")
            except Exception as e:
                logger.error(f"Error during disconnect: {connection_id}, error: {e}")
        elif connection_id:
            logger.warning(
                f"Connection {connection_id} was not fully established, skipping disconnect"
            )


@router.websocket("/chat-rooms/{room_id}")
async def websocket_chat_room(websocket: WebSocket, room_id: str):
    """チャットルーム用WebSocketエンドポイント"""
    try:
        # 接続全体のタイムアウト設定
        connection_task = asyncio.create_task(
            _handle_chat_room_connection(websocket, room_id)
        )

        try:
            await asyncio.wait_for(
                connection_task, timeout=WEBSOCKET_CONNECTION_TIMEOUT
            )
        except asyncio.TimeoutError:
            logger.error(f"WebSocket connection timeout for room {room_id}")
            await websocket.close(
                code=status.WS_1011_INTERNAL_ERROR, reason="Connection timeout"
            )
            return

    except Exception as e:
        logger.error(f"Unexpected error in chat room WebSocket: {e}")
        await websocket.close(
            code=status.WS_1011_INTERNAL_ERROR, reason="Internal server error"
        )


async def _handle_chat_room_connection(websocket: WebSocket, room_id: str):
    """チャットルーム接続の実際の処理"""
    connection_id = None
    connection_established = False

    try:
        # 認証（タイムアウト付き）
        try:
            user = await asyncio.wait_for(
                WebSocketAuth.authenticate_websocket(websocket),
                timeout=WEBSOCKET_AUTH_TIMEOUT,
            )
            logger.info(f"WebSocket authentication successful for user {user.id}")
        except asyncio.TimeoutError:
            logger.warning(f"WebSocket authentication timeout for room {room_id}")
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION, reason="Authentication timeout"
            )
            return
        except AuthenticationException as e:
            logger.warning(f"Authentication failed: {e}")
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION, reason="Authentication failed"
            )
            return

        # 接続を確立
        try:
            connection_id = await manager.connect(websocket, room_id, user)
            connection_established = True
            logger.info(
                f"WebSocket connection established: {connection_id} for room {room_id}"
            )
        except Exception as e:
            logger.error(f"Failed to establish connection: {e}")
            await websocket.close(
                code=status.WS_1011_INTERNAL_ERROR,
                reason="Connection establishment failed",
            )
            return

        # 接続成功通知
        try:
            await manager.send_personal_message(
                {
                    "type": "connection_established",
                    "room_id": room_id,
                    "user_id": user.id,
                    "timestamp": manager.connection_info[connection_id][
                        "connected_at"
                    ].isoformat(),
                },
                connection_id,
            )
        except Exception as e:
            logger.error(f"Failed to send connection established message: {e}")

        # ルーム参加通知
        try:
            await WebSocketMessageHandler.handle_join_session(
                room_id, connection_id, user
            )
        except Exception as e:
            logger.error(f"Failed to handle join session: {e}")
            # クライアントにエラーを通知
            await manager.send_personal_message(
                {"type": "error", "message": "Failed to join room"}, connection_id
            )
            # エラーが発生した場合は接続を切断
            await websocket.close(
                code=status.WS_1011_INTERNAL_ERROR, reason="Room join failed"
            )
            return

        # メッセージ受信ループ
        while True:
            try:
                # メッセージを受信
                data = await websocket.receive_text()
                message = json.loads(data)

                # メッセージを処理
                await WebSocketMessageHandler.handle_message(
                    websocket, message, connection_id, user
                )

            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected: {connection_id}")
                break
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received from {connection_id}")
                await manager.send_personal_message(
                    {"type": "error", "message": "Invalid JSON format"}, connection_id
                )
            except Exception as e:
                logger.error(f"Error processing message from {connection_id}: {e}")
                try:
                    await manager.send_personal_message(
                        {"type": "error", "message": "Internal server error"},
                        connection_id,
                    )
                except Exception as send_error:
                    logger.error(
                        f"Failed to send error message to {connection_id}: {send_error}"
                    )
                    # エラーメッセージの送信に失敗した場合は接続を切断
                    break

    except Exception as e:
        logger.error(f"Error in chat room connection handler: {e}")
        await websocket.close(
            code=status.WS_1011_INTERNAL_ERROR, reason="Internal server error"
        )
    finally:
        # 接続を適切に切断（接続が確立されている場合のみ）
        if connection_id and connection_established:
            try:
                await manager.disconnect(connection_id)
                logger.info(f"WebSocket connection properly closed: {connection_id}")
            except Exception as e:
                logger.error(f"Error during disconnect: {connection_id}, error: {e}")
        elif connection_id:
            logger.warning(
                f"Connection {connection_id} was not fully established, skipping disconnect"
            )


# 基本的な接続管理API
@router.get("/connections/stats")
async def get_connection_stats():
    """接続統計を取得"""
    try:
        stats = manager.get_connection_stats()
        return {
            "stats": stats,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to get connection stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get connection stats")


@router.post("/connections/cleanup")
async def cleanup_inactive_connections():
    """非アクティブな接続をクリーンアップ"""
    try:
        await manager.cleanup_inactive_connections()
        return {
            "status": "cleanup_completed",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to cleanup connections: {e}")
        raise HTTPException(status_code=500, detail="Failed to cleanup connections")
