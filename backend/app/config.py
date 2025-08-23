from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """アプリケーション設定"""

    # 基本設定
    APP_NAME: str = "Bridge Line API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # サーバー設定
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # データベース設定
    DATABASE_URL: str = (
        "postgresql+asyncpg://bridge_user:bridge_password@postgres/bridge_line_db"
    )
    TEST_DATABASE_URL: Optional[str] = (
        "postgresql+asyncpg://bridge_user:bridge_password@postgres/bridge_line_test_db"
    )

    # セキュリティ設定
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # API設定
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Bridge Line API"

    # CORS設定
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ]

    # Firebase設定
    # GOOGLE_APPLICATION_CREDENTIALS環境変数でfirebase-admin-key.jsonを指定
    # 詳細設定はfirebase-admin-key.jsonファイル内に含まれている

    # Stripe設定
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_PRICE_ID: Optional[str] = None

    # OpenAI設定
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_PERSONAL_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"

    def get_openai_api_key(self) -> str:
        """OpenAI APIキーを取得（個人APIキーを優先）"""
        return self.OPENAI_PERSONAL_API_KEY or self.OPENAI_API_KEY or ""

    # Redis設定
    REDIS_URL: str = "redis://redis:6379"

    # ストレージ設定
    STORAGE_BUCKET_NAME: Optional[str] = None
    STORAGE_PROJECT_ID: Optional[str] = None

    # メール設定
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # ファイルアップロード設定
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    # WebSocket設定
    WS_MESSAGE_QUEUE_URL: str = "redis://localhost:6379"
    WEBSOCKET_URL: str = "ws://localhost:8000/ws"

    # ログ設定
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # 初期管理者設定（オプション - 手動設定済み）
    INITIAL_ADMIN_FIREBASE_UID: Optional[str] = (
        None  # 現在: g7lzX9SnUUeBpRAae9CjynV0CX43
    )
    INITIAL_ADMIN_EMAIL: Optional[str] = None  # 現在: admin@example.com
    INITIAL_ADMIN_DISPLAY_NAME: Optional[str] = None  # 現在: 管理者1

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore",  # 環境変数の追加フィールドを無視（トラブルシューティング用）
    }


# 設定インスタンス
settings = Settings()
