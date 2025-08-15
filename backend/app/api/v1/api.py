from fastapi import APIRouter

from app.api.v1 import (
    auth,
    users,
    teams,
    voice_sessions,
    transcriptions,
    analyses,
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

# 文字起こし
api_router.include_router(
    transcriptions.router, prefix="/transcriptions", tags=["文字起こし"]
)

# AI分析
api_router.include_router(
    analyses.router, prefix="/analyses", tags=["AI分析"]
)
