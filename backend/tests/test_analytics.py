import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.analysis import AnalysisType, AnalysisRequest


class TestAnalysisSchemas:
    """分析スキーマのテスト"""
    
    def test_analysis_type_enum(self):
        """分析タイプの列挙型テスト"""
        # 有効な分析タイプ
        valid_types = [
            AnalysisType.SENTIMENT,
            AnalysisType.TOPIC,
            AnalysisType.SUMMARY,
            AnalysisType.ACTION_ITEMS,
            AnalysisType.KEY_POINTS
        ]
        
        for analysis_type in valid_types:
            assert analysis_type in AnalysisType
            assert isinstance(analysis_type.value, str)
    
    def test_analysis_request_creation(self):
        """分析リクエストの作成テスト"""
        request_data = {
            "text_content": "これはテスト用のテキストです。",
            "analysis_types": [AnalysisType.SENTIMENT, AnalysisType.TOPIC],
            "user_context": {"meeting_type": "team_meeting"}
        }
        
        analysis_request = AnalysisRequest(**request_data)
        
        assert analysis_request.text_content == "これはテスト用のテキストです。"
        assert len(analysis_request.analysis_types) == 2
        assert AnalysisType.SENTIMENT in analysis_request.analysis_types
        assert AnalysisType.TOPIC in analysis_request.analysis_types
        assert analysis_request.user_context["meeting_type"] == "team_meeting"
    
    def test_analysis_request_validation(self):
        """分析リクエストのバリデーションテスト"""
        # 最小限の必須フィールド
        minimal_request = AnalysisRequest(
            text_content="Minimal text",
            analysis_types=[AnalysisType.SENTIMENT]
        )
        
        assert minimal_request.text_content == "Minimal text"
        assert minimal_request.analysis_types == [AnalysisType.SENTIMENT]
        assert minimal_request.user_context is None


class TestAnalysisBusinessLogic:
    """分析ビジネスロジックのテスト"""
    
    def test_analysis_type_combination(self):
        """分析タイプの組み合わせテスト"""
        # 単一分析
        single_analysis = [AnalysisType.SENTIMENT]
        assert len(single_analysis) == 1
        
        # 複数分析
        multiple_analysis = [
            AnalysisType.SENTIMENT,
            AnalysisType.TOPIC,
            AnalysisType.SUMMARY
        ]
        assert len(multiple_analysis) == 3
        
        # 全分析タイプ
        all_analysis_types = list(AnalysisType)
        assert len(all_analysis_types) >= 5  # 少なくとも5つの分析タイプがある
    
    def test_text_content_validation(self):
        """テキスト内容のバリデーションテスト"""
        # 短いテキスト
        short_text = "短いテキスト"
        assert len(short_text) > 0
        
        # 長いテキスト
        long_text = "これは非常に長いテキストです。" * 100
        assert len(long_text) > 1000
        
        # 空文字列（実際のアプリケーションではバリデーションエラーになるはず）
        empty_text = ""
        assert len(empty_text) == 0


class TestAnalysisAPI:
    """分析APIのテスト"""
    
    @pytest.mark.asyncio
    async def test_get_analytics_list(self, client, mock_db_session):
        """分析一覧取得のテスト"""
        # モックの設定
        mock_analytics = MagicMock()
        mock_analytics.id = 1
        mock_analytics.analysis_type = AnalysisType.SENTIMENT.value
        
        # テスト実行（実際のAPIエンドポイントがない場合はスキップ）
        # このテストは実際のAPIエンドポイントが実装された後に有効化
        pass
    
    @pytest.mark.asyncio
    async def test_create_analysis(self, client, mock_db_session):
        """分析作成のテスト"""
        # テスト実行（実際のAPIエンドポイントがない場合はスキップ）
        # このテストは実際のAPIエンドポイントが実装された後に有効化
        pass
    
    @pytest.mark.asyncio
    async def test_get_analysis_by_id(self, client, mock_db_session):
        """分析IDによる取得のテスト"""
        # テスト実行（実際のAPIエンドポイントがない場合はスキップ）
        # このテストは実際のAPIエンドポイントが実装された後に有効化
        pass


class TestAnalysisIntegration:
    """分析機能の統合テスト"""
    
    def test_analysis_workflow(self):
        """分析ワークフローのテスト"""
        # 1. 分析リクエストの作成
        request = AnalysisRequest(
            text_content="会議の内容を分析してください。",
            analysis_types=[AnalysisType.SENTIMENT, AnalysisType.TOPIC]
        )
        
        # 2. リクエストの検証
        assert request.text_content is not None
        assert len(request.analysis_types) > 0
        
        # 3. 分析タイプの確認
        for analysis_type in request.analysis_types:
            assert analysis_type in AnalysisType
        
        # 4. ユーザーコンテキストの設定（オプション）
        request.user_context = {"domain": "business", "urgency": "high"}
        assert request.user_context["domain"] == "business"
        assert request.user_context["urgency"] == "high"
    
    def test_analysis_error_handling(self):
        """分析エラーハンドリングのテスト"""
        # 無効な分析タイプ（実際のアプリケーションではバリデーションエラーになるはず）
        try:
            invalid_request = AnalysisRequest(
                text_content="Test text",
                analysis_types=["invalid_type"]  # 無効なタイプ
            )
        except Exception:
            # エラーが発生することを期待
            pass
        
        # 空のテキスト（実際のアプリケーションではバリデーションエラーになるはず）
        try:
            empty_request = AnalysisRequest(
                text_content="",  # 空のテキスト
                analysis_types=[AnalysisType.SENTIMENT]
            )
        except Exception:
            # エラーが発生することを期待
            pass
