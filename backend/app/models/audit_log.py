from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base


class AuditLog(Base):
    """監査ログモデル"""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    # ログ情報
    log_id = Column(String(255), unique=True, index=True, nullable=False)
    action = Column(String(100), nullable=False)  # create, update, delete, login, etc.
    resource_type = Column(String(50), nullable=False)  # user, team, voice_session, etc.
    resource_id = Column(String(255), nullable=True)
    
    # ユーザー情報
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user_email = Column(String(255), nullable=True)
    user_ip = Column(String(45), nullable=True)  # IPv4/IPv6対応
    
    # 詳細情報
    description = Column(Text, nullable=True)
    details = Column(JSON, nullable=True)  # 追加の詳細情報
    
    # セッション情報
    session_id = Column(String(255), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # リレーションシップ（循環参照を避けるため、back_populatesは使用しない）
    user = relationship("User")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', resource='{self.resource_type}')>"

    @property
    def is_system_action(self) -> bool:
        """システムアクションかどうか"""
        return self.user_id is None

    @property
    def is_user_action(self) -> bool:
        """ユーザーアクションかどうか"""
        return self.user_id is not None

    @property
    def is_create_action(self) -> bool:
        """作成アクションかどうか"""
        return self.action == "create"

    @property
    def is_update_action(self) -> bool:
        """更新アクションかどうか"""
        return self.action == "update"

    @property
    def is_delete_action(self) -> bool:
        """削除アクションかどうか"""
        return self.action == "delete"

    @property
    def is_login_action(self) -> bool:
        """ログインアクションかどうか"""
        return self.action == "login"

    @property
    def is_logout_action(self) -> bool:
        """ログアウトアクションかどうか"""
        return self.action == "logout"

    def add_detail(self, key: str, value: any):
        """詳細情報を追加"""
        if not self.details:
            self.details = {}
        self.details[key] = value

    def get_detail(self, key: str, default: any = None):
        """詳細情報を取得"""
        if not self.details:
            return default
        return self.details.get(key, default)

    def get_audit_summary(self) -> dict:
        """監査サマリーを取得"""
        return {
            "log_id": self.log_id,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "user_id": self.user_id,
            "user_email": self.user_email,
            "user_ip": self.user_ip,
            "description": self.description,
            "session_id": self.session_id,
            "is_system_action": self.is_system_action,
            "is_user_action": self.is_user_action,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def create_system_log(cls, action: str, resource_type: str, description: str = None, details: dict = None):
        """システムログを作成"""
        return cls(
            log_id=f"sys_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{action}",
            action=action,
            resource_type=resource_type,
            description=description,
            details=details
        )

    @classmethod
    def create_user_log(cls, user_id: int, action: str, resource_type: str, description: str = None, details: dict = None):
        """ユーザーログを作成"""
        return cls(
            log_id=f"user_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{action}",
            action=action,
            resource_type=resource_type,
            user_id=user_id,
            description=description,
            details=details
        )
