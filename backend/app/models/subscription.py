from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class Subscription(Base):
    """サブスクリプション状態管理モデル
    
    役割:
    - サブスクリプションの状態管理
    - プラン情報の管理
    - 更新・キャンセルの処理
    - ユーザー数の管理
    """
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
 # サブスクリプション情報
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    stripe_subscription_id = Column(String(255), nullable=False, unique=True)
    stripe_price_id = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False)  # active, past_due, canceled, incomplete, incomplete_expired, trialing, unpaid
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    canceled_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    quantity = Column(Integer, nullable=False, default=0)  # Number of users
    subscription_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="subscriptions")
    organization = relationship("Organization", back_populates="subscriptions")
    billing_records = relationship("Billing", back_populates="subscription")

    def __repr__(self):
        return f"<Subscription(id={self.id}, org_id={self.organization_id}, status='{self.status}', quantity={self.quantity})>"