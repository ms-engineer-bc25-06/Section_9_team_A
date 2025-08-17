from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # データベース設定
    DATABASE_URL: str = "postgresql+asyncpg://bridge_user:bridge_password@postgres:5432/bridge_line_db"
    TEST_DATABASE_URL: str = "postgresql+asyncpg://bridge_user:bridge_password@postgres:5432/bridge_line_test_db"
    
    # Redis設定
    REDIS_URL: str = "redis://redis:6379"
    
    # セキュリティ設定
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API設定
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Bridge Line API"
    
    # CORS設定
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # 環境設定
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # WebSocket設定
    WEBSOCKET_URL: str = "ws://localhost:8000/ws"
    
    # Firebase設定（オプション）
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None
    
    # Stripe設定
    STRIPE_SECRET_KEY: str = "your-stripe-secret-key"
    STRIPE_WEBHOOK_SECRET: str = "your-stripe-webhook-secret"
    STRIPE_PRICE_ID: str = "your-stripe-price-id"
    
    # SMTP設定
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "your-email@gmail.com"
    SMTP_PASSWORD: str = "your-app-password"
    
    # OpenAI設定
    OPENAI_API_KEY: str = "your-openai-api-key"
    
    # ストレージ設定
    STORAGE_BUCKET_NAME: str = "your-storage-bucket-name"
    STORAGE_PROJECT_ID: str = "your-storage-project-id"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# グローバル設定インスタンス
settings = Settings()
