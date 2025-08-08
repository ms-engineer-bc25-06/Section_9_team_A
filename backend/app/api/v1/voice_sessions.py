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
    VoiceSessionQueryParams,
    VoiceSessionStats,
    VoiceSessionAudioUpdate,
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
