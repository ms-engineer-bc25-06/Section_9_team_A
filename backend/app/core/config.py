import os
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """アプリケーション設定"""
    
    # 基本設定
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    LOG_LEVEL: str = "INFO"
    
    # データベース設定
    DATABASE_URL: str = "postgresql+asyncpg://bridge_user:bridge_password@postgres:5432/bridge_line_db"
    TEST_DATABASE_URL: Optional[str] = None
    
    # セキュリティ設定
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS設定
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Firebase設定
    FIREBASE_PROJECT_ID: Optional[str] = None
    FIREBASE_PRIVATE_KEY_ID: Optional[str] = None
    FIREBASE_PRIVATE_KEY: Optional[str] = None
    FIREBASE_CLIENT_EMAIL: Optional[str] = None
    FIREBASE_CLIENT_ID: Optional[str] = None
    FIREBASE_AUTH_URI: str = "https://accounts.google.com/o/oauth2/auth"
    FIREBASE_TOKEN_URI: str = "https://oauth2.googleapis.com/token"
    FIREBASE_AUTH_PROVIDER_X509_CERT_URL: str = "https://www.googleapis.com/oauth2/v1/certs"
    FIREBASE_CLIENT_X509_CERT_URL: Optional[str] = None
    
    # OpenAI設定
    OPENAI_API_KEY: Optional[str] = None
    
    # Stripe設定
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    # SMTP設定
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # WebSocket設定
    WEBSOCKET_URL: str = "ws://localhost:8000/ws"
    
    # フロントエンド設定
    FRONTEND_URL: str = "http://localhost:3000"
    
    # 初期管理者設定
    INITIAL_ADMIN_FIREBASE_UID: Optional[str] = None
    INITIAL_ADMIN_EMAIL: Optional[str] = None
    INITIAL_ADMIN_DISPLAY_NAME: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # 追加の環境変数を無視


# 設定インスタンスを作成
settings = Settings()
