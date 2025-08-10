"""
WebSocketメッセージハンドラーの初期化とルーター登録
"""

import json
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import structlog

from app.core.websocket import manager
from app.services.participant_management_service import (
    participant_management_service,
    ParticipantRole,
    ParticipantStatus
)
from app.services.voice_session_service import VoiceSessionService
from app.core.database import get_db
from app.core.exceptions import (
    BridgeLineException,
    ValidationException,
    NotFoundException,
    PermissionException,
)

logger = structlog.get_logger()


class WebSocketMessageHandler:
    """WebSocketメッセージハンドラー"""
    
    @staticmethod
    async def handle_message(
        websocket,
        message: Dict[str, Any],
        connection_id: str,
        user: Any
    ) -> None:
        """WebSocketメッセージを処理"""
        try:
            message_type = message.get("type")
            
            if message_type == "join_session":
                await WebSocketMessageHandler.handle_join_session(
                    message.get("session_id"),
                    connection_id,
                    user,
                    message.get("role", "participant")
                )
                
            elif message_type == "leave_session":
                await WebSocketMessageHandler.handle_leave_session(
                    message.get("session_id"),
                    connection_id,
                    user
                )
                
            elif message_type == "audio_data":
                await WebSocketMessageHandler.handle_audio_data(
                    message.get("session_id"),
                    connection_id,
                    user,
                    message.get("audio_data"),
                    message.get("audio_level", 0.0)
                )
                
            elif message_type == "chat_message":
                await WebSocketMessageHandler.handle_chat_message(
                    message.get("session_id"),
                    connection_id,
                    user,
                    message.get("message"),
                    message.get("message_type", "text")
                )
                
            elif message_type == "participant_action":
                await WebSocketMessageHandler.handle_participant_action(
                    message.get("session_id"),
                    connection_id,
                    user,
                    message.get("action"),
                    message.get("target_user_id"),
                    message.get("action_data", {})
                )
                
            elif message_type == "session_control":
                await WebSocketMessageHandler.handle_session_control(
                    message.get("session_id"),
                    connection_id,
                    user,
                    message.get("control_type"),
                    message.get("control_data", {})
                )
                
            elif message_type == "ping":
                await WebSocketMessageHandler.handle_ping(connection_id)
                
            else:
                logger.warning(f"Unknown message type: {message_type}")
                await manager.send_personal_message(
                    {"type": "error", "message": f"Unknown message type: {message_type}"},
                    connection_id
                )
                
        except Exception as e:
            logger.error(f"Message handling error: {e}", connection_id=connection_id)
            await manager.send_personal_message(
                {"type": "error", "message": "Internal server error"},
                connection_id
            )
    
    @staticmethod
    async def handle_join_session(
        session_id: str,
        connection_id: str,
        user: Any,
        role: str = "participant"
    ) -> None:
        """セッション参加処理"""
        try:
            # 役割の検証
            try:
                participant_role = ParticipantRole(role)
            except ValueError:
                participant_role = ParticipantRole.PARTICIPANT
            
            # 参加者管理サービスでセッション参加
            participant = await participant_management_service.join_session(
                session_id=session_id,
                user=user,
                role=participant_role,
                connection_id=connection_id
            )
            
            # 参加成功通知
            await manager.send_personal_message(
                {
                    "type": "join_success",
                    "session_id": session_id,
                    "participant": {
                        "user_id": participant.user_id,
                        "display_name": participant.user.display_name,
                        "role": participant.role.value,
                        "status": participant.status.value
                    },
                    "session_info": {
                        "total_participants": len(await participant_management_service.get_session_participants(session_id)),
                        "session_stats": await participant_management_service.get_session_stats(session_id)
                    }
                },
                connection_id
            )
            
            # 既存参加者一覧を送信
            participants = await participant_management_service.get_session_participants(session_id)
            await manager.send_personal_message(
                {
                    "type": "participants_list",
                    "session_id": session_id,
                    "participants": [
                        {
                            "user_id": p.user_id,
                            "display_name": p.user.display_name,
                            "role": p.role.value,
                            "status": p.status.value,
                            "joined_at": p.joined_at.isoformat(),
                            "is_speaking": p.is_speaking,
                            "audio_level": p.audio_level
                        }
                        for p in participants
                    ]
                },
                connection_id
            )
            
            logger.info(
                "セッション参加処理完了",
                session_id=session_id,
                user_id=user.id,
                role=participant_role.value
            )
            
        except Exception as e:
            logger.error(f"セッション参加処理に失敗: {e}", session_id=session_id, user_id=user.id)
            await manager.send_personal_message(
                {"type": "join_error", "message": str(e)},
                connection_id
            )
    
    @staticmethod
    async def handle_leave_session(
        session_id: str,
        connection_id: str,
        user: Any
    ) -> None:
        """セッション退出処理"""
        try:
            # 参加者管理サービスでセッション退出
            success = await participant_management_service.leave_session(session_id, user.id)
            
            if success:
                # 退出成功通知
                await manager.send_personal_message(
                    {
                        "type": "leave_success",
                        "session_id": session_id,
                        "message": "セッションから正常に退出しました"
                    },
                    connection_id
                )
                
                logger.info(
                    "セッション退出処理完了",
                    session_id=session_id,
                    user_id=user.id
                )
            else:
                await manager.send_personal_message(
                    {"type": "leave_error", "message": "セッション退出に失敗しました"},
                    connection_id
                )
                
        except Exception as e:
            logger.error(f"セッション退出処理に失敗: {e}", session_id=session_id, user_id=user.id)
            await manager.send_personal_message(
                {"type": "leave_error", "message": str(e)},
                connection_id
            )
    
    @staticmethod
    async def handle_audio_data(
        session_id: str,
        connection_id: str,
        user: Any,
        audio_data: str,
        audio_level: float
    ) -> None:
        """音声データ処理"""
        try:
            # 音声レベルを更新
            await participant_management_service.update_audio_level(
                session_id, user.id, audio_level
            )
            
            # 音声データを他の参加者に転送
            participants = await participant_management_service.get_session_participants(session_id)
            
            for participant in participants:
                if (participant.user_id != user.id and 
                    participant.connection_id and 
                    participant.status != ParticipantStatus.MUTED):
                    
                    await manager.send_personal_message(
                        {
                            "type": "audio_data",
                            "session_id": session_id,
                            "user_id": user.id,
                            "display_name": user.display_name,
                            "audio_data": audio_data,
                            "audio_level": audio_level,
                            "timestamp": datetime.now().isoformat()
                        },
                        participant.connection_id
                    )
                    
        except Exception as e:
            logger.error(f"音声データ処理に失敗: {e}", session_id=session_id, user_id=user.id)
    
    @staticmethod
    async def handle_chat_message(
        session_id: str,
        connection_id: str,
        user: Any,
        message: str,
        message_type: str = "text"
    ) -> None:
        """チャットメッセージ処理"""
        try:
            # 参加者情報を取得
            participant = await participant_management_service.get_participant_info(session_id, user.id)
            if not participant:
                await manager.send_personal_message(
                    {"type": "error", "message": "セッションに参加していません"},
                    connection_id
                )
                return
            
            # メッセージカウントを更新
            participant.messages_sent += 1
            
            # チャットメッセージを全参加者に転送
            participants = await participant_management_service.get_session_participants(session_id)
            
            chat_message = {
                "type": "chat_message",
                "session_id": session_id,
                "user_id": user.id,
                "display_name": user.display_name,
                "role": participant.role.value,
                "message": message,
                "message_type": message_type,
                "timestamp": datetime.now().isoformat()
            }
            
            for p in participants:
                if p.connection_id:
                    await manager.send_personal_message(chat_message, p.connection_id)
                    
            logger.info(
                "チャットメッセージを送信",
                session_id=session_id,
                user_id=user.id,
                message_type=message_type
            )
            
        except Exception as e:
            logger.error(f"チャットメッセージ処理に失敗: {e}", session_id=session_id, user_id=user.id)
            await manager.send_personal_message(
                {"type": "error", "message": "メッセージ送信に失敗しました"},
                connection_id
            )
    
    @staticmethod
    async def handle_participant_action(
        session_id: str,
        connection_id: str,
        user: Any,
        action: str,
        target_user_id: int,
        action_data: Dict[str, Any]
    ) -> None:
        """参加者アクション処理"""
        try:
            if action == "mute":
                muted = action_data.get("muted", True)
                participant = await participant_management_service.mute_participant(
                    session_id, target_user_id, muted, user.id
                )
                
                await manager.send_personal_message(
                    {
                        "type": "action_success",
                        "action": "mute",
                        "target_user_id": target_user_id,
                        "muted": muted,
                        "message": f"参加者のミュート状態を{'有効' if muted else '無効'}にしました"
                    },
                    connection_id
                )
                
            elif action == "change_role":
                new_role = action_data.get("new_role", "participant")
                try:
                    participant_role = ParticipantRole(new_role)
                    participant = await participant_management_service.change_participant_role(
                        session_id, target_user_id, participant_role, user.id
                    )
                    
                    await manager.send_personal_message(
                        {
                            "type": "action_success",
                            "action": "change_role",
                            "target_user_id": target_user_id,
                            "new_role": new_role,
                            "message": f"参加者の役割を{new_role}に変更しました"
                        },
                        connection_id
                    )
                    
                except ValueError:
                    await manager.send_personal_message(
                        {"type": "action_error", "message": f"無効な役割: {new_role}"},
                        connection_id
                    )
                    
            elif action == "remove":
                # 参加者削除処理
                success = await participant_management_service.leave_session(session_id, target_user_id)
                
                if success:
                    await manager.send_personal_message(
                        {
                            "type": "action_success",
                            "action": "remove",
                            "target_user_id": target_user_id,
                            "message": "参加者をセッションから削除しました"
                        },
                        connection_id
                    )
                else:
                    await manager.send_personal_message(
                        {"type": "action_error", "message": "参加者の削除に失敗しました"},
                        connection_id
                    )
                    
            else:
                await manager.send_personal_message(
                    {"type": "action_error", "message": f"不明なアクション: {action}"},
                    connection_id
                )
                
        except PermissionException as e:
            await manager.send_personal_message(
                {"type": "action_error", "message": str(e)},
                connection_id
            )
        except Exception as e:
            logger.error(f"参加者アクション処理に失敗: {e}", session_id=session_id, user_id=user.id)
            await manager.send_personal_message(
                {"type": "action_error", "message": "アクション処理に失敗しました"},
                connection_id
            )
    
    @staticmethod
    async def handle_session_control(
        session_id: str,
        connection_id: str,
        user: Any,
        control_type: str,
        control_data: Dict[str, Any]
    ) -> None:
        """セッション制御処理"""
        try:
            if control_type == "start_recording":
                # 録音開始処理
                await manager.send_personal_message(
                    {
                        "type": "control_success",
                        "control_type": "start_recording",
                        "message": "録音を開始しました"
                    },
                    connection_id
                )
                
            elif control_type == "stop_recording":
                # 録音停止処理
                await manager.send_personal_message(
                    {
                        "type": "control_success",
                        "control_type": "stop_recording",
                        "message": "録音を停止しました"
                    },
                    connection_id
                )
                
            elif control_type == "end_session":
                # セッション終了処理
                await manager.send_personal_message(
                    {
                        "type": "control_success",
                        "control_type": "end_session",
                        "message": "セッションを終了しました"
                    },
                    connection_id
                )
                
                # 全参加者にセッション終了通知
                participants = await participant_management_service.get_session_participants(session_id)
                for p in participants:
                    if p.connection_id:
                        await manager.send_personal_message(
                            {
                                "type": "session_ended",
                                "session_id": session_id,
                                "ended_by": user.id,
                                "message": "セッションが終了されました"
                            },
                            p.connection_id
                        )
                        
            else:
                await manager.send_personal_message(
                    {"type": "control_error", "message": f"不明な制御タイプ: {control_type}"},
                    connection_id
                )
                
        except Exception as e:
            logger.error(f"セッション制御処理に失敗: {e}", session_id=session_id, user_id=user.id)
            await manager.send_personal_message(
                {"type": "control_error", "message": "制御処理に失敗しました"},
                connection_id
            )
    
    @staticmethod
    async def handle_ping(connection_id: str) -> None:
        """ping応答"""
        try:
            await manager.send_personal_message(
                {
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                },
                connection_id
            )
        except Exception as e:
            logger.error(f"ping応答に失敗: {e}", connection_id=connection_id)
    
    @staticmethod
    async def handle_join_session(
        session_id: str,
        connection_id: str,
        user: Any
    ) -> None:
        """セッション参加通知（既存メソッドとの互換性）"""
        # 既に実装済みのため、重複を避ける
        pass


def initialize_message_handlers():
    """WebSocketメッセージハンドラーを初期化"""
    logger.info("WebSocketメッセージハンドラーを初期化しました")
    # 現在は何もしない（必要に応じて初期化処理を追加）
    return True
