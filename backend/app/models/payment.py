from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class Payment(Base):
    """支払い処理モデル
    
    役割:
    - 実際の支払い処理
    - 支払い方法の管理
    - 支払い状態の追跡
    - Stripe等の外部決済サービスとの連携
    """
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    stripe_payment_intent_id = Column(String(255), nullable=False, unique=True)
    stripe_checkout_session_id = Column(String(255), nullable=True, unique=True)
    amount = Column(Integer, nullable=False)  # Amount in cents
    currency = Column(String(3), nullable=False, default='jpy')
    status = Column(String(50), nullable=False)  # pending, succeeded, failed, canceled
    payment_method = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    payment_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="payments")
    billing = relationship("Billing", back_populates="payment", uselist=False)  # 1対1の関係

    def __repr__(self):
        return f"<Payment(id={self.id}, org_id={self.organization_id}, amount={self.amount}, status='{self.status}')>"
