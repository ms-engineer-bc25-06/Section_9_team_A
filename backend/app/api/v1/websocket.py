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
    except HTTPException as e:
        logger.warning(f"HTTP error: {e}")
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION, reason=str(e.detail)
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
    except HTTPException as e:
        logger.warning(f"HTTP error: {e}")
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION, reason=str(e.detail)
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


# 接続管理API
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


# 参加者管理API
@router.get("/voice-sessions/{session_id}/participants")
async def get_session_participants_detailed(session_id: str):
    """セッションの参加者詳細情報を取得"""
    try:
        from app.services.participant_management_service import participant_manager

        participants = await participant_manager.get_session_participants(session_id)

        participant_list = [
            {
                "user_id": p.user_id,
                "display_name": p.user.display_name,
                "avatar_url": p.user.avatar_url,
                "role": p.role.value,
                "status": p.status.value,
                "is_muted": p.is_muted,
                "is_speaking": p.is_speaking,
                "audio_level": p.audio_level,
                "connection_quality": p.connection_quality,
                "joined_at": p.joined_at.isoformat(),
                "last_activity": p.last_activity.isoformat(),
                "permissions": list(p.permissions),
            }
            for p in participants
        ]

        return {
            "session_id": session_id,
            "participants": participant_list,
            "count": len(participant_list),
        }
    except Exception as e:
        logger.error(f"Failed to get participants for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get participants")


