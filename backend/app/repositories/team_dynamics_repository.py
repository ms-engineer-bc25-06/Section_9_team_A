from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, asc, func
from sqlalchemy.orm import selectinload
import structlog

from app.models.team_dynamics import (
    TeamInteraction,
    TeamCompatibility,
    TeamCohesion,
    OrganizationMemberProfile
)
from app.repositories.base import BaseRepository

logger = structlog.get_logger()


class TeamDynamicsRepository(BaseRepository[Any, Any, Any]):
    """チームダイナミクスリポジトリ"""

    def __init__(self):
        super().__init__(TeamInteraction)  # デフォルトモデル

    # TeamInteraction 関連メソッド
    async def get_team_interactions(
        self, db: AsyncSession, team_id: int, limit: int = 100
    ) -> List[TeamInteraction]:
        """チームの相互作用パターンを取得"""
        result = await db.execute(
            select(TeamInteraction)
            .where(TeamInteraction.team_id == team_id)
            .order_by(desc(TeamInteraction.timestamp))
            .limit(limit)
        )
        return result.scalars().all()

    async def get_session_interactions(
        self, db: AsyncSession, session_id: int
    ) -> List[TeamInteraction]:
        """セッションの相互作用パターンを取得"""
        result = await db.execute(
            select(TeamInteraction)
            .where(TeamInteraction.session_id == session_id)
            .order_by(TeamInteraction.timestamp)
        )
        return result.scalars().all()

    async def get_user_interactions(
        self, db: AsyncSession, user_id: int, limit: int = 100
    ) -> List[TeamInteraction]:
        """ユーザーの相互作用パターンを取得"""
        result = await db.execute(
            select(TeamInteraction)
            .where(
                or_(
                    TeamInteraction.speaker_id == user_id,
                    TeamInteraction.listener_id == user_id
                )
            )
            .order_by(desc(TeamInteraction.timestamp))
            .limit(limit)
        )
        return result.scalars().all()

    async def create_interaction(
        self, db: AsyncSession, interaction_data: Dict[str, Any]
    ) -> TeamInteraction:
        """相互作用パターンを作成"""
        db_interaction = TeamInteraction(**interaction_data)
        db.add(db_interaction)
        await db.commit()
        await db.refresh(db_interaction)
        return db_interaction

    # TeamCompatibility 関連メソッド
    async def get_team_compatibilities(
        self, db: AsyncSession, team_id: int
    ) -> List[TeamCompatibility]:
        """チームの相性スコアを取得"""
        result = await db.execute(
            select(TeamCompatibility)
            .where(TeamCompatibility.team_id == team_id)
            .order_by(desc(TeamCompatibility.overall_compatibility))
        )
        return result.scalars().all()

    async def get_member_compatibility(
        self, db: AsyncSession, team_id: int, member1_id: int, member2_id: int
    ) -> Optional[TeamCompatibility]:
        """2人のメンバー間の相性を取得"""
        result = await db.execute(
            select(TeamCompatibility)
            .where(
                and_(
                    TeamCompatibility.team_id == team_id,
                    or_(
                        and_(
                            TeamCompatibility.member1_id == member1_id,
                            TeamCompatibility.member2_id == member2_id
                        ),
                        and_(
                            TeamCompatibility.member1_id == member2_id,
                            TeamCompatibility.member2_id == member1_id
                        )
                    )
                )
            )
        )
        return result.scalar_one_or_none()

    async def create_compatibility(
        self, db: AsyncSession, compatibility_data: Dict[str, Any]
    ) -> TeamCompatibility:
        """相性スコアを作成"""
        db_compatibility = TeamCompatibility(**compatibility_data)
        db.add(db_compatibility)
        await db.commit()
        await db.refresh(db_compatibility)
        return db_compatibility

    async def update_compatibility(
        self, db: AsyncSession, compatibility_id: int, update_data: Dict[str, Any]
    ) -> Optional[TeamCompatibility]:
        """相性スコアを更新"""
        compatibility = await db.get(TeamCompatibility, compatibility_id)
        if not compatibility:
            return None
        
        for field, value in update_data.items():
            if hasattr(compatibility, field):
                setattr(compatibility, field, value)
        
        await db.commit()
        await db.refresh(compatibility)
        return compatibility

    # TeamCohesion 関連メソッド
    async def get_team_cohesions(
        self, db: AsyncSession, team_id: int, limit: int = 50
    ) -> List[TeamCohesion]:
        """チームの結束力分析を取得"""
        result = await db.execute(
            select(TeamCohesion)
            .where(TeamCohesion.team_id == team_id)
            .order_by(desc(TeamCohesion.analysis_date))
            .limit(limit)
        )
        return result.scalars().all()

    async def get_session_cohesion(
        self, db: AsyncSession, session_id: int
    ) -> Optional[TeamCohesion]:
        """セッションの結束力分析を取得"""
        result = await db.execute(
            select(TeamCohesion)
            .where(TeamCohesion.session_id == session_id)
        )
        return result.scalar_one_or_none()

    async def create_cohesion(
        self, db: AsyncSession, cohesion_data: Dict[str, Any]
    ) -> TeamCohesion:
        """結束力分析を作成"""
        db_cohesion = TeamCohesion(**cohesion_data)
        db.add(db_cohesion)
        await db.commit()
        await db.refresh(db_cohesion)
        return db_cohesion

    # OrganizationMemberProfile 関連メソッド
    async def get_member_profile(
        self, db: AsyncSession, user_id: int, team_id: int
    ) -> Optional[OrganizationMemberProfile]:
        """チームメンバープロファイルを取得"""
        result = await db.execute(
            select(OrganizationMemberProfile)
            .where(
                and_(
                    OrganizationMemberProfile.user_id == user_id,
                    OrganizationMemberProfile.team_id == team_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_team_profiles(
        self, db: AsyncSession, team_id: int
    ) -> List[OrganizationMemberProfile]:
        """チームの全メンバープロファイルを取得"""
        result = await db.execute(
            select(OrganizationMemberProfile)
            .where(OrganizationMemberProfile.team_id == team_id)
            .order_by(OrganizationMemberProfile.last_updated.desc())
        )
        return result.scalars().all()

    async def create_member_profile(
        self, db: AsyncSession, profile_data: Dict[str, Any]
    ) -> OrganizationMemberProfile:
        """メンバープロファイルを作成"""
        db_profile = OrganizationMemberProfile(**profile_data)
        db.add(db_profile)
        await db.commit()
        await db.refresh(db_profile)
        return db_profile

    async def update_member_profile(
        self, db: AsyncSession, profile_id: int, update_data: Dict[str, Any]
    ) -> Optional[OrganizationMemberProfile]:
        """メンバープロファイルを更新"""
        profile = await db.get(OrganizationMemberProfile, profile_id)
        if not profile:
            return None
        
        for field, value in update_data.items():
            if hasattr(profile, field):
                setattr(profile, field, value)
        
        await db.commit()
        await db.refresh(profile)
        return profile

    # 分析・統計メソッド
    async def get_team_interaction_stats(
        self, db: AsyncSession, team_id: int
    ) -> Dict[str, Any]:
        """チームの相互作用統計を取得"""
        result = await db.execute(
            select(
                TeamInteraction.interaction_type,
                func.count(TeamInteraction.id).label('count'),
                func.avg(TeamInteraction.interaction_strength).label('avg_strength')
            )
            .where(TeamInteraction.team_id == team_id)
            .group_by(TeamInteraction.interaction_type)
        )
        
        stats = {}
        for row in result:
            stats[row.interaction_type] = {
                'count': row.count,
                'avg_strength': float(row.avg_strength) if row.avg_strength else 0.0
            }
        
        return stats

    async def get_team_compatibility_summary(
        self, db: AsyncSession, team_id: int
    ) -> Dict[str, Any]:
        """チームの相性サマリーを取得"""
        result = await db.execute(
            select(
                func.avg(TeamCompatibility.overall_compatibility).label('avg_compatibility'),
                func.min(TeamCompatibility.overall_compatibility).label('min_compatibility'),
                func.max(TeamCompatibility.overall_compatibility).label('max_compatibility'),
                func.count(TeamCompatibility.id).label('total_pairs')
            )
            .where(TeamCompatibility.team_id == team_id)
        )
        
        row = result.first()
        return {
            'avg_compatibility': float(row.avg_compatibility) if row.avg_compatibility else 0.0,
            'min_compatibility': float(row.min_compatibility) if row.min_compatibility else 0.0,
            'max_compatibility': float(row.max_compatibility) if row.max_compatibility else 0.0,
            'total_pairs': row.total_pairs
        }

    async def get_team_cohesion_trend(
        self, db: AsyncSession, team_id: int, days: int = 30
    ) -> List[Dict[str, Any]]:
        """チームの結束力トレンドを取得"""
        result = await db.execute(
            select(
                func.date(TeamCohesion.analysis_date).label('date'),
                func.avg(TeamCohesion.cohesion_score).label('avg_score')
            )
            .where(TeamCohesion.team_id == team_id)
            .group_by(func.date(TeamCohesion.analysis_date))
            .order_by(func.date(TeamCohesion.analysis_date))
        )
        
        trend = []
        for row in result:
            trend.append({
                'date': row.date.isoformat(),
                'avg_score': float(row.avg_score) if row.avg_score else 0.0
            })
        
        return trend


# シングルトンインスタンス
team_dynamics_repository = TeamDynamicsRepository()
