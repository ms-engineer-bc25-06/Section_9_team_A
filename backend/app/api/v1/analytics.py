from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from typing import List, Optional

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.schemas.analysis import (
    AnalysisCreate, AnalysisUpdate, AnalysisResponse, AnalysisListResponse,
    AnalysisRequest, AnalysisType
)
from app.services.ai_analysis_service import AIAnalysisService
from app.dependencies import get_openai_client
from app.core.exceptions import AnalysisError

router = APIRouter()
logger = structlog.get_logger()

@router.get("/", response_model=AnalysisListResponse)
async def get_analytics(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="ページ番号"),
    page_size: int = Query(20, ge=1, le=100, description="ページサイズ"),
    analysis_type: Optional[AnalysisType] = Query(None, description="分析タイプでフィルタリング"),
    status: Optional[str] = Query(None, description="ステータスでフィルタリング")
):
    """ユーザーのAI分析一覧を取得"""
    try:
        openai_client = get_openai_client()
        ai_analysis_service = AIAnalysisService(openai_client)
        
        result = await ai_analysis_service.get_user_analyses(
            db=db,
            user=current_user,
            page=page,
            page_size=page_size,
            analysis_type=analysis_type
        )
        
        return AnalysisListResponse(
            analyses=result["analyses"],
            total_count=result["total_count"],
            page=result["page"],
            page_size=result["page_size"]
        )
        
    except AnalysisError as e:
        logger.error("分析一覧取得でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error("予期しないエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="分析一覧の取得に失敗しました"
        )

@router.post("/", response_model=List[AnalysisResponse])
async def create_analysis(
    analysis_request: AnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """新しいAI分析を作成"""
    try:
        openai_client = get_openai_client()
        ai_analysis_service = AIAnalysisService(openai_client)
        
        analyses = await ai_analysis_service.analyze_text(
            db=db,
            user=current_user,
            text_content=analysis_request.text_content,
            analysis_types=analysis_request.analysis_types,
            metadata=analysis_request.user_context
        )
        
        logger.info(
            "分析完了",
            user_id=current_user.id,
            analysis_count=len(analyses),
            analysis_types=[a.analysis_type.value for a in analyses]
        )
        
        return analyses
        
    except AnalysisError as e:
        logger.error("分析作成でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error("予期しないエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="分析の作成に失敗しました"
        )

@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """指定されたAI分析の詳細を取得"""
    try:
        openai_client = get_openai_client()
        ai_analysis_service = AIAnalysisService(openai_client)
        
        analysis = await ai_analysis_service.get_analysis_by_id(
            db=db,
            analysis_id=analysis_id,
            user=current_user
        )
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="指定された分析が見つかりません"
            )
        
        return analysis
        
    except HTTPException:
        raise
    except AnalysisError as e:
        logger.error("分析詳細取得でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error("予期しないエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="分析詳細の取得に失敗しました"
        )

@router.put("/{analysis_id}", response_model=AnalysisResponse)
async def update_analysis(
    analysis_id: str,
    analysis_update: AnalysisUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """AI分析情報を更新"""
    try:
        # 現在の分析データを取得
        openai_client = get_openai_client()
        ai_analysis_service = AIAnalysisService(openai_client)
        
        current_analysis = await ai_analysis_service.get_analysis_by_id(
            db=db,
            analysis_id=analysis_id,
            user=current_user
        )
        
        if not current_analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="指定された分析が見つかりません"
            )
        
        # 更新データを準備
        update_data = {}
        if analysis_update.title is not None:
            update_data["title"] = analysis_update.title
        if analysis_update.summary is not None:
            update_data["summary"] = analysis_update.summary
        if analysis_update.keywords is not None:
            update_data["keywords"] = analysis_update.keywords
        if analysis_update.topics is not None:
            update_data["topics"] = analysis_update.topics
        if analysis_update.status is not None:
            update_data["status"] = analysis_update.status
        
        # 更新実行
        updated_analysis = await ai_analysis_service._save_analysis(
            db=db,
            user=current_user,
            analysis_type=current_analysis.analysis_type,
            content=current_analysis.content,
            result=current_analysis.result,
            voice_session_id=current_analysis.voice_session_id,
            transcription_id=current_analysis.transcription_id
        )
        
        logger.info(
            "分析更新完了",
            user_id=current_user.id,
            analysis_id=analysis_id
        )
        
        return updated_analysis
        
    except HTTPException:
        raise
    except AnalysisError as e:
        logger.error("分析更新でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error("予期しないエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="分析の更新に失敗しました"
        )

