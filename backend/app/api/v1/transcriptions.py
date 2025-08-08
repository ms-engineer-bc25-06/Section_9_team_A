from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User

router = APIRouter()
logger = structlog.get_logger()


@router.get("/")
async def get_transcriptions(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """ユーザーの文字起こし一覧を取得"""
    # TODO: 文字起こしモデルとサービスを実装後に完成
    return {"message": "Transcriptions endpoint - coming soon"}


@router.post("/")
async def create_transcription(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """新しい文字起こしを作成"""
    # TODO: 文字起こし作成機能を実装
    return {"message": "Create transcription - coming soon"}


@router.get("/{transcription_id}")
async def get_transcription(
    transcription_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """指定された文字起こしの詳細を取得"""
    # TODO: 文字起こし詳細取得機能を実装
    return {"message": f"Transcription {transcription_id} details - coming soon"}


@router.put("/{transcription_id}")
async def update_transcription(
    transcription_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """文字起こし情報を更新"""
    # TODO: 文字起こし更新機能を実装
    return {"message": f"Update transcription {transcription_id} - coming soon"}


@router.delete("/{transcription_id}")
async def delete_transcription(
    transcription_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """文字起こしを削除"""
    # TODO: 文字起こし削除機能を実装
    return {"message": f"Delete transcription {transcription_id} - coming soon"}
