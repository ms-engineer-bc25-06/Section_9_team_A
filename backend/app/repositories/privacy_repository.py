from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, asc, func
from sqlalchemy.orm import selectinload
import structlog

from app.models.privacy import (
    PrivacyLevel,
    DataCategory,
    EncryptedData,
    DataAccessPermission,
    PrivacySettings,
    DataRetentionPolicy,
    PrivacyAuditLog,
)
from app.repositories.base import BaseRepository

logger = structlog.get_logger()


class PrivacyRepository(BaseRepository[Any, Any, Any]):
    """プライバシーリポジトリ"""

    def __init__(self):
        super().__init__(EncryptedData)  # デフォルトモデル

    # EncryptedData 関連メソッド
    async def get_encrypted_data_by_id(
        self, db: AsyncSession, data_id: str
    ) -> Optional[EncryptedData]:
        """データIDで暗号化データを取得"""
        result = await db.execute(
            select(EncryptedData).where(EncryptedData.data_id == data_id)
        )
        return result.scalar_one_or_none()

    async def get_user_encrypted_data(
        self, db: AsyncSession, user_id: int, category: Optional[DataCategory] = None
    ) -> List[EncryptedData]:
        """ユーザーの暗号化データを取得"""
        query = select(EncryptedData).where(EncryptedData.owner_id == user_id)
        
        if category:
            query = query.where(EncryptedData.data_category == category)
        
        result = await db.execute(query.order_by(desc(EncryptedData.created_at)))
        return result.scalars().all()

    async def get_data_by_privacy_level(
        self, db: AsyncSession, privacy_level: PrivacyLevel, limit: int = 100
    ) -> List[EncryptedData]:
        """プライバシーレベル別にデータを取得"""
        result = await db.execute(
            select(EncryptedData)
            .where(EncryptedData.privacy_level == privacy_level)
            .order_by(desc(EncryptedData.created_at))
            .limit(limit)
        )
        return result.scalars().all()

    async def create_encrypted_data(
        self, db: AsyncSession, data: Dict[str, Any]
    ) -> EncryptedData:
        """暗号化データを作成"""
        db_data = EncryptedData(**data)
        db.add(db_data)
        await db.commit()
        await db.refresh(db_data)
        return db_data

    async def update_encrypted_data(
        self, db: AsyncSession, data_id: str, update_data: Dict[str, Any]
    ) -> Optional[EncryptedData]:
        """暗号化データを更新"""
        data = await self.get_encrypted_data_by_id(db, data_id)
        if not data:
            return None
        
        for field, value in update_data.items():
            if hasattr(data, field):
                setattr(data, field, value)
        
        await db.commit()
        await db.refresh(data)
        return data

    async def delete_encrypted_data(
        self, db: AsyncSession, data_id: str
    ) -> bool:
        """暗号化データを削除"""
        data = await self.get_encrypted_data_by_id(db, data_id)
        if not data:
            return False
        
        await db.delete(data)
        await db.commit()
        return True

    # DataAccessPermission 関連メソッド
    async def get_user_permissions(
        self, db: AsyncSession, user_id: int
    ) -> List[DataAccessPermission]:
        """ユーザーのアクセス権限を取得"""
        result = await db.execute(
            select(DataAccessPermission)
            .where(DataAccessPermission.user_id == user_id)
            .order_by(desc(DataAccessPermission.created_at))
        )
        return result.scalars().all()

    async def get_data_permissions(
        self, db: AsyncSession, data_id: int
    ) -> List[DataAccessPermission]:
        """データのアクセス権限を取得"""
        result = await db.execute(
            select(DataAccessPermission)
            .where(DataAccessPermission.encrypted_data_id == data_id)
            .order_by(DataAccessPermission.created_at)
        )
        return result.scalars().all()

    async def check_user_access(
        self, db: AsyncSession, user_id: int, data_id: int, required_permission: str = "read"
    ) -> bool:
        """ユーザーがデータにアクセスできるかチェック"""
        permission = await db.execute(
            select(DataAccessPermission)
            .where(
                and_(
                    DataAccessPermission.user_id == user_id,
                    DataAccessPermission.encrypted_data_id == data_id
                )
            )
        )
        
        perm = permission.scalar_one_or_none()
        if not perm or perm.is_expired:
            return False
        
        if required_permission == "read":
            return perm.can_read
        elif required_permission == "write":
            return perm.can_write
        elif required_permission == "delete":
            return perm.can_delete
        elif required_permission == "share":
            return perm.can_share
        
        return False

    async def grant_permission(
        self, db: AsyncSession, permission_data: Dict[str, Any]
    ) -> DataAccessPermission:
        """アクセス権限を付与"""
        db_permission = DataAccessPermission(**permission_data)
        db.add(db_permission)
        await db.commit()
        await db.refresh(db_permission)
        return db_permission

    async def revoke_permission(
        self, db: AsyncSession, permission_id: int
    ) -> bool:
        """アクセス権限を削除"""
        permission = await db.get(DataAccessPermission, permission_id)
        if not permission:
            return False
        
        await db.delete(permission)
        await db.commit()
        return True

    # PrivacySettings 関連メソッド
    async def get_user_privacy_settings(
        self, db: AsyncSession, user_id: int
    ) -> Optional[PrivacySettings]:
        """ユーザーのプライバシー設定を取得"""
        result = await db.execute(
            select(PrivacySettings).where(PrivacySettings.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_privacy_settings(
        self, db: AsyncSession, settings_data: Dict[str, Any]
    ) -> PrivacySettings:
        """プライバシー設定を作成"""
        db_settings = PrivacySettings(**settings_data)
        db.add(db_settings)
        await db.commit()
        await db.refresh(db_settings)
        return db_settings

    async def update_privacy_settings(
        self, db: AsyncSession, user_id: int, update_data: Dict[str, Any]
    ) -> Optional[PrivacySettings]:
        """プライバシー設定を更新"""
        settings = await self.get_user_privacy_settings(db, user_id)
        if not settings:
            return None
        
        for field, value in update_data.items():
            if hasattr(settings, field):
                setattr(settings, field, value)
        
        await db.commit()
        await db.refresh(settings)
        return settings

    # DataRetentionPolicy 関連メソッド
    async def get_active_retention_policies(
        self, db: AsyncSession, category: Optional[DataCategory] = None
    ) -> List[DataRetentionPolicy]:
        """アクティブな保持ポリシーを取得"""
        query = select(DataRetentionPolicy).where(DataRetentionPolicy.is_active == True)
        
        if category:
            query = query.where(DataRetentionPolicy.data_category == category)
        
        result = await db.execute(query.order_by(DataRetentionPolicy.retention_days))
        return result.scalars().all()

    async def get_policy_by_category(
        self, db: AsyncSession, category: DataCategory, user_role: Optional[str] = None
    ) -> Optional[DataRetentionPolicy]:
        """カテゴリ別の保持ポリシーを取得"""
        query = select(DataRetentionPolicy).where(
            and_(
                DataRetentionPolicy.data_category == category,
                DataRetentionPolicy.is_active == True
            )
        )
        
        if user_role:
            query = query.where(
                or_(
                    DataRetentionPolicy.user_role == user_role,
                    DataRetentionPolicy.user_role.is_(None)
                )
            )
        
        result = await db.execute(query)
        return result.scalar_one_or_none()

    # PrivacyAuditLog 関連メソッド
    async def create_audit_log(
        self, db: AsyncSession, log_data: Dict[str, Any]
    ) -> PrivacyAuditLog:
        """監査ログを作成"""
        db_log = PrivacyAuditLog(**log_data)
        db.add(db_log)
        await db.commit()
        await db.refresh(db_log)
        return db_log

    async def get_user_audit_logs(
        self, db: AsyncSession, user_id: int, limit: int = 100
    ) -> List[PrivacyAuditLog]:
        """ユーザーの監査ログを取得"""
        result = await db.execute(
            select(PrivacyAuditLog)
            .where(PrivacyAuditLog.user_id == user_id)
            .order_by(desc(PrivacyAuditLog.timestamp))
            .limit(limit)
        )
        return result.scalars().all()

    async def get_audit_logs_by_action(
        self, db: AsyncSession, action: str, limit: int = 100
    ) -> List[PrivacyAuditLog]:
        """アクション別の監査ログを取得"""
        result = await db.execute(
            select(PrivacyAuditLog)
            .where(PrivacyAuditLog.action == action)
            .order_by(desc(PrivacyAuditLog.timestamp))
            .limit(limit)
        )
        return result.scalars().all()

    # 分析・統計メソッド
    async def get_privacy_violations(
        self, db: AsyncSession, days: int = 30
    ) -> List[PrivacyAuditLog]:
        """プライバシー侵害の監査ログを取得"""
        result = await db.execute(
            select(PrivacyAuditLog)
            .where(
                and_(
                    PrivacyAuditLog.success == False,
                    PrivacyAuditLog.timestamp >= func.now() - func.interval(f'{days} days')
                )
            )
            .order_by(desc(PrivacyAuditLog.timestamp))
        )
        return result.scalars().all()

    async def get_data_access_stats(
        self, db: AsyncSession, user_id: int, days: int = 30
    ) -> Dict[str, Any]:
        """データアクセス統計を取得"""
        result = await db.execute(
            select(
                PrivacyAuditLog.action,
                func.count(PrivacyAuditLog.id).label('count'),
                func.avg(func.case((PrivacyAuditLog.success == True, 1), else_=0)).label('success_rate')
            )
            .where(
                and_(
                    PrivacyAuditLog.user_id == user_id,
                    PrivacyAuditLog.timestamp >= func.now() - func.interval(f'{days} days')
                )
            )
            .group_by(PrivacyAuditLog.action)
        )
        
        stats = {}
        for row in result:
            stats[row.action] = {
                'count': row.count,
                'success_rate': float(row.success_rate) if row.success_rate else 0.0
            }
        
        return stats

    async def get_expired_data_count(
        self, db: AsyncSession, user_id: Optional[int] = None
    ) -> int:
        """期限切れデータの数を取得"""
        query = select(EncryptedData.id).where(EncryptedData.expires_at < func.now())
        
        if user_id:
            query = query.where(EncryptedData.owner_id == user_id)
        
        result = await db.execute(query)
        return len(result.scalars().all())

    async def get_privacy_level_distribution(
        self, db: AsyncSession
    ) -> Dict[str, int]:
        """プライバシーレベルの分布を取得"""
        result = await db.execute(
            select(
                EncryptedData.privacy_level,
                func.count(EncryptedData.id).label('count')
            )
            .group_by(EncryptedData.privacy_level)
        )
        
        distribution = {}
        for row in result:
            if row.privacy_level:
                distribution[row.privacy_level.value] = row.count
        
        return distribution


# シングルトンインスタンス
privacy_repository = PrivacyRepository()
