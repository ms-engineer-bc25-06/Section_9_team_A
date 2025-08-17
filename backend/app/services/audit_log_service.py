from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, asc, func
from datetime import datetime, timedelta
import structlog

from app.models.audit_log import AuditLog
from app.repositories.audit_log_repository import audit_log_repository
from app.schemas.audit_log import (
    AuditLogFilter,
    AuditLogStats,
    SystemAuditLogCreate,
    UserAuditLogCreate,
)

logger = structlog.get_logger()


class AuditLogService:
    """監査ログサービス"""

    async def get_audit_logs(
        self, db: AsyncSession, filter_params: AuditLogFilter, current_user: Any
    ) -> Dict[str, Any]:
        """監査ログ一覧を取得"""
        try:
            # 管理者でない場合は自分のログのみ
            if not current_user.is_superuser:
                filter_params.user_id = current_user.id

            audit_logs = await audit_log_repository.get_audit_logs(
                db, filter_params
            )
            
            total = await audit_log_repository.count_audit_logs(db, filter_params)
            
            return {
                "audit_logs": audit_logs,
                "total": total,
                "page": filter_params.page,
                "size": filter_params.size
            }
        except Exception as e:
            logger.error(f"Failed to get audit logs: {str(e)}")
            raise

    async def get_audit_log(
        self, db: AsyncSession, audit_log_id: int, current_user: Any
    ) -> Optional[AuditLog]:
        """特定の監査ログを取得"""
        try:
            audit_log = await audit_log_repository.get(db, audit_log_id)
            
            if not audit_log:
                return None
            
            # 管理者でない場合は自分のログのみアクセス可能
            if not current_user.is_superuser and audit_log.user_id != current_user.id:
                return None
            
            return audit_log
        except Exception as e:
            logger.error(f"Failed to get audit log: {str(e)}")
            raise

    async def create_system_log(
        self, db: AsyncSession, audit_log_data: SystemAuditLogCreate
    ) -> AuditLog:
        """システム監査ログを作成"""
        try:
            audit_log = AuditLog.create_system_log(
                action=audit_log_data.action,
                resource_type=audit_log_data.resource_type,
                description=audit_log_data.description,
                details=audit_log_data.details
            )
            
            result = await audit_log_repository.create(db, audit_log)
            logger.info(f"System audit log created: {audit_log.action} on {audit_log.resource_type}")
            return result
        except Exception as e:
            logger.error(f"Failed to create system audit log: {str(e)}")
            raise

    async def create_user_log(
        self, db: AsyncSession, audit_log_data: UserAuditLogCreate
    ) -> AuditLog:
        """ユーザー監査ログを作成"""
        try:
            audit_log = AuditLog.create_user_log(
                user_id=audit_log_data.user_id,
                action=audit_log_data.action,
                resource_type=audit_log_data.resource_type,
                description=audit_log_data.description,
                details=audit_log_data.details
            )
            
            # 追加情報を設定
            if audit_log_data.user_ip:
                audit_log.user_ip = audit_log_data.user_ip
            if audit_log_data.session_id:
                audit_log.session_id = audit_log_data.session_id
            if audit_log_data.user_agent:
                audit_log.user_agent = audit_log_data.user_agent
            
            result = await audit_log_repository.create(db, audit_log)
            logger.info(f"User audit log created: {audit_log.action} by user {audit_log.user_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to create user audit log: {str(e)}")
            raise

    async def get_audit_log_stats(
        self, db: AsyncSession, current_user: Any
    ) -> AuditLogStats:
        """監査ログ統計を取得"""
        try:
            # 管理者でない場合は自分のログのみ
            user_filter = None
            if not current_user.is_superuser:
                user_filter = current_user.id

            total_logs = await audit_log_repository.count_audit_logs(db, None)
            
            # 今日のログ数
            today = datetime.utcnow().date()
            logs_today = await audit_log_repository.count_logs_by_date(db, today, user_filter)
            
            # 今週のログ数
            week_ago = datetime.utcnow() - timedelta(days=7)
            logs_this_week = await audit_log_repository.count_logs_since(db, week_ago, user_filter)
            
            # 今月のログ数
            month_ago = datetime.utcnow() - timedelta(days=30)
            logs_this_month = await audit_log_repository.count_logs_since(db, month_ago, user_filter)
            
            # アクション別カウント
            action_counts = await audit_log_repository.get_action_counts(db, user_filter)
            
            # リソースタイプ別カウント
            resource_type_counts = await audit_log_repository.get_resource_type_counts(db, user_filter)
            
            # ユーザー別アクションカウント
            user_action_counts = await audit_log_repository.get_user_action_counts(db, user_filter)
            
            return AuditLogStats(
                total_logs=total_logs,
                logs_today=logs_today,
                logs_this_week=logs_this_week,
                logs_this_month=logs_this_month,
                action_counts=action_counts,
                resource_type_counts=resource_type_counts,
                user_action_counts=user_action_counts
            )
        except Exception as e:
            logger.error(f"Failed to get audit log stats: {str(e)}")
            raise

    async def get_user_audit_logs(
        self, db: AsyncSession, user_id: int, limit: int
    ) -> List[AuditLog]:
        """特定ユーザーの監査ログを取得"""
        try:
            audit_logs = await audit_log_repository.get_user_audit_logs(db, user_id, limit)
            return audit_logs
        except Exception as e:
            logger.error(f"Failed to get user audit logs: {str(e)}")
            raise

    async def delete_audit_log(
        self, db: AsyncSession, audit_log_id: int
    ) -> bool:
        """監査ログを削除"""
        try:
            success = await audit_log_repository.delete(db, audit_log_id)
            if success:
                logger.info(f"Audit log deleted: {audit_log_id}")
            return success
        except Exception as e:
            logger.error(f"Failed to delete audit log: {str(e)}")
            raise

    async def cleanup_old_logs(
        self, db: AsyncSession, days_to_keep: int = 365
    ) -> int:
        """古いログをクリーンアップ"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            deleted_count = await audit_log_repository.delete_logs_before(db, cutoff_date)
            logger.info(f"Cleaned up {deleted_count} old audit logs")
            return deleted_count
        except Exception as e:
            logger.error(f"Failed to cleanup old logs: {str(e)}")
            raise

    async def export_audit_logs(
        self, db: AsyncSession, filter_params: AuditLogFilter, format: str = "json"
    ) -> Any:
        """監査ログをエクスポート"""
        try:
            audit_logs = await audit_log_repository.get_audit_logs(db, filter_params)
            
            if format == "json":
                return audit_logs
            elif format == "csv":
                # CSV形式でのエクスポート実装
                return self._convert_to_csv(audit_logs)
            else:
                raise ValueError(f"Unsupported export format: {format}")
        except Exception as e:
            logger.error(f"Failed to export audit logs: {str(e)}")
            raise

    def _convert_to_csv(self, audit_logs: List[AuditLog]) -> str:
        """監査ログをCSV形式に変換"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # ヘッダー
        writer.writerow([
            "ID", "Log ID", "Action", "Resource Type", "Resource ID",
            "User ID", "User Email", "User IP", "Description",
            "Session ID", "User Agent", "Created At"
        ])
        
        # データ
        for log in audit_logs:
            writer.writerow([
                log.id, log.log_id, log.action, log.resource_type, log.resource_id,
                log.user_id, log.user_email, log.user_ip, log.description,
                log.session_id, log.user_agent, log.created_at
            ])
        
        return output.getvalue()


# シングルトンインスタンス
audit_log_service = AuditLogService()
