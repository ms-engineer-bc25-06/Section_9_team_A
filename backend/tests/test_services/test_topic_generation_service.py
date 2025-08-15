import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.topic_generation_service import TopicGenerationService
from app.integrations.openai_client import OpenAIClient
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.user_repository import UserRepository
from app.schemas.topic_generation import TopicGenerationRequest, PersonalizedTopicRequest
from app.core.exceptions import AnalysisError

class TestTopicGenerationService:
    """トピック生成サービスのテストクラス"""
    
    @pytest.fixture
    def mock_openai_client(self):
        """モックOpenAIクライアント"""
        return MagicMock(spec=OpenAIClient)
    
    @pytest.fixture
    def mock_analysis_repository(self):
        """モック分析リポジトリ"""
        return MagicMock(spec=AnalysisRepository)
    
    @pytest.fixture
    def mock_user_repository(self):
        """モックユーザーリポジトリ"""
        return MagicMock(spec=UserRepository)
    
    @pytest.fixture
    def mock_db(self):
        """モックデータベースセッション"""
        return AsyncMock(spec=AsyncSession)
    
    @pytest.fixture
    def topic_generation_service(self, mock_openai_client, mock_analysis_repository, mock_user_repository):
        """トピック生成サービスインスタンス"""
        return TopicGenerationService(
            openai_client=mock_openai_client,
            analysis_repository=mock_analysis_repository,
            user_repository=mock_user_repository
        )
    
    @pytest.fixture
    def sample_topic_request(self):
        """サンプルトピック生成リクエスト"""
        return TopicGenerationRequest(
            text_content="今日は良い天気ですね。",
            analysis_types=["personality", "communication"],
            user_context={"interests": ["天気", "自然"]}
        )
    
    @pytest.fixture
    def sample_personalized_request(self):
        """サンプルパーソナライズドトピックリクエスト"""
        return PersonalizedTopicRequest(
            user_id=1,
            current_topics=["天気", "仕事"],
            preferred_topics=["技術", "音楽"],
            avoid_topics=["政治", "宗教"]
        )

    @pytest.mark.asyncio
    async def test_generate_topics_success(self, topic_generation_service, mock_openai_client, sample_topic_request):
        """トピック生成成功テスト"""
        # モックの設定
        mock_openai_client.analyze_text.return_value = {
            "topics": ["天気について", "自然の美しさ", "季節の変化"],
            "confidence": 0.85,
            "analysis": "テキストから自然に関するトピックが抽出されました"
        }
        
        # 実行
        result = await topic_generation_service.generate_topics(sample_topic_request)
        
        # 検証
        assert result is not None
        assert "topics" in result
        assert len(result["topics"]) > 0
        mock_openai_client.analyze_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_topics_openai_error(self, topic_generation_service, mock_openai_client, sample_topic_request):
        """トピック生成失敗テスト（OpenAIエラー）"""
        # モックの設定
        mock_openai_client.analyze_text.side_effect = Exception("OpenAI API error")
        
        # 実行と検証
        with pytest.raises(AnalysisError) as exc_info:
            await topic_generation_service.generate_topics(sample_topic_request)
        
        assert "トピック生成に失敗しました" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_generate_topics_fallback(self, topic_generation_service, mock_openai_client, sample_topic_request):
        """トピック生成フォールバックテスト"""
        # モックの設定
        mock_openai_client.analyze_text.side_effect = Exception("OpenAI API error")
        
        # 実行
        result = await topic_generation_service.generate_topics(sample_topic_request)
        
        # 検証（フォールバックトピックが返される）
        assert result is not None
        assert "topics" in result
        assert len(result["topics"]) > 0
        # フォールバックトピックが含まれていることを確認
        fallback_topics = ["一般的な会話", "趣味について", "最近の出来事"]
        assert any(topic in result["topics"] for topic in fallback_topics)
    
    @pytest.mark.asyncio
    async def test_generate_personalized_topics_success(self, topic_generation_service, mock_openai_client, mock_user_repository, sample_personalized_request):
        """パーソナライズドトピック生成成功テスト"""
        # モックの設定
        mock_user_repository.get.return_value = MagicMock(
            id=1,
            interests=["技術", "音楽", "旅行"],
            communication_style="friendly"
        )
        
        mock_openai_client.analyze_text.return_value = {
            "topics": ["最新の技術トレンド", "お気に入りの音楽", "旅行の思い出"],
            "confidence": 0.90,
            "analysis": "ユーザーの興味に基づいてパーソナライズドされたトピックが生成されました"
        }
        
        # 実行
        result = await topic_generation_service.generate_personalized_topics(sample_personalized_request)
        
        # 検証
        assert result is not None
        assert "topics" in result
        assert len(result["topics"]) > 0
        mock_user_repository.get.assert_called_once_with(mock_user_repository.get.return_value, 1)
        mock_openai_client.analyze_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_personalized_topics_user_not_found(self, topic_generation_service, mock_user_repository, sample_personalized_request):
        """パーソナライズドトピック生成失敗テスト（ユーザー不存在）"""
        # モックの設定
        mock_user_repository.get.return_value = None
        
        # 実行と検証
        with pytest.raises(AnalysisError) as exc_info:
            await topic_generation_service.generate_personalized_topics(sample_personalized_request)
        
        assert "ユーザーが見つかりません" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_generate_personalized_topics_openai_error(self, topic_generation_service, mock_openai_client, mock_user_repository, sample_personalized_request):
        """パーソナライズドトピック生成失敗テスト（OpenAIエラー）"""
        # モックの設定
        mock_user_repository.get.return_value = MagicMock(
            id=1,
            interests=["技術", "音楽"],
            communication_style="friendly"
        )
        mock_openai_client.analyze_text.side_effect = Exception("OpenAI API error")
        
        # 実行と検証
        with pytest.raises(AnalysisError) as exc_info:
            await topic_generation_service.generate_personalized_topics(sample_personalized_request)
        
        assert "パーソナライズドトピック生成に失敗しました" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_generate_topics_for_team_success(self, topic_generation_service, mock_openai_client, mock_analysis_repository):
        """チーム向けトピック生成成功テスト"""
        # モックの設定
        mock_analysis_repository.get_team_analyses.return_value = [
            {"analysis_type": "communication", "content": "チームのコミュニケーションパターン分析"},
            {"analysis_type": "personality", "content": "チームメンバーの個性分析"}
        ]
        
        mock_openai_client.analyze_text.return_value = {
            "topics": ["チームビルディング", "効果的なコミュニケーション", "チームワークの向上"],
            "confidence": 0.88,
            "analysis": "チーム分析に基づいて適切なトピックが生成されました"
        }
        
        # 実行
        result = await topic_generation_service.generate_topics_for_team(team_id=1, context="チーム改善")
        
        # 検証
        assert result is not None
        assert "topics" in result
        assert len(result["topics"]) > 0
        mock_analysis_repository.get_team_analyses.assert_called_once()
        mock_openai_client.analyze_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_topics_for_team_no_analyses(self, topic_generation_service, mock_analysis_repository):
        """チーム向けトピック生成失敗テスト（分析データなし）"""
        # モックの設定
        mock_analysis_repository.get_team_analyses.return_value = []
        
        # 実行と検証
        with pytest.raises(AnalysisError) as exc_info:
            await topic_generation_service.generate_topics_for_team(team_id=1, context="チーム改善")
        
        assert "チームの分析データが見つかりません" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_generate_topics_for_team_openai_error(self, topic_generation_service, mock_openai_client, mock_analysis_repository):
        """チーム向けトピック生成失敗テスト（OpenAIエラー）"""
        # モックの設定
        mock_analysis_repository.get_team_analyses.return_value = [
            {"analysis_type": "communication", "content": "チームのコミュニケーションパターン分析"}
        ]
        mock_openai_client.analyze_text.side_effect = Exception("OpenAI API error")
        
        # 実行と検証
        with pytest.raises(AnalysisError) as exc_info:
            await topic_generation_service.generate_topics_for_team(team_id=1, context="チーム改善")
        
        assert "チーム向けトピック生成に失敗しました" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_save_topic_analysis_success(self, topic_generation_service, mock_analysis_repository, mock_db):
        """トピック分析保存成功テスト"""
        # モックの設定
        mock_analysis_repository.create.return_value = MagicMock(id=1)
        
        # 実行
        result = await topic_generation_service.save_topic_analysis(
            mock_db, user_id=1, topics=["トピック1", "トピック2"], analysis_data={"confidence": 0.85}
        )
        
        # 検証
        assert result is not None
        mock_analysis_repository.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_save_topic_analysis_database_error(self, topic_generation_service, mock_analysis_repository, mock_db):
        """トピック分析保存失敗テスト（データベースエラー）"""
        # モックの設定
        mock_analysis_repository.create.side_effect = Exception("Database error")
        
        # 実行と検証
        with pytest.raises(AnalysisError) as exc_info:
            await topic_generation_service.save_topic_analysis(
                mock_db, user_id=1, topics=["トピック1"], analysis_data={"confidence": 0.85}
            )
        
        assert "トピック分析の保存に失敗しました" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_topic_suggestions_success(self, topic_generation_service, mock_analysis_repository):
        """トピック提案取得成功テスト"""
        # モックの設定
        mock_analysis_repository.get_recent_analyses.return_value = [
            {"topics": ["トピック1", "トピック2"]},
            {"topics": ["トピック3", "トピック4"]}
        ]
        
        # 実行
        result = await topic_generation_service.get_topic_suggestions(user_id=1, limit=5)
        
        # 検証
        assert result is not None
        assert len(result) > 0
        mock_analysis_repository.get_recent_analyses.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_topic_suggestions_no_analyses(self, topic_generation_service, mock_analysis_repository):
        """トピック提案取得失敗テスト（分析データなし）"""
        # モックの設定
        mock_analysis_repository.get_recent_analyses.return_value = []
        
        # 実行
        result = await topic_generation_service.get_topic_suggestions(user_id=1, limit=5)
        
        # 検証（フォールバックトピックが返される）
        assert result is not None
        assert len(result) > 0
        # フォールバックトピックが含まれていることを確認
        fallback_topics = ["一般的な会話", "趣味について", "最近の出来事"]
        assert any(topic in result for topic in fallback_topics)
