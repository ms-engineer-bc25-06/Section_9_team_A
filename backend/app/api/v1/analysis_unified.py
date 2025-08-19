"""
統合された分析API
分析、分析データ取得、比較分析、AI分析を統合
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from typing import List, Optional, Dict, Any

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.schemas.analysis import (
    AnalysisCreate, AnalysisUpdate, AnalysisResponse, AnalysisListResponse,
    AnalysisRequest, AnalysisType
)
from app.schemas.comparison_analysis import (
    ComparisonRequest, ComparisonResult, ComparisonAnalytics
)
from app.services.ai_analysis_service import AIAnalysisService
from app.services.comparison_analysis_service import ComparisonAnalysisService
from app.dependencies import get_openai_client
from app.core.exceptions import AnalysisError

router = APIRouter()
logger = structlog.get_logger()


# ==================== 基本分析機能 ====================

@router.get("/", response_model=AnalysisListResponse)
async def get_analyses(
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


@router.get("/analytics")
async def get_analytics(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    start_date: Optional[str] = Query(None, description="開始日"),
    end_date: Optional[str] = Query(None, description="終了日"),
    analysis_type: Optional[AnalysisType] = Query(None, description="分析タイプ")
):
    """分析データの統計情報を取得"""
    try:
        openai_client = get_openai_client()
        ai_analysis_service = AIAnalysisService(openai_client)
        
        # 分析統計を取得
        analytics_data = await ai_analysis_service.get_analytics_summary(
            db=db,
            user=current_user,
            start_date=start_date,
            end_date=end_date,
            analysis_type=analysis_type
        )
        
        return {
            "user_id": current_user.id,
            "total_analyses": analytics_data.get("total_analyses", 0),
            "analyses_by_type": analytics_data.get("analyses_by_type", {}),
            "analyses_by_status": analytics_data.get("analyses_by_status", {}),
            "recent_analyses": analytics_data.get("recent_analyses", []),
            "success_rate": analytics_data.get("success_rate", 0.0),
            "average_processing_time": analytics_data.get("average_processing_time", 0.0)
        }
        
    except Exception as e:
        logger.error("分析統計取得でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="分析統計の取得に失敗しました"
        )


# ==================== 比較分析機能 ====================

@router.post("/compare", response_model=ComparisonResult)
async def create_comparison_analysis(
    comparison_request: ComparisonRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """比較分析を作成"""
    try:
        comparison_service = ComparisonAnalysisService()
        
        result = await comparison_service.create_comparison_analysis(
            db=db,
            user=current_user,
            request=comparison_request
        )
        
        logger.info(
            "比較分析完了",
            user_id=current_user.id,
            comparison_id=result.id,
            comparison_type=result.comparison_type.value
        )
        
        return result
        
    except Exception as e:
        logger.error("比較分析作成でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="比較分析の作成に失敗しました"
        )


@router.get("/compare/{comparison_id}", response_model=ComparisonResult)
async def get_comparison_analysis(
    comparison_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """比較分析の詳細を取得"""
    try:
        comparison_service = ComparisonAnalysisService()
        
        result = await comparison_service.get_comparison_analysis(
            db=db,
            comparison_id=comparison_id,
            user=current_user
        )
        
        return result
        
    except Exception as e:
        logger.error("比較分析取得でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="比較分析の取得に失敗しました"
        )


@router.get("/compare/{comparison_id}/analytics", response_model=ComparisonAnalytics)
async def get_comparison_analytics(
    comparison_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """比較分析の分析データを取得"""
    try:
        comparison_service = ComparisonAnalysisService()
        
        analytics = await comparison_service.get_comparison_analytics(
            db=db,
            comparison_id=comparison_id,
            user=current_user
        )
        
        return analytics
        
    except Exception as e:
        logger.error("比較分析統計取得でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="比較分析統計の取得に失敗しました"
        )


# ==================== 分析管理機能 ====================

@router.put("/{analysis_id}", response_model=AnalysisResponse)
async def update_analysis(
    analysis_id: int,
    analysis_update: AnalysisUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """分析を更新"""
    try:
        openai_client = get_openai_client()
        ai_analysis_service = AIAnalysisService(openai_client)
        
        updated_analysis = await ai_analysis_service.update_analysis(
            db=db,
            analysis_id=analysis_id,
            user=current_user,
            update_data=analysis_update
        )
        
        return updated_analysis
        
    except Exception as e:
        logger.error("分析更新でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="分析の更新に失敗しました"
        )


@router.delete("/{analysis_id}")
async def delete_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """分析を削除"""
    try:
        openai_client = get_openai_client()
        ai_analysis_service = AIAnalysisService(openai_client)
        
        await ai_analysis_service.delete_analysis(
            db=db,
            analysis_id=analysis_id,
            user=current_user
        )
        
        return {"message": "分析が正常に削除されました"}
        
    except Exception as e:
        logger.error("分析削除でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="分析の削除に失敗しました"
        )


# ==================== 分析エクスポート機能 ====================

@router.get("/{analysis_id}/export")
async def export_analysis(
    analysis_id: int,
    format: str = Query("json", description="エクスポート形式 (json, csv, pdf)"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """分析結果をエクスポート"""
    try:
        openai_client = get_openai_client()
        ai_analysis_service = AIAnalysisService(openai_client)
        
        export_data = await ai_analysis_service.export_analysis(
            db=db,
            analysis_id=analysis_id,
            user=current_user,
            export_format=format
        )
        
        return export_data
        
    except Exception as e:
        logger.error("分析エクスポートでエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="分析のエクスポートに失敗しました"
        )


# ==================== ヘルスチェック ====================

@router.get("/health")
async def health_check():
    """分析サービス ヘルスチェック"""
    return {
        "status": "healthy",
        "service": "unified_analysis",
        "features": [
            "basic_analysis",
            "comparison_analysis", 
            "analytics",
            "export"
        ]
    }
