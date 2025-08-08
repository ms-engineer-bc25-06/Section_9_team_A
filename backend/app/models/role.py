from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Role(Base):
    """ロールモデル"""

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # admin, user, moderator
    display_name = Column(String(100), nullable=False)  # 管理者, ユーザー, モデレーター
    description = Column(String(255), nullable=True)
    permissions = Column(String(500), nullable=True)  # JSON形式で権限を保存
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # リレーションシップ
    user_roles = relationship("UserRole", back_populates="role")

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}', display_name='{self.display_name}')>"


class UserRole(Base):
    """ユーザーロール関連モデル"""

    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # 誰が割り当てたか
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)  # 権限の有効期限

    # リレーションシップ
    # user = relationship("User", foreign_keys=[user_id], back_populates="user_roles")  # 一時的に無効化（循環参照エラー回避）
    role = relationship("Role", back_populates="user_roles")
    # assigned_by_user = relationship("User", foreign_keys=[assigned_by])  # 一時的に無効化（複数FK参照エラー回避）

    def __repr__(self):
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id}, is_active={self.is_active})>"
