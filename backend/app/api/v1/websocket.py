import json
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, status
import structlog
from datetime import datetime

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


@router.post("/voice-sessions/{session_id}/recording/start")
async def start_session_recording(session_id: str):
    """セッション録音を開始"""
    try:
        from app.services.audio_processing_service import audio_processor

        await audio_processor.start_recording(session_id)

        return {
            "session_id": session_id,
            "status": "recording_started",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to start recording for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to start recording")


@router.post("/voice-sessions/{session_id}/recording/stop")
async def stop_session_recording(session_id: str):
    """セッション録音を停止"""
    try:
        from app.services.audio_processing_service import audio_processor

        await audio_processor.stop_recording(session_id)

        return {
            "session_id": session_id,
            "status": "recording_stopped",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to stop recording for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop recording")


@router.get("/voice-sessions/{session_id}/audio-levels")
async def get_session_audio_levels(session_id: str, user_id: Optional[int] = None):
    """セッションの音声レベルを取得"""
    try:
        from app.services.audio_processing_service import audio_processor

        if user_id:
            # 特定ユーザーの音声レベル履歴
            levels = await audio_processor.get_session_audio_levels(session_id, user_id)
            return {
                "session_id": session_id,
                "user_id": user_id,
                "levels": [
                    {
                        "level": level.level,
                        "is_speaking": level.is_speaking,
                        "rms": level.rms,
                        "peak": level.peak,
                        "timestamp": level.timestamp.isoformat(),
                    }
                    for level in levels
                ],
            }
        else:
            # 全参加者の現在の音声レベル
            participant_levels = (
                await audio_processor.get_session_participants_audio_levels(session_id)
            )
            return {
                "session_id": session_id,
                "participant_levels": {
                    str(user_id): {
                        "level": level.level,
                        "is_speaking": level.is_speaking,
                        "rms": level.rms,
                        "peak": level.peak,
                        "timestamp": level.timestamp.isoformat(),
                    }
                    for user_id, level in participant_levels.items()
                },
            }
    except Exception as e:
        logger.error(f"Failed to get audio levels for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get audio levels")


@router.delete("/voice-sessions/{session_id}/audio-buffer")
async def clear_session_audio_buffer(session_id: str):
    """セッションの音声バッファをクリア"""
    try:
        from app.services.audio_processing_service import audio_processor

        await audio_processor.clear_session_buffer(session_id)

        return {
            "session_id": session_id,
            "status": "buffer_cleared",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to clear audio buffer for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear audio buffer")
