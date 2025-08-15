from fastapi import APIRouter

from app.api.v1 import (
    auth,
    users,
    teams,
    voice_sessions,
)

api_router = APIRouter()

# 認証関連
api_router.include_router(auth.router, prefix="/auth", tags=["認証"])

# ユーザー管理
api_router.include_router(users.router, prefix="/users", tags=["ユーザー"])

# チーム管理
api_router.include_router(teams.router, prefix="/teams", tags=["チーム"])

# 音声セッション
api_router.include_router(
    voice_sessions.router, prefix="/voice-sessions", tags=["音声セッション"]
)
