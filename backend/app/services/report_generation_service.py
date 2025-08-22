import uuid
import json
import base64
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models.analysis import Analysis
from app.models.user import User
from app.models.report import Report, ReportTemplate, ReportExport
from app.schemas.comparison_analysis import (
    ComparisonResult, ComparisonReport, ReportGenerationRequest
)
from app.schemas.report_generation import (
    ReportGenerationOptions, ReportFormat, ReportType, ChartType,
    ChartData, VisualizationConfig, ReportSection
)
from app.core.exceptions import (
    NotFoundException, ValidationException, BusinessLogicException
)

logger = structlog.get_logger()


class ReportGenerationService:
    """比較分析レポート生成サービス"""

    def __init__(self):
        pass

    async def generate_comparison_report(
        self,
        db: AsyncSession,
        user: User,
        comparison_result: ComparisonResult,
        report_request: ReportGenerationRequest,
        options: Optional[ReportGenerationOptions] = None
    ) -> ComparisonReport:
        """比較分析レポートを生成"""
        try:
            # デフォルトオプションの設定
            if options is None:
                options = ReportGenerationOptions(
                    report_format=ReportFormat(report_request.report_format),
                    language=report_request.language,
                    include_charts=report_request.include_charts,
                    include_recommendations=report_request.include_recommendations
                )
            
            # レポートの基本情報を生成
            title, summary = self._generate_report_title_and_summary(comparison_result, options)
            key_findings = self._extract_key_findings(comparison_result)
            detailed_analysis = self._create_detailed_analysis(comparison_result)
            
            # 高度な可視化データの生成
            visualizations = []
            charts_data = []
            if options.include_charts:
                visualizations, charts_data = self._create_advanced_visualizations(
                    comparison_result, options
                )
            
            # アクションプランの生成
            action_items, next_steps = [], []
            if options.include_recommendations:
                action_items, next_steps = self._generate_action_plan(comparison_result)
            
            # カスタムセクションの追加
            custom_sections = self._generate_custom_sections(
                comparison_result, options.custom_sections
            )
            
            # レポートの生成
            report = ComparisonReport(
                report_id=str(uuid.uuid4()),
                comparison_id=report_request.comparison_id,
                generated_at=datetime.utcnow(),
                title=title,
                summary=summary,
                key_findings=key_findings,
                detailed_analysis=detailed_analysis,
                visualizations=visualizations,
                action_items=action_items,
                next_steps=next_steps,
                report_format=report_request.report_format,
                include_charts=report_request.include_charts,
                include_recommendations=report_request.include_recommendations
            )
            
            # データベースにレポートを保存
            await self._save_report_to_db(db, user, report, ReportType.COMPARISON, options)
            
            logger.info(
                "比較分析レポートを生成",
                report_id=report.report_id,
                comparison_id=report.comparison_id,
                format=options.report_format.value
            )
            
            return report
            
        except Exception as e:
            logger.error(f"レポート生成に失敗: {e}")
            raise

    async def generate_team_comparison_report(
        self,
        db: AsyncSession,
        user: User,
        team_comparison_data: Dict[str, Any],
        report_request: ReportGenerationRequest
    ) -> ComparisonReport:
        """チーム比較レポートを生成"""
        try:
            # チーム比較用のレポート内容を生成
            title = f"チーム比較分析レポート - {team_comparison_data.get('source_team_name', '')} vs {team_comparison_data.get('target_team_name', '')}"
            summary = self._generate_team_comparison_summary(team_comparison_data)
            key_findings = self._extract_team_comparison_findings(team_comparison_data)
            
            # 詳細分析の作成
            detailed_analysis = {
                "team_comparison": team_comparison_data,
                "performance_metrics": team_comparison_data.get("performance_metrics", {}),
                "collaboration_opportunities": team_comparison_data.get("collaboration_opportunities", [])
            }
            
            # 可視化データの生成
            visualizations = []
            if report_request.include_charts:
                visualizations = self._create_team_comparison_visualizations(team_comparison_data)
            
            # アクションプランの生成
            action_items, next_steps = [], []
            if report_request.include_recommendations:
                action_items, next_steps = self._generate_team_action_plan(team_comparison_data)
            
            return ComparisonReport(
                report_id=str(uuid.uuid4()),
                comparison_id=report_request.comparison_id,
                generated_at=datetime.utcnow(),
                title=title,
                summary=summary,
                key_findings=key_findings,
                detailed_analysis=detailed_analysis,
                visualizations=visualizations,
                action_items=action_items,
                next_steps=next_steps,
                report_format=report_request.report_format,
                include_charts=report_request.include_charts,
                include_recommendations=report_request.include_recommendations
            )
            
        except Exception as e:
            logger.error(f"チーム比較レポート生成に失敗: {e}")
            raise

    async def generate_industry_benchmark_report(
        self,
        db: AsyncSession,
        user: User,
        industry_data: Dict[str, Any],
        report_request: ReportGenerationRequest
    ) -> ComparisonReport:
        """業界ベンチマークレポートを生成"""
        try:
            # 業界比較用のレポート内容を生成
            title = f"業界ベンチマーク分析レポート - {industry_data.get('industry', '')}業界"
            summary = self._generate_industry_benchmark_summary(industry_data)
            key_findings = self._extract_industry_benchmark_findings(industry_data)
            
            # 詳細分析の作成
            detailed_analysis = {
                "industry_benchmark": industry_data,
                "relative_position": industry_data.get("relative_position", {}),
                "improvement_opportunities": industry_data.get("improvement_opportunities", [])
            }
            
            # 可視化データの生成
            visualizations = []
            if report_request.include_charts:
                visualizations = self._create_industry_benchmark_visualizations(industry_data)
            
            # アクションプランの生成
            action_items, next_steps = [], []
            if report_request.include_recommendations:
                action_items, next_steps = self._generate_industry_action_plan(industry_data)
            
            return ComparisonReport(
                report_id=str(uuid.uuid4()),
                comparison_id=report_request.comparison_id,
                generated_at=datetime.utcnow(),
                title=title,
                summary=summary,
                key_findings=key_findings,
                detailed_analysis=detailed_analysis,
                visualizations=visualizations,
                action_items=action_items,
                next_steps=next_steps,
                report_format=report_request.report_format,
                include_charts=report_request.include_charts,
                include_recommendations=report_request.include_recommendations
            )
            
        except Exception as e:
            logger.error(f"業界ベンチマークレポート生成に失敗: {e}")
            raise

    # プライベートメソッド

    def _generate_report_title_and_summary(
        self, comparison_result: ComparisonResult, options: ReportGenerationOptions
    ) -> tuple[str, str]:
        """レポートのタイトルと概要を生成"""
        # 言語に応じたタイトル生成
        if options.language == "en":
            title = f"{comparison_result.comparison_type.value} Analysis Report"
        else:
            title = f"{comparison_result.comparison_type.value}分析レポート"
        
        # 言語に応じた概要生成
        if options.language == "en":
            summary = f"""
            This report summarizes the results of {comparison_result.comparison_type.value} analysis
            regarding {comparison_result.comparison_scope.value}. The analysis was conducted
            based on data from {comparison_result.total_participants} total participants,
            and results were generated with a confidence level of {comparison_result.confidence_level:.1%}.
            """
        else:
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

    def _create_advanced_visualizations(
        self, comparison_result: ComparisonResult, options: ReportGenerationOptions
    ) -> Tuple[List[Dict[str, Any]], List[ChartData]]:
        """高度な可視化データを作成"""
        visualizations = []
        charts_data = []
        
        # パフォーマンス分布の可視化
        if comparison_result.performance_distribution:
            chart_data = self._create_performance_distribution_chart(
                comparison_result.performance_distribution, options
            )
            charts_data.append(chart_data)
            visualizations.append({
                "type": "performance_distribution",
                "title": chart_data.title,
                "chart_id": chart_data.chart_id,
                "chart_type": chart_data.chart_type.value
            })
        
        # 強み・成長領域の可視化
        chart_data = self._create_strength_growth_chart(comparison_result, options)
        charts_data.append(chart_data)
        visualizations.append({
            "type": "strength_growth_chart",
            "title": chart_data.title,
            "chart_id": chart_data.chart_id,
            "chart_type": chart_data.chart_type.value
        })
        
        # 改善提案の優先度マトリックス
        if comparison_result.improvement_suggestions:
            chart_data = self._create_improvement_priority_matrix(
                comparison_result.improvement_suggestions, options
            )
            charts_data.append(chart_data)
            visualizations.append({
                "type": "improvement_priority_matrix",
                "title": chart_data.title,
                "chart_id": chart_data.chart_id,
                "chart_type": chart_data.chart_type.value
            })
        
        # 成長トレンドの可視化
        if hasattr(comparison_result, 'growth_trends') and comparison_result.growth_trends:
            chart_data = self._create_growth_trend_chart(comparison_result.growth_trends, options)
            charts_data.append(chart_data)
            visualizations.append({
                "type": "growth_trend_chart",
                "title": chart_data.title,
                "chart_id": chart_data.chart_id,
                "chart_type": chart_data.chart_type.value
            })
        
        # 比較結果のサマリーチャート
        chart_data = self._create_comparison_summary_chart(comparison_result, options)
        charts_data.append(chart_data)
        visualizations.append({
            "type": "comparison_summary_chart",
            "title": chart_data.title,
            "chart_id": chart_data.chart_id,
            "chart_type": chart_data.chart_type.value
        })
        
        return visualizations, charts_data

    def _generate_action_plan(
        self, comparison_result: ComparisonResult
    ) -> tuple[List[str], List[str]]:
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

    def _generate_custom_sections(
        self, comparison_result: ComparisonResult, custom_sections: List[str]
    ) -> Dict[str, Any]:
        """カスタムセクションを生成"""
        custom_data = {}
        
        for section in custom_sections:
            if section == "trend_analysis":
                custom_data[section] = self._generate_trend_analysis(comparison_result)
            elif section == "benchmark_comparison":
                custom_data[section] = self._generate_benchmark_comparison(comparison_result)
            elif section == "risk_assessment":
                custom_data[section] = self._generate_risk_assessment(comparison_result)
        
        return custom_data

    def _generate_trend_analysis(self, comparison_result: ComparisonResult) -> Dict[str, Any]:
        """トレンド分析を生成"""
        return {
            "trend_period": "過去3ヶ月",
            "trend_direction": "改善傾向",
            "key_drivers": ["継続的な学習", "フィードバックの活用"],
            "trend_strength": "中程度"
        }

    def _generate_benchmark_comparison(self, comparison_result: ComparisonResult) -> Dict[str, Any]:
        """ベンチマーク比較を生成"""
        return {
            "benchmark_type": "組織内平均",
            "relative_position": "平均以上",
            "gap_analysis": "10%の改善余地",
            "benchmark_reliability": "高"
        }

    def _generate_risk_assessment(self, comparison_result: ComparisonResult) -> Dict[str, Any]:
        """リスク評価を生成"""
        return {
            "risk_level": "低",
            "identified_risks": ["成長の停滞", "スキルの偏り"],
            "mitigation_strategies": ["継続的な学習", "多様なスキル開発"],
            "monitoring_frequency": "月次"
        }

    def _generate_team_comparison_summary(self, team_data: Dict[str, Any]) -> str:
        """チーム比較レポートの概要を生成"""
        return f"""
        このレポートは、2つのチーム間の比較分析結果をまとめたものです。
        両チームの相対的な強み、補完領域、協働機会を特定し、
        チーム間の相互学習と協働の可能性を探っています。
        """

    def _extract_team_comparison_findings(self, team_data: Dict[str, Any]) -> List[str]:
        """チーム比較の主要な発見を抽出"""
        findings = []
        
        if team_data.get("shared_strengths"):
            findings.append(f"共通の強み: {', '.join(team_data['shared_strengths'])}")
        
        if team_data.get("complementary_areas"):
            findings.append(f"補完領域: {', '.join(team_data['complementary_areas'])}")
        
        if team_data.get("learning_opportunities"):
            findings.append(f"学習機会: {len(team_data['learning_opportunities'])}件の機会を特定")
        
        return findings

    def _create_team_comparison_visualizations(self, team_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """チーム比較の可視化データを作成"""
        visualizations = []
        
        # チーム間の相対的なパフォーマンス比較
        if team_data.get("relative_performance"):
            visualizations.append({
                "type": "team_performance_comparison",
                "title": "チーム間パフォーマンス比較",
                "data": team_data["relative_performance"],
                "chart_type": "comparison_chart"
            })
        
        # 共通の強みと補完領域
        visualizations.append({
            "type": "team_synergy_analysis",
            "title": "チーム間の相乗効果分析",
            "data": {
                "shared_strengths": team_data.get("shared_strengths", []),
                "complementary_areas": team_data.get("complementary_areas", [])
            },
            "chart_type": "venn_diagram"
        })
        
        return visualizations

    def _generate_team_action_plan(self, team_data: Dict[str, Any]) -> tuple[List[str], List[str]]:
        """チーム比較のアクションプランを生成"""
        action_items = []
        next_steps = []
        
        # 協働機会の実現
        if team_data.get("collaboration_potential"):
            for opportunity in team_data["collaboration_potential"]:
                action_items.append(f"{opportunity}の実現計画を策定する")
        
        # 相互学習の促進
        if team_data.get("learning_opportunities"):
            for learning in team_data["learning_opportunities"]:
                action_items.append(f"{learning}の具体的な実施計画を立てる")
        
        next_steps = [
            "チーム間の定期的な振り返りミーティングの設定",
            "共同プロジェクトの企画・実施",
            "知識共有セッションの定期開催",
            "協働効果の測定・評価"
        ]
        
        return action_items, next_steps

    def _generate_industry_benchmark_summary(self, industry_data: Dict[str, Any]) -> str:
        """業界ベンチマークレポートの概要を生成"""
        return f"""
        このレポートは、{industry_data.get('industry', '')}業界のベンチマークデータとの
        比較分析結果をまとめたものです。業界平均との相対的な位置づけ、
        業界のベストプラクティス、改善機会を特定しています。
        """

    def _extract_industry_benchmark_findings(self, industry_data: Dict[str, Any]) -> List[str]:
        """業界ベンチマークの主要な発見を抽出"""
        findings = []
        
        if industry_data.get("relative_position"):
            for key, value in industry_data["relative_position"].items():
                findings.append(f"{key}: {value}")
        
        if industry_data.get("improvement_opportunities"):
            findings.append(f"改善機会: {len(industry_data['improvement_opportunities'])}件の機会を特定")
        
        if industry_data.get("industry_best_practices"):
            findings.append(f"業界のベストプラクティス: {len(industry_data['industry_best_practices'])}件を参考に")
        
        return findings

    def _create_industry_benchmark_visualizations(self, industry_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """業界ベンチマークの可視化データを作成"""
        visualizations = []
        
        # 業界平均との比較
        if industry_data.get("industry_average"):
            visualizations.append({
                "type": "industry_benchmark_comparison",
                "title": "業界平均との比較",
                "data": industry_data["industry_average"],
                "chart_type": "benchmark_chart"
            })
        
        # 相対的位置づけ
        if industry_data.get("relative_position"):
            visualizations.append({
                "type": "relative_position_analysis",
                "title": "業界内での相対的位置づけ",
                "data": industry_data["relative_position"],
                "chart_type": "position_chart"
            })
        
        return visualizations

    def _generate_industry_action_plan(self, industry_data: Dict[str, Any]) -> tuple[List[str], List[str]]:
        """業界ベンチマークのアクションプランを生成"""
        action_items = []
        next_steps = []
        
        # 業界水準に向けた改善
        if industry_data.get("improvement_opportunities"):
            for opportunity in industry_data["improvement_opportunities"]:
                action_items.append(f"{opportunity}の具体的な実施計画を策定する")
        
        # ベストプラクティスの活用
        if industry_data.get("industry_best_practices"):
            for practice in industry_data["industry_best_practices"]:
                action_items.append(f"{practice}の導入・活用を検討する")
        
        next_steps = [
            "業界動向の定期的な調査・分析",
            "業界内の他社との交流機会の創出",
            "業界認定資格の取得検討",
            "業界のベストプラクティスの継続的な学習"
        ]
        
        return action_items, next_steps

    async def _save_report_to_db(
        self,
        db: AsyncSession,
        user: User,
        report: ComparisonReport,
        report_type: ReportType,
        options: ReportGenerationOptions
    ) -> None:
        """レポートをデータベースに保存"""
        try:
            # レポートモデルの作成
            db_report = Report(
                report_id=report.report_id,
                comparison_id=report.comparison_id,
                report_type=report_type.value,
                title=report.title,
                summary=report.summary,
                key_findings=report.key_findings,
                detailed_analysis=report.detailed_analysis,
                visualizations=report.visualizations,
                charts_data=self._prepare_charts_data_for_db(report),
                action_items=report.action_items,
                next_steps=report.next_steps,
                report_format=options.report_format.value,
                include_charts=options.include_charts,
                include_recommendations=options.include_recommendations,
                language=options.language,
                generated_by=user.id,
                is_public=False,  # デフォルトは非公開
                tags=["comparison_analysis", "auto_generated"]
            )
            
            db.add(db_report)
            await db.commit()
            
            logger.info(f"レポートをデータベースに保存: {report.report_id}")
            
        except Exception as e:
            await db.rollback()
            logger.error(f"レポートのデータベース保存に失敗: {e}")
            raise

    def _prepare_charts_data_for_db(self, report: ComparisonReport) -> List[Dict[str, Any]]:
        """チャートデータをデータベース保存用に準備"""
        # 現在の実装では空のリストを返す
        # 実際のチャートデータは別途管理
        return []

    # チャート生成メソッド

    def _create_performance_distribution_chart(
        self, performance_data: Dict[str, Any], options: ReportGenerationOptions
    ) -> ChartData:
        """パフォーマンス分布チャートを作成"""
        chart_id = f"performance_dist_{uuid.uuid4().hex[:8]}"
        
        # 言語に応じたタイトル
        if options.language == "en":
            title = "Performance Distribution"
        else:
            title = "パフォーマンス分布"
        
        # チャート設定
        config = VisualizationConfig(
            chart_type=ChartType.BAR_CHART,
            title=title,
            description="パフォーマンスレベルの分布を示します",
            data_source="comparison_analysis",
            x_axis="performance_level",
            y_axis="count",
            colors=options.chart_colors or ["#4CAF50", "#2196F3", "#FFC107", "#F44336"],
            theme=options.chart_theme or "default",
            animation=options.chart_animation
        )
        
        return ChartData(
            chart_id=chart_id,
            chart_type=ChartType.BAR_CHART,
            title=title,
            data=performance_data,
            config=config
        )

    def _create_strength_growth_chart(
        self, comparison_result: ComparisonResult, options: ReportGenerationOptions
    ) -> ChartData:
        """強み・成長領域チャートを作成"""
        chart_id = f"strength_growth_{uuid.uuid4().hex[:8]}"
        
        # 言語に応じたタイトル
        if options.language == "en":
            title = "Strengths and Growth Areas"
        else:
            title = "強みと成長領域"
        
        # データの準備
        chart_data = {
            "strengths": comparison_result.strength_areas,
            "growth_areas": comparison_result.growth_areas,
            "strength_count": len(comparison_result.strength_areas),
            "growth_count": len(comparison_result.growth_areas)
        }
        
        # チャート設定
        config = VisualizationConfig(
            chart_type=ChartType.RADAR_CHART,
            title=title,
            description="強みと成長領域をレーダーチャートで表示します",
            data_source="comparison_analysis",
            colors=options.chart_colors or ["#4CAF50", "#FF9800"],
            theme=options.chart_theme or "default",
            animation=options.chart_animation
        )
        
        return ChartData(
            chart_id=chart_id,
            chart_type=ChartType.RADAR_CHART,
            title=title,
            data=chart_data,
            config=config
        )

    def _create_improvement_priority_matrix(
        self, improvement_suggestions: List[str], options: ReportGenerationOptions
    ) -> ChartData:
        """改善提案の優先度マトリックスチャートを作成"""
        chart_id = f"improvement_matrix_{uuid.uuid4().hex[:8]}"
        
        # 言語に応じたタイトル
        if options.language == "en":
            title = "Improvement Priority Matrix"
        else:
            title = "改善提案の優先度マトリックス"
        
        # データの準備
        chart_data = {
            "suggestions": improvement_suggestions,
            "impact_levels": ["high", "medium", "low"],
            "effort_levels": ["low", "medium", "high"],
            "matrix_data": self._create_priority_matrix_data(improvement_suggestions)
        }
        
        # チャート設定
        config = VisualizationConfig(
            chart_type=ChartType.HEATMAP,
            title=title,
            description="改善提案の影響度と努力度をマトリックスで表示します",
            data_source="comparison_analysis",
            colors=options.chart_colors or ["#E3F2FD", "#2196F3", "#1976D2"],
            theme=options.chart_theme or "default",
            animation=options.chart_animation
        )
        
        return ChartData(
            chart_id=chart_id,
            chart_type=ChartType.HEATMAP,
            title=title,
            data=chart_data,
            config=config
        )

    def _create_growth_trend_chart(
        self, growth_trends: Dict[str, Any], options: ReportGenerationOptions
    ) -> ChartData:
        """成長トレンドチャートを作成"""
        chart_id = f"growth_trend_{uuid.uuid4().hex[:8]}"
        
        # 言語に応じたタイトル
        if options.language == "en":
            title = "Growth Trends Over Time"
        else:
            title = "成長トレンド"
        
        # チャート設定
        config = VisualizationConfig(
            chart_type=ChartType.LINE_CHART,
            title=title,
            description="時間経過による成長トレンドを表示します",
            data_source="comparison_analysis",
            x_axis="time_period",
            y_axis="performance_score",
            colors=options.chart_colors or ["#4CAF50", "#2196F3"],
            theme=options.chart_theme or "default",
            animation=options.chart_animation
        )
        
        return ChartData(
            chart_id=chart_id,
            chart_type=ChartType.LINE_CHART,
            title=title,
            data=growth_trends,
            config=config
        )

    def _create_comparison_summary_chart(
        self, comparison_result: ComparisonResult, options: ReportGenerationOptions
    ) -> ChartData:
        """比較結果のサマリーチャートを作成"""
        chart_id = f"comparison_summary_{uuid.uuid4().hex[:8]}"
        
        # 言語に応じたタイトル
        if options.language == "en":
            title = "Comparison Summary"
        else:
            title = "比較結果サマリー"
        
        # データの準備
        summary_data = {
            "total_participants": comparison_result.total_participants,
            "confidence_level": comparison_result.confidence_level,
            "strength_count": len(comparison_result.strength_areas),
            "growth_count": len(comparison_result.growth_areas),
            "suggestion_count": len(comparison_result.improvement_suggestions)
        }
        
        # チャート設定
        config = VisualizationConfig(
            chart_type=ChartType.GAUGE_CHART,
            title=title,
            description="比較分析の主要指標をサマリーで表示します",
            data_source="comparison_analysis",
            colors=options.chart_colors or ["#4CAF50", "#2196F3", "#FF9800", "#F44336"],
            theme=options.chart_theme or "default",
            animation=options.chart_animation
        )
        
        return ChartData(
            chart_id=chart_id,
            chart_type=ChartType.GAUGE_CHART,
            title=title,
            data=summary_data,
            config=config
        )

    def _create_priority_matrix_data(self, suggestions: List[str]) -> List[Dict[str, Any]]:
        """優先度マトリックスのデータを作成"""
        matrix_data = []
        
        for i, suggestion in enumerate(suggestions):
            # ランダムな影響度と努力度を生成（実際の実装では適切なロジックを使用）
            impact = ["high", "medium", "low"][i % 3]
            effort = ["low", "medium", "high"][(i + 1) % 3]
            
            matrix_data.append({
                "suggestion": suggestion,
                "impact": impact,
                "effort": effort,
                "priority": self._calculate_priority(impact, effort)
            })
        
        return matrix_data

    def _calculate_priority(self, impact: str, effort: str) -> str:
        """影響度と努力度から優先度を計算"""
        impact_scores = {"high": 3, "medium": 2, "low": 1}
        effort_scores = {"high": 1, "medium": 2, "low": 3}
        
        priority_score = impact_scores.get(impact, 1) * effort_scores.get(effort, 1)
        
        if priority_score >= 6:
            return "high"
        elif priority_score >= 3:
            return "medium"
        else:
            return "low"

    # レポートエクスポート機能

    async def export_report(
        self,
        db: AsyncSession,
        user: User,
        report_id: str,
        export_format: ReportFormat,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """レポートをエクスポート"""
        try:
            # レポートの取得
            report = await self._get_report_by_id(db, report_id)
            if not report:
                raise NotFoundException("レポートが見つかりません")
            
            # エクスポート処理
            if export_format == ReportFormat.PDF:
                export_result = await self._export_to_pdf(report, options)
            elif export_format == ReportFormat.HTML:
                export_result = await self._export_to_html(report, options)
            elif export_format == ReportFormat.EXCEL:
                export_result = await self._export_to_excel(report, options)
            elif export_format == ReportFormat.POWERPOINT:
                export_result = await self._export_to_powerpoint(report, options)
            else:
                export_result = await self._export_to_json(report, options)
            
            # エクスポート履歴の保存
            await self._save_export_history(db, user, report_id, export_format, export_result)
            
            logger.info(
                "レポートをエクスポート",
                report_id=report_id,
                format=export_format.value,
                user_id=user.id
            )
            
            return export_result
            
        except Exception as e:
            logger.error(f"レポートエクスポートに失敗: {e}")
            raise

    async def _get_report_by_id(self, db: AsyncSession, report_id: str) -> Optional[Report]:
        """IDでレポートを取得"""
        result = await db.execute(
            select(Report).where(Report.report_id == report_id)
        )
        return result.scalar_one_or_none()

    async def _export_to_pdf(self, report: Report, options: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """PDF形式でエクスポート"""
        # TODO: 実際のPDF生成処理を実装
        return {
            "format": "pdf",
            "file_size": 1024000,  # 1MB
            "download_url": f"/reports/{report.report_id}/download.pdf",
            "status": "completed"
        }

    async def _export_to_html(self, report: Report, options: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """HTML形式でエクスポート"""
        # TODO: 実際のHTML生成処理を実装
        return {
            "format": "html",
            "file_size": 512000,  # 500KB
            "download_url": f"/reports/{report.report_id}/download.html",
            "status": "completed"
        }

    async def _export_to_excel(self, report: Report, options: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Excel形式でエクスポート"""
        # TODO: 実際のExcel生成処理を実装
        return {
            "format": "excel",
            "file_size": 256000,  # 250KB
            "download_url": f"/reports/{report.report_id}/download.xlsx",
            "status": "completed"
        }

    async def _export_to_powerpoint(self, report: Report, options: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """PowerPoint形式でエクスポート"""
        # TODO: 実際のPowerPoint生成処理を実装
        return {
            "format": "powerpoint",
            "file_size": 2048000,  # 2MB
            "download_url": f"/reports/{report.report_id}/download.pptx",
            "status": "completed"
        }

    async def _export_to_json(self, report: Report, options: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """JSON形式でエクスポート"""
        # TODO: 実際のJSON生成処理を実装
        return {
            "format": "json",
            "file_size": 128000,  # 125KB
            "download_url": f"/reports/{report.report_id}/download.json",
            "status": "completed"
        }

    async def _save_export_history(
        self,
        db: AsyncSession,
        user: User,
        report_id: str,
        export_format: ReportFormat,
        export_result: Dict[str, Any]
    ) -> None:
        """エクスポート履歴を保存"""
        try:
            export_history = ReportExport(
                report_id=report_id,
                export_format=export_format.value,
                export_type="download",
                file_size=export_result.get("file_size", 0),
                download_url=export_result.get("download_url", ""),
                status=export_result.get("status", "completed"),
                exported_by=user.id
            )
            
            db.add(export_history)
            await db.commit()
            
        except Exception as e:
            await db.rollback()
            logger.error(f"エクスポート履歴の保存に失敗: {e}")


# グローバルインスタンス
report_generation_service = ReportGenerationService()
