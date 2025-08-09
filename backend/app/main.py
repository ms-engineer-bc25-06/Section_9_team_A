from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import structlog

from app.config import settings
from app.api.v1.api import api_router
from app.api.v1 import websocket as websocket_v1
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

    # WebSocket メッセージハンドラー初期化
    try:
        await initialize_message_handlers()
        logger.info("WebSocket message handlers initialized")
    except Exception as e:
        logger.error(f"Failed to initialize WebSocket message handlers: {e}")

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
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host設定（開発環境では無効化）
if settings.ENVIRONMENT == "production":
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])


# 例外ハンドラー追加
@app.exception_handler(BridgeLineException)
async def bridge_line_exception_handler(request, exc: BridgeLineException):
    """BridgeLine例外のハンドラー"""
    return handle_bridge_line_exceptions(exc)


# APIルーターの追加
app.include_router(api_router, prefix="/api/v1")
# WebSocket ルーターの追加
app.include_router(websocket_v1.router, prefix="/api/v1")


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {"message": "Bridge Line API", "version": "1.0.0", "status": "running"}


@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy", "service": "bridge-line-api"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )