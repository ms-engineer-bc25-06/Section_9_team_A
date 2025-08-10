import asyncio
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
import structlog
from enum import Enum

from app.models.user import User
from app.models.voice_session import VoiceSession
from app.core.websocket import manager
from app.core.exceptions import (
    BridgeLineException,
    ValidationException,
    NotFoundException,
    PermissionException,
)

logger = structlog.get_logger()


class ParticipantRole(str, Enum):
    """参加者の役割"""
    HOST = "host"           # ホスト（セッション作成者）
    MODERATOR = "moderator"  # モデレーター
    PARTICIPANT = "participant"  # 一般参加者
    OBSERVER = "observer"    # オブザーバー（音声なし）


class ParticipantStatus(str, Enum):
    """参加者のステータス"""
    CONNECTED = "connected"      # 接続中
    DISCONNECTED = "disconnected"  # 切断中
    MUTED = "muted"             # ミュート中
    SPEAKING = "speaking"        # 発言中
    AWAY = "away"               # 離席中


class ParticipantInfo:
    """参加者情報"""
    def __init__(
        self,
        user_id: int,
        user: User,
        role: ParticipantRole = ParticipantRole.PARTICIPANT,
        status: ParticipantStatus = ParticipantStatus.CONNECTED,
        joined_at: Optional[datetime] = None,
        connection_id: Optional[str] = None
    ):
        self.user_id = user_id
        self.user = user
        self.role = role
        self.status = status
        self.joined_at = joined_at or datetime.now()
        self.connection_id = connection_id
        self.last_activity = datetime.now()
        self.audio_level = 0.0
        self.is_speaking = False
        self.speak_time_total = 0.0
        self.speak_time_session = 0.0
        self.messages_sent = 0
        self.quality_metrics = {}
        # 追加属性
        self.is_muted = False
        self.connection_quality = "good"
        self.permissions = set()
        self.avatar_url = getattr(user, 'avatar_url', None)
        self.display_name = getattr(user, 'full_name', user.username)
        
        # 権限を設定
        self._set_permissions()
    
    def _set_permissions(self):
        """役割に基づいて権限を設定"""
        role_permissions = {
            ParticipantRole.HOST: {
                "manage_participants", "mute_participants", "change_roles",
                "control_recording", "end_session", "view_analytics"
            },
            ParticipantRole.MODERATOR: {
                "manage_participants", "mute_participants", "control_recording",
                "view_analytics"
            },
            ParticipantRole.PARTICIPANT: {
                "send_messages", "speak", "view_participants"
            },
            ParticipantRole.OBSERVER: {
                "view_participants", "send_messages"
            }
        }
        self.permissions = role_permissions.get(self.role, set())


