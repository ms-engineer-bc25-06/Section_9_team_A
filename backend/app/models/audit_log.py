# TODO: 仮AuditLogテーブル（後ほど消す）
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func

from app.core.database import Base


class AuditLog(Base):
    """監査ログモデル"""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # ログ情報
    action = Column(String(100), nullable=False)  # create, update, delete, login, etc.
    resource_type = Column(
        String(100), nullable=True
    )  # user, voice_session, team, etc.
    resource_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)  # JSON形式で詳細を保存

    # IPアドレス
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return (
            f"<AuditLog(id={self.id}, action='{self.action}', user_id={self.user_id})>"
        )
