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
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Billing(Base):
    """請求モデル"""

    __tablename__ = "billings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 請求情報
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="JPY")
    stripe_payment_intent_id = Column(String(255), nullable=True)
    status = Column(String(50), default="pending")  # pending, completed, failed

    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Billing(id={self.id}, amount={self.amount}, status='{self.status}')>"
