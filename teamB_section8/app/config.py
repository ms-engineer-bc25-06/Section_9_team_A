"""
アプリ全体の設定管理
- .envファイルから環境変数を読み込む
- 設定値をクラスで管理
"""

from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    .envファイルや環境変数から設定値を取得するクラス
    """

    LINE_CHANNEL_SECRET: str
    LINE_ACCESS_TOKEN: str
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    DATABASE_URL: str = "sqlite:///./data/app.db"
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = True
    PORT: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
