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
    
    # リレーションシップ
    user = relationship("User")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', resource='{self.resource_type}')>"

    @property
    def is_system_action(self) -> bool:
        """システムアクションかどうか"""
        return self.user_id is None


