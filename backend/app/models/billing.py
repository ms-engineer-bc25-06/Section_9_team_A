# TODO: 仮Billingテーブル（後ほど消す）
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    Float,
    JSON,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Billing(Base):
    """決済モデル"""

    __tablename__ = "billings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)

    # 決済情報
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="JPY")
    status = Column(
        String(50), default="pending"
    )  # pending, completed, failed, refunded

    # 外部サービス情報
    stripe_payment_intent_id = Column(String(255), nullable=True)
    stripe_invoice_id = Column(String(255), nullable=True)

    # 決済詳細
    description = Column(Text, nullable=True)
    meta_data = Column(JSON, nullable=True)  # 追加の決済情報

    # 請求情報
    billing_address = Column(JSON, nullable=True)
    tax_amount = Column(Float, default=0.0)

    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    paid_at = Column(DateTime(timezone=True), nullable=True)

    # リレーションシップ
    user = relationship("User", back_populates="billings")
    subscription = relationship("Subscription", back_populates="billings")

    def __repr__(self):
        return f"<Billing(id={self.id}, user_id={self.user_id}, amount={self.amount}, status='{self.status}')>"
