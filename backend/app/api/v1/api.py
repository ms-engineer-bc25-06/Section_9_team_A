from fastapi import APIRouter

from app.api.v1 import (
    auth,
    users,
    teams,
    voice_sessions,
    transcriptions,
    analytics,
    billing,
    subscriptions,
    invitations,
    webhooks,
    chat_rooms,
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

# チャットルーム
api_router.include_router(
    chat_rooms.router, prefix="/chat-rooms", tags=["チャットルーム"]
)

# 文字起こし
api_router.include_router(
    transcriptions.router, prefix="/transcriptions", tags=["文字起こし"]
)

# AI分析
api_router.include_router(analytics.router, prefix="/analytics", tags=["AI分析"])

# 決済管理
api_router.include_router(billing.router, prefix="/billing", tags=["決済"])

# サブスクリプション
api_router.include_router(
    subscriptions.router, prefix="/subscriptions", tags=["サブスクリプション"]
)

# 招待管理
api_router.include_router(invitations.router, prefix="/invitations", tags=["招待"])

# Webhook
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhook"])
