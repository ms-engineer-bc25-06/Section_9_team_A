from fastapi import APIRouter

from app.api.v1 import (
    auth,
    users,
    voice_sessions,
    transcriptions,
    chat_rooms,
    privacy,
    subscriptions,
    invitations,
    webhooks,
    # 統合されたAPI
    analysis_unified,
    admin_unified,
    team_unified,
    # 個別のAPI（統合されていないもの）
    participant_management,
    topic_generation,
    audio_enhancement,
    personal_growth,
    industry_management,
    comparison_analysis,
    report_management,
    feedback_approvals,
    admin_users,
    admin_role,
)

api_router = APIRouter()

# 認証関連
api_router.include_router(auth.router, prefix="/auth", tags=["認証"])

# ユーザー管理
api_router.include_router(users.router, prefix="/users", tags=["ユーザー"])

# 音声セッション
api_router.include_router(voice_sessions.router, prefix="/voice-sessions", tags=["音声セッション"])

# 文字起こし
api_router.include_router(transcriptions.router, prefix="/transcriptions", tags=["文字起こし"])

# チャットルーム
api_router.include_router(chat_rooms.router, prefix="/chat-rooms", tags=["チャットルーム"])

# プライバシー制御
api_router.include_router(privacy.router, prefix="/privacy", tags=["プライバシー制御"])

# サブスクリプション管理
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["サブスクリプション"])

# 招待管理
api_router.include_router(invitations.router, prefix="/invitations", tags=["招待管理"])

# Webhooks
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])

# 統合された分析API
api_router.include_router(analysis_unified.router, prefix="/analyses", tags=["統合分析"])

# 統合された管理者API
api_router.include_router(admin_unified.router, prefix="/admin", tags=["統合管理者"])

# 管理者用ユーザー管理API
api_router.include_router(admin_users.router, tags=["管理者ユーザー管理"])

# 管理者権限チェックAPI
api_router.include_router(admin_role.router, prefix="/admin-role", tags=["管理者権限"])

# 統合されたチームAPI
api_router.include_router(team_unified.router, prefix="/teams", tags=["統合チーム"])

# 参加者管理
api_router.include_router(participant_management.router, prefix="/participants", tags=["参加者管理"])

# トピック生成
api_router.include_router(topic_generation.router, prefix="/topics", tags=["トピック生成"])

# 音声エンハンスメント
api_router.include_router(audio_enhancement.router, prefix="/audio-enhancement", tags=["音声エンハンスメント"])

# 個人成長
api_router.include_router(personal_growth.router, prefix="/personal-growth", tags=["個人成長"])

# 業界管理
api_router.include_router(industry_management.router, prefix="/industry", tags=["業界管理"])

# 比較分析
api_router.include_router(comparison_analysis.router, prefix="/comparison", tags=["比較分析"])

# レポート管理
api_router.include_router(report_management.router, prefix="/reports", tags=["レポート管理"])

# フィードバック承認
api_router.include_router(feedback_approvals.router, prefix="/feedback-approvals", tags=["フィードバック承認"])
