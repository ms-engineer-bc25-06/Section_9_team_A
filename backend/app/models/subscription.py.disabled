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
    
    # リレーションシップ
    user = relationship("User", back_populates="subscriptions")

    billing_records = relationship("Billing", back_populates="subscription")

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