# TODO: 仮Baseモデル（後ほど消す）
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase


# SQLAlchemy 2.0スタイルのベースクラス
class Base(DeclarativeBase):
    pass
