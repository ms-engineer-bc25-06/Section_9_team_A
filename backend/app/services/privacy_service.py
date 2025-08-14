import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

from app.models.user import User
from app.models.privacy import (
    EncryptedData, DataAccessPermission, PrivacySettings, 
    DataRetentionPolicy, PrivacyAuditLog, PrivacyLevel, DataCategory
)
from app.core.exceptions import PrivacyError, AccessDeniedError
from app.config import settings

logger = structlog.get_logger()

class PrivacyService:
    """プライバシー制御サービス"""
    
    def __init__(self):
        self.master_key = self._get_or_generate_master_key()
        
    def _get_or_generate_master_key(self) -> bytes:
        """マスターキーの取得または生成"""
        if hasattr(settings, 'MASTER_ENCRYPTION_KEY') and settings.MASTER_ENCRYPTION_KEY:
            return base64.urlsafe_b64decode(settings.MASTER_ENCRYPTION_KEY)
        else:
            # 開発環境用のデフォルトキー（本番環境では環境変数から取得）
            return Fernet.generate_key()
    
    def _generate_encryption_key(self, user_id: int, salt: bytes = None) -> tuple[bytes, bytes]:
        """ユーザー固有の暗号化キーを生成"""
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(str(user_id).encode()))
        return key, salt
    
    async def encrypt_data(
        self,
        db: AsyncSession,
        user: User,
        data: Union[str, dict],
        data_type: str,
        data_category: DataCategory,
        privacy_level: PrivacyLevel = PrivacyLevel.PRIVATE,
        expires_at: Optional[datetime] = None
    ) -> EncryptedData:
        """データを暗号化して保存"""
        try:
            # データをJSON文字列に変換
            if isinstance(data, dict):
                data_str = json.dumps(data, ensure_ascii=False)
            else:
                data_str = str(data)
            
            # 暗号化キーを生成
            encryption_key, salt = self._generate_encryption_key(user.id)
            fernet = Fernet(encryption_key)
            
            # データを暗号化
            encrypted_content = fernet.encrypt(data_str.encode('utf-8'))
            
            # 暗号化データを保存
            encrypted_data = EncryptedData(
                data_id=str(uuid.uuid4()),
                data_type=data_type,
                data_category=data_category,
                encrypted_content=base64.urlsafe_b64encode(encrypted_content).decode(),
                encryption_algorithm="Fernet",
                encryption_key_id=base64.urlsafe_b64encode(salt).decode(),
                iv=base64.urlsafe_b64encode(salt).decode(),  # FernetではIVは不要だが、互換性のため
                original_size=len(data_str),
                owner_id=user.id,
                privacy_level=privacy_level,
                expires_at=expires_at
            )
            
            db.add(encrypted_data)
            await db.commit()
            await db.refresh(encrypted_data)
            
            logger.info(
                "データ暗号化完了",
                user_id=user.id,
                data_id=encrypted_data.data_id,
                data_type=data_type,
                privacy_level=privacy_level.value
            )
            
            return encrypted_data
            
        except Exception as e:
            logger.error("データ暗号化でエラー", error=str(e), user_id=user.id)
            raise PrivacyError(f"データの暗号化に失敗しました: {str(e)}")
    
    async def decrypt_data(
        self,
        db: AsyncSession,
        user: User,
        encrypted_data: EncryptedData,
        requesting_user: User
    ) -> Union[str, dict]:
        """暗号化データを復号化"""
        try:
            # アクセス権限をチェック
            if not await self._check_access_permission(
                db, requesting_user, encrypted_data, "read"
            ):
                raise AccessDeniedError("このデータへのアクセス権限がありません")
            
            # 暗号化キーを再構築
            salt = base64.urlsafe_b64decode(encrypted_data.encryption_key_id)
            encryption_key, _ = self._generate_encryption_key(encrypted_data.owner_id, salt)
            fernet = Fernet(encryption_key)
            
            # データを復号化
            encrypted_content = base64.urlsafe_b64decode(encrypted_data.encrypted_content)
            decrypted_content = fernet.decrypt(encrypted_content).decode('utf-8')
            
            # JSONとして解析を試行
            try:
                return json.loads(decrypted_content)
            except json.JSONDecodeError:
                return decrypted_content
            
        except Exception as e:
            logger.error("データ復号化でエラー", error=str(e), user_id=user.id)
            raise PrivacyError(f"データの復号化に失敗しました: {str(e)}")
    
    async def _check_access_permission(
        self,
        db: AsyncSession,
        requesting_user: User,
        encrypted_data: EncryptedData,
        action: str
    ) -> bool:
        """アクセス権限をチェック"""
        # 所有者は常にアクセス可能
        if requesting_user.id == encrypted_data.owner_id:
            return True
        
        # 管理者は常にアクセス可能
        if requesting_user.is_admin:
            return True
        
        # プライバシーレベルに基づく権限チェック
        if encrypted_data.privacy_level == PrivacyLevel.PUBLIC:
            return True
        
        elif encrypted_data.privacy_level == PrivacyLevel.TEAM:
            # 同じチームのメンバーかチェック
            return await self._check_team_membership(db, requesting_user, encrypted_data.owner_id)
        
        elif encrypted_data.privacy_level == PrivacyLevel.MANAGER:
            # マネージャー権限かチェック
            return await self._check_manager_role(db, requesting_user, encrypted_data.owner_id)
        
        elif encrypted_data.privacy_level == PrivacyLevel.PRIVATE:
            return False
        
        # 明示的な権限設定をチェック
        return await self._check_explicit_permission(
            db, requesting_user, encrypted_data, action
        )
    
    async def _check_team_membership(
        self, db: AsyncSession, user: User, owner_id: int
    ) -> bool:
        """チームメンバーシップをチェック"""
        # 簡易実装 - 実際のチームモデルに合わせて調整が必要
        try:
            # 同じチームに所属しているかチェック
            # ここでは仮の実装
            return True
        except Exception:
            return False
    
    async def _check_manager_role(
        self, db: AsyncSession, user: User, owner_id: int
    ) -> bool:
        """マネージャー権限をチェック"""
        # 簡易実装 - 実際のロールモデルに合わせて調整が必要
        try:
            # マネージャーロールを持っているかチェック
            return user.is_admin  # 仮の実装
        except Exception:
            return False
    
    async def _check_explicit_permission(
        self,
        db: AsyncSession,
        user: User,
        encrypted_data: EncryptedData,
        action: str
    ) -> bool:
        """明示的な権限設定をチェック"""
        try:
            query = select(DataAccessPermission).where(
                and_(
                    DataAccessPermission.encrypted_data_id == encrypted_data.id,
                    DataAccessPermission.user_id == user.id,
                    DataAccessPermission.is_active == True,
                    or_(
                        DataAccessPermission.expires_at.is_(None),
                        DataAccessPermission.expires_at > datetime.utcnow()
                    )
                )
            )
            
            result = await db.execute(query)
            permission = result.scalar_one_or_none()
            
            if not permission:
                return False
            
            # アクションに応じた権限チェック
            if action == "read":
                return permission.can_read
            elif action == "write":
                return permission.can_write
            elif action == "delete":
                return permission.can_delete
            elif action == "share":
                return permission.can_share
            
            return False
            
        except Exception:
            return False
    
    async def grant_access_permission(
        self,
        db: AsyncSession,
        owner: User,
        target_user: User,
        encrypted_data: EncryptedData,
        permissions: Dict[str, bool],
        expires_at: Optional[datetime] = None
    ) -> DataAccessPermission:
        """アクセス権限を付与"""
        try:
            # 権限付与の権限チェック
            if not await self._check_access_permission(db, owner, encrypted_data, "share"):
                raise AccessDeniedError("権限付与の権限がありません")
            
            # 既存の権限をチェック
            existing_permission = await self._get_existing_permission(
                db, target_user.id, encrypted_data.id
            )
            
            if existing_permission:
                # 既存の権限を更新
                existing_permission.can_read = permissions.get("read", existing_permission.can_read)
                existing_permission.can_write = permissions.get("write", existing_permission.can_write)
                existing_permission.can_delete = permissions.get("delete", existing_permission.can_delete)
                existing_permission.can_share = permissions.get("share", existing_permission.can_share)
                existing_permission.expires_at = expires_at
                existing_permission.updated_at = datetime.utcnow()
                
                await db.commit()
                await db.refresh(existing_permission)
                
                return existing_permission
            else:
                # 新しい権限を作成
                new_permission = DataAccessPermission(
                    encrypted_data_id=encrypted_data.id,
                    user_id=target_user.id,
                    access_level=encrypted_data.privacy_level,
                    can_read=permissions.get("read", False),
                    can_write=permissions.get("write", False),
                    can_delete=permissions.get("delete", False),
                    can_share=permissions.get("share", False),
                    expires_at=expires_at,
                    granted_by=owner.id
                )
                
                db.add(new_permission)
                await db.commit()
                await db.refresh(new_permission)
                
                return new_permission
                
        except Exception as e:
            logger.error("権限付与でエラー", error=str(e), owner_id=owner.id, target_user_id=target_user.id)
            raise PrivacyError(f"権限の付与に失敗しました: {str(e)}")
    
    async def _get_existing_permission(
        self, db: AsyncSession, user_id: int, encrypted_data_id: int
    ) -> Optional[DataAccessPermission]:
        """既存の権限を取得"""
        try:
            query = select(DataAccessPermission).where(
                and_(
                    DataAccessPermission.user_id == user_id,
                    DataAccessPermission.encrypted_data_id == encrypted_data_id
                )
            )
            
            result = await db.execute(query)
            return result.scalar_one_or_none()
            
        except Exception:
            return None
    
    async def revoke_access_permission(
        self,
        db: AsyncSession,
        owner: User,
        target_user: User,
        encrypted_data: EncryptedData
    ) -> bool:
        """アクセス権限を削除"""
        try:
            # 権限削除の権限チェック
            if not await self._check_access_permission(db, owner, encrypted_data, "share"):
                raise AccessDeniedError("権限削除の権限がありません")
            
            # 既存の権限を取得
            existing_permission = await self._get_existing_permission(
                db, target_user.id, encrypted_data.id
            )
            
            if existing_permission:
                await db.delete(existing_permission)
                await db.commit()
                
                logger.info(
                    "アクセス権限削除完了",
                    owner_id=owner.id,
                    target_user_id=target_user.id,
                    data_id=encrypted_data.data_id
                )
                
                return True
            
            return False
            
        except Exception as e:
            logger.error("権限削除でエラー", error=str(e), owner_id=owner.id, target_user_id=target_user.id)
            raise PrivacyError(f"権限の削除に失敗しました: {str(e)}")
    
    async def get_privacy_settings(
        self, db: AsyncSession, user: User
    ) -> PrivacySettings:
        """ユーザーのプライバシー設定を取得"""
        try:
            query = select(PrivacySettings).where(PrivacySettings.user_id == user.id)
            result = await db.execute(query)
            settings = result.scalar_one_or_none()
            
            if not settings:
                # デフォルト設定を作成
                settings = PrivacySettings(user_id=user.id)
                db.add(settings)
                await db.commit()
                await db.refresh(settings)
            
            return settings
            
        except Exception as e:
            logger.error("プライバシー設定取得でエラー", error=str(e), user_id=user.id)
            raise PrivacyError(f"プライバシー設定の取得に失敗しました: {str(e)}")
    
    async def update_privacy_settings(
        self,
        db: AsyncSession,
        user: User,
        settings_update: Dict[str, Any]
    ) -> PrivacySettings:
        """プライバシー設定を更新"""
        try:
            settings = await self.get_privacy_settings(db, user)
            
            # 更新可能なフィールドのみ更新
            updatable_fields = [
                'default_profile_privacy', 'default_analysis_privacy',
                'default_goals_privacy', 'default_improvement_privacy',
                'auto_delete_after_days', 'auto_delete_enabled',
                'allow_team_sharing', 'allow_manager_access',
                'allow_anonymous_analytics', 'notify_on_access', 'notify_on_breach'
            ]
            
            for field in updatable_fields:
                if field in settings_update:
                    setattr(settings, field, settings_update[field])
            
            settings.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(settings)
            
            logger.info(
                "プライバシー設定更新完了",
                user_id=user.id,
                updated_fields=list(settings_update.keys())
            )
            
            return settings
            
        except Exception as e:
            logger.error("プライバシー設定更新でエラー", error=str(e), user_id=user.id)
            raise PrivacyError(f"プライバシー設定の更新に失敗しました: {str(e)}")
    
    async def log_privacy_action(
        self,
        db: AsyncSession,
        user: User,
        action: str,
        data_id: Optional[str] = None,
        action_details: Optional[Dict[str, Any]] = None,
        accessed_by: Optional[User] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> PrivacyAuditLog:
        """プライバシー関連のアクションをログに記録"""
        try:
            audit_log = PrivacyAuditLog(
                user_id=user.id,
                data_id=data_id,
                action=action,
                action_details=action_details,
                accessed_by=accessed_by.id if accessed_by else None,
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                error_message=error_message
            )
            
            db.add(audit_log)
            await db.commit()
            await db.refresh(audit_log)
            
            return audit_log
            
        except Exception as e:
            logger.error("監査ログ記録でエラー", error=str(e), user_id=user.id)
            # 監査ログの記録に失敗しても、メインの処理は継続
            return None
    
    async def cleanup_expired_data(self, db: AsyncSession) -> int:
        """期限切れデータの自動削除"""
        try:
            # 期限切れのデータを検索
            expired_data = await self._get_expired_data(db)
            
            deleted_count = 0
            for data in expired_data:
                try:
                    await db.delete(data)
                    deleted_count += 1
                    
                    # 監査ログに記録
                    await self.log_privacy_action(
                        db, data.owner, "auto_delete",
                        data_id=data.data_id,
                        action_details={"reason": "expired", "expired_at": data.expires_at.isoformat()},
                        success=True
                    )
                    
                except Exception as e:
                    logger.error(f"データ削除でエラー: {str(e)}", data_id=data.data_id)
            
            await db.commit()
            
            logger.info(f"期限切れデータ削除完了: {deleted_count}件")
            return deleted_count
            
        except Exception as e:
            logger.error("期限切れデータ削除でエラー", error=str(e))
            raise PrivacyError(f"期限切れデータの削除に失敗しました: {str(e)}")
    
    async def _get_expired_data(self, db: AsyncSession) -> List[EncryptedData]:
        """期限切れのデータを取得"""
        try:
            query = select(EncryptedData).where(
                and_(
                    EncryptedData.expires_at.isnot(None),
                    EncryptedData.expires_at < datetime.utcnow()
                )
            )
            
            result = await db.execute(query)
            return result.scalars().all()
            
        except Exception:
            return []
