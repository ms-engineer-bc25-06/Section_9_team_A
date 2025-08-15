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
    admin_role,
    audio_enhancement,
    participant_management,
    topic_generation,
    team_dynamics,
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

# 音声品質向上
api_router.include_router(
    audio_enhancement.router, prefix="/audio-enhancement", tags=["音声品質向上"]
)

# 管理者のルートを登録
api_router.include_router(admin_role.router, prefix="/admin-role", tags=["管理者"])

# 参加者管理
api_router.include_router(
    participant_management.router, prefix="/participant-management", tags=["参加者管理"]
)

# トークテーマ生成
api_router.include_router(
    topic_generation.router, prefix="/topic-generation", tags=["トークテーマ生成"]
)

# チームダイナミクス分析
api_router.include_router(
    team_dynamics.router, prefix="/team-dynamics", tags=["チームダイナミクス分析"]
)
