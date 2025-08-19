from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from typing import List, Optional, Tuple

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.schemas.industry_management import (
    IndustryBenchmarkCreate, IndustryBenchmarkUpdate, IndustryBenchmarkResponse,
    IndustryBenchmarkRequestCreate, IndustryBenchmarkRequestUpdate, IndustryBenchmarkRequestResponse,
    IndustryBenchmarkFilter, IndustryBenchmarkStats, CompanySize, RequestStatus
)
from app.services.industry_management_service import industry_management_service
from app.core.exceptions import (
    NotFoundException, PermissionException, ValidationException,
    BusinessLogicException, DuplicateException
)

router = APIRouter()
logger = structlog.get_logger()


@router.post("/benchmarks", response_model=IndustryBenchmarkResponse)
async def create_industry_benchmark(
    benchmark_data: IndustryBenchmarkCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    業界ベンチマークを作成
    
    管理者または責任者のみが実行可能です。
    業界コードと企業規模の組み合わせは一意である必要があります。
    """
    try:
        result = await industry_management_service.create_industry_benchmark(
            db, current_user, benchmark_data
        )

        logger.info(
            "業界ベンチマークを作成",
            benchmark_id=result.id,
            industry_code=result.industry_code,
            created_by=current_user.id
        )

        return result

    except PermissionException as e:
        logger.warning(f"業界ベンチマーク作成で権限エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except DuplicateException as e:
        logger.warning(f"業界ベンチマーク作成で重複エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"業界ベンチマーク作成でエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="業界ベンチマークの作成に失敗しました"
        )


@router.get("/benchmarks", response_model=Tuple[List[IndustryBenchmarkResponse], int])
async def get_industry_benchmarks(
    skip: int = Query(0, ge=0, description="スキップ件数"),
    limit: int = Query(100, ge=1, le=1000, description="取得件数"),
    industry_name: Optional[str] = Query(None, description="業界名フィルター"),
    company_size: Optional[CompanySize] = Query(None, description="企業規模フィルター"),
    is_active: Optional[bool] = Query(None, description="有効フラグフィルター"),
    is_public: Optional[bool] = Query(None, description="公開フラグフィルター"),
    tags: Optional[List[str]] = Query(None, description="タグフィルター"),
    created_by: Optional[int] = Query(None, description="作成者フィルター"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    業界ベンチマーク一覧を取得
    
    フィルター条件を指定して業界ベンチマークの一覧を取得します。
    一般ユーザーは公開されているベンチマークのみ閲覧可能です。
    """
    try:
        # フィルターの構築
        filters = IndustryBenchmarkFilter(
            industry_name=industry_name,
            company_size=company_size,
            is_active=is_active,
            is_public=is_public,
            tags=tags,
            created_by=created_by
        )

        result = await industry_management_service.get_industry_benchmarks(
            db, current_user, filters, skip, limit
        )

        logger.info(
            "業界ベンチマーク一覧を取得",
            user_id=current_user.id,
            skip=skip,
            limit=limit,
            total_count=result[1]
        )

        return result

    except Exception as e:
        logger.error(f"業界ベンチマーク一覧取得でエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="業界ベンチマーク一覧の取得に失敗しました"
        )


@router.get("/benchmarks/{benchmark_id}", response_model=IndustryBenchmarkResponse)
async def get_industry_benchmark(
    benchmark_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    業界ベンチマーク詳細を取得
    
    指定されたIDの業界ベンチマークの詳細情報を取得します。
    一般ユーザーは公開されているベンチマークのみ閲覧可能です。
    """
    try:
        result = await industry_management_service.get_industry_benchmark(
            db, current_user, benchmark_id
        )

        logger.info(
            "業界ベンチマーク詳細を取得",
            user_id=current_user.id,
            benchmark_id=benchmark_id
        )

        return result

    except NotFoundException as e:
        logger.warning(f"業界ベンチマーク詳細取得で見つからない: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionException as e:
        logger.warning(f"業界ベンチマーク詳細取得で権限エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"業界ベンチマーク詳細取得でエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="業界ベンチマーク詳細の取得に失敗しました"
        )


@router.put("/benchmarks/{benchmark_id}", response_model=IndustryBenchmarkResponse)
async def update_industry_benchmark(
    benchmark_id: int,
    update_data: IndustryBenchmarkUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    業界ベンチマークを更新
    
    管理者または責任者のみが実行可能です。
    更新可能なフィールドのみを指定してください。
    """
    try:
        result = await industry_management_service.update_industry_benchmark(
            db, current_user, benchmark_id, update_data
        )

        logger.info(
            "業界ベンチマークを更新",
            user_id=current_user.id,
            benchmark_id=benchmark_id
        )

        return result

    except NotFoundException as e:
        logger.warning(f"業界ベンチマーク更新で見つからない: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionException as e:
        logger.warning(f"業界ベンチマーク更新で権限エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"業界ベンチマーク更新でエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="業界ベンチマークの更新に失敗しました"
        )


@router.delete("/benchmarks/{benchmark_id}")
async def delete_industry_benchmark(
    benchmark_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    業界ベンチマークを削除（論理削除）
    
    管理者または責任者のみが実行可能です。
    物理削除ではなく、is_activeをFalseに設定する論理削除を行います。
    """
    try:
        result = await industry_management_service.delete_industry_benchmark(
            db, current_user, benchmark_id
        )

        logger.info(
            "業界ベンチマークを削除",
            user_id=current_user.id,
            benchmark_id=benchmark_id
        )

        return {"message": "業界ベンチマークを削除しました", "benchmark_id": benchmark_id}

    except NotFoundException as e:
        logger.warning(f"業界ベンチマーク削除で見つからない: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionException as e:
        logger.warning(f"業界ベンチマーク削除で権限エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"業界ベンチマーク削除でエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="業界ベンチマークの削除に失敗しました"
        )


@router.post("/requests", response_model=IndustryBenchmarkRequestResponse)
async def create_benchmark_request(
    request_data: IndustryBenchmarkRequestCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    業界ベンチマーク追加リクエストを作成
    
    一般ユーザーが新しい業界ベンチマークの追加をリクエストします。
    管理者・責任者がレビュー後に承認・却下を決定します。
    """
    try:
        result = await industry_management_service.create_benchmark_request(
            db, current_user, request_data
        )

        logger.info(
            "業界ベンチマーク追加リクエストを作成",
            user_id=current_user.id,
            request_id=result.id,
            industry_code=result.industry_code
        )

        return result

    except DuplicateException as e:
        logger.warning(f"業界ベンチマーク追加リクエスト作成で重複エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"業界ベンチマーク追加リクエスト作成でエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="業界ベンチマーク追加リクエストの作成に失敗しました"
        )


@router.get("/requests", response_model=Tuple[List[IndustryBenchmarkRequestResponse], int])
async def get_benchmark_requests(
    skip: int = Query(0, ge=0, description="スキップ件数"),
    limit: int = Query(100, ge=1, le=1000, description="取得件数"),
    status: Optional[RequestStatus] = Query(None, description="ステータスフィルター"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    業界ベンチマーク追加リクエスト一覧を取得
    
    管理者・責任者は全リクエストを閲覧可能です。
    一般ユーザーは自分のリクエストのみ閲覧可能です。
    """
    try:
        result = await industry_management_service.get_benchmark_requests(
            db, current_user, status, skip, limit
        )

        logger.info(
            "業界ベンチマーク追加リクエスト一覧を取得",
            user_id=current_user.id,
            skip=skip,
            limit=limit,
            total_count=result[1]
        )

        return result

    except Exception as e:
        logger.error(f"業界ベンチマーク追加リクエスト一覧取得でエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="業界ベンチマーク追加リクエスト一覧の取得に失敗しました"
        )


@router.put("/requests/{request_id}", response_model=IndustryBenchmarkRequestResponse)
async def review_benchmark_request(
    request_id: int,
    review_data: IndustryBenchmarkRequestUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    業界ベンチマーク追加リクエストをレビュー
    
    管理者または責任者のみが実行可能です。
    リクエストの承認・却下を決定します。
    承認された場合、自動的にベンチマークが作成されます。
    """
    try:
        result = await industry_management_service.review_benchmark_request(
            db, current_user, request_id, review_data
        )

        logger.info(
            "業界ベンチマーク追加リクエストをレビュー",
            user_id=current_user.id,
            request_id=request_id,
            status=review_data.status
        )

        return result

    except NotFoundException as e:
        logger.warning(f"業界ベンチマーク追加リクエストレビューで見つからない: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionException as e:
        logger.warning(f"業界ベンチマーク追加リクエストレビューで権限エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"業界ベンチマーク追加リクエストレビューでエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="業界ベンチマーク追加リクエストのレビューに失敗しました"
        )


@router.get("/stats", response_model=IndustryBenchmarkStats)
async def get_benchmark_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    業界ベンチマーク統計情報を取得
    
    管理者または責任者のみが実行可能です。
    ベンチマーク数、リクエスト数、データ品質などの統計情報を提供します。
    """
    try:
        result = await industry_management_service.get_benchmark_stats(db, current_user)

        logger.info(
            "業界ベンチマーク統計情報を取得",
            user_id=current_user.id
        )

        return result

    except PermissionException as e:
        logger.warning(f"業界ベンチマーク統計情報取得で権限エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"業界ベンチマーク統計情報取得でエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="業界ベンチマーク統計情報の取得に失敗しました"
        )


@router.get("/available-industries")
async def get_available_industries(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    利用可能な業界一覧を取得
    
    データベースに登録されている業界の一覧を取得します。
    """
    try:
        # 業界名の一覧を取得
        result = await industry_management_service.get_industry_benchmarks(
            db, current_user, None, 0, 1000
        )
        
        # 業界名を重複なく抽出
        industries = list(set(benchmark.industry_name for benchmark in result[0]))
        industries.sort()

        return {
            "industries": industries,
            "total_count": len(industries)
        }

    except Exception as e:
        logger.error(f"利用可能な業界一覧取得でエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="利用可能な業界一覧の取得に失敗しました"
        )


@router.get("/available-company-sizes")
async def get_available_company_sizes():
    """
    利用可能な企業規模一覧を取得
    
    システムで定義されている企業規模の一覧を取得します。
    """
    company_sizes = [
        {
            "value": CompanySize.STARTUP,
            "display_name": "スタートアップ",
            "description": "従業員50名未満、設立5年未満"
        },
        {
            "value": CompanySize.MEDIUM,
            "display_name": "中堅企業",
            "description": "従業員50-1000名、設立5-20年"
        },
        {
            "value": CompanySize.LARGE,
            "display_name": "大企業",
            "description": "従業員1000名以上、設立20年以上"
        }
    ]

    return {
        "company_sizes": company_sizes,
        "total_count": len(company_sizes)
    }
