from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.services.voice_session_service import VoiceSessionService
from app.schemas.voice_session import (
    VoiceSessionCreate,
    VoiceSessionUpdate,
    VoiceSessionResponse,
    VoiceSessionListResponse,
    VoiceSessionDetailResponse,
    VoiceSessionFilters,
    VoiceSessionQueryParams,
    VoiceSessionStats,
    VoiceSessionAudioUpdate,
    ParticipantAddRequest,
    ParticipantListResponse,
    ParticipantUpdateRequest,
    RecordingControlRequest,
    RecordingStatusResponse,
    RecordingStatusEnum,
    RealtimeStatsResponse,
    SessionProgressResponse,
)
from app.core.exceptions import (
    BridgeLineException,
    ValidationException,
    NotFoundException,
    PermissionException,
)
from app.api.deps import get_voice_session_service, handle_bridge_line_exceptions

router = APIRouter()
logger = structlog.get_logger()


@router.get("/", response_model=VoiceSessionListResponse)
async def get_voice_sessions(
    page: int = Query(1, ge=1, description="ページ番号"),
    size: int = Query(10, ge=1, le=100, description="ページサイズ"),
    status: Optional[str] = Query(None, description="ステータスでフィルター"),
    is_public: Optional[bool] = Query(None, description="公開設定でフィルター"),
    is_analyzed: Optional[bool] = Query(None, description="分析完了でフィルター"),
    search: Optional[str] = Query(None, description="検索キーワード"),
    current_user: User = Depends(get_current_active_user),
    voice_session_service: VoiceSessionService = Depends(get_voice_session_service),
):
    """ユーザーの音声セッション一覧を取得"""
    try:
        # クエリパラメータ作成
        query_params = VoiceSessionQueryParams(
            page=page,
            size=size,
            status=status,
            is_public=is_public,
            is_analyzed=is_analyzed,
            search=search,
        )

        # サービス呼び出し
        result = await voice_session_service.get_user_sessions(
            user_id=current_user.id, query_params=query_params
        )

        return result

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        logger.error(f"Failed to get voice sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"},
        )


@router.post(
    "/", response_model=VoiceSessionResponse, status_code=status.HTTP_201_CREATED
)
async def create_voice_session(
    session_data: VoiceSessionCreate,
    current_user: User = Depends(get_current_active_user),
    voice_session_service: VoiceSessionService = Depends(get_voice_session_service),
):
    """新しい音声セッションを作成"""
    try:
        # サービス呼び出し
        result = await voice_session_service.create_session(
            user_id=current_user.id, session_data=session_data
        )

        return result

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        logger.error(f"Failed to create voice session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"},
        )


@router.post(
    "/dev", response_model=VoiceSessionResponse, status_code=status.HTTP_201_CREATED
)
async def create_voice_session_dev(
    session_data: VoiceSessionCreate,
    voice_session_service: VoiceSessionService = Depends(get_voice_session_service),
):
    """開発環境用：認証不要で音声セッションを作成"""
    try:
        # 開発環境用のダミーユーザーID
        dummy_user_id = 1
        
        # サービス呼び出し
        result = await voice_session_service.create_session(
            user_id=dummy_user_id, session_data=session_data
        )

        return result

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        logger.error(f"Failed to create voice session (dev): {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"},
        )


@router.get("/{session_id}", response_model=VoiceSessionDetailResponse)
async def get_voice_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    voice_session_service: VoiceSessionService = Depends(get_voice_session_service),
):
    """指定された音声セッションの詳細を取得"""
    try:
        # サービス呼び出し
        result = await voice_session_service.get_session_by_id(
            session_id=session_id, user_id=current_user.id
        )

        return result

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        logger.error(f"Failed to get voice session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"},
        )


@router.put("/{session_id}", response_model=VoiceSessionResponse)
async def update_voice_session(
    session_id: int,
    session_data: VoiceSessionUpdate,
    current_user: User = Depends(get_current_active_user),
    voice_session_service: VoiceSessionService = Depends(get_voice_session_service),
):
    """音声セッション情報を更新"""
    try:
        # サービス呼び出し
        result = await voice_session_service.update_session(
            session_id=session_id, user_id=current_user.id, update_data=session_data
        )

        return result

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        logger.error(f"Failed to update voice session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"},
        )


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_voice_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    voice_session_service: VoiceSessionService = Depends(get_voice_session_service),
):
    """音声セッションを削除"""
    try:
        # サービス呼び出し
        success = await voice_session_service.delete_session(
            session_id=session_id, user_id=current_user.id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "Voice session not found"},
            )

        return None

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        logger.error(f"Failed to delete voice session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"},
        )


