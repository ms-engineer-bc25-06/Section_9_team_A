"""
FastAPIアプリケーションのエントリーポイント
- ルーター登録
- CORS設定
- ログ設定
- 例外ハンドリング
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from app.routers import webhook, health
from app.utils.logger import setup_logger
import uvicorn

# ロガー初期化
setup_logger()

# FastAPIインスタンス生成
app: FastAPI = FastAPI(
    title="LINE BOT API", description="LINEとOpenAI連携BOT", version="1.0.0"
)

# CORS設定（全許可。必要に応じて制限可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(webhook.router)
app.include_router(health.router)


# グローバル例外ハンドラ
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"[エラー] {exc}")
    return {"detail": "サーバー内部エラーが発生しました。管理者に連絡してください。"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
