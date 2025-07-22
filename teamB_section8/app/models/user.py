"""
ユーザーテーブル定義
"""

from sqlalchemy import Column, Integer, String, DateTime
from app.models.database import Base
import datetime


class User(Base):
    """
    ユーザー情報を管理するテーブル
    """

    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    line_user_id = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
