from app.services.topic_generation_service import TopicGenerationService
from app.repositories import (
    analysis_repository,
    user_repository,
    transcription_repository,
    voice_session_repository,
    chat_room_repository,
    subscription_repository,
    organization_repository,
    billing_repository
)
from app.integrations.openai_client import openai_client

def get_topic_generation_service() -> TopicGenerationService:
    """トークテーマ生成サービスの依存関係を取得"""
    return TopicGenerationService(
        openai_client=openai_client,
        analysis_repository=analysis_repository,
        user_repository=user_repository
    )

def get_openai_client():
    """OpenAIクライアントの依存関係を取得"""
    return openai_client

def get_analysis_repository():
    """分析リポジトリの依存関係を取得"""
    return analysis_repository

def get_user_repository():
    """ユーザーリポジトリの依存関係を取得"""
    return user_repository

def get_transcription_repository():
    """転写リポジトリの依存関係を取得"""
    return transcription_repository

def get_voice_session_repository():
    """音声セッションリポジトリの依存関係を取得"""
    return voice_session_repository

def get_chat_room_repository():
    """チャットルームリポジトリの依存関係を取得"""
    return chat_room_repository

def get_subscription_repository():
    """サブスクリプションリポジトリの依存関係を取得"""
    return subscription_repository

def get_team_repository():
    """チームリポジトリの依存関係を取得（organization_repositoryに統合）"""
    return organization_repository

def get_billing_repository():
    """請求リポジトリの依存関係を取得"""
    return billing_repository
