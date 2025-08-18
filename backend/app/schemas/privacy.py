from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field
from enum import Enum

from .common import TimestampMixin


class PrivacyLevel(str, Enum):
    """プライバシーレベル"""
    PUBLIC = "public"
    TEAM = "team"
    PRIVATE = "private"
    CONFIDENTIAL = "confidential"


class DataCategory(str, Enum):
    """データカテゴリ"""
    PROFILE = "profile"
    ANALYSIS = "analysis"
    GOALS = "goals"
    PROGRESS = "progress"
    COMMUNICATION = "communication"
    PERFORMANCE = "performance"
    PERSONAL = "personal"


class AccessPermission(str, Enum):
    """アクセス権限"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


class PrivacySettingsBase(BaseModel):
    """プライバシー設定ベース"""
    user_id: int = Field(..., description="ユーザーID")
    profile_visibility: PrivacyLevel = Field(default=PrivacyLevel.TEAM, description="プロフィールの可視性")
    analysis_visibility: PrivacyLevel = Field(default=PrivacyLevel.PRIVATE, description="分析結果の可視性")
    goals_visibility: PrivacyLevel = Field(default=PrivacyLevel.PRIVATE, description="目標の可視性")
    progress_visibility: PrivacyLevel = Field(default=PrivacyLevel.TEAM, description="進捗の可視性")
    communication_visibility: PrivacyLevel = Field(default=PrivacyLevel.TEAM, description="コミュニケーションの可視性")
    allow_team_access: bool = Field(default=True, description="チームメンバーからのアクセスを許可")
    allow_manager_access: bool = Field(default=True, description="マネージャーからのアクセスを許可")
    allow_hr_access: bool = Field(default=False, description="HRからのアクセスを許可")
    data_retention_days: int = Field(default=365, description="データ保持日数")
    auto_delete_enabled: bool = Field(default=True, description="自動削除を有効化")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PrivacySettingsCreate(PrivacySettingsBase):
    """プライバシー設定作成"""
    pass


class PrivacySettingsUpdate(BaseModel):
    """プライバシー設定更新"""
    profile_visibility: Optional[PrivacyLevel] = Field(None, description="プロフィールの可視性")
    analysis_visibility: Optional[PrivacyLevel] = Field(None, description="分析結果の可視性")
    goals_visibility: Optional[PrivacyLevel] = Field(None, description="目標の可視性")
    progress_visibility: Optional[PrivacyLevel] = Field(None, description="進捗の可視性")
    communication_visibility: Optional[PrivacyLevel] = Field(None, description="コミュニケーションの可視性")
    allow_team_access: Optional[bool] = Field(None, description="チームメンバーからのアクセスを許可")
    allow_manager_access: Optional[bool] = Field(None, description="マネージャーからのアクセスを許可")
    allow_hr_access: Optional[bool] = Field(None, description="HRからのアクセスを許可")
    data_retention_days: Optional[int] = Field(None, description="データ保持日数")
    auto_delete_enabled: Optional[bool] = Field(None, description="自動削除を有効化")


class PrivacySettingsResponse(PrivacySettingsBase):
    """プライバシー設定レスポンス"""
    id: int = Field(..., description="プライバシー設定ID")


class DataAccessPermissionBase(BaseModel):
    """データアクセス権限ベース"""
    user_id: int = Field(..., description="ユーザーID")
    granted_to_user_id: int = Field(..., description="権限を付与されたユーザーID")
    data_category: DataCategory = Field(..., description="データカテゴリ")
    permission_level: AccessPermission = Field(..., description="権限レベル")
    granted_by_user_id: int = Field(..., description="権限を付与したユーザーID")
    expires_at: Optional[datetime] = Field(default=None, description="権限の有効期限")
    is_active: bool = Field(default=True, description="権限が有効かどうか")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class DataAccessPermissionCreate(BaseModel):
    """データアクセス権限作成"""
    granted_to_user_id: int = Field(..., description="権限を付与されたユーザーID")
    data_category: DataCategory = Field(..., description="データカテゴリ")
    permission_level: AccessPermission = Field(..., description="権限レベル")
    expires_at: Optional[datetime] = Field(default=None, description="権限の有効期限")


class DataAccessPermissionUpdate(BaseModel):
    """データアクセス権限更新"""
    permission_level: Optional[AccessPermission] = Field(None, description="権限レベル")
    expires_at: Optional[datetime] = Field(default=None, description="権限の有効期限")
    is_active: Optional[bool] = Field(None, description="権限が有効かどうか")


class DataAccessPermissionResponse(DataAccessPermissionBase):
    """データアクセス権限レスポンス"""
    id: int = Field(..., description="データアクセス権限ID")


class EncryptedDataBase(BaseModel):
    """暗号化データベース"""
    user_id: int = Field(..., description="ユーザーID")
    data_category: DataCategory = Field(..., description="データカテゴリ")
    encrypted_content: str = Field(..., description="暗号化されたコンテンツ")
    encryption_key_id: str = Field(..., description="暗号化キーID")
    data_type: str = Field(..., description="データタイプ")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="メタデータ")
    is_active: bool = Field(default=True, description="データが有効かどうか")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class EncryptedDataCreate(BaseModel):
    """暗号化データ作成"""
    data_category: DataCategory = Field(..., description="データカテゴリ")
    encrypted_content: str = Field(..., description="暗号化されたコンテンツ")
    encryption_key_id: str = Field(..., description="暗号化キーID")
    data_type: str = Field(..., description="データタイプ")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="メタデータ")


class EncryptedDataUpdate(BaseModel):
    """暗号化データ更新"""
    encrypted_content: Optional[str] = Field(None, description="暗号化されたコンテンツ")
    encryption_key_id: Optional[str] = Field(None, description="暗号化キーID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="メタデータ")
    is_active: Optional[bool] = Field(None, description="データが有効かどうか")


class EncryptedDataResponse(EncryptedDataBase):
    """暗号化データレスポンス"""
    id: int = Field(..., description="暗号化データID")


class DataRetentionPolicyBase(BaseModel):
    """データ保持ポリシーベース"""
    user_id: int = Field(..., description="ユーザーID")
    data_category: DataCategory = Field(..., description="データカテゴリ")
    retention_period_days: int = Field(..., description="保持期間（日数）")
    auto_delete_enabled: bool = Field(default=True, description="自動削除を有効化")
    archive_before_delete: bool = Field(default=False, description="削除前にアーカイブ")
    notify_before_deletion: bool = Field(default=True, description="削除前に通知")
    deletion_schedule: str = Field(default="daily", description="削除スケジュール")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class DataRetentionPolicyCreate(BaseModel):
    """データ保持ポリシー作成"""
    data_category: DataCategory = Field(..., description="データカテゴリ")
    retention_period_days: int = Field(..., description="保持期間（日数）")
    auto_delete_enabled: bool = Field(default=True, description="自動削除を有効化")
    archive_before_delete: bool = Field(default=False, description="削除前にアーカイブ")
    notify_before_deletion: bool = Field(default=True, description="削除前に通知")
    deletion_schedule: str = Field(default="daily", description="削除スケジュール")


class DataRetentionPolicyUpdate(BaseModel):
    """データ保持ポリシー更新"""
    retention_period_days: Optional[int] = Field(None, description="保持期間（日数）")
    auto_delete_enabled: Optional[bool] = Field(None, description="自動削除を有効化")
    archive_before_delete: Optional[bool] = Field(None, description="削除前にアーカイブ")
    notify_before_deletion: Optional[bool] = Field(None, description="削除前に通知")
    deletion_schedule: Optional[str] = Field(None, description="削除スケジュール")


class DataRetentionPolicyResponse(DataRetentionPolicyBase):
    """データ保持ポリシーレスポンス"""
    id: int = Field(..., description="データ保持ポリシーID")


class PrivacyAuditLogBase(BaseModel):
    """プライバシー監査ログベース"""
    user_id: int = Field(..., description="ユーザーID")
    action: str = Field(..., description="実行されたアクション")
    data_category: Optional[DataCategory] = Field(default=None, description="データカテゴリ")
    target_user_id: Optional[int] = Field(default=None, description="対象ユーザーID")
    permission_level: Optional[AccessPermission] = Field(default=None, description="権限レベル")
    ip_address: Optional[str] = Field(default=None, description="IPアドレス")
    user_agent: Optional[str] = Field(default=None, description="ユーザーエージェント")
    success: bool = Field(..., description="アクションが成功したかどうか")
    error_message: Optional[str] = Field(default=None, description="エラーメッセージ")
    created_at: Optional[datetime] = None


class PrivacyAuditLogResponse(PrivacyAuditLogBase):
    """プライバシー監査ログレスポンス"""
    id: int = Field(..., description="プライバシー監査ログID")