class ParticipantManagementService:
    """参加者管理サービス"""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict[int, ParticipantInfo]] = {}
        self.session_metadata: Dict[str, Dict] = {}
        self.role_permissions = self._initialize_role_permissions()
        
        logger.info("参加者管理サービスを初期化しました")
    
    def _initialize_role_permissions(self) -> Dict[ParticipantRole, Set[str]]:
        """役割別権限を初期化"""
        return {
            ParticipantRole.HOST: {
                "manage_participants", "mute_participants", "change_roles",
                "control_recording", "end_session", "view_analytics"
            },
            ParticipantRole.MODERATOR: {
                "manage_participants", "mute_participants", "control_recording",
                "view_analytics"
            },
            ParticipantRole.PARTICIPANT: {
                "send_messages", "speak", "view_participants"
            },
            ParticipantRole.OBSERVER: {
                "view_participants", "send_messages"
            }
        }
    
    async def join_session(
        self,
        session_id: str,
        user: User,
        role: ParticipantRole = ParticipantRole.PARTICIPANT,
        connection_id: Optional[str] = None
    ) -> ParticipantInfo:
        """セッションに参加"""
        try:
            # セッションが存在しない場合は作成
            if session_id not in self.active_sessions:
                self.active_sessions[session_id] = {}
                self.session_metadata[session_id] = {
                    "created_at": datetime.now(),
                    "max_participants": 50,
                    "recording_enabled": False,
                    "session_type": "voice_chat"
                }
            
            # 既存の参加者かチェック
            if user.id in self.active_sessions[session_id]:
                participant = self.active_sessions[session_id][user.id]
                participant.connection_id = connection_id
                participant.status = ParticipantStatus.CONNECTED
                participant.last_activity = datetime.now()
                
                logger.info(
                    "参加者が再接続",
                    session_id=session_id,
                    user_id=user.id,
                    role=participant.role.value
                )
                return participant
            
            # 新しい参加者として追加
            participant = ParticipantInfo(
                user_id=user.id,
                user=user,
                role=role,
                status=ParticipantStatus.CONNECTED,
                joined_at=datetime.now(),
                connection_id=connection_id
            )
            
            self.active_sessions[session_id][user.id] = participant
            
            # 参加者数制限チェック
            if len(self.active_sessions[session_id]) > self.session_metadata[session_id]["max_participants"]:
                raise ValidationException("セッションの参加者数上限に達しています")
            
            # 参加通知を全参加者に送信
            await self._broadcast_participant_update(session_id, "participant_joined", participant)
            
            logger.info(
                "新しい参加者がセッションに参加",
                session_id=session_id,
                user_id=user.id,
                role=role.value,
                total_participants=len(self.active_sessions[session_id])
            )
            
            return participant
            
        except Exception as e:
            logger.error(f"セッション参加に失敗: {e}", session_id=session_id, user_id=user.id)
            raise
    
    async def leave_session(self, session_id: str, user_id: int) -> bool:
        """セッションから退出"""
        try:
            if session_id not in self.active_sessions:
                return False
            
            if user_id not in self.active_sessions[session_id]:
                return False
            
            participant = self.active_sessions[session_id][user_id]
            participant.status = ParticipantStatus.DISCONNECTED
            participant.last_activity = datetime.now()
            
            # 退出通知を全参加者に送信
            await self._broadcast_participant_update(session_id, "participant_left", participant)
            
            # 参加者リストから削除
            del self.active_sessions[session_id][user_id]
            
            # セッションが空になった場合の処理
            if not self.active_sessions[session_id]:
                await self._cleanup_empty_session(session_id)
            
            logger.info(
                "参加者がセッションから退出",
                session_id=session_id,
                user_id=user_id,
                remaining_participants=len(self.active_sessions.get(session_id, {}))
            )
            
            return True
            
        except Exception as e:
            logger.error(f"セッション退出に失敗: {e}", session_id=session_id, user_id=user_id)
            return False
    
    async def update_participant_status(
        self,
        session_id: str,
        user_id: int,
        status: ParticipantStatus,
        updated_by: int
    ) -> ParticipantInfo:
        """参加者のステータスを更新"""
        try:
            if not await self._check_permission(session_id, updated_by, "manage_participants"):
                raise PermissionException("参加者管理の権限がありません")
            
            if session_id not in self.active_sessions or user_id not in self.active_sessions[session_id]:
                raise NotFoundException("参加者が見つかりません")
            
            participant = self.active_sessions[session_id][user_id]
            old_status = participant.status
            participant.status = status
            participant.last_activity = datetime.now()
            
            # ステータス変更通知を全参加者に送信
            await self._broadcast_participant_update(
                session_id, "participant_status_changed", participant, {"old_status": old_status.value}
            )
            
            logger.info(
                "参加者ステータスを更新",
                session_id=session_id,
                user_id=user_id,
                old_status=old_status.value,
                new_status=status.value,
                updated_by=updated_by
            )
            
            return participant
            
        except Exception as e:
            logger.error(f"参加者ステータス更新に失敗: {e}", session_id=session_id, user_id=user_id)
            raise
    
    async def change_participant_role(
        self,
        session_id: str,
        user_id: int,
        new_role: ParticipantRole,
        changed_by: int
    ) -> ParticipantInfo:
        """参加者の役割を変更"""
        try:
            if not await self._check_permission(session_id, changed_by, "change_roles"):
                raise PermissionException("役割変更の権限がありません")
            
            if session_id not in self.active_sessions or user_id not in self.active_sessions[session_id]:
                raise NotFoundException("参加者が見つかりません")
            
            participant = self.active_sessions[session_id][user_id]
            old_role = participant.role
            participant.role = new_role
            participant.last_activity = datetime.now()
            
            # 役割変更通知を全参加者に送信
            await self._broadcast_participant_update(
                session_id, "participant_role_changed", participant, {"old_role": old_role.value}
            )
            
            logger.info(
                "参加者役割を変更",
                session_id=session_id,
                user_id=user_id,
                old_role=old_role.value,
                new_role=new_role.value,
                changed_by=changed_by
            )
            
            return participant
            
        except Exception as e:
            logger.error(f"参加者役割変更に失敗: {e}", session_id=session_id, user_id=user_id)
            raise
    
    async def mute_participant(
        self,
        session_id: str,
        user_id: int,
        muted: bool,
        muted_by: int
    ) -> ParticipantInfo:
        """参加者をミュート/ミュート解除"""
        try:
            if not await self._check_permission(session_id, muted_by, "mute_participants"):
                raise PermissionException("ミュート制御の権限がありません")
            
            if session_id not in self.active_sessions or user_id not in self.active_sessions[session_id]:
                raise NotFoundException("参加者が見つかりません")
            
            participant = self.active_sessions[session_id][user_id]
            participant.status = ParticipantStatus.MUTED if muted else ParticipantStatus.CONNECTED
            participant.is_muted = muted  # is_muted属性も更新
            participant.last_activity = datetime.now()
            
            # ミュート状態変更通知を全参加者に送信
            await self._broadcast_participant_update(
                session_id, "participant_muted", participant, {"muted": muted}
            )
            
            logger.info(
                "参加者ミュート状態を変更",
                session_id=session_id,
                user_id=user_id,
                muted=muted,
                muted_by=muted_by
            )
            
            return participant
            
        except Exception as e:
            logger.error(f"参加者ミュート制御に失敗: {e}", session_id=session_id, user_id=user_id)
            raise
    
    async def get_session_participants(
        self,
        session_id: str,
        include_disconnected: bool = False
    ) -> List[ParticipantInfo]:
        """セッションの参加者一覧を取得"""
        try:
            if session_id not in self.active_sessions:
                return []
            
            participants = list(self.active_sessions[session_id].values())
            
            if not include_disconnected:
                participants = [p for p in participants if p.status != ParticipantStatus.DISCONNECTED]
            
            # 参加時刻順にソート
            participants.sort(key=lambda x: x.joined_at)
            
            return participants
            
        except Exception as e:
            logger.error(f"参加者一覧取得に失敗: {e}", session_id=session_id)
            return []
    
    async def get_participant_info(
        self,
        session_id: str,
        user_id: int
    ) -> Optional[ParticipantInfo]:
        """特定の参加者情報を取得"""
        try:
            if session_id not in self.active_sessions:
                return None
            
            return self.active_sessions[session_id].get(user_id)
            
        except Exception as e:
            logger.error(f"参加者情報取得に失敗: {e}", session_id=session_id, user_id=user_id)
            return None
    
    async def update_audio_level(
        self,
        session_id: str,
        user_id: int,
        audio_level: float
    ) -> None:
        """参加者の音声レベルを更新"""
        try:
            if session_id not in self.active_sessions or user_id not in self.active_sessions[session_id]:
                return
            
            participant = self.active_sessions[session_id][user_id]
            participant.audio_level = audio_level
            
            # 発言状態の判定
            is_speaking = audio_level > 0.1  # 閾値
            if is_speaking != participant.is_speaking:
                participant.is_speaking = is_speaking
                if is_speaking:
                    participant.status = ParticipantStatus.SPEAKING
                    participant.speak_time_session += 0.1  # 100ms単位で累積
                else:
                    participant.status = ParticipantStatus.CONNECTED
            
            # 音声レベル更新通知（頻度制限あり）
            if audio_level > 0.05:  # 一定レベル以上の場合のみ通知
                await self._broadcast_audio_level_update(session_id, user_id, audio_level)
                
        except Exception as e:
            logger.error(f"音声レベル更新に失敗: {e}", session_id=session_id, user_id=user_id)
    
    async def _check_permission(
        self,
        session_id: str,
        user_id: int,
        permission: str
    ) -> bool:
        """権限チェック"""
        try:
            if session_id not in self.active_sessions or user_id not in self.active_sessions[session_id]:
                return False
            
            participant = self.active_sessions[session_id][user_id]
            return permission in self.role_permissions.get(participant.role, set())
            
        except Exception:
            return False
    
    async def _broadcast_participant_update(
        self,
        session_id: str,
        event_type: str,
        participant: ParticipantInfo,
        additional_data: Optional[Dict] = None
    ) -> None:
        """参加者更新通知を全参加者にブロードキャスト"""
        try:
            message = {
                "type": event_type,
                "session_id": session_id,
                "participant": {
                    "user_id": participant.user_id,
                    "display_name": participant.user.display_name,
                    "role": participant.role.value,
                    "status": participant.status.value,
                    "joined_at": participant.joined_at.isoformat(),
                    "last_activity": participant.last_activity.isoformat()
                }
            }
            
            if additional_data:
                message.update(additional_data)
            
            # 全参加者に通知
            for p in self.active_sessions[session_id].values():
                if p.connection_id and p.connection_id in manager.connection_info:
                    await manager.send_personal_message(message, p.connection_id)
                    
        except Exception as e:
            logger.error(f"参加者更新通知の送信に失敗: {e}", session_id=session_id)
    
    async def _broadcast_audio_level_update(
        self,
        session_id: str,
        user_id: int,
        audio_level: float
    ) -> None:
        """音声レベル更新通知をブロードキャスト"""
        try:
            message = {
                "type": "audio_level_update",
                "session_id": session_id,
                "user_id": user_id,
                "audio_level": audio_level,
                "timestamp": datetime.now().isoformat()
            }
            
            # 全参加者に通知
            for p in self.active_sessions[session_id].values():
                if p.connection_id and p.connection_id in manager.connection_info:
                    await manager.send_personal_message(message, p.connection_id)
                    
        except Exception as e:
            logger.error(f"音声レベル更新通知の送信に失敗: {e}", session_id=session_id)
    
    async def _cleanup_empty_session(self, session_id: str) -> None:
        """空のセッションをクリーンアップ"""
        try:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            if session_id in self.session_metadata:
                del self.session_metadata[session_id]
            
            logger.info(f"空のセッションをクリーンアップ: {session_id}")
            
        except Exception as e:
            logger.error(f"セッションクリーンアップに失敗: {e}", session_id=session_id)
    
    async def get_session_stats(self, session_id: str) -> Dict:
        """セッション統計情報を取得"""
        try:
            if session_id not in self.active_sessions:
                return {}
            
            participants = self.active_sessions[session_id]
            connected_count = len([p for p in participants.values() if p.status != ParticipantStatus.DISCONNECTED])
            speaking_count = len([p for p in participants.values() if p.status == ParticipantStatus.SPEAKING])
            muted_count = len([p for p in participants.values() if p.status == ParticipantStatus.MUTED])
            
            total_speak_time = sum(p.speak_time_session for p in participants.values())
            
            return {
                "total_participants": len(participants),
                "connected_participants": connected_count,
                "active_participants": connected_count,  # active_participantsを追加
                "speaking_participants": speaking_count,
                "muted_participants": muted_count,
                "total_speak_time": total_speak_time,
                "session_duration": (datetime.now() - self.session_metadata[session_id]["created_at"]).total_seconds()
            }
            
        except Exception as e:
            logger.error(f"セッション統計取得に失敗: {e}", session_id=session_id)
            return {}


# グローバルインスタンス
participant_management_service = ParticipantManagementService()
