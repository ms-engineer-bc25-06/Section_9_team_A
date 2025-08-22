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
    DATABASE_URL: str = "postgresql+asyncpg://bridge_user:bridge_password@postgres/bridge_line_db"
    TEST_DATABASE_URL: Optional[str] = "postgresql+asyncpg://bridge_user:bridge_password@postgres/bridge_line_test_db"

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
    FIREBASE_PROJECT_ID: Optional[str] = "section9-teama"
    FIREBASE_PRIVATE_KEY_ID: Optional[str] = "d6f06fd341432d73a00075f0cf2cef42dfefe998"
    FIREBASE_PRIVATE_KEY: Optional[str] = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCxQI3K+ouvE8A8\ny0Sc6RxCEOCi1g+duQmH0dlkK1qElp9Vr/bcik+YosbqrQp1c4MT2gjVqcNoEgz9\nqgn1Pcj9UneG+xSs+ftOWj13Bf67Pba1WvMHvdqVhKEmRAiLICgSW0FKQ6TaPF55\nmE5ciseUainTMD2mXGEYLYLfresqOsrRzIyVMpjK4FmN961SIQHtViaE4tOd4EGk\nWCMEXPHpUd4alK8hhPZCcTD7LduB54bjimV8+QkhpncrV/7kfp2c286VFJGjmrfi\nqcFihiwGVmg54YN8KZuIskN/6EWyWjhSBblRsiode7Oryg3zoD2mdDAtQ1nrmFfI\nB7NK4+CLAgMBAAECggEAErTZ4gycFk+Sz7eyF49AhLZsRrMptb8UAuoCM+ChbnHJ\nAg2Ok4rjSJwROy4k9u1IbZ1qpkYC0eZpyZGa+G9bWWTNKYkxDupY+9VpPDj9P7yN\nHkmpcW03duUm7rdqYWh04i8QTmqiKMgLPnD1AC5DTuX/YQLr1rVUJ+2RrNKZiXy6\n2qIYBsXOfTSESbCtACsvInc3Xv4wk++NhY2MAaijp+F6YCUpj+4ZhpW0WrVTa4Cl\nsNr7mbMatw2IOvjH+23QvivRB1VydfYYfHlOW8ZDRk+Rl47JRFWpWLIAPHn+zPl7\nzh2B6OzTqYQQVwBJAEYWBKxLqsMAUGUF1EbwHsU7lQKBgQDlNDq23EFQGhgKqYGT\nizV/UMQrrbva51OUXixz9D9rzE0fUSRG+T5bVcKo/0b1KXKksWJDGLrLRyrwGDKc\nCLe+mmMQ7i/U+YE9rxLlQxOS+1Hbi3fl8BYsjzSpgUoo/wmnYRF2yhIsVyeWoIkG\nhF5eMUgOfBsDJb5YLB57cJCoPQKBgQDF+XmHqsXSMXUtaBSoNWWRUZZor+XTfe7y\noeeYqZpDrKRtmCxoCvlcXae9107Yi8qBf+ClPnt7kROj7R1koJnDto5P3bEqw0jk\nkvq1XggzyppAgQVMX5IMTanol6hV/2Jgp3jNYuY9F1duc5bAPO9cN/80LYiIZH68\nGtZFd0PwZwKBgBAxTmyYxux3y3cFXqgjz5W9CP7k+T6P1THILW/Ls6dT+abavqtc\n9HDTcDssPcEYOoc0GPMQjjHKR1hK/VhUrVaD5bfOfAaZ0e2frsAPqxRZOQE/qyrN\neWOQgnHvNmQLEI2IqAkyYXJMffmAQe358AjLhoGvduEUC4yDIWwrGa0pAoGALsuY\nWWQZXGTKYNBASb5NYrsZRWeGeKZEy99PQfuc9jAhsbINlQ47AQU2OB5jibYJSPD0\nJbsOLxgMv2u1zepUTjmhi+lIDmaYnUbMsgAnCi7ypRqaKQJSIExfRBZM+P7jvxr2\n5/1flMMmrHnwAUKmBXNLBIdaxXqTplzllwfo7DMCgYEAm5Yangg4uJ4pARH5ljhp\ncZS3qGeU3B+UOgwC/BfdT5n2WfAY0lCWbuhes/hn9LEXMHtIpYHnBJFvdWSZHdGt\niWjG7qJixDn12JdTob1VabyvRnYqkMMQfJWONFmq9rRshZYtYD7AR2yB/WBqRkSf\nYoCXamz8VJ1tUKHaeApzsbo=\n-----END PRIVATE KEY-----\n"
    FIREBASE_CLIENT_EMAIL: Optional[str] = "firebase-adminsdk-fbsvc@section9-teama.iam.gserviceaccount.com"
    FIREBASE_CLIENT_ID: Optional[str] = "105025232353434627915"
    FIREBASE_AUTH_URI: str = "https://accounts.google.com/o/oauth2/auth"
    FIREBASE_TOKEN_URI: str = "https://oauth2.googleapis.com/token"
    FIREBASE_AUTH_PROVIDER_X509_CERT_URL: str = (
        "https://www.googleapis.com/oauth2/v1/certs"
    )
    FIREBASE_CLIENT_X509_CERT_URL: Optional[str] = "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40section9-teama.iam.gserviceaccount.com"

    # Stripe設定
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_PRICE_ID: Optional[str] = None

    # OpenAI設定
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"

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
    INITIAL_ADMIN_FIREBASE_UID: Optional[str] = None  # 現在: g7lzX9SnUUeBpRAae9CjynV0CX43
    INITIAL_ADMIN_EMAIL: Optional[str] = None         # 現在: admin@example.com
    INITIAL_ADMIN_DISPLAY_NAME: Optional[str] = None  # 現在: 管理者1

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # 環境変数の追加フィールドを無視（トラブルシューティング用）


# 設定インスタンス
settings = Settings()