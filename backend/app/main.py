from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import structlog

from app.config import settings
from app.api.v1.api import api_router
from app.core.message_handlers import initialize_message_handlers
from app.core.exceptions import BridgeLineException
from app.api.deps import handle_bridge_line_exceptions

# ログ設定
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理"""
    # 起動時
    logger.info("Starting Bridge Line API server")

    # データベースマイグレーションは Alembic を使用（自動作成は行わない）
    logger.info("Skipping automatic table creation. Use Alembic migrations instead.")

    # 初期管理者の自動設定
    try:
        from app.core.startup import startup_events

        await startup_events()
    except Exception as e:
        logger.error(f"Failed to initialize admin user: {e}")

    yield

    # シャットダウン時
    logger.info("Shutting down Bridge Line API server")


# FastAPIアプリケーション作成
app = FastAPI(
    title="Bridge Line API",
    description="AI音声チャットアプリケーションのバックエンドAPI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "*"  # 開発環境ではすべてのオリジンを許可
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,  # 24時間
)


# カスタムCORSヘッダーを追加するミドルウェア
@app.middleware("http")
async def add_cors_headers(request, call_next):
    """カスタムCORSヘッダーを追加"""
    response = await call_next(request)

    # プリフライトリクエストの処理
    if request.method == "OPTIONS":
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response.headers["Access-Control-Allow-Methods"] = (
            "GET, POST, PUT, DELETE, OPTIONS, HEAD"
        )
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Max-Age"] = "86400"

    # 通常のリクエストにもCORSヘッダーを追加
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response.headers["Access-Control-Allow-Credentials"] = "true"

    return response


# Trusted Host設定（開発環境では無効化）
if settings.ENVIRONMENT == "production":
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])


# 例外ハンドラー追加
@app.exception_handler(BridgeLineException)
async def bridge_line_exception_handler(request, exc: BridgeLineException):
    """BridgeLine例外のハンドラー"""
    return handle_bridge_line_exceptions(exc)


# ヘルスチェックエンドポイント
@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    try:
        from app.core.database import test_database_connection

        db_status = await test_database_connection()
        return {
            "status": "healthy" if db_status else "unhealthy",
            "database": "connected" if db_status else "disconnected",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# APIルーターの追加
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {"message": "Bridge Line API", "version": "1.0.0", "status": "running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
