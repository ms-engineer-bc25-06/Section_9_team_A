import json
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, status
import structlog

from app.core.websocket import manager, WebSocketAuth, WebSocketMessageHandler
from app.services.voice_session_service import VoiceSessionService
from app.core.database import get_db
from app.core.exceptions import AuthenticationException, NotFoundException

router = APIRouter()
logger = structlog.get_logger()


@router.websocket("/voice-sessions/{session_id}")
async def websocket_voice_session(websocket: WebSocket, session_id: str):
    """音声セッション用WebSocketエンドポイント"""
    connection_id = None

    try:
        # 認証
        user = await WebSocketAuth.authenticate_websocket(websocket)

        # セッション存在確認
        async for db in get_db():
            voice_session_service = VoiceSessionService(db)
            session = await voice_session_service.get_session_by_session_id(session_id)
            if not session:
                await websocket.close(
                    code=status.WS_1008_POLICY_VIOLATION, reason="Session not found"
                )
                return

        # 接続を確立
        connection_id = await manager.connect(websocket, session_id, user)

        # 接続成功通知
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

        # セッション参加通知
        await WebSocketMessageHandler.handle_join_session(
            session_id, connection_id, user
        )

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
                await manager.send_personal_message(
                    {"type": "error", "message": "Internal server error"}, connection_id
                )

    except AuthenticationException as e:
        logger.warning(f"Authentication failed: {e}")
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION, reason="Authentication failed"
        )
    except NotFoundException as e:
        logger.warning(f"Session not found: {e}")
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION, reason="Session not found"
        )
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close(
            code=status.WS_1011_INTERNAL_ERROR, reason="Internal server error"
        )
    finally:
        # 接続を切断
        if connection_id:
            manager.disconnect(connection_id)


@router.websocket("/chat-rooms/{room_id}")
async def websocket_chat_room(websocket: WebSocket, room_id: str):
    """チャットルーム用WebSocketエンドポイント"""
    connection_id = None

    try:
        # 認証
        user = await WebSocketAuth.authenticate_websocket(websocket)

        # ルーム存在確認（将来的に実装）
        # async for db in get_db():
        #     chat_room_service = ChatRoomService(db)
        #     room = await chat_room_service.get_room_by_id(room_id)
        #     if not room:
        #         await websocket.close(code=status.WS_1008_POLICY_VIOLATION,
        #                             reason="Room not found")
        #         return

        # 接続を確立
        connection_id = await manager.connect(websocket, room_id, user)

        # 接続成功通知
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

        # ルーム参加通知
        await WebSocketMessageHandler.handle_join_session(room_id, connection_id, user)

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
                await manager.send_personal_message(
                    {"type": "error", "message": "Internal server error"}, connection_id
                )

    except AuthenticationException as e:
        logger.warning(f"Authentication failed: {e}")
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION, reason="Authentication failed"
        )
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close(
            code=status.WS_1011_INTERNAL_ERROR, reason="Internal server error"
        )
    finally:
        # 接続を切断
        if connection_id:
            manager.disconnect(connection_id)


@router.get("/voice-sessions/{session_id}/participants")
async def get_session_participants(session_id: str):
    """セッション参加者一覧を取得"""
    participants = manager.get_session_participants(session_id)
    return {
        "session_id": session_id,
        "participants": list(participants),
        "count": len(participants),
    }


@router.get("/voice-sessions/{session_id}/status")
async def get_session_status(session_id: str):
    """セッション状態を取得"""
    connection_count = manager.get_session_connection_count(session_id)
    participants = manager.get_session_participants(session_id)

    return {
        "session_id": session_id,
        "connection_count": connection_count,
        "participant_count": len(participants),
        "participants": list(participants),
        "is_active": connection_count > 0,
    }
