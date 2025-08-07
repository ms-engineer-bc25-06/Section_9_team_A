# TODO: 仮Subscriptionテーブル（後ほど消す）
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
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
    status = Column(String(50), default="active")  # active, cancelled, expired
    stripe_subscription_id = Column(String(255), nullable=True)

    # 期間
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)

    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Subscription(id={self.id}, plan_type='{self.plan_type}')>"
