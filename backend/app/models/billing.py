from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class Billing(Base):
    """請求モデル"""

    __tablename__ = "billings"

    id = Column(Integer, primary_key=True, index=True)

    
    # 請求情報
    billing_id = Column(String(255), unique=True, index=True, nullable=False)
    invoice_number = Column(String(255), unique=True, index=True, nullable=True)
    
    # 料金情報
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="JPY")
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    
    # 請求状態
    status = Column(String(50), default="pending")  # pending, paid, failed, refunded
    payment_method = Column(String(50), nullable=True)  # credit_card, bank_transfer, etc.
    
    # 外部サービス情報
    stripe_payment_intent_id = Column(String(255), nullable=True)
    stripe_invoice_id = Column(String(255), nullable=True)

    # 請求詳細
    description = Column(Text, nullable=True)
    billing_metadata = Column(JSON, nullable=True)  # 追加情報
    
    # 外部キー
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
    
    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    paid_at = Column(DateTime(timezone=True), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    
    # リレーションシップ
    user = relationship("User", back_populates="billing_records")
    subscription = relationship("Subscription", back_populates="billing_records")

    def __repr__(self):
        return f"<Billing(id={self.id}, amount={self.amount}, status='{self.status}')>"

    @property
    def is_paid(self) -> bool:
        """支払い済みかどうか"""
        return self.status == "paid" and self.paid_at is not None

    @property
    def is_overdue(self) -> bool:
        """支払い期限切れかどうか"""
        if not self.due_date or self.is_paid:
            return False
        return datetime.utcnow() > self.due_date