@router.get("/team/{team_id}", response_model=VoiceSessionListResponse)
async def get_team_voice_sessions(
    team_id: int,
    page: int = Query(1, ge=1, description="ページ番号"),
    size: int = Query(10, ge=1, le=100, description="ページサイズ"),
    status: Optional[str] = Query(None, description="ステータスでフィルター"),
    is_public: Optional[bool] = Query(None, description="公開設定でフィルター"),
    is_analyzed: Optional[bool] = Query(None, description="分析完了でフィルター"),
    search: Optional[str] = Query(None, description="検索キーワード"),
    current_user: User = Depends(get_current_active_user),
    voice_session_service: VoiceSessionService = Depends(get_voice_session_service),
):
    """チームの音声セッション一覧を取得"""
    try:
        # クエリパラメータ作成
        query_params = VoiceSessionQueryParams(
            page=page,
            size=size,
            status=status,
            is_public=is_public,
            is_analyzed=is_analyzed,
            search=search,
        )

        # サービス呼び出し
        result = await voice_session_service.get_team_sessions(
            team_id=team_id, user_id=current_user.id, query_params=query_params
        )

        return result

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        logger.error(f"Failed to get team voice sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"},
        )


@router.get("/public/list", response_model=VoiceSessionListResponse)
async def get_public_voice_sessions(
    page: int = Query(1, ge=1, description="ページ番号"),
    size: int = Query(10, ge=1, le=100, description="ページサイズ"),
    status: Optional[str] = Query(None, description="ステータスでフィルター"),
    is_analyzed: Optional[bool] = Query(None, description="分析完了でフィルター"),
    search: Optional[str] = Query(None, description="検索キーワード"),
    voice_session_service: VoiceSessionService = Depends(get_voice_session_service),
):
    """公開音声セッション一覧を取得"""
    try:
        # クエリパラメータ作成
        query_params = VoiceSessionQueryParams(
            page=page,
            size=size,
            status=status,
            is_public=True,  # 公開セッションのみ
            is_analyzed=is_analyzed,
            search=search,
        )

        # サービス呼び出し
        result = await voice_session_service.get_public_sessions(
            query_params=query_params
        )

        return result

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        logger.error(f"Failed to get public voice sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"},
        )


@router.get("/search", response_model=VoiceSessionListResponse)
async def search_voice_sessions(
    q: str = Query(..., description="検索キーワード"),
    page: int = Query(1, ge=1, description="ページ番号"),
    size: int = Query(10, ge=1, le=100, description="ページサイズ"),
    current_user: User = Depends(get_current_active_user),
    voice_session_service: VoiceSessionService = Depends(get_voice_session_service),
):
    """音声セッションを検索"""
    try:
        # クエリパラメータ作成
        query_params = VoiceSessionQueryParams(
            page=page,
            size=size,
            search=q,
        )

        # サービス呼び出し
        result = await voice_session_service.search_sessions(
            user_id=current_user.id, search_term=q, query_params=query_params
        )

        return result

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        logger.error(f"Failed to search voice sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"},
        )


@router.get("/stats/user", response_model=VoiceSessionStats)
async def get_user_voice_session_stats(
    current_user: User = Depends(get_current_active_user),
    voice_session_service: VoiceSessionService = Depends(get_voice_session_service),
):
    """ユーザーの音声セッション統計を取得"""
    try:
        # サービス呼び出し
        result = await voice_session_service.get_user_stats(user_id=current_user.id)

        return result

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        logger.error(f"Failed to get user voice session stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"},
        )


