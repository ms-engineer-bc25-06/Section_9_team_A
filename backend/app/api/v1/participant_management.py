from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.services.participant_management_service import (
    participant_management_service,
    ParticipantRole,
    ParticipantStatus
)
from app.schemas.participant_management import (
    ParticipantInfoResponse,
    ParticipantListResponse,
    ParticipantUpdateRequest,
    ParticipantRoleUpdateRequest,
    ParticipantMuteRequest,
    ParticipantStatsResponse,
    SessionStatsResponse,
    ParticipantActionRequest,
    ParticipantActionResponse
)
from app.core.exceptions import (
    BridgeLineException,
    ValidationException,
    NotFoundException,
    PermissionException,
)
from app.api.deps import handle_bridge_line_exceptions

router = APIRouter(prefix="/participant-management", tags=["参加者管理"])
logger = structlog.get_logger()


@router.get("/sessions/{session_id}/participants", response_model=ParticipantListResponse)
async def get_session_participants(
    session_id: str,
    include_disconnected: bool = Query(False, description="切断中の参加者も含める"),
    current_user: User = Depends(get_current_active_user),
):
    """セッションの参加者一覧を取得"""
    try:
        participants = await participant_management_service.get_session_participants(
            session_id, include_disconnected
        )
        
        participant_responses = []
        for participant in participants:
            participant_responses.append(ParticipantInfoResponse(
                user_id=participant.user_id,
                display_name=participant.user.display_name,
                email=participant.user.email,
                role=participant.role.value,
                status=participant.status.value,
                joined_at=participant.joined_at,
                last_activity=participant.last_activity,
                is_speaking=participant.is_speaking,
                audio_level=participant.audio_level,
                speak_time_session=participant.speak_time_session,
                messages_sent=participant.messages_sent
            ))
        
        return ParticipantListResponse(
            session_id=session_id,
            participants=participant_responses,
            total_count=len(participant_responses),
            connected_count=len([p for p in participants if p.status != ParticipantStatus.DISCONNECTED]),
            speaking_count=len([p for p in participants if p.status == ParticipantStatus.SPEAKING]),
            muted_count=len([p for p in participants if p.status == ParticipantStatus.MUTED])
        )
        
    except Exception as e:
        logger.error(f"参加者一覧取得に失敗: {e}", session_id=session_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="参加者一覧の取得に失敗しました"
        )


@router.get("/sessions/{session_id}/participants/{user_id}", response_model=ParticipantInfoResponse)
async def get_participant_info(
    session_id: str,
    user_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """特定の参加者情報を取得"""
    try:
        participant = await participant_management_service.get_participant_info(session_id, user_id)
        
        if not participant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="参加者が見つかりません"
            )
        
        return ParticipantInfoResponse(
            user_id=participant.user_id,
            display_name=participant.user.display_name,
            email=participant.user.email,
            role=participant.role.value,
            status=participant.status.value,
            joined_at=participant.joined_at,
            last_activity=participant.last_activity,
            is_speaking=participant.is_speaking,
            audio_level=participant.audio_level,
            speak_time_session=participant.speak_time_session,
            messages_sent=participant.messages_sent
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"参加者情報取得に失敗: {e}", session_id=session_id, user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="参加者情報の取得に失敗しました"
        )


@router.put("/sessions/{session_id}/participants/{user_id}/role", response_model=ParticipantInfoResponse)
async def update_participant_role(
    session_id: str,
    user_id: int,
    role_update: ParticipantRoleUpdateRequest,
    current_user: User = Depends(get_current_active_user),
):
    """参加者の役割を変更"""
    try:
        # 役割の検証
        try:
            new_role = ParticipantRole(role_update.new_role)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"無効な役割: {role_update.new_role}"
            )
        
        # 役割変更を実行
        participant = await participant_management_service.change_participant_role(
            session_id, user_id, new_role, current_user.id
        )
        
        return ParticipantInfoResponse(
            user_id=participant.user_id,
            display_name=participant.user.display_name,
            email=participant.user.email,
            role=participant.role.value,
            status=participant.status.value,
            joined_at=participant.joined_at,
            last_activity=participant.last_activity,
            is_speaking=participant.is_speaking,
            audio_level=participant.audio_level,
            speak_time_session=participant.speak_time_session,
            messages_sent=participant.messages_sent
        )
        
    except PermissionException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"参加者役割変更に失敗: {e}", session_id=session_id, user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="参加者役割の変更に失敗しました"
        )


@router.put("/sessions/{session_id}/participants/{user_id}/mute", response_model=ParticipantInfoResponse)
async def mute_participant(
    session_id: str,
    user_id: int,
    mute_request: ParticipantMuteRequest,
    current_user: User = Depends(get_current_active_user),
):
    """参加者をミュート/ミュート解除"""
    try:
        # ミュート制御を実行
        participant = await participant_management_service.mute_participant(
            session_id, user_id, mute_request.muted, current_user.id
        )
        
        return ParticipantInfoResponse(
            user_id=participant.user_id,
            display_name=participant.user.display_name,
            email=participant.user.email,
            role=participant.role.value,
            status=participant.status.value,
            joined_at=participant.joined_at,
            last_activity=participant.last_activity,
            is_speaking=participant.is_speaking,
            audio_level=participant.audio_level,
            speak_time_session=participant.speak_time_session,
            messages_sent=participant.messages_sent
        )
        
    except PermissionException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"参加者ミュート制御に失敗: {e}", session_id=session_id, user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="参加者ミュート制御に失敗しました"
        )


