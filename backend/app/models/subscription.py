# TODO: 仮Subscriptionテーブル（後ほど消す）
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


class Subscription(Base):
    """サブスクリプションモデル"""

    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # サブスクリプション情報
    plan_type = Column(String(50), nullable=False)  # free, basic, premium
    status = Column(String(50), default="active")  # active, canceled, expired

    # 外部サービス情報
    stripe_subscription_id = Column(String(255), nullable=True)
    stripe_customer_id = Column(String(255), nullable=True)

    # 期間情報
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True), nullable=True)
    trial_end_date = Column(DateTime(timezone=True), nullable=True)

    # 使用量制限
    monthly_voice_minutes = Column(Integer, default=0)
    monthly_analysis_count = Column(Integer, default=0)

    # 価格情報
    amount = Column(Float, nullable=True)
    currency = Column(String(3), default="JPY")

    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    canceled_at = Column(DateTime(timezone=True), nullable=True)

    # リレーションシップ
    user = relationship("User", back_populates="subscriptions")
    billings = relationship("Billing", back_populates="subscription")

    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, plan='{self.plan_type}')>"
