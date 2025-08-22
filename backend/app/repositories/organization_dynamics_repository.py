from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, asc, func, distinct
from sqlalchemy.orm import selectinload
import structlog
from datetime import datetime, timedelta

from app.models.team_dynamics import (
    TeamInteraction,
    TeamCompatibility,
    TeamCohesion,
    OrganizationMemberProfile
)
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.models.user import User
from app.repositories.base import BaseRepository

logger = structlog.get_logger()


class OrganizationDynamicsRepository(BaseRepository[Any, Any, Any]):
    """組織ダイナミクス分析リポジトリ"""

    def __init__(self):
        super().__init__(OrganizationMemberProfile)  # デフォルトモデル

    # 組織レベルの相互作用分析
    async def get_organization_interactions(
        self, 
        db: AsyncSession, 
        organization_id: int, 
        days: int = 30,
        limit: int = 100
    ) -> List[TeamInteraction]:
        """組織全体の相互作用パターンを取得"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # 組織に所属するチームの相互作用を取得
            result = await db.execute(
                select(TeamInteraction)
                .join(OrganizationMember, TeamInteraction.team_id == OrganizationMember.team_id)
                .where(
                    and_(
                        OrganizationMember.organization_id == organization_id,
                        TeamInteraction.timestamp >= cutoff_date
                    )
                )
                .order_by(desc(TeamInteraction.timestamp))
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting organization interactions: {e}")
            return []

    async def get_organization_communication_patterns(
        self, 
        db: AsyncSession, 
        organization_id: int
    ) -> Dict[str, Any]:
        """組織のコミュニケーションパターンを分析"""
        try:
            # 組織全体の相互作用タイプ別統計
            result = await db.execute(
                select(
                    TeamInteraction.interaction_type,
                    func.count(TeamInteraction.id).label('count'),
                    func.avg(TeamInteraction.interaction_strength).label('avg_strength')
                )
                .join(OrganizationMember, TeamInteraction.team_id == OrganizationMember.team_id)
                .where(OrganizationMember.organization_id == organization_id)
                .group_by(TeamInteraction.interaction_type)
            )
            
            patterns = {}
            for row in result.fetchall():
                patterns[row.interaction_type] = {
                    'count': row.count,
                    'avg_strength': float(row.avg_strength) if row.avg_strength else 0.0
                }
            
            return patterns
        except Exception as e:
            logger.error(f"Error analyzing communication patterns: {e}")
            return {}

    async def get_organization_cohesion_analysis(
        self, 
        db: AsyncSession, 
        organization_id: int
    ) -> Dict[str, Any]:
        """組織全体の結束力分析"""
        try:
            # 組織に所属するチームの結束力スコアを取得
            result = await db.execute(
                select(
                    func.avg(TeamCohesion.cohesion_score).label('avg_cohesion'),
                    func.avg(TeamCohesion.opinion_alignment).label('avg_opinion_alignment'),
                    func.avg(TeamCohesion.cultural_formation).label('avg_cultural_formation'),
                    func.count(TeamCohesion.id).label('team_count')
                )
                .join(OrganizationMember, TeamCohesion.team_id == OrganizationMember.team_id)
                .where(OrganizationMember.organization_id == organization_id)
            )
            
            row = result.fetchone()
            if row:
                return {
                    'avg_cohesion': float(row.avg_cohesion) if row.avg_cohesion else 0.0,
                    'avg_opinion_alignment': float(row.avg_opinion_alignment) if row.avg_opinion_alignment else 0.0,
                    'avg_cultural_formation': float(row.avg_cultural_formation) if row.avg_cultural_formation else 0.0,
                    'team_count': row.team_count,
                    'overall_health': self._calculate_organization_health(
                        row.avg_cohesion, row.avg_opinion_alignment, row.avg_cultural_formation
                    )
                }
            return {}
        except Exception as e:
            logger.error(f"Error analyzing organization cohesion: {e}")
            return {}

    async def get_organization_member_compatibility_matrix(
        self, 
        db: AsyncSession, 
        organization_id: int
    ) -> List[Dict[str, Any]]:
        """組織メンバー間の相性マトリックスを取得"""
        try:
            # 組織内のメンバー間相性を取得
            result = await db.execute(
                select(TeamCompatibility)
                .join(OrganizationMember, TeamCompatibility.team_id == OrganizationMember.team_id)
                .where(OrganizationMember.organization_id == organization_id)
                .order_by(desc(TeamCompatibility.overall_compatibility))
            )
            
            compatibilities = []
            for comp in result.scalars().all():
                compatibilities.append({
                    'member1_id': comp.member1_id,
                    'member2_id': comp.member2_id,
                    'communication_score': comp.communication_style_score,
                    'personality_score': comp.personality_compatibility,
                    'work_style_score': comp.work_style_score,
                    'overall_score': comp.overall_compatibility,
                    'last_updated': comp.last_updated.isoformat() if comp.last_updated else None
                })
            
            return compatibilities
        except Exception as e:
            logger.error(f"Error getting compatibility matrix: {e}")
            return []

    async def get_organization_performance_metrics(
        self, 
        db: AsyncSession, 
        organization_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """組織のパフォーマンス指標を取得"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # 組織の相互作用統計
            interaction_stats = await db.execute(
                select(
                    func.count(TeamInteraction.id).label('total_interactions'),
                    func.avg(TeamInteraction.interaction_strength).label('avg_strength'),
                    func.avg(TeamInteraction.duration).label('avg_duration')
                )
                .join(OrganizationMember, TeamInteraction.team_id == OrganizationMember.team_id)
                .where(
                    and_(
                        OrganizationMember.organization_id == organization_id,
                        TeamInteraction.timestamp >= cutoff_date
                    )
                )
            )
            
            # 組織の結束力統計
            cohesion_stats = await db.execute(
                select(
                    func.avg(TeamCohesion.cohesion_score).label('avg_cohesion'),
                    func.count(TeamCohesion.id).label('analysis_count')
                )
                .join(OrganizationMember, TeamCohesion.team_id == OrganizationMember.team_id)
                .where(OrganizationMember.organization_id == organization_id)
            )
            
            interaction_row = interaction_stats.fetchone()
            cohesion_row = cohesion_stats.fetchone()
            
            return {
                'interactions': {
                    'total': interaction_row.total_interactions if interaction_row else 0,
                    'avg_strength': float(interaction_row.avg_strength) if interaction_row and interaction_row.avg_strength else 0.0,
                    'avg_duration': float(interaction_row.avg_duration) if interaction_row and interaction_row.avg_duration else 0.0
                },
                'cohesion': {
                    'avg_score': float(cohesion_row.avg_cohesion) if cohesion_row and cohesion_row.avg_cohesion else 0.0,
                    'analysis_count': cohesion_row.analysis_count if cohesion_row else 0
                },
                'period_days': days
            }
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {}

    async def get_organization_improvement_recommendations(
        self, 
        db: AsyncSession, 
        organization_id: int
    ) -> List[Dict[str, Any]]:
        """組織改善のための推奨事項を取得"""
        try:
            recommendations = []
            
            # 低結束力チームの特定
            low_cohesion_teams = await db.execute(
                select(TeamCohesion)
                .join(OrganizationMember, TeamCohesion.team_id == OrganizationMember.team_id)
                .where(
                    and_(
                        OrganizationMember.organization_id == organization_id,
                        TeamCohesion.cohesion_score < 60
                    )
                )
                .order_by(TeamCohesion.cohesion_score)
            )
            
            for team in low_cohesion_teams.scalars().all():
                recommendations.append({
                    'type': 'low_cohesion',
                    'team_id': team.team_id,
                    'score': team.cohesion_score,
                    'priority': 'high' if team.cohesion_score < 30 else 'medium',
                    'suggestion': team.improvement_suggestions or 'チーム結束力の向上が必要です'
                })
            
            # 低相性メンバーペアの特定
            low_compatibility_pairs = await db.execute(
                select(TeamCompatibility)
                .join(OrganizationMember, TeamCompatibility.team_id == OrganizationMember.team_id)
                .where(
                    and_(
                        OrganizationMember.organization_id == organization_id,
                        TeamCompatibility.overall_compatibility < 50
                    )
                )
                .order_by(TeamCompatibility.overall_compatibility)
            )
            
            for pair in low_compatibility_pairs.scalars().all():
                recommendations.append({
                    'type': 'low_compatibility',
                    'member1_id': pair.member1_id,
                    'member2_id': pair.member2_id,
                    'score': pair.overall_compatibility,
                    'priority': 'medium',
                    'suggestion': 'メンバー間の相性改善が必要です'
                })
            
            return recommendations
        except Exception as e:
            logger.error(f"Error getting improvement recommendations: {e}")
            return []

    async def create_organization_analysis_report(
        self, 
        db: AsyncSession, 
        organization_id: int
    ) -> Dict[str, Any]:
        """組織分析レポートを作成"""
        try:
            # 各種分析データを収集
            cohesion_analysis = await self.get_organization_cohesion_analysis(db, organization_id)
            compatibility_matrix = await self.get_organization_member_compatibility_matrix(db, organization_id)
            performance_metrics = await self.get_organization_performance_metrics(db, organization_id)
            improvement_recommendations = await self.get_organization_improvement_recommendations(db, organization_id)
            
            # レポートを生成
            report = {
                'organization_id': organization_id,
                'generated_at': datetime.utcnow().isoformat(),
                'cohesion_analysis': cohesion_analysis,
                'compatibility_matrix': compatibility_matrix,
                'performance_metrics': performance_metrics,
                'improvement_recommendations': improvement_recommendations,
                'summary': self._generate_organization_summary(
                    cohesion_analysis, performance_metrics, improvement_recommendations
                )
            }
            
            return report
        except Exception as e:
            logger.error(f"Error creating organization analysis report: {e}")
            return {}

    def _calculate_organization_health(
        self, 
        cohesion: float, 
        opinion_alignment: float, 
        cultural_formation: float
    ) -> str:
        """組織の健全性を計算"""
        if not all([cohesion, opinion_alignment, cultural_formation]):
            return "unknown"
        
        avg_score = (cohesion + opinion_alignment + cultural_formation) / 3
        
        if avg_score >= 80:
            return "excellent"
        elif avg_score >= 60:
            return "good"
        elif avg_score >= 40:
            return "fair"
        else:
            return "poor"

    def _generate_organization_summary(
        self, 
        cohesion_analysis: Dict[str, Any], 
        performance_metrics: Dict[str, Any], 
        recommendations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """組織分析のサマリーを生成"""
        high_priority_count = len([r for r in recommendations if r.get('priority') == 'high'])
        medium_priority_count = len([r for r in recommendations if r.get('priority') == 'medium'])
        
        return {
            'overall_health': cohesion_analysis.get('overall_health', 'unknown'),
            'total_recommendations': len(recommendations),
            'high_priority_issues': high_priority_count,
            'medium_priority_issues': medium_priority_count,
            'needs_attention': high_priority_count > 0 or medium_priority_count > 0
        }


# グローバルインスタンス
organization_dynamics_repository = OrganizationDynamicsRepository() 