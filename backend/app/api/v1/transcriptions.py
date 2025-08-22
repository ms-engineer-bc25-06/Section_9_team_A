from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import structlog

from app.api.deps import get_current_user, get_db
from app.schemas.transcription import (
    TranscriptionCreate,
    TranscriptionUpdate,
    TranscriptionResponse,
    TranscriptionListResponse,
    TranscriptionQueryParams,
)
from app.models.user import User
from app.models.transcription import Transcription
from app.repositories.transcription_repository import transcription_repository

logger = structlog.get_logger()

router = APIRouter()


@router.post("/", response_model=TranscriptionResponse)
async def create_transcription(
    transcription: TranscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """文字起こしを作成"""
    try:
        # 基本的なバリデーション
        if not transcription.content.strip():
            raise HTTPException(status_code=400, detail="文字起こしの内容は必須です")
        
        # 文字起こしIDの生成（UUIDベース）
        import uuid
        transcription_id = str(uuid.uuid4())
        
        # データベースに保存
        db_transcription = await transcription_repository.create(
            db=db,
            obj_in=transcription,
            transcription_id=transcription_id,
        )
        
        logger.info(
            "Transcription created",
            transcription_id=db_transcription.id,
            user_id=current_user.id,
        )
        
        return db_transcription
        
    except Exception as e:
        logger.error(f"Failed to create transcription: {e}")
        raise HTTPException(status_code=500, detail="文字起こしの作成に失敗しました")


@router.get("/", response_model=TranscriptionListResponse)
async def list_transcriptions(
    page: int = Query(1, ge=1, description="ページ番号"),
    size: int = Query(20, ge=1, le=100, description="ページサイズ"),
    voice_session_id: Optional[int] = Query(None, description="音声セッションID"),
    user_id: Optional[int] = Query(None, description="ユーザーID"),
    status: Optional[str] = Query(None, description="ステータス"),
    language: Optional[str] = Query(None, description="言語"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """文字起こし一覧を取得"""
    try:
        # クエリパラメータの構築
        query_params = TranscriptionQueryParams(
            page=page,
            size=size,
            voice_session_id=voice_session_id,
            user_id=user_id,
            status=status,
            language=language,
        )
        
        # データベースから取得
        transcriptions, total = await transcription_repository.get_multi(
            db=db,
            query_params=query_params,
        )
        
        return TranscriptionListResponse(
            transcriptions=transcriptions,
            total=total,
            page=page,
            size=size,
        )
        
    except Exception as e:
        logger.error(f"Failed to list transcriptions: {e}")
        raise HTTPException(status_code=500, detail="文字起こし一覧の取得に失敗しました")


@router.get("/{transcription_id}", response_model=TranscriptionResponse)
async def get_transcription(
    transcription_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """特定の文字起こしを取得"""
    try:
        transcription = await transcription_repository.get(db=db, id=transcription_id)
        if not transcription:
            raise HTTPException(status_code=404, detail="文字起こしが見つかりません")
        
        return transcription
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get transcription {transcription_id}: {e}")
        raise HTTPException(status_code=500, detail="文字起こしの取得に失敗しました")


@router.put("/{transcription_id}", response_model=TranscriptionResponse)
async def update_transcription(
    transcription_id: int,
    transcription_update: TranscriptionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """文字起こしを更新"""
    try:
        # 既存の文字起こしを取得
        existing_transcription = await transcription_repository.get(db=db, id=transcription_id)
        if not existing_transcription:
            raise HTTPException(status_code=404, detail="文字起こしが見つかりません")
        
        # 権限チェック（自分の文字起こしまたは管理者のみ）
        if existing_transcription.user_id != current_user.id:
            # TODO: 管理者権限チェックを追加
            raise HTTPException(status_code=403, detail="この文字起こしを更新する権限がありません")
        
        # 更新
        updated_transcription = await transcription_repository.update(
            db=db,
            db_obj=existing_transcription,
            obj_in=transcription_update,
        )
        
        logger.info(
            "Transcription updated",
            transcription_id=transcription_id,
            user_id=current_user.id,
        )
        
        return updated_transcription
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update transcription {transcription_id}: {e}")
        raise HTTPException(status_code=500, detail="文字起こしの更新に失敗しました")


@router.delete("/{transcription_id}")
async def delete_transcription(
    transcription_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """文字起こしを削除"""
    try:
        # 既存の文字起こしを取得
        existing_transcription = await transcription_repository.get(db=db, id=transcription_id)
        if not existing_transcription:
            raise HTTPException(status_code=404, detail="文字起こしが見つかりません")
        
        # 権限チェック（自分の文字起こしまたは管理者のみ）
        if existing_transcription.user_id != current_user.id:
            # TODO: 管理者権限チェックを追加
            raise HTTPException(status_code=403, detail="この文字起こしを削除する権限がありません")
        
        # 削除
        await transcription_repository.remove(db=db, id=transcription_id)
        
        logger.info(
            "Transcription deleted",
            transcription_id=transcription_id,
            user_id=current_user.id,
        )
        
        return {"message": "文字起こしが削除されました"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete transcription {transcription_id}: {e}")
        raise HTTPException(status_code=500, detail="文字起こしの削除に失敗しました")
