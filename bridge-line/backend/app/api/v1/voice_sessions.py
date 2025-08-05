from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User

router = APIRouter()
logger = structlog.get_logger()


@router.get("/")
async def get_voice_sessions(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """ユーザーの音声セッション一覧を取得"""
    # TODO: 音声セッションモデルとサービスを実装後に完成
    return {"message": "Voice sessions endpoint - coming soon"}


@router.post("/")
async def create_voice_session(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """新しい音声セッションを作成"""
    # TODO: 音声セッション作成機能を実装
    return {"message": "Create voice session - coming soon"}


@router.get("/{session_id}")
async def get_voice_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """指定された音声セッションの詳細を取得"""
    # TODO: 音声セッション詳細取得機能を実装
    return {"message": f"Voice session {session_id} details - coming soon"}


@router.put("/{session_id}")
async def update_voice_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """音声セッション情報を更新"""
    # TODO: 音声セッション更新機能を実装
    return {"message": f"Update voice session {session_id} - coming soon"}


@router.delete("/{session_id}")
async def delete_voice_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """音声セッションを削除"""
    # TODO: 音声セッション削除機能を実装
    return {"message": f"Delete voice session {session_id} - coming soon"}