@router.put("/{session_id}/audio", response_model=VoiceSessionResponse)
async def update_voice_session_audio(
    session_id: int,
    audio_data: VoiceSessionAudioUpdate,
    current_user: User = Depends(get_current_active_user),
    voice_session_service: VoiceSessionService = Depends(get_voice_session_service),
):
    """音声ファイル情報を更新"""
    try:
        # サービス呼び出し
        result = await voice_session_service.update_audio_info(
            session_id=session_id, user_id=current_user.id, audio_data=audio_data
        )

        return result

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        logger.error(f"Failed to update voice session audio {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"},
        )


@router.post("/{session_id}/generate-id")
async def generate_session_id(
    current_user: User = Depends(get_current_active_user),
    voice_session_service: VoiceSessionService = Depends(get_voice_session_service),
):
    """ユニークなセッションIDを生成"""
    try:
        # サービス呼び出し
        session_id = await voice_session_service.generate_session_id()

        return {"session_id": session_id}

    except Exception as e:
        logger.error(f"Failed to generate session ID: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"},
        )


@router.post("/{session_id}/start", response_model=VoiceSessionResponse)
async def start_voice_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    voice_session_service: VoiceSessionService = Depends(get_voice_session_service),
):
    """音声セッションを開始"""
    try:
        # サービス呼び出し
        result = await voice_session_service.start_session(
            session_id=session_id, user_id=current_user.id
        )

        return result

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        logger.error(f"Failed to start voice session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"},
        )


@router.post("/{session_id}/end", response_model=VoiceSessionResponse)
async def end_voice_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    voice_session_service: VoiceSessionService = Depends(get_voice_session_service),
):
    """音声セッションを終了"""
    try:
        # サービス呼び出し
        result = await voice_session_service.end_session(
            session_id=session_id, user_id=current_user.id
        )

        return result

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        logger.error(f"Failed to end voice session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"},
        )


@router.post("/{session_id}/pause", response_model=VoiceSessionResponse)
async def pause_voice_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    voice_session_service: VoiceSessionService = Depends(get_voice_session_service),
):
    """音声セッションを一時停止"""
    try:
        # 一時停止用の更新データ
        update_data = VoiceSessionUpdate(status="paused")

        # サービス呼び出し
        result = await voice_session_service.update_session(
            session_id=session_id, user_id=current_user.id, update_data=update_data
        )

        return result

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        logger.error(f"Failed to pause voice session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"},
        )


@router.post("/{session_id}/resume", response_model=VoiceSessionResponse)
async def resume_voice_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    voice_session_service: VoiceSessionService = Depends(get_voice_session_service),
):
    """音声セッションを再開"""
    try:
        # 再開用の更新データ
        update_data = VoiceSessionUpdate(status="active")

        # サービス呼び出し
        result = await voice_session_service.update_session(
            session_id=session_id, user_id=current_user.id, update_data=update_data
        )

        return result

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        logger.error(f"Failed to resume voice session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"},
        )


# 参加者管理API
@router.post("/{session_id}/participants", response_model=VoiceSessionResponse)
async def add_participant(
    session_id: str,
    participant_data: ParticipantAddRequest,
    current_user: User = Depends(get_current_active_user),
    voice_session_service: VoiceSessionService = Depends(get_voice_session_service),
):
    """音声セッションに参加者を追加"""
    try:
        # サービス呼び出し
        result = await voice_session_service.add_participant(
            session_id=session_id,
            user_id=current_user.id,
            participant_user_id=participant_data.user_id,
            role=participant_data.role,
        )

        return result

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        logger.error(f"Failed to add participant to session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"},
        )


@router.delete(
    "/{session_id}/participants/{participant_user_id}",
    response_model=VoiceSessionResponse,
)
async def remove_participant(
    session_id: str,
    participant_user_id: int,
    current_user: User = Depends(get_current_active_user),
    voice_session_service: VoiceSessionService = Depends(get_voice_session_service),
):
    """音声セッションから参加者を削除"""
    try:
        # サービス呼び出し
        result = await voice_session_service.remove_participant(
            session_id=session_id,
            user_id=current_user.id,
            participant_user_id=participant_user_id,
        )

        return result

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        logger.error(f"Failed to remove participant from session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"},
        )


