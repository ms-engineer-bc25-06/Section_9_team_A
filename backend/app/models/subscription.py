# FIXME 空ファイルのため、ダミーコードを配置
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from app.core.database import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    plan = Column(String, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
