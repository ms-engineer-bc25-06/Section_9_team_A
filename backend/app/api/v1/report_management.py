from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from typing import List, Optional, Tuple

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.schemas.report_generation import (
    ReportGenerationOptions, ReportFormat, ReportType, ReportFilter,
    ReportResponse, ReportListResponse, ReportExportRequest, ReportShareRequest,
    ReportStats
)
from app.services.report_generation_service import report_generation_service
from app.core.exceptions import (
    NotFoundException, PermissionException, ValidationException,
    BusinessLogicException
)

router = APIRouter()
logger = structlog.get_logger()


@router.get("/reports", response_model=ReportListResponse)
async def get_reports(
    page: int = Query(1, ge=1, description="ページ番号"),
    page_size: int = Query(20, ge=1, le=100, description="ページサイズ"),
    report_type: Optional[ReportType] = Query(None, description="レポートタイプフィルター"),
    report_format: Optional[ReportFormat] = Query(None, description="レポート形式フィルター"),
    language: Optional[str] = Query(None, description="言語フィルター"),
    is_public: Optional[bool] = Query(None, description="公開フラグフィルター"),
    tags: Optional[List[str]] = Query(None, description="タグフィルター"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    レポート一覧を取得
    
    フィルター条件を指定してレポートの一覧を取得します。
    一般ユーザーは自分のレポートと公開されているレポートのみ閲覧可能です。
    """
    try:
        # フィルターの構築
        filters = ReportFilter(
            report_type=report_type,
            report_format=report_format,
            language=language,
            is_public=is_public,
            tags=tags,
            generated_by=current_user.id if not is_public else None
        )
        
        # ページネーション計算
        skip = (page - 1) * page_size
        
        # レポート一覧の取得
        reports, total_count = await report_generation_service.get_reports(
            db, current_user, filters, skip, page_size
        )
        
        # ページ情報の計算
        total_pages = (total_count + page_size - 1) // page_size
        
        logger.info(
            "レポート一覧を取得",
            user_id=current_user.id,
            page=page,
            page_size=page_size,
            total_count=total_count
        )
        
        return ReportListResponse(
            reports=reports,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"レポート一覧取得でエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="レポート一覧の取得に失敗しました"
        )


@router.get("/reports/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    レポート詳細を取得
    
    指定されたIDのレポートの詳細情報を取得します。
    一般ユーザーは自分のレポートと公開されているレポートのみ閲覧可能です。
    """
    try:
        report = await report_generation_service.get_report(db, current_user, report_id)
        
        logger.info(
            "レポート詳細を取得",
            user_id=current_user.id,
            report_id=report_id
        )
        
        return report
        
    except NotFoundException as e:
        logger.warning(f"レポート詳細取得で見つからない: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionException as e:
        logger.warning(f"レポート詳細取得で権限エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"レポート詳細取得でエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="レポート詳細の取得に失敗しました"
        )


@router.post("/reports/{report_id}/export")
async def export_report(
    report_id: str,
    export_request: ReportExportRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    レポートをエクスポート
    
    指定されたレポートを指定された形式でエクスポートします。
    サポートされている形式: PDF, HTML, Excel, PowerPoint, JSON
    """
    try:
        export_result = await report_generation_service.export_report(
            db, current_user, report_id, export_request.export_format
        )
        
        logger.info(
            "レポートをエクスポート",
            user_id=current_user.id,
            report_id=report_id,
            format=export_request.export_format.value
        )
        
        return export_result
        
    except NotFoundException as e:
        logger.warning(f"レポートエクスポートで見つからない: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionException as e:
        logger.warning(f"レポートエクスポートで権限エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"レポートエクスポートでエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="レポートのエクスポートに失敗しました"
        )


@router.post("/reports/{report_id}/share")
async def share_report(
    report_id: str,
    share_request: ReportShareRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    レポートを共有
    
    指定されたレポートを他のユーザーやチームと共有します。
    共有タイプ: user, team, public, link
    """
    try:
        share_result = await report_generation_service.share_report(
            db, current_user, report_id, share_request
        )
        
        logger.info(
            "レポートを共有",
            user_id=current_user.id,
            report_id=report_id,
            share_type=share_request.share_type
        )
        
        return share_result
        
    except NotFoundException as e:
        logger.warning(f"レポート共有で見つからない: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionException as e:
        logger.warning(f"レポート共有で権限エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"レポート共有でエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="レポートの共有に失敗しました"
        )


@router.delete("/reports/{report_id}")
async def delete_report(
    report_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    レポートを削除
    
    指定されたレポートを削除します。
    自分のレポートのみ削除可能です。
    """
    try:
        result = await report_generation_service.delete_report(db, current_user, report_id)
        
        logger.info(
            "レポートを削除",
            user_id=current_user.id,
            report_id=report_id
        )
        
        return {"message": "レポートを削除しました", "report_id": report_id}
        
    except NotFoundException as e:
        logger.warning(f"レポート削除で見つからない: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionException as e:
        logger.warning(f"レポート削除で権限エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"レポート削除でエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="レポートの削除に失敗しました"
        )


@router.get("/reports/{report_id}/download/{format}")
async def download_report(
    report_id: str,
    format: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    レポートをダウンロード
    
    指定されたレポートを指定された形式でダウンロードします。
    """
    try:
        download_result = await report_generation_service.download_report(
            db, current_user, report_id, format
        )
        
        logger.info(
            "レポートをダウンロード",
            user_id=current_user.id,
            report_id=report_id,
            format=format
        )
        
        return download_result
        
    except NotFoundException as e:
        logger.warning(f"レポートダウンロードで見つからない: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionException as e:
        logger.warning(f"レポートダウンロードで権限エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"レポートダウンロードでエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="レポートのダウンロードに失敗しました"
        )


@router.get("/reports/stats", response_model=ReportStats)
async def get_report_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    レポート統計情報を取得
    
    レポートの生成数、形式別統計、利用統計などの情報を提供します。
    """
    try:
        stats = await report_generation_service.get_report_stats(db, current_user)
        
        logger.info(
            "レポート統計情報を取得",
            user_id=current_user.id
        )
        
        return stats
        
    except PermissionException as e:
        logger.warning(f"レポート統計情報取得で権限エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"レポート統計情報取得でエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="レポート統計情報の取得に失敗しました"
        )


@router.get("/reports/formats")
async def get_available_formats():
    """
    利用可能なレポート形式一覧を取得
    
    システムでサポートされているレポート形式の一覧を取得します。
    """
    formats = [
        {
            "value": ReportFormat.PDF,
            "display_name": "PDF",
            "description": "Portable Document Format",
            "file_extension": ".pdf",
            "mime_type": "application/pdf"
        },
        {
            "value": ReportFormat.HTML,
            "display_name": "HTML",
            "description": "HyperText Markup Language",
            "file_extension": ".html",
            "mime_type": "text/html"
        },
        {
            "value": ReportFormat.EXCEL,
            "display_name": "Excel",
            "description": "Microsoft Excel Spreadsheet",
            "file_extension": ".xlsx",
            "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        },
        {
            "value": ReportFormat.POWERPOINT,
            "display_name": "PowerPoint",
            "description": "Microsoft PowerPoint Presentation",
            "file_extension": ".pptx",
            "mime_type": "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        },
        {
            "value": ReportFormat.JSON,
            "display_name": "JSON",
            "description": "JavaScript Object Notation",
            "file_extension": ".json",
            "mime_type": "application/json"
        }
    ]
    
    return {
        "formats": formats,
        "total_count": len(formats)
    }


@router.get("/reports/templates")
async def get_report_templates(
    template_type: Optional[ReportType] = Query(None, description="テンプレートタイプフィルター"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    レポートテンプレート一覧を取得
    
    利用可能なレポートテンプレートの一覧を取得します。
    """
    try:
        templates = await report_generation_service.get_report_templates(
            db, current_user, template_type
        )
        
        logger.info(
            "レポートテンプレート一覧を取得",
            user_id=current_user.id,
            template_type=template_type
        )
        
        return {
            "templates": templates,
            "total_count": len(templates)
        }
        
    except Exception as e:
        logger.error(f"レポートテンプレート一覧取得でエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="レポートテンプレート一覧の取得に失敗しました"
        )
