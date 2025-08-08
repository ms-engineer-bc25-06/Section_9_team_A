# TODO: 仮AuditLogテーブル（後ほど消す）
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    JSON,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class AuditLog(Base):
    """監査ログモデル"""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=True
    )  # 匿名アクセスの場合null

    # ログ情報
    action = Column(String(100), nullable=False)  # create, update, delete, login, etc.
    resource_type = Column(
        String(100), nullable=False
    )  # user, team, voice_session, etc.
    resource_id = Column(String(255), nullable=True)

    # 詳細情報
    description = Column(Text, nullable=True)
    meta_data = Column(JSON, nullable=True)  # 追加のログ情報

    # IPアドレスとユーザーエージェント
    ip_address = Column(String(45), nullable=True)  # IPv6対応
    user_agent = Column(Text, nullable=True)

    # 結果
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)

    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # リレーションシップ
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, user_id={self.user_id}, action='{self.action}', resource='{self.resource_type}')>"
