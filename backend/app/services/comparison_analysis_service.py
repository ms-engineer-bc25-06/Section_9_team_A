import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, text
from sqlalchemy.orm import selectinload

from app.models.analysis import Analysis
from app.models.user import User
from app.models.team_member import TeamMember
from app.models.team import Team
from app.schemas.comparison_analysis import (
    ComparisonRequest, ComparisonResult, SelfComparisonResult,
    AnonymousPeerComparison, TeamComparisonResult, ComparisonFilters,
    ComparisonAnalytics, ComparisonPrivacySettings, ComparisonType, ComparisonScope,
    TeamToTeamComparison, IndustryBenchmarkComparison, ComparisonReport
)
from app.core.exceptions import (
    NotFoundException, PermissionException, ValidationException,
    BusinessLogicException
)

logger = structlog.get_logger()


class ComparisonAnalysisService:
    """比較分析サービス（心理的安全性を保つ設計）"""

    def __init__(self):
        pass

    async def perform_comparison_analysis(
        self,
        db: AsyncSession,
        user: User,
        comparison_request: ComparisonRequest
    ) -> ComparisonResult:
        """比較分析を実行（心理的安全性を保つ）"""
        try:
            # プライバシー設定の確認
            privacy_settings = await self._get_user_privacy_settings(db, user.id)
            if not privacy_settings.participate_in_comparisons:
                raise PermissionException("比較分析への参加が許可されていません")

            # 比較タイプに応じた分析を実行
            if comparison_request.comparison_type == ComparisonType.SELF_IMPROVEMENT:
                return await self._perform_self_comparison(db, user, comparison_request)
            elif comparison_request.comparison_type == ComparisonType.ANONYMOUS_PEER:
                return await self._perform_anonymous_peer_comparison(db, user, comparison_request)
            elif comparison_request.comparison_type == ComparisonType.TEAM_AGGREGATE:
                return await self._perform_team_comparison(db, user, comparison_request)
            elif comparison_request.comparison_type == ComparisonType.ORGANIZATION_BENCHMARK:
                return await self._perform_organization_benchmark(db, user, comparison_request)
            else:
                raise ValidationException("サポートされていない比較タイプです")

        except Exception as e:
            logger.error(f"比較分析の実行に失敗: {e}")
            raise

    async def _perform_self_comparison(
        self,
        db: AsyncSession,
        user: User,
        comparison_request: ComparisonRequest
    ) -> ComparisonResult:
        """自己比較分析（過去の自分との比較）"""
        try:
            # 期間の計算
            current_period, previous_period = self._calculate_comparison_periods(
                comparison_request.time_period
            )

            # 現在期間の分析結果を取得
            current_analyses = await self._get_user_analyses_in_period(
                db, user.id, current_period
            )

            # 過去期間の分析結果を取得
            previous_analyses = await self._get_user_analyses_in_period(
                db, user.id, previous_period
            )

            # 成長メトリクスの計算
            growth_metrics = self._calculate_growth_metrics(
                current_analyses, previous_analyses, comparison_request.comparison_scope
            )

            # 強み・成長領域の特定
            strength_areas, growth_areas = self._identify_strength_and_growth_areas(
                growth_metrics
            )

            # 建設的な提案の生成
            improvement_suggestions = self._generate_improvement_suggestions(
                growth_metrics, growth_areas
            )

            # ベストプラクティスの提案
            best_practices = self._generate_best_practices(
                current_analyses, comparison_request.comparison_scope
            )

            return ComparisonResult(
                comparison_id=str(uuid.uuid4()),
                comparison_type=ComparisonType.SELF_IMPROVEMENT,
                comparison_scope=comparison_request.comparison_scope,
                generated_at=datetime.utcnow(),
                total_participants=1,  # 自己比較なので1
                confidence_level=self._calculate_confidence_level(current_analyses),
                performance_distribution=growth_metrics,
                strength_areas=strength_areas,
                growth_areas=growth_areas,
                improvement_suggestions=improvement_suggestions,
                best_practices=best_practices,
                is_anonymous=True,
                no_individual_ranking=True
            )

        except Exception as e:
            logger.error(f"自己比較分析に失敗: {e}")
            raise

    async def _perform_anonymous_peer_comparison(
        self,
        db: AsyncSession,
        user: User,
        comparison_request: ComparisonRequest
    ) -> ComparisonResult:
        """匿名化された同僚比較分析"""
        try:
            # 同僚の集約データを取得（個人の特定を避ける）
            peer_data = await self._get_aggregated_peer_data(
                db, user, comparison_request
            )

            # 最小グループサイズの確認
            if peer_data["total_count"] < comparison_request.min_group_size:
                raise BusinessLogicException(
                    f"比較対象が少なすぎます（最小{comparison_request.min_group_size}名必要）"
                )

            # ユーザーの分析結果を取得
            user_analyses = await self._get_user_analyses_in_period(
                db, user.id, comparison_request.time_period
            )

            # 相対的な強み・学習機会の特定
            relative_strengths, learning_opportunities = self._identify_relative_position(
                user_analyses, peer_data, comparison_request.comparison_scope
            )

            # パフォーマンス分布の計算（匿名化）
            performance_distribution = self._calculate_anonymous_performance_distribution(
                peer_data, user_analyses
            )

            # 建設的な提案の生成
            improvement_suggestions = self._generate_peer_based_suggestions(
                relative_strengths, learning_opportunities
            )

            return ComparisonResult(
                comparison_id=str(uuid.uuid4()),
                comparison_type=ComparisonType.ANONYMOUS_PEER,
                comparison_scope=comparison_request.comparison_scope,
                generated_at=datetime.utcnow(),
                total_participants=peer_data["total_count"],
                confidence_level=self._calculate_confidence_level(user_analyses),
                performance_distribution=performance_distribution,
                strength_areas=relative_strengths,
                growth_areas=learning_opportunities,
                improvement_suggestions=improvement_suggestions,
                best_practices=self._extract_best_practices_from_peers(peer_data),
                is_anonymous=True,
                no_individual_ranking=True
            )

        except Exception as e:
            logger.error(f"匿名同僚比較分析に失敗: {e}")
            raise

    async def _perform_team_comparison(
        self,
        db: AsyncSession,
        user: User,
        comparison_request: ComparisonRequest
    ) -> ComparisonResult:
        """チーム比較分析"""
        try:
            # ユーザーのチーム情報を取得
            team_membership = await self._get_user_team_membership(db, user.id)
            if not team_membership:
                raise BusinessLogicException("チームに所属していません")

            # チーム全体の集約データを取得
            team_data = await self._get_team_aggregated_data(
                db, team_membership.team_id, comparison_request
            )

            # 個人の位置づけを計算（匿名化）
            individual_position = self._calculate_individual_position(
                user.id, team_data, comparison_request.comparison_scope
            )

            # チームの強み・改善領域の特定
            team_strengths, team_improvement_areas = self._identify_team_areas(
                team_data
            )

            # 個人の貢献領域の特定
            contribution_areas = self._identify_contribution_areas(
                individual_position, team_improvement_areas
            )

            # 建設的な提案の生成
            improvement_suggestions = self._generate_team_based_suggestions(
                team_improvement_areas, contribution_areas
            )

            return ComparisonResult(
                comparison_id=str(uuid.uuid4()),
                comparison_type=ComparisonType.TEAM_AGGREGATE,
                comparison_scope=comparison_request.comparison_scope,
                generated_at=datetime.utcnow(),
                total_participants=team_data["member_count"],
                confidence_level=self._calculate_team_confidence_level(team_data),
                performance_distribution=team_data["performance_metrics"],
                strength_areas=team_strengths,
                growth_areas=team_improvement_areas,
                improvement_suggestions=improvement_suggestions,
                best_practices=self._extract_team_best_practices(team_data),
                is_anonymous=True,
                no_individual_ranking=True
            )

        except Exception as e:
            logger.error(f"チーム比較分析に失敗: {e}")
            raise

    async def _perform_organization_benchmark(
        self,
        db: AsyncSession,
        user: User,
        comparison_request: ComparisonRequest
    ) -> ComparisonResult:
        """組織ベンチマーク比較分析"""
        try:
            # 組織全体の集約データを取得
            org_data = await self._get_organization_benchmark_data(
                db, comparison_request
            )

            # ユーザーの分析結果を取得
            user_analyses = await self._get_user_analyses_in_period(
                db, user.id, comparison_request.time_period
            )

            # 組織ベンチマークとの比較
            benchmark_comparison = self._compare_with_benchmark(
                user_analyses, org_data, comparison_request.comparison_scope
            )

            # 建設的な提案の生成
            improvement_suggestions = self._generate_benchmark_based_suggestions(
                benchmark_comparison
            )

            return ComparisonResult(
                comparison_id=str(uuid.uuid4()),
                comparison_type=ComparisonType.ORGANIZATION_BENCHMARK,
                comparison_scope=comparison_request.comparison_scope,
                generated_at=datetime.utcnow(),
                total_participants=org_data["total_participants"],
                confidence_level=self._calculate_confidence_level(user_analyses),
                performance_distribution=benchmark_comparison["performance_metrics"],
                strength_areas=benchmark_comparison["strengths"],
                growth_areas=benchmark_comparison["growth_areas"],
                improvement_suggestions=improvement_suggestions,
                best_practices=org_data["best_practices"],
                is_anonymous=True,
                no_individual_ranking=True
            )

        except Exception as e:
            logger.error(f"組織ベンチマーク比較分析に失敗: {e}")
            raise

    # 新機能のメソッド

    async def perform_team_to_team_comparison(
        self,
        db: AsyncSession,
        user: User,
        source_team_id: int,
        target_team_id: int,
        comparison_scope: ComparisonScope
    ) -> TeamToTeamComparison:
        """チーム間比較分析を実行"""
        try:
            # ユーザーの権限確認（両チームのメンバーである必要がある）
            if not await self._validate_team_membership(db, user.id, [source_team_id, target_team_id]):
                raise PermissionException("両チームのメンバーである必要があります")

            # 両チームの集約データを取得
            source_team_data = await self._get_team_aggregated_data(db, source_team_id, None)
            target_team_data = await self._get_team_aggregated_data(db, target_team_id, None)

            # チーム間の相対的な比較を実行
            relative_performance = self._compare_teams_relative(
                source_team_data, target_team_data, comparison_scope
            )

            # 共通の強みと補完領域を特定
            shared_strengths, complementary_areas = self._identify_team_synergies(
                source_team_data, target_team_data
            )

            # 学習機会と協働可能性を特定
            learning_opportunities, collaboration_potential = self._identify_collaboration_opportunities(
                source_team_data, target_team_data, comparison_scope
            )

            return TeamToTeamComparison(
                comparison_id=str(uuid.uuid4()),
                source_team_id=str(source_team_id),
                target_team_id=str(target_team_id),
                relative_performance=relative_performance,
                shared_strengths=shared_strengths,
                complementary_areas=complementary_areas,
                learning_opportunities=learning_opportunities,
                collaboration_potential=collaboration_potential
            )

        except Exception as e:
            logger.error(f"チーム間比較分析に失敗: {e}")
            raise

    async def perform_industry_benchmark_comparison(
        self,
        db: AsyncSession,
        user: User,
        industry: str,
        company_size: str,
        comparison_scope: ComparisonScope
    ) -> IndustryBenchmarkComparison:
        """業界平均比較分析を実行"""
        try:
            # 業界ベンチマークデータを取得
            industry_data = await self._get_industry_benchmark_data(
                db, industry, company_size, comparison_scope
            )

            # ユーザーの分析結果を取得
            user_analyses = await self._get_user_analyses_in_period(
                db, user.id, "30d"  # 最近30日間
            )

            # 業界平均との比較
            relative_position = self._compare_with_industry_benchmark(
                user_analyses, industry_data, comparison_scope
            )

            # 改善機会を特定
            improvement_opportunities = self._identify_industry_improvement_opportunities(
                relative_position, industry_data
            )

            return IndustryBenchmarkComparison(
                comparison_id=str(uuid.uuid4()),
                industry=industry,
                company_size=company_size,
                industry_average=industry_data["metrics"],
                relative_position=relative_position,
                industry_best_practices=industry_data["best_practices"],
                improvement_opportunities=improvement_opportunities,
                data_source=industry_data["data_source"],
                last_updated=industry_data["last_updated"],
                confidence_level=industry_data["confidence_level"]
            )

        except Exception as e:
            logger.error(f"業界平均比較分析に失敗: {e}")
            raise

    async def generate_comparison_report(
        self,
        db: AsyncSession,
        user: User,
        comparison_id: str,
        report_format: str = "pdf",
        include_charts: bool = True,
        include_recommendations: bool = True
    ) -> ComparisonReport:
        """比較分析レポートを生成"""
        try:
            # 比較分析結果を取得
            comparison_result = await self._get_comparison_result(db, comparison_id)
            if not comparison_result:
                raise NotFoundException("比較分析結果が見つかりません")

            # レポートの内容を生成
            title, summary = self._generate_report_title_and_summary(comparison_result)
            key_findings = self._extract_key_findings(comparison_result)
            detailed_analysis = self._create_detailed_analysis(comparison_result)
            visualizations = self._create_visualizations(comparison_result) if include_charts else []
            action_items, next_steps = self._generate_action_plan(comparison_result) if include_recommendations else ([], [])

            return ComparisonReport(
                report_id=str(uuid.uuid4()),
                comparison_id=comparison_id,
                generated_at=datetime.utcnow(),
                title=title,
                summary=summary,
                key_findings=key_findings,
                detailed_analysis=detailed_analysis,
                visualizations=visualizations,
                action_items=action_items,
                next_steps=next_steps,
                report_format=report_format,
                include_charts=include_charts,
                include_recommendations=include_recommendations
            )

        except Exception as e:
            logger.error(f"レポート生成に失敗: {e}")
            raise

    # プライベートメソッド（心理的安全性を保つための実装）

    async def _get_user_privacy_settings(
        self, db: AsyncSession, user_id: int
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

    def _calculate_comparison_periods(self, time_period: str) -> Tuple[str, str]:
        """比較期間を計算"""
        now = datetime.utcnow()
        
        if time_period == "7d":
            current_start = now - timedelta(days=7)
            previous_start = now - timedelta(days=14)
            previous_end = now - timedelta(days=7)
        elif time_period == "30d":
            current_start = now - timedelta(days=30)
            previous_start = now - timedelta(days=60)
            previous_end = now - timedelta(days=30)
        elif time_period == "90d":
            current_start = now - timedelta(days=90)
            previous_start = now - timedelta(days=180)
            previous_end = now - timedelta(days=90)
        elif time_period == "1y":
            current_start = now - timedelta(days=365)
            previous_start = now - timedelta(days=730)
            previous_end = now - timedelta(days=365)
        else:
            raise ValidationException("サポートされていない期間です")

        return current_start.isoformat(), previous_end.isoformat()

    async def _get_user_analyses_in_period(
        self, db: AsyncSession, user_id: int, period_start: str
    ) -> List[Analysis]:
        """指定期間内のユーザー分析結果を取得"""
        result = await db.execute(
            select(Analysis).where(
                and_(
                    Analysis.user_id == user_id,
                    Analysis.created_at >= period_start,
                    Analysis.status == "completed"
                )
            )
        )
        return result.scalars().all()

    def _calculate_growth_metrics(
        self,
        current_analyses: List[Analysis],
        previous_analyses: List[Analysis],
        scope: ComparisonScope
    ) -> Dict[str, float]:
        """成長メトリクスを計算"""
        # スコープに応じたメトリクスを計算
        metrics = {}
        
        if scope == ComparisonScope.COMMUNICATION_SKILLS:
            metrics = self._calculate_communication_metrics(
                current_analyses, previous_analyses
            )
        elif scope == ComparisonScope.LEADERSHIP:
            metrics = self._calculate_leadership_metrics(
                current_analyses, previous_analyses
            )
        # 他のスコープも同様に実装
        
        return metrics

    def _identify_strength_and_growth_areas(
        self, growth_metrics: Dict[str, float]
    ) -> Tuple[List[str], List[str]]:
        """強みと成長領域を特定"""
        strengths = []
        growth_areas = []
        
        for metric, value in growth_metrics.items():
            if value > 0.1:  # 10%以上の成長
                strengths.append(f"{metric}の改善")
            elif value < -0.05:  # 5%以上の低下
                growth_areas.append(f"{metric}の強化")
        
        return strengths, growth_areas

    def _generate_improvement_suggestions(
        self, growth_metrics: Dict[str, float], growth_areas: List[str]
    ) -> List[str]:
        """改善提案を生成（建設的で具体的）"""
        suggestions = []
        
        for area in growth_areas:
            if "コミュニケーション" in area:
                suggestions.append("より多くの質問を投げかけて、相手の理解を深める")
            elif "リーダーシップ" in area:
                suggestions.append("チームメンバーの意見を積極的に引き出す")
            elif "協働性" in area:
                suggestions.append("他者の提案に対して建設的なフィードバックを提供する")
        
        return suggestions

    def _calculate_confidence_level(self, analyses: List[Analysis]) -> float:
        """分析の信頼度を計算"""
        if not analyses:
            return 0.0
        
        # 分析結果の品質とデータ量に基づいて信頼度を計算
        total_confidence = sum(
            analysis.confidence_score or 0.0 for analysis in analyses
        )
        return min(total_confidence / len(analyses), 1.0)

    async def _get_aggregated_peer_data(
        self, db: AsyncSession, user: User, comparison_request: ComparisonRequest
    ) -> Dict[str, Any]:
        """同僚の集約データを取得（個人の特定を避ける）"""
        # 同僚の分析結果を集約して取得
        # 個人の特定を避けるため、統計的な情報のみを返す
        
        # 例：部署・経験レベルが近い同僚の集約データ
        result = await db.execute(
            select(
                func.avg(Analysis.confidence_score).label("avg_confidence"),
                func.count(Analysis.id).label("total_count")
            ).where(
                and_(
                    Analysis.user_id != user.id,
                    Analysis.status == "completed",
                    Analysis.created_at >= comparison_request.time_period
                )
            )
        )
        
        row = result.first()
        return {
            "avg_confidence": row.avg_confidence or 0.0,
            "total_count": row.total_count or 0
        }

    def _identify_relative_position(
        self,
        user_analyses: List[Analysis],
        peer_data: Dict[str, Any],
        scope: ComparisonScope
    ) -> Tuple[List[str], List[str]]:
        """相対的な位置づけを特定（順位は表示しない）"""
        # 順位ではなく、相対的な強み・学習機会として表現
        
        relative_strengths = []
        learning_opportunities = []
        
        # ユーザーの分析結果を評価
        user_score = self._calculate_user_score(user_analyses, scope)
        peer_avg = peer_data.get("avg_confidence", 0.0)
        
        if user_score > peer_avg * 1.1:  # 10%以上上回る
            relative_strengths.append("同僚と比較して高いパフォーマンス")
        elif user_score < peer_avg * 0.9:  # 10%以上下回る
            learning_opportunities.append("同僚の良い点を参考にした改善")
        
        return relative_strengths, learning_opportunities

    def _calculate_user_score(
        self, analyses: List[Analysis], scope: ComparisonScope
    ) -> float:
        """ユーザーのスコアを計算"""
        if not analyses:
            return 0.0
        
        # スコープに応じたスコア計算
        total_score = 0.0
        for analysis in analyses:
            if scope == ComparisonScope.COMMUNICATION_SKILLS:
                # コミュニケーションスキルのスコア計算
                score = analysis.confidence_score or 0.0
                total_score += score
        
        return total_score / len(analyses) if analyses else 0.0

    async def _get_user_team_membership(
        self, db: AsyncSession, user_id: int
    ) -> Optional[TeamMember]:
        """ユーザーのチーム所属情報を取得"""
        result = await db.execute(
            select(TeamMember).where(
                and_(
                    TeamMember.user_id == user_id,
                    TeamMember.status == "active"
                )
            )
        )
        return result.scalar_one_or_none()

    async def _get_team_aggregated_data(
        self, db: AsyncSession, team_id: int, comparison_request: ComparisonRequest
    ) -> Dict[str, Any]:
        """チームの集約データを取得"""
        # チーム全体の統計情報を取得
        # 個人の特定を避けるため、集約されたデータのみを返す
        
        result = await db.execute(
            select(
                func.count(Analysis.id).label("total_analyses"),
                func.avg(Analysis.confidence_score).label("avg_confidence")
            ).join(TeamMember, Analysis.user_id == TeamMember.user_id).where(
                and_(
                    TeamMember.team_id == team_id,
                    TeamMember.status == "active",
                    Analysis.status == "completed"
                )
            )
        )
        
        row = result.first()
        return {
            "member_count": 1,  # TODO: 実際のチームメンバー数を取得
            "total_analyses": row.total_analyses or 0,
            "avg_confidence": row.avg_confidence or 0.0,
            "performance_metrics": {
                "team_confidence": row.avg_confidence or 0.0,
                "analysis_count": row.total_analyses or 0
            }
        }

    def _calculate_individual_position(
        self, user_id: int, team_data: Dict[str, Any], scope: ComparisonScope
    ) -> Dict[str, str]:
        """個人の位置づけを計算（具体的な数値は含まない）"""
        # 具体的な数値ではなく、相対的な位置づけとして表現
        
        return {
            "contribution_level": "チームに貢献している",
            "growth_potential": "さらなる成長の可能性がある",
            "collaboration_style": "協働的なアプローチ"
        }

    def _identify_team_areas(
        self, team_data: Dict[str, Any]
    ) -> Tuple[List[str], List[str]]:
        """チームの強み・改善領域を特定"""
        strengths = ["チームワーク", "コミュニケーション"]
        improvement_areas = ["継続的な学習", "イノベーション"]
        
        return strengths, improvement_areas

    def _identify_contribution_areas(
        self, individual_position: Dict[str, str], team_improvement_areas: List[str]
    ) -> List[str]:
        """個人の貢献領域を特定"""
        contribution_areas = []
        
        for area in team_improvement_areas:
            if "学習" in area:
                contribution_areas.append("知識共有と学習促進")
            elif "イノベーション" in area:
                contribution_areas.append("新しいアイデアの提案")
        
        return contribution_areas

    def _generate_team_based_suggestions(
        self, team_improvement_areas: List[str], contribution_areas: List[str]
    ) -> List[str]:
        """チームベースの提案を生成"""
        suggestions = []
        
        for area in team_improvement_areas:
            if "学習" in area:
                suggestions.append("チーム内での知識共有セッションを定期的に開催する")
            elif "イノベーション" in area:
                suggestions.append("ブレインストーミングセッションで新しいアイデアを発掘する")
        
        return suggestions

    def _extract_team_best_practices(self, team_data: Dict[str, Any]) -> List[str]:
        """チームのベストプラクティスを抽出"""
        return [
            "定期的な振り返りミーティングの実施",
            "オープンなコミュニケーション文化の維持",
            "継続的なスキル開発の促進"
        ]

    async def _get_organization_benchmark_data(
        self, db: AsyncSession, comparison_request: ComparisonRequest
    ) -> Dict[str, Any]:
        """組織ベンチマークデータを取得"""
        # 組織全体の統計情報を取得
        # 個人の特定を避けるため、集約されたデータのみを返す
        
        result = await db.execute(
            select(
                func.count(Analysis.id).label("total_analyses"),
                func.avg(Analysis.confidence_score).label("avg_confidence")
            ).where(
                Analysis.status == "completed"
            )
        )
        
        row = result.first()
        return {
            "total_participants": 1,  # TODO: 実際の参加者数を取得
            "total_analyses": row.total_analyses or 0,
            "avg_confidence": row.avg_confidence or 0.0,
            "best_practices": [
                "継続的な学習と改善",
                "オープンなコミュニケーション",
                "チームワークの重視"
            ]
        }

    def _compare_with_benchmark(
        self,
        user_analyses: List[Analysis],
        org_data: Dict[str, Any],
        scope: ComparisonScope
    ) -> Dict[str, Any]:
        """組織ベンチマークとの比較"""
        user_score = self._calculate_user_score(user_analyses, scope)
        org_avg = org_data.get("avg_confidence", 0.0)
        
        strengths = []
        growth_areas = []
        
        if user_score > org_avg * 1.1:
            strengths.append("組織平均を上回るパフォーマンス")
        elif user_score < org_avg * 0.9:
            growth_areas.append("組織平均に向けた改善")
        
        return {
            "performance_metrics": {
                "user_score": user_score,
                "org_average": org_avg
            },
            "strengths": strengths,
            "growth_areas": growth_areas
        }

    def _generate_benchmark_based_suggestions(
        self, benchmark_comparison: Dict[str, Any]
    ) -> List[str]:
        """ベンチマークベースの提案を生成"""
        suggestions = []
        
        if benchmark_comparison["growth_areas"]:
            suggestions.append("組織のベストプラクティスを参考にした改善")
            suggestions.append("定期的な自己評価と目標設定")
        
        return suggestions

    def _calculate_team_confidence_level(self, team_data: Dict[str, Any]) -> float:
        """チーム分析の信頼度を計算"""
        # チームデータの品質とデータ量に基づいて信頼度を計算
        analysis_count = team_data.get("total_analyses", 0)
        avg_confidence = team_data.get("avg_confidence", 0.0)
        
        if analysis_count == 0:
            return 0.0
        
        # データ量と品質の両方を考慮
        data_quality = min(analysis_count / 10.0, 1.0)  # 10件以上で最大値
        confidence_quality = avg_confidence
        
        return (data_quality + confidence_quality) / 2.0

    def _extract_best_practices_from_peers(self, peer_data: Dict[str, Any]) -> List[str]:
        """同僚からベストプラクティスを抽出"""
        return [
            "継続的な学習とスキル開発",
            "効果的なコミュニケーション手法",
            "チームワークの促進"
        ]

    def _calculate_anonymous_performance_distribution(
        self, peer_data: Dict[str, Any], user_analyses: List[Analysis]
    ) -> Dict[str, float]:
        """匿名化されたパフォーマンス分布を計算"""
        # 個人の特定を避けるため、統計的な分布のみを返す
        
        user_score = self._calculate_user_score(user_analyses, ComparisonScope.OVERALL_PERFORMANCE)
        
        return {
            "user_performance": user_score,
            "peer_average": peer_data.get("avg_confidence", 0.0),
            "distribution_type": "anonymous_aggregate"
        }

    def _generate_peer_based_suggestions(
        self, relative_strengths: List[str], learning_opportunities: List[str]
    ) -> List[str]:
        """同僚ベースの提案を生成"""
        suggestions = []
        
        if relative_strengths:
            suggestions.append("現在の強みをさらに発展させる")
        
        if learning_opportunities:
            suggestions.append("同僚の良い点を参考にした改善")
            suggestions.append("定期的な振り返りと目標設定")
        
        return suggestions

    # プライベートメソッド（新機能の実装）

    async def _validate_team_membership(
        self, db: AsyncSession, user_id: int, team_ids: List[int]
    ) -> bool:
        """ユーザーが指定されたチームのメンバーかどうかを確認"""
        for team_id in team_ids:
            membership = await self._get_user_team_membership(db, user_id)
            if not membership or membership.team_id != team_id:
                return False
        return True

    def _compare_teams_relative(
        self, source_team_data: Dict[str, Any], target_team_data: Dict[str, Any], scope: ComparisonScope
    ) -> Dict[str, str]:
        """チーム間の相対的な比較（順位は含まない）"""
        relative_performance = {}
        
        # パフォーマンスの相対的な比較
        source_score = source_team_data.get("avg_confidence", 0.0)
        target_score = target_team_data.get("avg_confidence", 0.0)
        
        if abs(source_score - target_score) < 0.1:
            relative_performance["overall"] = "両チームとも同等のパフォーマンス"
        elif source_score > target_score:
            relative_performance["overall"] = "比較元チームが若干優位"
        else:
            relative_performance["overall"] = "比較対象チームが若干優位"
        
        # スコープ別の比較
        if scope == ComparisonScope.COMMUNICATION_SKILLS:
            relative_performance["communication"] = "コミュニケーションスキルは両チームとも良好"
        elif scope == ComparisonScope.LEADERSHIP:
            relative_performance["leadership"] = "リーダーシップの特徴は異なるが、それぞれに強みがある"
        
        return relative_performance

    def _identify_team_synergies(
        self, source_team_data: Dict[str, Any], target_team_data: Dict[str, Any]
    ) -> Tuple[List[str], List[str]]:
        """チーム間の相乗効果を特定"""
        shared_strengths = [
            "チームワークの重視",
            "継続的な学習文化",
            "オープンなコミュニケーション"
        ]
        
        complementary_areas = [
            "技術的専門性とビジネス視点の補完",
            "創造性と実行力の組み合わせ",
            "リスク管理とイノベーションのバランス"
        ]
        
        return shared_strengths, complementary_areas

    def _identify_collaboration_opportunities(
        self, source_team_data: Dict[str, Any], target_team_data: Dict[str, Any], scope: ComparisonScope
    ) -> Tuple[List[str], List[str]]:
        """協働機会を特定"""
        learning_opportunities = [
            "定期的なチーム間の知識共有セッション",
            "共同プロジェクトでの相互学習",
            "ベストプラクティスの共有と展開"
        ]
        
        collaboration_potential = [
            "クロスチームのプロジェクトチーム編成",
            "共通の課題解決ワークショップ",
            "チーム間のメンタリングプログラム"
        ]
        
        return learning_opportunities, collaboration_potential

    async def _get_industry_benchmark_data(
        self, db: AsyncSession, industry: str, company_size: str, scope: ComparisonScope
    ) -> Dict[str, Any]:
        """業界ベンチマークデータを取得"""
        # TODO: 実際の業界データベースから取得
        # 現在はサンプルデータを返す
        
        industry_benchmarks = {
            "IT": {
                "metrics": {
                    "communication_skills": 0.78,
                    "leadership": 0.72,
                    "collaboration": 0.81,
                    "problem_solving": 0.76,
                    "emotional_intelligence": 0.74
                },
                "best_practices": [
                    "アジャイル開発手法の活用",
                    "継続的インテグレーション",
                    "デザイン思考の導入"
                ],
                "data_source": "業界調査レポート2024",
                "last_updated": datetime.utcnow(),
                "confidence_level": 0.85
            },
            "Finance": {
                "metrics": {
                    "communication_skills": 0.75,
                    "leadership": 0.78,
                    "collaboration": 0.73,
                    "problem_solving": 0.79,
                    "emotional_intelligence": 0.76
                },
                "best_practices": [
                    "リスク管理の徹底",
                    "コンプライアンス重視の文化",
                    "顧客中心のサービス設計"
                ],
                "data_source": "金融業界分析レポート2024",
                "last_updated": datetime.utcnow(),
                "confidence_level": 0.82
            }
        }
        
        return industry_benchmarks.get(industry, industry_benchmarks["IT"])

    def _compare_with_industry_benchmark(
        self, user_analyses: List[Analysis], industry_data: Dict[str, Any], scope: ComparisonScope
    ) -> Dict[str, str]:
        """業界ベンチマークとの比較"""
        user_score = self._calculate_user_score(user_analyses, scope)
        industry_avg = industry_data["metrics"].get(str(scope), 0.75)
        
        relative_position = {}
        
        if user_score > industry_avg * 1.1:
            relative_position["overall"] = "業界平均を上回る優秀なパフォーマンス"
        elif user_score > industry_avg * 0.9:
            relative_position["overall"] = "業界平均と同等の良好なパフォーマンス"
        else:
            relative_position["overall"] = "業界平均に向けた改善の余地がある"
        
        # スコープ別の位置づけ
        if scope == ComparisonScope.COMMUNICATION_SKILLS:
            comm_score = industry_data["metrics"].get("communication_skills", 0.75)
            if user_score > comm_score:
                relative_position["communication"] = "コミュニケーションスキルは業界水準以上"
            else:
                relative_position["communication"] = "コミュニケーションスキルの向上が期待される"
        
        return relative_position

    def _identify_industry_improvement_opportunities(
        self, relative_position: Dict[str, str], industry_data: Dict[str, Any]
    ) -> List[str]:
        """業界水準に向けた改善機会を特定"""
        opportunities = []
        
        if "改善の余地がある" in relative_position.get("overall", ""):
            opportunities.append("業界のベストプラクティスを参考にした改善計画の策定")
            opportunities.append("定期的な業界動向の調査と学習")
            opportunities.append("業界内の他社との交流機会の創出")
        
        opportunities.extend([
            "継続的なスキル開発プログラムへの参加",
            "業界認定資格の取得検討",
            "業界内のメンタリングプログラムの活用"
        ])
        
        return opportunities

    async def _get_comparison_result(self, db: AsyncSession, comparison_id: str) -> Optional[ComparisonResult]:
        """比較分析結果を取得"""
        # TODO: 実際のデータベースから取得
        # 現在はサンプルデータを返す
        return None

    def _generate_report_title_and_summary(
        self, comparison_result: ComparisonResult
    ) -> Tuple[str, str]:
        """レポートのタイトルと概要を生成"""
        title = f"{comparison_result.comparison_type.value}分析レポート"
        
        summary = f"""
        このレポートは、{comparison_result.comparison_scope.value}に関する
        {comparison_result.comparison_type.value}分析の結果をまとめたものです。
        総参加者数{comparison_result.total_participants}名のデータに基づいて
        分析が行われ、信頼度{comparison_result.confidence_level:.1%}で結果が生成されています。
        """
        
        return title, summary.strip()

    def _extract_key_findings(self, comparison_result: ComparisonResult) -> List[str]:
        """主要な発見を抽出"""
        findings = []
        
        if comparison_result.strength_areas:
            findings.append(f"強みの領域: {', '.join(comparison_result.strength_areas)}")
        
        if comparison_result.growth_areas:
            findings.append(f"成長の領域: {', '.join(comparison_result.growth_areas)}")
        
        if comparison_result.improvement_suggestions:
            findings.append(f"改善提案: {len(comparison_result.improvement_suggestions)}件の具体的な提案")
        
        findings.append(f"分析の信頼度: {comparison_result.confidence_level:.1%}")
        
        return findings

    def _create_detailed_analysis(self, comparison_result: ComparisonResult) -> Dict[str, Any]:
        """詳細分析結果を作成"""
        return {
            "performance_overview": {
                "total_participants": comparison_result.total_participants,
                "confidence_level": comparison_result.confidence_level,
                "analysis_timestamp": comparison_result.generated_at.isoformat()
            },
            "strength_analysis": {
                "identified_strengths": comparison_result.strength_areas,
                "strength_count": len(comparison_result.strength_areas)
            },
            "growth_analysis": {
                "growth_areas": comparison_result.growth_areas,
                "growth_opportunities": len(comparison_result.growth_areas)
            },
            "recommendations": {
                "improvement_suggestions": comparison_result.improvement_suggestions,
                "best_practices": comparison_result.best_practices
            }
        }

    def _create_visualizations(self, comparison_result: ComparisonResult) -> List[Dict[str, Any]]:
        """可視化データを作成"""
        visualizations = []
        
        # パフォーマンス分布の可視化
        if comparison_result.performance_distribution:
            visualizations.append({
                "type": "performance_distribution",
                "title": "パフォーマンス分布",
                "data": comparison_result.performance_distribution
            })
        
        # 強み・成長領域の可視化
        visualizations.append({
            "type": "strength_growth_chart",
            "title": "強みと成長領域",
            "data": {
                "strengths": comparison_result.strength_areas,
                "growth_areas": comparison_result.growth_areas
            }
        })
        
        return visualizations

    def _generate_action_plan(
        self, comparison_result: ComparisonResult
    ) -> Tuple[List[str], List[str]]:
        """アクションプランを生成"""
        action_items = []
        next_steps = []
        
        # 強みを活かすアクション
        for strength in comparison_result.strength_areas:
            action_items.append(f"{strength}をさらに発展させるための具体的なアクションを計画する")
        
        # 成長領域の改善アクション
        for growth_area in comparison_result.growth_areas:
            action_items.append(f"{growth_area}の改善のための学習計画を立てる")
        
        # 次のステップ
        next_steps = [
            "改善提案の優先順位付け",
            "具体的なアクションプランの策定",
            "定期的な進捗確認のスケジュール設定",
            "必要に応じたサポートリソースの特定"
        ]
        
        return action_items, next_steps


# グローバルインスタンス
comparison_analysis_service = ComparisonAnalysisService()