@router.get("/{session_id}/participants", response_model=ParticipantListResponse)
async def get_participants(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    voice_session_service: VoiceSessionService = Depends(get_voice_session_service),
):
    """音声セッションの参加者一覧を取得"""
    try:
        # サービス呼び出し
        result = await voice_session_service.get_participants(
            session_id=session_id, user_id=current_user.id
        )

        return result

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        logger.error(f"Failed to get participants for session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"},
        )


@router.put(
    "/{session_id}/participants/{participant_user_id}/role",
    response_model=VoiceSessionResponse,
)
async def update_participant_role(
    session_id: str,
    participant_user_id: int,
    role_data: ParticipantUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    voice_session_service: VoiceSessionService = Depends(get_voice_session_service),
):
    """参加者の権限を更新"""
    try:
        # サービス呼び出し
        result = await voice_session_service.update_participant_role(
            session_id=session_id,
            user_id=current_user.id,
            participant_user_id=participant_user_id,
            new_role=role_data.role,
        )

        return result

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        logger.error(f"Failed to update participant role in session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"},
        )


# 録音制御API
@router.post("/{session_id}/recording/start", response_model=RecordingStatusResponse)
async def start_recording(
    session_id: str,
    recording_data: RecordingControlRequest,
    current_user: User = Depends(get_current_active_user),
    voice_session_service: VoiceSessionService = Depends(get_voice_session_service),
):
    """録音を開始"""
    try:
        # サービス呼び出し
        result = await voice_session_service.start_recording(
            session_id=session_id,
            user_id=current_user.id,
            quality=recording_data.quality,
            format=recording_data.format,
        )

        return result

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        logger.error(f"Failed to start recording for session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"},
        )


@router.post("/{session_id}/recording/stop", response_model=RecordingStatusResponse)
async def stop_recording(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    voice_session_service: VoiceSessionService = Depends(get_voice_session_service),
):
    """録音を停止"""
    try:
        # サービス呼び出し
        result = await voice_session_service.stop_recording(
            session_id=session_id, user_id=current_user.id
        )

        return result

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        logger.error(f"Failed to stop recording for session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"},
        )


@router.post("/{session_id}/recording/pause", response_model=RecordingStatusResponse)
async def pause_recording(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    voice_session_service: VoiceSessionService = Depends(get_voice_session_service),
):
    """録音を一時停止"""
    try:
        # サービス呼び出し
        result = await voice_session_service.pause_recording(
            session_id=session_id, user_id=current_user.id
        )

        return result

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        logger.error(f"Failed to pause recording for session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"},
        )


@router.post("/{session_id}/recording/resume", response_model=RecordingStatusResponse)
async def resume_recording(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    voice_session_service: VoiceSessionService = Depends(get_voice_session_service),
):
    """録音を再開"""
    try:
        # サービス呼び出し
        result = await voice_session_service.resume_recording(
            session_id=session_id, user_id=current_user.id
        )

        return result

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        logger.error(f"Failed to resume recording for session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"},
        )


@router.get("/{session_id}/recording/status", response_model=RecordingStatusResponse)
async def get_recording_status(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    voice_session_service: VoiceSessionService = Depends(get_voice_session_service),
):
    """録音状態を取得"""
    try:
        # サービス呼び出し
        result = await voice_session_service.get_recording_status(
            session_id=session_id, user_id=current_user.id
        )

        return result

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        logger.error(f"Failed to get recording status for session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"},
        )


# リアルタイム統計API
@router.get("/{session_id}/stats/realtime", response_model=RealtimeStatsResponse)
async def get_realtime_stats(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    voice_session_service: VoiceSessionService = Depends(get_voice_session_service),
):
    """リアルタイム統計を取得"""
    try:
        # サービス呼び出し
        result = await voice_session_service.get_realtime_stats(
            session_id=session_id, user_id=current_user.id
        )

        return result

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        logger.error(f"Failed to get realtime stats for session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"},
        )


@router.get("/{session_id}/progress", response_model=SessionProgressResponse)
async def get_session_progress(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    voice_session_service: VoiceSessionService = Depends(get_voice_session_service),
):
    """セッション進行状況を取得"""
    try:
        # サービス呼び出し
        result = await voice_session_service.get_session_progress(
            session_id=session_id, user_id=current_user.id
        )

        return result

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        logger.error(f"Failed to get session progress for session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"},
        )
