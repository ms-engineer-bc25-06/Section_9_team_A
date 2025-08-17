from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base


class Subscription(Base):
    """サブスクリプションモデル"""

    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)

    # サブスクリプション情報
    subscription_id = Column(String(255), unique=True, index=True, nullable=False)
    plan_type = Column(String(50), nullable=False)  # free, basic, premium
    plan_name = Column(String(255), nullable=False)
    
    # 料金情報
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="JPY")
    billing_cycle = Column(String(50), default="monthly")  # monthly, yearly
    
    # 制限情報
    max_voice_minutes = Column(Integer, nullable=True)
    max_analysis_count = Column(Integer, nullable=True)
    max_team_members = Column(Integer, nullable=True)
    max_storage_gb = Column(Integer, nullable=True)
    
    # サブスクリプション状態
    status = Column(String(50), default="active")  # active, canceled, expired, past_due
    is_active = Column(Boolean, default=True)
    
    # 期間情報
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    trial_end_date = Column(DateTime(timezone=True), nullable=True)
    
    # 外部キー
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    canceled_at = Column(DateTime(timezone=True), nullable=True)
    
    # リレーションシップ（循環参照を避けるため、back_populatesは使用しない）
    user = relationship("User")
    billing_records = relationship("Billing")

    def __repr__(self):
        return f"<Subscription(id={self.id}, plan='{self.plan_type}', status='{self.status}')>"

    @property
    def is_expired(self) -> bool:
        """サブスクリプションが期限切れかどうか"""
        if not self.end_date:
            return False
        return datetime.utcnow() > self.end_date

    @property
    def is_trial_active(self) -> bool:
        """トライアル期間中かどうか"""
        if not self.trial_end_date:
            return False
        return datetime.utcnow() <= self.trial_end_date

    @property
    def days_until_expiry(self) -> int:
        """期限までの日数"""
        if not self.end_date:
            return -1
        delta = self.end_date - datetime.utcnow()
        return max(0, delta.days)

    @property
    def is_canceled(self) -> bool:
        """キャンセル済みかどうか"""
        return self.status == "canceled" and self.canceled_at is not None

    @property
    def is_past_due(self) -> bool:
        """支払い期限切れかどうか"""
        return self.status == "past_due"

    def cancel_subscription(self, cancel_reason: str = None):
        """サブスクリプションをキャンセル"""
        self.status = "canceled"
        self.canceled_at = datetime.utcnow()
        self.is_active = False

    def activate_subscription(self):
        """サブスクリプションを有効化"""
        self.status = "active"
        self.is_active = True
        self.canceled_at = None

    def extend_trial(self, additional_days: int):
        """トライアル期間を延長"""
        if self.trial_end_date:
            self.trial_end_date = self.trial_end_date + datetime.timedelta(days=additional_days)
        else:
            self.trial_end_date = datetime.utcnow() + datetime.timedelta(days=additional_days)

    def get_usage_summary(self) -> dict:
        """使用量サマリーを取得"""
        return {
            "plan_type": self.plan_type,
            "plan_name": self.plan_name,
            "status": self.status,
            "billing_cycle": self.billing_cycle,
            "amount": self.amount,
            "currency": self.currency,
            "is_active": self.is_active,
            "days_until_expiry": self.days_until_expiry,
            "is_trial_active": self.is_trial_active
        }
