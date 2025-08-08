# FIXME 空ファイルのため、ダミーコードを配置
from sqlalchemy import Column, Integer, String, ForeignKey, Float
from app.core.database import Base

class Billing(Base):
    __tablename__ = "billing"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, nullable=False)
