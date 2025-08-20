from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class OrganizationMember(Base):
    """組織メンバーモデル（チームメンバー機能を統合）"""
    __tablename__ = "organization_members"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # メンバー情報（旧TeamMember機能）
    role = Column(String(50), nullable=False, default='member')  # member, admin, owner
    status = Column(String(50), nullable=False, default='active')  # active, inactive, suspended
    is_active = Column(Boolean, default=True)
    
    # タイムスタンプ
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="members")
    user = relationship("User", back_populates="organization_memberships")

    def __repr__(self):
        return f"<OrganizationMember(id={self.id}, org_id={self.organization_id}, user_id={self.user_id}, role='{self.role}')>"
