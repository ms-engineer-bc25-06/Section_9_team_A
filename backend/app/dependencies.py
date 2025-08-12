from app.services.topic_generation_service import TopicGenerationService
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.user_repository import UserRepository
from app.integrations.openai_client import OpenAIClient

def get_topic_generation_service() -> TopicGenerationService:
    """トークテーマ生成サービスの依存関係を取得"""
    openai_client = OpenAIClient()
    analysis_repository = AnalysisRepository()
    user_repository = UserRepository()
    
    return TopicGenerationService(
        openai_client=openai_client,
        analysis_repository=analysis_repository,
        user_repository=user_repository
    )