@router.post("/voice-sessions/{session_id}/participants/{user_id}/mute")
async def mute_participant(
    session_id: str, user_id: int, muted_by: int, mute: bool = True
):
    """参加者をミュート/アンミュート"""
    try:
        from app.services.participant_management_service import participant_manager

        await participant_manager.mute_participant(session_id, user_id, muted_by, mute)

        return {
            "session_id": session_id,
            "user_id": user_id,
            "muted": mute,
            "muted_by": muted_by,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(
            f"Failed to mute participant {user_id} in session {session_id}: {e}"
        )
        raise HTTPException(status_code=500, detail="Failed to mute participant")


@router.post("/voice-sessions/{session_id}/participants/{user_id}/role")
async def change_participant_role(
    session_id: str, user_id: int, new_role: str, changed_by: int
):
    """参加者のロールを変更"""
    try:
        from app.services.participant_management_service import (
            participant_manager,
            ParticipantRole,
        )

        role = ParticipantRole(new_role)
        await participant_manager.change_participant_role(
            session_id, user_id, role, changed_by
        )

        return {
            "session_id": session_id,
            "user_id": user_id,
            "new_role": new_role,
            "changed_by": changed_by,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(
            f"Failed to change role for participant {user_id} in session {session_id}: {e}"
        )
        raise HTTPException(status_code=500, detail="Failed to change participant role")


@router.get("/voice-sessions/{session_id}/participants/{user_id}/stats")
async def get_participant_stats(session_id: str, user_id: int):
    """参加者の統計情報を取得"""
    try:
        from app.services.participant_management_service import participant_manager

        stats = await participant_manager.get_participant_stats(session_id, user_id)
        activity = await participant_manager.get_participant_activity(
            session_id, user_id, 20
        )

        return {
            "session_id": session_id,
            "user_id": user_id,
            "stats": stats,
            "recent_activity": activity,
        }
    except Exception as e:
        logger.error(
            f"Failed to get stats for participant {user_id} in session {session_id}: {e}"
        )
        raise HTTPException(status_code=500, detail="Failed to get participant stats")


# メッセージングAPI
@router.get("/voice-sessions/{session_id}/messages")
async def get_session_messages(session_id: str, limit: int = 50, offset: int = 0):
    """セッションのメッセージ履歴を取得"""
    try:
        from app.services.messaging_service import messaging_service

        messages = await messaging_service.get_session_messages(
            session_id, limit, offset
        )

        message_list = [
            {
                "id": msg.id,
                "session_id": msg.session_id,
                "user_id": msg.user_id,
                "message_type": msg.message_type.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "priority": msg.priority.value,
                "metadata": msg.metadata,
                "edited_at": msg.edited_at.isoformat() if msg.edited_at else None,
                "deleted_at": msg.deleted_at.isoformat() if msg.deleted_at else None,
            }
            for msg in messages
        ]

        return {
            "session_id": session_id,
            "messages": message_list,
            "count": len(message_list),
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        logger.error(f"Failed to get messages for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get messages")


@router.get("/voice-sessions/{session_id}/messages/search")
async def search_session_messages(session_id: str, query: str, limit: int = 20):
    """セッションのメッセージを検索"""
    try:
        from app.services.messaging_service import messaging_service

        messages = await messaging_service.search_messages(session_id, query, limit)

        message_list = [
            {
                "id": msg.id,
                "session_id": msg.session_id,
                "user_id": msg.user_id,
                "message_type": msg.message_type.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "priority": msg.priority.value,
                "metadata": msg.metadata,
            }
            for msg in messages
        ]

        return {
            "session_id": session_id,
            "query": query,
            "messages": message_list,
            "count": len(message_list),
            "limit": limit,
        }
    except Exception as e:
        logger.error(f"Failed to search messages for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to search messages")


# セッション制御API
@router.post("/voice-sessions/{session_id}/control/start")
async def start_session_control(session_id: str, user_id: int):
    """セッション制御を開始"""
    try:
        from app.services.participant_management_service import participant_manager

        # 権限チェック
        can_manage = await participant_manager.check_permission(
            session_id, user_id, "manage_session"
        )
        if not can_manage:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        # システムメッセージを送信
        from app.services.messaging_service import messaging_service

        await messaging_service.send_system_message(
            session_id, "Session control started by host", priority="high"
        )

        return {
            "session_id": session_id,
            "status": "control_started",
            "started_by": user_id,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to start session control for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to start session control")


@router.post("/voice-sessions/{session_id}/control/stop")
async def stop_session_control(session_id: str, user_id: int):
    """セッション制御を停止"""
    try:
        from app.services.participant_management_service import participant_manager

        # 権限チェック
        can_manage = await participant_manager.check_permission(
            session_id, user_id, "manage_session"
        )
        if not can_manage:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        # システムメッセージを送信
        from app.services.messaging_service import messaging_service

        await messaging_service.send_system_message(
            session_id, "Session control stopped by host", priority="high"
        )

        return {
            "session_id": session_id,
            "status": "control_stopped",
            "stopped_by": user_id,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to stop session control for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop session control")


@router.get("/voice-sessions/{session_id}/status/detailed")
async def get_session_detailed_status(session_id: str):
    """セッションの詳細状態を取得"""
    try:
        from app.services.participant_management_service import participant_manager
        from app.services.audio_processing_service import audio_processor
        from app.services.messaging_service import messaging_service

        # 参加者情報
        participants = await participant_manager.get_session_participants(session_id)

        # 音声レベル情報
        audio_levels = await audio_processor.get_session_participants_audio_levels(
            session_id
        )

        # メッセージ統計
        messages = await messaging_service.get_session_messages(session_id, 1, 0)
        last_message = messages[0] if messages else None

        # 接続情報
        connection_count = manager.get_session_connection_count(session_id)

        return {
            "session_id": session_id,
            "connection_count": connection_count,
            "participant_count": len(participants),
            "is_active": connection_count > 0,
            "participants": [
                {
                    "user_id": p.user_id,
                    "display_name": p.user.display_name,
                    "role": p.role.value,
                    "status": p.status.value,
                    "is_muted": p.is_muted,
                    "is_speaking": p.is_speaking,
                    "audio_level": audio_levels.get(p.user_id, {}).get("level", 0.0)
                    if p.user_id in audio_levels
                    else 0.0,
                }
                for p in participants
            ],
            "last_message": {
                "id": last_message.id,
                "content": last_message.content,
                "timestamp": last_message.timestamp.isoformat(),
            }
            if last_message
            else None,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to get detailed status for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get session status")
