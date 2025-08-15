from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, asc, func
from datetime import datetime, date, timedelta
import structlog

from app.models.audit_log import AuditLog
from app.repositories.base import BaseRepository

logger = structlog.get_logger()


class AuditLogRepository(BaseRepository[AuditLog, Any, Any]):
    """監査ログリポジトリ"""

    def __init__(self):
        super().__init__(AuditLog)

    async def get_audit_logs(
        self, db: AsyncSession, filter_params: Any
    ) -> List[AuditLog]:
        """監査ログ一覧を取得"""
        try:
            query = select(AuditLog)
            
            # フィルター条件を適用
            if filter_params:
                conditions = []
                
                if filter_params.action:
                    conditions.append(AuditLog.action == filter_params.action)
                
                if filter_params.resource_type:
                    conditions.append(AuditLog.resource_type == filter_params.resource_type)
                
                if filter_params.user_id:
                    conditions.append(AuditLog.user_id == filter_params.user_id)
                
                if conditions:
                    query = query.where(and_(*conditions))
            
            # 作成日時で降順ソート
            query = query.order_by(desc(AuditLog.created_at))
            
            # ページネーション
            if filter_params:
                offset = (filter_params.page - 1) * filter_params.size
                query = query.offset(offset).limit(filter_params.size)
            
            result = await db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Failed to get audit logs: {str(e)}")
            raise

    async def count_audit_logs(
        self, db: AsyncSession, filter_params: Any
    ) -> int:
        """監査ログ数をカウント"""
        try:
            query = select(func.count(AuditLog.id))
            
            # フィルター条件を適用
            if filter_params:
                conditions = []
                
                if filter_params.action:
                    conditions.append(AuditLog.action == filter_params.action)
                
                if filter_params.resource_type:
                    conditions.append(AuditLog.resource_type == filter_params.resource_type)
                
                if filter_params.user_id:
                    conditions.append(AuditLog.user_id == filter_params.user_id)
                
                if conditions:
                    query = query.where(and_(*conditions))
            
            result = await db.execute(query)
            return result.scalar()
            
        except Exception as e:
            logger.error(f"Failed to count audit logs: {str(e)}")
            raise

    async def get_user_audit_logs(
        self, db: AsyncSession, user_id: int, limit: int
    ) -> List[AuditLog]:
        """特定ユーザーの監査ログを取得"""
        try:
            query = (
                select(AuditLog)
                .where(AuditLog.user_id == user_id)
                .order_by(desc(AuditLog.created_at))
                .limit(limit)
            )
            
            result = await db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Failed to get user audit logs: {str(e)}")
            raise

    async def count_logs_by_date(
        self, db: AsyncSession, target_date: date, user_id: Optional[int] = None
    ) -> int:
        """特定日付のログ数をカウント"""
        try:
            start_datetime = datetime.combine(target_date, datetime.min.time())
            end_datetime = datetime.combine(target_date, datetime.max.time())
            
            query = select(func.count(AuditLog.id)).where(
                and_(
                    AuditLog.created_at >= start_datetime,
                    AuditLog.created_at <= end_datetime
                )
            )
            
            if user_id:
                query = query.where(AuditLog.user_id == user_id)
            
            result = await db.execute(query)
            return result.scalar()
            
        except Exception as e:
            logger.error(f"Failed to count logs by date: {str(e)}")
            raise

    async def count_logs_since(
        self, db: AsyncSession, since_datetime: datetime, user_id: Optional[int] = None
    ) -> int:
        """特定日時以降のログ数をカウント"""
        try:
            query = select(func.count(AuditLog.id)).where(
                AuditLog.created_at >= since_datetime
            )
            
            if user_id:
                query = query.where(AuditLog.user_id == user_id)
            
            result = await db.execute(query)
            return result.scalar()
            
        except Exception as e:
            logger.error(f"Failed to count logs since: {str(e)}")
            raise

    async def get_action_counts(
        self, db: AsyncSession, user_id: Optional[int] = None
    ) -> Dict[str, int]:
        """アクション別カウントを取得"""
        try:
            query = (
                select(AuditLog.action, func.count(AuditLog.id))
                .group_by(AuditLog.action)
                .order_by(desc(func.count(AuditLog.id)))
            )
            
            if user_id:
                query = query.where(AuditLog.user_id == user_id)
            
            result = await db.execute(query)
            return dict(result.all())
            
        except Exception as e:
            logger.error(f"Failed to get action counts: {str(e)}")
            raise

    async def get_resource_type_counts(
        self, db: AsyncSession, user_id: Optional[int] = None
    ) -> Dict[str, int]:
        """リソースタイプ別カウントを取得"""
        try:
            query = (
                select(AuditLog.resource_type, func.count(AuditLog.id))
                .group_by(AuditLog.resource_type)
                .order_by(desc(func.count(AuditLog.id)))
            )
            
            if user_id:
                query = query.where(AuditLog.user_id == user_id)
            
            result = await db.execute(query)
            return dict(result.all())
            
        except Exception as e:
            logger.error(f"Failed to get resource type counts: {str(e)}")
            raise

    async def get_user_action_counts(
        self, db: AsyncSession, user_id: Optional[int] = None
    ) -> Dict[str, int]:
        """ユーザー別アクションカウントを取得"""
        try:
            query = (
                select(AuditLog.user_id, func.count(AuditLog.id))
                .where(AuditLog.user_id.isnot(None))
                .group_by(AuditLog.user_id)
                .order_by(desc(func.count(AuditLog.id)))
            )
            
            if user_id:
                query = query.where(AuditLog.user_id == user_id)
            
            result = await db.execute(query)
            return {str(uid): count for uid, count in result.all()}
            
        except Exception as e:
            logger.error(f"Failed to get user action counts: {str(e)}")
            raise

    async def delete_logs_before(
        self, db: AsyncSession, cutoff_datetime: datetime
    ) -> int:
        """特定日時以前のログを削除"""
        try:
            query = (
                select(AuditLog)
                .where(AuditLog.created_at < cutoff_datetime)
            )
            
            result = await db.execute(query)
            logs_to_delete = result.scalars().all()
            
            deleted_count = 0
            for log in logs_to_delete:
                await db.delete(log)
                deleted_count += 1
            
            await db.commit()
            logger.info(f"Deleted {deleted_count} audit logs before {cutoff_datetime}")
            return deleted_count
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to delete logs before: {str(e)}")
            raise

    async def search_audit_logs(
        self, db: AsyncSession, search_term: str, limit: int = 100
    ) -> List[AuditLog]:
        """監査ログを検索"""
        try:
            query = (
                select(AuditLog)
                .where(
                    or_(
                        AuditLog.action.ilike(f"%{search_term}%"),
                        AuditLog.resource_type.ilike(f"%{search_term}%"),
                        AuditLog.description.ilike(f"%{search_term}%"),
                        AuditLog.user_email.ilike(f"%{search_term}%")
                    )
                )
                .order_by(desc(AuditLog.created_at))
                .limit(limit)
            )
            
            result = await db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Failed to search audit logs: {str(e)}")
            raise

    async def get_recent_activity(
        self, db: AsyncSession, hours: int = 24, limit: int = 50
    ) -> List[AuditLog]:
        """最近のアクティビティを取得"""
        try:
            since_datetime = datetime.utcnow() - timedelta(hours=hours)
            
            query = (
                select(AuditLog)
                .where(AuditLog.created_at >= since_datetime)
                .order_by(desc(AuditLog.created_at))
                .limit(limit)
            )
            
            result = await db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Failed to get recent activity: {str(e)}")
            raise


# シングルトンインスタンス
audit_log_repository = AuditLogRepository()