@router.put("/sessions/{session_id}/participants/{user_id}/status", response_model=ParticipantInfoResponse)
async def update_participant_status(
    session_id: str,
    user_id: int,
    status_update: ParticipantUpdateRequest,
    current_user: User = Depends(get_current_active_user),
):
    """参加者のステータスを更新"""
    try:
        # ステータスの検証
        try:
            new_status = ParticipantStatus(status_update.status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"無効なステータス: {status_update.status}"
            )
        
        # ステータス更新を実行
        participant = await participant_management_service.update_participant_status(
            session_id, user_id, new_status, current_user.id
        )
        
        return ParticipantInfoResponse(
            user_id=participant.user_id,
            display_name=participant.user.display_name,
            email=participant.user.email,
            role=participant.role.value,
            status=participant.status.value,
            joined_at=participant.joined_at,
            last_activity=participant.last_activity,
            is_speaking=participant.is_speaking,
            audio_level=participant.audio_level,
            speak_time_session=participant.speak_time_session,
            messages_sent=participant.messages_sent
        )
        
    except PermissionException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"参加者ステータス更新に失敗: {e}", session_id=session_id, user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="参加者ステータスの更新に失敗しました"
        )


@router.delete("/sessions/{session_id}/participants/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_participant(
    session_id: str,
    user_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """参加者をセッションから削除"""
    try:
        # 参加者削除を実行
        success = await participant_management_service.leave_session(session_id, user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="参加者が見つかりません"
            )
        
        logger.info(
            "参加者をセッションから削除",
            session_id=session_id,
            user_id=user_id,
            removed_by=current_user.id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"参加者削除に失敗: {e}", session_id=session_id, user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="参加者の削除に失敗しました"
        )


@router.get("/sessions/{session_id}/stats", response_model=SessionStatsResponse)
async def get_session_stats(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """セッション統計情報を取得"""
    try:
        stats = await participant_management_service.get_session_stats(session_id)
        
        return SessionStatsResponse(
            session_id=session_id,
            total_participants=stats.get("total_participants", 0),
            connected_participants=stats.get("connected_participants", 0),
            speaking_participants=stats.get("speaking_participants", 0),
            muted_participants=stats.get("muted_participants", 0),
            total_speak_time=stats.get("total_speak_time", 0.0),
            session_duration=stats.get("session_duration", 0.0)
        )
        
    except Exception as e:
        logger.error(f"セッション統計取得に失敗: {e}", session_id=session_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="セッション統計の取得に失敗しました"
        )


@router.get("/sessions/{session_id}/participants/{user_id}/stats", response_model=ParticipantStatsResponse)
async def get_participant_stats(
    session_id: str,
    user_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """参加者の統計情報を取得"""
    try:
        participant = await participant_management_service.get_participant_info(session_id, user_id)
        
        if not participant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="参加者が見つかりません"
            )
        
        return ParticipantStatsResponse(
            user_id=participant.user_id,
            display_name=participant.user.display_name,
            role=participant.role.value,
            joined_at=participant.joined_at,
            last_activity=participant.last_activity,
            speak_time_total=participant.speak_time_total,
            speak_time_session=participant.speak_time_session,
            messages_sent=participant.messages_sent,
            current_audio_level=participant.audio_level,
            is_speaking=participant.is_speaking,
            quality_metrics=participant.quality_metrics
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"参加者統計取得に失敗: {e}", session_id=session_id, user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="参加者統計の取得に失敗しました"
        )


@router.post("/sessions/{session_id}/participants/{user_id}/actions", response_model=ParticipantActionResponse)
async def execute_participant_action(
    session_id: str,
    user_id: int,
    action_request: ParticipantActionRequest,
    current_user: User = Depends(get_current_active_user),
):
    """参加者に対するアクションを実行"""
    try:
        action = action_request.action
        action_data = action_request.action_data or {}
        
        if action == "mute":
            muted = action_data.get("muted", True)
            participant = await participant_management_service.mute_participant(
                session_id, user_id, muted, current_user.id
            )
            message = f"参加者を{'ミュート' if muted else 'ミュート解除'}しました"
            
        elif action == "change_role":
            new_role = action_data.get("new_role", "participant")
            try:
                participant_role = ParticipantRole(new_role)
                participant = await participant_management_service.change_participant_role(
                    session_id, user_id, participant_role, current_user.id
                )
                message = f"参加者の役割を{new_role}に変更しました"
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"無効な役割: {new_role}"
                )
                
        elif action == "remove":
            success = await participant_management_service.leave_session(session_id, user_id)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="参加者が見つかりません"
                )
            message = "参加者をセッションから削除しました"
            participant = None
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不明なアクション: {action}"
            )
        
        return ParticipantActionResponse(
            action=action,
            target_user_id=user_id,
            success=True,
            message=message,
            participant_info=participant and ParticipantInfoResponse(
                user_id=participant.user_id,
                display_name=participant.user.display_name,
                email=participant.user.email,
                role=participant.role.value,
                status=participant.status.value,
                joined_at=participant.joined_at,
                last_activity=participant.last_activity,
                is_speaking=participant.is_speaking,
                audio_level=participant.audio_level,
                speak_time_session=participant.speak_time_session,
                messages_sent=participant.messages_sent
            )
        )
        
    except HTTPException:
        raise
    except PermissionException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"参加者アクション実行に失敗: {e}", session_id=session_id, user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="参加者アクションの実行に失敗しました"
        )


@router.get("/health")
async def health_check():
    """参加者管理サービスのヘルスチェック"""
    try:
        # 基本的な動作確認
        active_sessions_count = len(participant_management_service.active_sessions)
        
        return {
            "status": "healthy",
            "service": "participant_management",
            "active_sessions": active_sessions_count,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"ヘルスチェックに失敗: {e}")
        return {
            "status": "unhealthy",
            "service": "participant_management",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
