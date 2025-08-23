from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.models.base import Base


class PrivacyLevel(str, enum.Enum):
    """プライバシーレベル"""
    PUBLIC = "public"           # 全員に公開
    TEAM = "team"              # チームメンバーのみ
    MANAGER = "manager"        # マネージャーのみ
    PRIVATE = "private"        # 本人のみ
    ADMIN = "admin"            # 管理者のみ


class DataCategory(str, enum.Enum):
    """データカテゴリ"""
    PROFILE = "profile"        # プロフィール情報
    ANALYSIS = "analysis"      # 分析結果
    GOALS = "goals"           # 成長目標
    IMPROVEMENT = "improvement" # 改善計画
    COMMUNICATION = "communication" # コミュニケーション履歴
    PERFORMANCE = "performance" # パフォーマンスデータ


class EncryptedData(Base):
    """暗号化データモデル"""
    
    __tablename__ = "encrypted_data"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # データ識別子
    data_id = Column(String(255), unique=True, index=True, nullable=False)
    data_type = Column(String(100), nullable=False)  # データの種類
    data_category = Column(Enum(DataCategory), nullable=False)
    
    # 暗号化情報
    encrypted_content = Column(Text, nullable=False)  # 暗号化されたコンテンツ
    encryption_algorithm = Column(String(50), nullable=False)  # 暗号化アルゴリズム
    encryption_key_id = Column(String(255), nullable=False)  # 暗号化キーID
    iv = Column(String(255), nullable=False)  # 初期化ベクトル
    
    # メタデータ
    original_size = Column(Integer, nullable=True)  # 元のデータサイズ
    compression_ratio = Column(Integer, nullable=True)  # 圧縮率
    
    # 所有者と権限
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    privacy_level = Column(Enum(PrivacyLevel), default=PrivacyLevel.PRIVATE)
    
    # 有効期限
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # リレーションシップ
    owner = relationship("User", back_populates="encrypted_data")
    access_permissions = relationship("DataAccessPermission", back_populates="encrypted_data", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<EncryptedData(id={self.id}, type='{self.data_type}', category='{self.data_category}')>"

    @property
    def is_expired(self) -> bool:
        """データが期限切れかどうか"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False

    @property
    def is_public(self) -> bool:
        """公開データかどうか"""
        return self.privacy_level == PrivacyLevel.PUBLIC

    @property
    def is_team_only(self) -> bool:
        """チーム限定かどうか"""
        return self.privacy_level == PrivacyLevel.TEAM

    @property
    def is_private(self) -> bool:
        """プライベートかどうか"""
        return self.privacy_level == PrivacyLevel.PRIVATE

    def get_encryption_info(self) -> dict:
        """暗号化情報を取得"""
        return {
            'algorithm': self.encryption_algorithm,
            'key_id': self.encryption_key_id,
            'iv': self.iv,
            'compression_ratio': self.compression_ratio
        }


class DataAccessPermission(Base):
    """データアクセス権限モデル"""
    
    __tablename__ = "data_access_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 対象データ
    encrypted_data_id = Column(Integer, ForeignKey("encrypted_data.id"), nullable=False)
    
    # アクセス権限を持つユーザー
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 権限レベル
    access_level = Column(Enum(PrivacyLevel), nullable=False)
    
    # 権限の種類
    can_read = Column(Boolean, default=False)
    can_write = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    can_share = Column(Boolean, default=False)
    
    # 権限の有効期限
    granted_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # 権限付与者
    granted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # リレーションシップ
    encrypted_data = relationship("EncryptedData", back_populates="access_permissions")
    user = relationship("User", foreign_keys=[user_id], back_populates="data_access_permissions")
    granter = relationship("User", foreign_keys=[granted_by], back_populates="granted_permissions")

    def __repr__(self):
        return f"<DataAccessPermission(user_id={self.user_id}, data_id={self.encrypted_data_id})>"

    @property
    def is_expired(self) -> bool:
        """権限が期限切れかどうか"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False

    @property
    def has_full_access(self) -> bool:
        """完全なアクセス権限があるかどうか"""
        return all([self.can_read, self.can_write, self.can_delete, self.can_share])

    @property
    def has_read_access(self) -> bool:
        """読み取り権限があるかどうか"""
        return self.can_read

    def can_access_data(self, required_level: PrivacyLevel) -> bool:
        """指定されたレベルのデータにアクセスできるかチェック"""
        if self.is_expired:
            return False
        
        # プライバシーレベルの優先順位チェック
        level_priority = {
            PrivacyLevel.PRIVATE: 1,
            PrivacyLevel.MANAGER: 2,
            PrivacyLevel.TEAM: 3,
            PrivacyLevel.PUBLIC: 4,
            PrivacyLevel.ADMIN: 5
        }
        
        return level_priority.get(self.access_level, 0) >= level_priority.get(required_level, 0)


class PrivacySettings(Base):
    """プライバシー設定モデル"""
    
    __tablename__ = "privacy_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 設定所有者
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # デフォルトプライバシーレベル
    default_profile_privacy = Column(Enum(PrivacyLevel), default=PrivacyLevel.TEAM)
    default_analysis_privacy = Column(Enum(PrivacyLevel), default=PrivacyLevel.PRIVATE)
    default_goals_privacy = Column(Enum(PrivacyLevel), default=PrivacyLevel.PRIVATE)
    default_improvement_privacy = Column(Enum(PrivacyLevel), default=PrivacyLevel.PRIVATE)
    
    # 自動データ削除設定
    auto_delete_after_days = Column(Integer, default=365)  # 365日後に自動削除
    auto_delete_enabled = Column(Boolean, default=True)
    
    # データ共有設定
    allow_team_sharing = Column(Boolean, default=True)
    allow_manager_access = Column(Boolean, default=True)
    allow_anonymous_analytics = Column(Boolean, default=False)
    
    # 通知設定
    notify_on_access = Column(Boolean, default=True)  # データアクセス時に通知
    notify_on_breach = Column(Boolean, default=True)  # プライバシー侵害時に通知
    
    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # リレーションシップ（循環参照を避けるため、back_populatesは使用しない）
    user = relationship("User")

    def __repr__(self):
        return f"<PrivacySettings(user_id={self.user_id})>"

    def get_default_privacy_for_category(self, category: DataCategory) -> PrivacyLevel:
        """カテゴリ別のデフォルトプライバシーレベルを取得"""
        category_mapping = {
            DataCategory.PROFILE: self.default_profile_privacy,
            DataCategory.ANALYSIS: self.default_analysis_privacy,
            DataCategory.GOALS: self.default_goals_privacy,
            DataCategory.IMPROVEMENT: self.default_improvement_privacy,
        }
        return category_mapping.get(category, PrivacyLevel.PRIVATE)

    def is_sharing_allowed(self, category: DataCategory) -> bool:
        """指定されたカテゴリの共有が許可されているかチェック"""
        if category == DataCategory.PROFILE:
            return self.allow_team_sharing
        elif category == DataCategory.ANALYSIS:
            return self.allow_manager_access
        return True

    def update_privacy_level(self, category: DataCategory, new_level: PrivacyLevel):
        """カテゴリ別のプライバシーレベルを更新"""
        if category == DataCategory.PROFILE:
            self.default_profile_privacy = new_level
        elif category == DataCategory.ANALYSIS:
            self.default_analysis_privacy = new_level
        elif category == DataCategory.GOALS:
            self.default_goals_privacy = new_level
        elif category == DataCategory.IMPROVEMENT:
            self.default_improvement_privacy = new_level


class DataRetentionPolicy(Base):
    """データ保持ポリシーモデル"""
    
    __tablename__ = "data_retention_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # ポリシー名
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # 適用対象
    data_category = Column(Enum(DataCategory), nullable=False)
    user_role = Column(String(50), nullable=True)  # 特定のロールに適用
    
    # 保持期間
    retention_days = Column(Integer, nullable=False)  # 保持日数
    
    # 削除後の処理
    deletion_action = Column(String(50), default="soft_delete")  # soft_delete, hard_delete, archive
    
    # ポリシーの有効性
    is_active = Column(Boolean, default=True)
    
    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<DataRetentionPolicy(name='{self.name}', category='{self.data_category}')>"

    @property
    def retention_period_hours(self) -> int:
        """保持期間を時間単位で取得"""
        return self.retention_days * 24

    @property
    def is_soft_delete(self) -> bool:
        """ソフト削除ポリシーかどうか"""
        return self.deletion_action == "soft_delete"

    @property
    def is_hard_delete(self) -> bool:
        """ハード削除ポリシーかどうか"""
        return self.deletion_action == "hard_delete"

    def should_apply_to_user(self, user_role: str) -> bool:
        """指定されたユーザーロールに適用すべきかチェック"""
        if not self.user_role:
            return True  # 全ロールに適用
        return self.user_role == user_role


class PrivacyAuditLog(Base):
    """プライバシー監査ログモデル"""
    
    __tablename__ = "privacy_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 監査対象
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    data_id = Column(String(255), nullable=True)  # 対象データID
    
    # アクション
    action = Column(String(100), nullable=False)  # access, modify, delete, share
    action_details = Column(JSON, nullable=True)  # アクションの詳細
    
    # アクセス情報
    accessed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6対応
    user_agent = Column(Text, nullable=True)
    
    # 結果
    success = Column(Boolean, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # タイムスタンプ
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # リレーションシップ（循環参照を避けるため、back_populatesは使用しない）
    user = relationship("User", foreign_keys=[user_id])
    actor = relationship("User", foreign_keys=[accessed_by])

    def __repr__(self):
        return f"<PrivacyAuditLog(action='{self.action}', user_id={self.user_id})>"

    @property
    def is_successful(self) -> bool:
        """アクションが成功したかどうか"""
        return self.success

    @property
    def is_access_action(self) -> bool:
        """アクセスアクションかどうか"""
        return self.action == "access"

    @property
    def is_modify_action(self) -> bool:
        """修正アクションかどうか"""
        return self.action == "modify"

    def get_action_summary(self) -> str:
        """アクションの要約を取得"""
        if self.success:
            return f"Successfully {self.action} data for user {self.user_id}"
        else:
            return f"Failed to {self.action} data for user {self.user_id}: {self.error_message}"

    def add_action_detail(self, key: str, value: any):
        """アクション詳細を追加"""
        if not self.action_details:
            self.action_details = {}
        
        self.action_details[key] = value
