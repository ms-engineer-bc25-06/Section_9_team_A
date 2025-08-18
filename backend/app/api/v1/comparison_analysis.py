from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from typing import List, Optional, Dict, Any

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.schemas.comparison_analysis import (
    ComparisonRequest, ComparisonResult, ComparisonAnalytics,
    ComparisonPrivacySettings, ComparisonFilters, ComparisonType, ComparisonScope
)
from app.services.comparison_analysis_service import comparison_analysis_service
from app.core.exceptions import (
    NotFoundException, PermissionException, ValidationException,
    BusinessLogicException
)

router = APIRouter()
logger = structlog.get_logger()


@router.post("/analyze", response_model=ComparisonResult)
async def perform_comparison_analysis(
    comparison_request: ComparisonRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    比較分析を実行（心理的安全性を保つ）
    
    このエンドポイントは、個人の特定を避け、建設的な成長提案に焦点を当てた
    比較分析を実行します。順位付けは行わず、相対的な強み・学習機会として
    結果を提供します。
    """
    try:
        # 心理的安全性の確認
        if not await _validate_psychological_safety(db, current_user, comparison_request):
            raise PermissionException(
                "心理的安全性を保つため、この比較分析は実行できません"
            )

        # 比較分析の実行
        result = await comparison_analysis_service.perform_comparison_analysis(
            db, current_user, comparison_request
        )

        logger.info(
            "比較分析を実行",
            user_id=current_user.id,
            comparison_type=comparison_request.comparison_type,
            comparison_scope=comparison_request.comparison_scope
        )

        return result

    except (ValidationException, PermissionException, BusinessLogicException) as e:
        logger.warning(f"比較分析の実行で検証エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"比較分析の実行で予期しないエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="比較分析の実行に失敗しました"
        )


@router.get("/self-improvement", response_model=ComparisonResult)
async def get_self_improvement_analysis(
    time_period: str = Query("30d", description="比較対象期間（7d, 30d, 90d, 1y）"),
    scope: ComparisonScope = Query(ComparisonScope.OVERALL_PERFORMANCE, description="比較対象の範囲"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    自己改善分析を取得（過去の自分との比較）
    
    このエンドポイントは、ユーザーの過去のパフォーマンスと現在の
    パフォーマンスを比較し、成長の可視化と改善提案を提供します。
    他者との比較は行わず、純粋に自己成長に焦点を当てています。
    """
    try:
        # 自己改善分析のリクエストを作成
        comparison_request = ComparisonRequest(
            comparison_type=ComparisonType.SELF_IMPROVEMENT,
            comparison_scope=scope,
            time_period=time_period,
            include_self=True,
            anonymization_level="high",
            focus_on_strengths=True,
            include_growth_suggestions=True,
            exclude_ranking=True
        )

        # 比較分析の実行
        result = await comparison_analysis_service.perform_comparison_analysis(
            db, current_user, comparison_request
        )

        logger.info(
            "自己改善分析を取得",
            user_id=current_user.id,
            time_period=time_period,
            scope=scope
        )

        return result

    except Exception as e:
        logger.error(f"自己改善分析の取得でエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="自己改善分析の取得に失敗しました"
        )


@router.get("/anonymous-peer", response_model=ComparisonResult)
async def get_anonymous_peer_comparison(
    time_period: str = Query("30d", description="比較対象期間"),
    scope: ComparisonScope = Query(ComparisonScope.OVERALL_PERFORMANCE, description="比較対象の範囲"),
    min_group_size: int = Query(5, ge=5, description="最小グループサイズ（個人の特定を避けるため）"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    匿名化された同僚比較分析を取得
    
    このエンドポイントは、同僚との比較分析を提供しますが、
    個人の特定を避けるため、以下の安全策を講じています：
    
    1. 最小グループサイズ5名以上で比較
    2. 個人名は表示されない
    3. 順位付けは行わない
    4. 統計的な集約データのみを提供
    5. 建設的な改善提案に焦点
    """
    try:
        # プライバシー設定の確認
        privacy_settings = await _get_user_privacy_settings(db, current_user.id)
        if not privacy_settings.allow_anonymous_comparison:
            raise PermissionException("匿名比較分析が許可されていません")

        # 匿名同僚比較分析のリクエストを作成
        comparison_request = ComparisonRequest(
            comparison_type=ComparisonType.ANONYMOUS_PEER,
            comparison_scope=scope,
            time_period=time_period,
            include_self=True,
            anonymization_level="high",
            focus_on_strengths=True,
            include_growth_suggestions=True,
            exclude_ranking=True
        )

        # 比較分析の実行
        result = await comparison_analysis_service.perform_comparison_analysis(
            db, current_user, comparison_request
        )

        logger.info(
            "匿名同僚比較分析を取得",
            user_id=current_user.id,
            time_period=time_period,
            scope=scope
        )

        return result

    except PermissionException as e:
        logger.warning(f"匿名同僚比較分析で権限エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"匿名同僚比較分析の取得でエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="匿名同僚比較分析の取得に失敗しました"
        )


@router.get("/team-comparison", response_model=ComparisonResult)
async def get_team_comparison_analysis(
    time_period: str = Query("30d", description="比較対象期間"),
    scope: ComparisonScope = Query(ComparisonScope.OVERALL_PERFORMANCE, description="比較対象の範囲"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    チーム比較分析を取得
    
    このエンドポイントは、チーム全体との比較分析を提供します。
    個人の特定を避け、チーム全体の強み・改善領域と個人の貢献
    可能性に焦点を当てています。
    """
    try:
        # プライバシー設定の確認
        privacy_settings = await _get_user_privacy_settings(db, current_user.id)
        if not privacy_settings.allow_team_comparison:
            raise PermissionException("チーム比較分析が許可されていません")

        # チーム比較分析のリクエストを作成
        comparison_request = ComparisonRequest(
            comparison_type=ComparisonType.TEAM_AGGREGATE,
            comparison_scope=scope,
            time_period=time_period,
            include_self=True,
            anonymization_level="high",
            focus_on_strengths=True,
            include_growth_suggestions=True,
            exclude_ranking=True
        )

        # 比較分析の実行
        result = await comparison_analysis_service.perform_comparison_analysis(
            db, current_user, comparison_request
        )

        logger.info(
            "チーム比較分析を取得",
            user_id=current_user.id,
            time_period=time_period,
            scope=scope
        )

        return result

    except PermissionException as e:
        logger.warning(f"チーム比較分析で権限エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"チーム比較分析の取得でエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="チーム比較分析の取得に失敗しました"
        )


@router.get("/organization-benchmark", response_model=ComparisonResult)
async def get_organization_benchmark_analysis(
    time_period: str = Query("30d", description="比較対象期間"),
    scope: ComparisonScope = Query(ComparisonScope.OVERALL_PERFORMANCE, description="比較対象の範囲"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    組織ベンチマーク比較分析を取得
    
    このエンドポイントは、組織全体のベンチマークとの比較分析を提供します。
    個人の特定を避け、組織全体のベストプラクティスと個人の成長機会に
    焦点を当てています。
    """
    try:
        # 組織ベンチマーク比較分析のリクエストを作成
        comparison_request = ComparisonRequest(
            comparison_type=ComparisonType.ORGANIZATION_BENCHMARK,
            comparison_scope=scope,
            time_period=time_period,
            include_self=True,
            anonymization_level="high",
            focus_on_strengths=True,
            include_growth_suggestions=True,
            exclude_ranking=True
        )

        # 比較分析の実行
        result = await comparison_analysis_service.perform_comparison_analysis(
            db, current_user, comparison_request
        )

        logger.info(
            "組織ベンチマーク比較分析を取得",
            user_id=current_user.id,
            time_period=time_period,
            scope=scope
        )

        return result

    except Exception as e:
        logger.error(f"組織ベンチマーク比較分析の取得でエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="組織ベンチマーク比較分析の取得に失敗しました"
        )


@router.get("/analytics", response_model=ComparisonAnalytics)
async def get_comparison_analytics(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    比較分析の統計情報を取得
    
    このエンドポイントは、比較分析の使用状況と心理的安全性の指標を提供します。
    ユーザーの参加率、満足度、安全性スコアなどの情報を含みます。
    """
    try:
        # 比較分析の統計情報を取得
        analytics = await _calculate_comparison_analytics(db, current_user.id)

        logger.info(
            "比較分析統計情報を取得",
            user_id=current_user.id
        )

        return analytics

    except Exception as e:
        logger.error(f"比較分析統計情報の取得でエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="比較分析統計情報の取得に失敗しました"
        )


@router.get("/privacy-settings", response_model=ComparisonPrivacySettings)
async def get_privacy_settings(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    比較分析のプライバシー設定を取得
    
    このエンドポイントは、ユーザーの比較分析に関するプライバシー設定を
    取得します。比較への参加可否、データの可視性レベルなどの設定を
    含みます。
    """
    try:
        # プライバシー設定を取得
        privacy_settings = await _get_user_privacy_settings(db, current_user.id)

        logger.info(
            "比較分析プライバシー設定を取得",
            user_id=current_user.id
        )

        return privacy_settings

    except Exception as e:
        logger.error(f"プライバシー設定の取得でエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="プライバシー設定の取得に失敗しました"
        )


@router.put("/privacy-settings", response_model=ComparisonPrivacySettings)
async def update_privacy_settings(
    privacy_settings: ComparisonPrivacySettings,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    比較分析のプライバシー設定を更新
    
    このエンドポイントは、ユーザーの比較分析に関するプライバシー設定を
    更新します。設定の変更は即座に反映され、今後の比較分析に適用されます。
    """
    try:
        # プライバシー設定を更新
        updated_settings = await _update_user_privacy_settings(
            db, current_user.id, privacy_settings
        )

        logger.info(
            "比較分析プライバシー設定を更新",
            user_id=current_user.id,
            settings=privacy_settings.dict()
        )

        return updated_settings

    except Exception as e:
        logger.error(f"プライバシー設定の更新でエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="プライバシー設定の更新に失敗しました"
        )


@router.get("/available-scopes", response_model=List[str])
async def get_available_comparison_scopes():
    """
    利用可能な比較対象範囲を取得
    
    このエンドポイントは、比較分析で利用可能なスコープの一覧を提供します。
    各スコープの説明も含まれています。
    """
    scopes = [
        "communication_skills - コミュニケーションスキル",
        "leadership - リーダーシップ",
        "collaboration - 協働性",
        "problem_solving - 問題解決",
        "emotional_intelligence - 感情知性",
        "overall_performance - 総合的なパフォーマンス"
    ]
    
    return scopes


@router.get("/safety-guidelines")
async def get_safety_guidelines():
    """
    心理的安全性のガイドラインを取得
    
    このエンドポイントは、比較分析における心理的安全性を保つための
    ガイドラインを提供します。ユーザーが安心して比較分析を利用できる
    よう、安全な使用方法を説明しています。
    """
    guidelines = {
        "心理的安全性の保証": [
            "個人の特定は行いません",
            "順位付けは提供しません",
            "建設的な改善提案に焦点を当てます",
            "匿名化された集約データのみを扱います"
        ],
        "比較分析の目的": [
            "自己成長と改善の促進",
            "チーム全体の能力向上",
            "組織全体の学習・改善",
            "評価・査定のためではありません"
        ],
        "安全な利用方法": [
            "比較結果は成長機会として捉える",
            "他者との比較ではなく、自己改善に活用する",
            "必要に応じてプライバシー設定を調整する",
            "不安を感じた場合はサポートに相談する"
        ],
        "データ保護": [
            "最小グループサイズ5名以上で比較",
            "個人データは集約して提供",
            "プライバシー設定で可視性を制御",
            "比較への参加は任意"
        ]
    }
    
    return guidelines


# プライベート関数（心理的安全性を保つための実装）

async def _validate_psychological_safety(
    db: AsyncSession, user: User, comparison_request: ComparisonRequest
) -> bool:
    """心理的安全性の検証"""
    try:
        # プライバシー設定の確認
        privacy_settings = await _get_user_privacy_settings(db, user.id)
        
        # 比較タイプに応じた権限チェック
        if comparison_request.comparison_type == ComparisonType.ANONYMOUS_PEER:
            if not privacy_settings.allow_anonymous_comparison:
                return False
        elif comparison_request.comparison_type == ComparisonType.TEAM_AGGREGATE:
            if not privacy_settings.allow_team_comparison:
                return False
        
        # 最小グループサイズの確認
        if comparison_request.comparison_type in [
            ComparisonType.ANONYMOUS_PEER,
            ComparisonType.TEAM_AGGREGATE
        ]:
            if comparison_request.min_group_size < 5:
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"心理的安全性の検証でエラー: {e}")
        return False


async def _get_user_privacy_settings(
    db: AsyncSession, user_id: int
) -> ComparisonPrivacySettings:
    """ユーザーのプライバシー設定を取得"""
    # TODO: プライバシー設定テーブルから取得
    # 現在はデフォルト設定を返す
    return ComparisonPrivacySettings(
        user_id=user_id,
        participate_in_comparisons=True,
        allow_anonymous_comparison=True,
        allow_team_comparison=True,
        data_visibility_level="aggregated",
        include_in_benchmarks=True,
        notify_comparison_results=True,
        notify_improvement_suggestions=True
    )


async def _update_user_privacy_settings(
    db: AsyncSession, user_id: int, privacy_settings: ComparisonPrivacySettings
) -> ComparisonPrivacySettings:
    """ユーザーのプライバシー設定を更新"""
    # TODO: プライバシー設定テーブルに保存
    # 現在は受け取った設定をそのまま返す
    privacy_settings.user_id = user_id
    return privacy_settings


async def _calculate_comparison_analytics(
    db: AsyncSession, user_id: int
) -> ComparisonAnalytics:
    """比較分析の統計情報を計算"""
    # TODO: 実際の統計情報を計算
    # 現在はサンプルデータを返す
    
    return ComparisonAnalytics(
        total_comparisons=10,
        user_participation_rate=0.8,
        average_confidence=0.85,
        safety_score=0.9,
        user_feedback_rating=0.85,
        improvement_adoption_rate=0.7,
        user_satisfaction=0.8
    )