@router.delete("/{analysis_id}")
async def delete_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """AI分析を削除"""
    try:
        # 現在の分析データを取得
        openai_client = get_openai_client()
        ai_analysis_service = AIAnalysisService(openai_client)
        
        current_analysis = await ai_analysis_service.get_analysis_by_id(
            db=db,
            analysis_id=analysis_id,
            user=current_user
        )
        
        if not current_analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="指定された分析が見つかりません"
            )
        
        # 削除実行（簡易版 - 実際の削除処理はリポジトリで実装）
        # ここでは論理削除またはステータス変更を想定
        update_data = {"status": "deleted"}
        await ai_analysis_service._save_analysis(
            db=db,
            user=current_user,
            analysis_type=current_analysis.analysis_type,
            content=current_analysis.content,
            result=current_analysis.result,
            voice_session_id=current_analysis.voice_session_id,
            transcription_id=current_analysis.transcription_id
        )
        
        logger.info(
            "分析削除完了",
            user_id=current_user.id,
            analysis_id=analysis_id
        )
        
        return {"message": "分析が正常に削除されました"}
        
    except HTTPException:
        raise
    except AnalysisError as e:
        logger.error("分析削除でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error("予期しないエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="分析の削除に失敗しました"
        )

@router.post("/batch", response_model=List[AnalysisResponse])
async def create_batch_analysis(
    analysis_requests: List[AnalysisRequest],
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """複数のAI分析を一括作成"""
    try:
        all_analyses = []
        
        for request in analysis_requests:
            openai_client = get_openai_client()
            ai_analysis_service = AIAnalysisService(openai_client)
            
            analyses = await ai_analysis_service.analyze_text(
                db=db,
                user=current_user,
                text_content=request.text_content,
                analysis_types=request.analysis_types,
                metadata=request.user_context
            )
            all_analyses.extend(analyses)
        
        logger.info(
            "一括分析完了",
            user_id=current_user.id,
            total_analysis_count=len(all_analyses)
        )
        
        return all_analyses
        
    except AnalysisError as e:
        logger.error("一括分析でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error("予期しないエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="一括分析の作成に失敗しました"
        )

@router.get("/types/{analysis_type}", response_model=List[AnalysisResponse])
async def get_analyses_by_type(
    analysis_type: AnalysisType,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="ページ番号"),
    page_size: int = Query(20, ge=1, le=100, description="ページサイズ")
):
    """特定の分析タイプの分析結果を取得"""
    try:
        openai_client = get_openai_client()
        ai_analysis_service = AIAnalysisService(openai_client)
        
        result = await ai_analysis_service.get_user_analyses(
            db=db,
            user=current_user,
            page=page,
            page_size=page_size,
            analysis_type=analysis_type
        )
        
        return result["analyses"]
        
    except AnalysisError as e:
        logger.error("分析タイプ別取得でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error("予期しないエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="分析タイプ別の取得に失敗しました"
        )

@router.get("/statistics/summary")
async def get_analysis_statistics(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, ge=1, le=365, description="統計期間（日数）")
):
    """ユーザーの分析統計を取得"""
    try:
        # 簡易的な統計情報を返す
        openai_client = get_openai_client()
        ai_analysis_service = AIAnalysisService(openai_client)
        
        result = await ai_analysis_service.get_user_analyses(
            db=db,
            user=current_user,
            page=1,
            page_size=1000  # 統計用に大量取得
        )
        
        analyses = result["analyses"]
        
        # 分析タイプ別の件数
        type_counts = {}
        for analysis in analyses:
            analysis_type = analysis.analysis_type.value
            type_counts[analysis_type] = type_counts.get(analysis_type, 0) + 1
        
        # 感情分析の平均スコア
        sentiment_scores = [
            a.sentiment_score for a in analyses 
            if a.sentiment_score is not None
        ]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0
        
        return {
            "total_count": len(analyses),
            "type_counts": type_counts,
            "average_sentiment": avg_sentiment,
            "period_days": days
        }
        
    except AnalysisError as e:
        logger.error("統計取得でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error("予期しないエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="統計情報の取得に失敗しました"
        )
