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

    @property
    def is_failed(self) -> bool:
        """支払い失敗かどうか"""
        return self.status == "failed"

    @property
    def is_refunded(self) -> bool:
        """返金済みかどうか"""
        return self.status == "refunded"

    @property
    def days_until_due(self) -> int:
        """支払い期限までの日数"""
        if not self.due_date:
            return -1
        delta = self.due_date - datetime.utcnow()
        return max(0, delta.days)

    @property
    def days_overdue(self) -> int:
        """支払い期限超過日数"""
        if not self.due_date or self.is_paid:
            return 0
        if datetime.utcnow() <= self.due_date:
            return 0
        delta = datetime.utcnow() - self.due_date
        return delta.days

    def mark_as_paid(self, payment_method: str = None, transaction_id: str = None):
        """支払い済みにマーク"""
        self.status = "paid"
        self.paid_at = datetime.utcnow()
        if payment_method:
            self.payment_method = payment_method
        if transaction_id:
            self.billing_metadata = self.billing_metadata or {}
            self.billing_metadata["transaction_id"] = transaction_id

    def mark_as_failed(self, failure_reason: str = None):
        """支払い失敗にマーク"""
        self.status = "failed"
        if failure_reason:
            self.billing_metadata = self.billing_metadata or {}
            self.billing_metadata["failure_reason"] = failure_reason

    def mark_as_refunded(self, refund_reason: str = None):
        """返金済みにマーク"""
        self.status = "refunded"
        if refund_reason:
            self.billing_metadata = self.billing_metadata or {}
            self.billing_metadata["refund_reason"] = refund_reason

    def set_due_date(self, days_from_now: int = 30):
        """支払い期限を設定"""
        self.due_date = datetime.utcnow() + datetime.timedelta(days=days_from_now)

    def get_billing_summary(self) -> dict:
        """請求サマリーを取得"""
        return {
            "billing_id": self.billing_id,
            "invoice_number": self.invoice_number,
            "amount": self.amount,
            "currency": self.currency,
            "total_amount": self.total_amount,
            "status": self.status,
            "payment_method": self.payment_method,
            "is_paid": self.is_paid,
            "is_overdue": self.is_overdue,
            "days_until_due": self.days_until_due,
            "days_overdue": self.days_overdue,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "paid_at": self.paid_at.isoformat() if self.paid_at else None
        }
