from app.services.topic_generation_service import TopicGenerationService
from app.repositories.analysis_repository import analysis_repository
from app.repositories.user_repository import user_repository
from app.repositories.transcription_repository import transcription_repository
from app.repositories.voice_session_repository import voice_session_repository
from app.repositories.chat_room_repository import chat_room_repository
from app.repositories.subscription_repository import subscription_repository
from app.repositories.team_repository import team_repository
from app.repositories.billing_repository import billing_repository
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
    """チームリポジトリの依存関係を取得"""
    return team_repository

def get_billing_repository():
    """請求リポジトリの依存関係を取得"""
    return billing_repository
