from fastapi import APIRouter

from app.api.v1 import (
    auth,
    users,
    teams,
    voice_sessions,
    transcriptions,
    analyses,
    chat_rooms,
    team_dynamics,
    privacy,
    subscriptions,
    invitations,
    billing,
    audit_logs,
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

# チャットルーム
api_router.include_router(
    chat_rooms.router, prefix="/chat-rooms", tags=["チャットルーム"]
)

# チームダイナミクス
api_router.include_router(
    team_dynamics.router, prefix="/team-dynamics", tags=["チームダイナミクス"]
)

# プライバシー制御
api_router.include_router(
    privacy.router, prefix="/privacy", tags=["プライバシー制御"]
)

# サブスクリプション管理
api_router.include_router(
    subscriptions.router, prefix="/subscriptions", tags=["サブスクリプション"]
)

# 招待管理
api_router.include_router(
    invitations.router, prefix="/invitations", tags=["招待管理"]
)

# 請求管理
api_router.include_router(
    billing.router, prefix="/billing", tags=["請求管理"]
)

# 監査ログ
api_router.include_router(
    audit_logs.router, prefix="/audit-logs", tags=["監査ログ"]
)
