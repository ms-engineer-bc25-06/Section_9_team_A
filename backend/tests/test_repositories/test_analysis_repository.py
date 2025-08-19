import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.repositories.analysis_repository import AnalysisRepository
from app.models.analysis import Analysis
from app.schemas.analysis import AnalysisCreate, AnalysisUpdate, AnalysisType
from app.core.exceptions import ValidationException, NotFoundException

class TestAnalysisRepository:
    """分析リポジトリのテストクラス"""
    
    @pytest.fixture
    def mock_db(self):
        """モックデータベースセッション"""
        return AsyncMock(spec=AsyncSession)
    
    @pytest.fixture
    def analysis_repository(self):
        """分析リポジトリインスタンス"""
        return AnalysisRepository()
    
    @pytest.fixture
    def sample_analysis(self):
        """サンプル分析オブジェクト"""
        analysis = Analysis(
            id=1,
            analysis_id="analysis_123",
            analysis_type=AnalysisType.PERSONALITY,
            content="テスト用の分析コンテンツ",
            user_id=1,
            voice_session_id=1,
            status="completed"
        )
        return analysis
    
    @pytest.fixture
    def sample_analysis_create(self):
        """サンプル分析作成データ"""
        return AnalysisCreate(
            analysis_type=AnalysisType.PERSONALITY,
            content="新しい分析コンテンツ",
            voice_session_id=1
        )
    
    @pytest.fixture
    def sample_analysis_update(self):
        """サンプル分析更新データ"""
        return AnalysisUpdate(
            title="更新された分析タイトル",
            summary="更新された要約",
            status="processing"
        )

    @pytest.mark.asyncio
    async def test_create_analysis_success(self, analysis_repository, mock_db, sample_analysis):
        """分析作成成功テスト"""
        # モックの設定
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # 実行
        result = await analysis_repository.create_analysis(mock_db, {
            "analysis_id": "analysis_123",
            "analysis_type": AnalysisType.PERSONALITY,
            "content": "テスト用の分析コンテンツ",
            "user_id": 1
        })
        
        # 検証
        assert result is not None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_analysis_database_error(self, analysis_repository, mock_db):
        """分析作成失敗テスト（データベースエラー）"""
        # データベースエラーをシミュレート
        mock_db.add.side_effect = Exception("Database error")
        mock_db.rollback.return_value = None
        
        # 実行と検証
        with pytest.raises(ValidationException) as exc_info:
            await analysis_repository.create_analysis(mock_db, {
                "analysis_id": "analysis_123",
                "analysis_type": AnalysisType.PERSONALITY,
                "content": "テスト用の分析コンテンツ",
                "user_id": 1
            })
        
        assert "分析データの作成に失敗しました" in str(exc_info.value)
        mock_db.rollback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_analysis_by_id_success(self, analysis_repository, mock_db, sample_analysis):
        """分析IDでの分析取得成功テスト"""
        # モックの設定
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_analysis
        mock_db.execute.return_value = mock_result
        
        # 実行
        result = await analysis_repository.get_analysis_by_id(mock_db, "analysis_123", 1)
        
        # 検証
        assert result == sample_analysis
        mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_analysis_by_id_not_found(self, analysis_repository, mock_db):
        """分析IDでの分析取得失敗テスト（分析不存在）"""
        # モックの設定
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        # 実行
        result = await analysis_repository.get_analysis_by_id(mock_db, "nonexistent_analysis", 1)
        
        # 検証
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_analysis_by_id_database_error(self, analysis_repository, mock_db):
        """分析IDでの分析取得失敗テスト（データベースエラー）"""
        # データベースエラーをシミュレート
        mock_db.execute.side_effect = Exception("Database connection failed")
        
        # 実行と検証
        with pytest.raises(ValidationException) as exc_info:
            await analysis_repository.get_analysis_by_id(mock_db, "analysis_123", 1)
        
        assert "分析データの取得に失敗しました" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_user_analyses_success(self, analysis_repository, mock_db, sample_analysis):
        """ユーザー分析一覧取得成功テスト"""
        # モックの設定
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_analysis]
        mock_db.execute.return_value = mock_result
        mock_db.scalar.return_value = 1  # 総件数
        
        # 実行
        result = await analysis_repository.get_user_analyses(
            mock_db, user_id=1, page=1, page_size=10
        )
        
        # 検証
        assert result["analyses"] == [sample_analysis]
        assert result["total_count"] == 1
        assert result["page"] == 1
        assert result["page_size"] == 10
        assert mock_db.execute.call_count == 2  # メインクエリ + カウントクエリ
    
    @pytest.mark.asyncio
    async def test_get_user_analyses_with_filters(self, analysis_repository, mock_db, sample_analysis):
        """フィルタ付きユーザー分析一覧取得成功テスト"""
        # モックの設定
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_analysis]
        mock_db.execute.return_value = mock_result
        mock_db.scalar.return_value = 1  # 総件数
        
        # 実行
        result = await analysis_repository.get_user_analyses(
            mock_db, 
            user_id=1, 
            page=1, 
            page_size=10,
            analysis_type=AnalysisType.PERSONALITY,
            status="completed"
        )
        
        # 検証
        assert result["analyses"] == [sample_analysis]
        assert mock_db.execute.call_count == 2
    
    @pytest.mark.asyncio
    async def test_get_user_analyses_database_error(self, analysis_repository, mock_db):
        """ユーザー分析一覧取得失敗テスト（データベースエラー）"""
        # データベースエラーをシミュレート
        mock_db.execute.side_effect = Exception("Database connection failed")
        
        # 実行と検証
        with pytest.raises(ValidationException) as exc_info:
            await analysis_repository.get_user_analyses(mock_db, user_id=1)
        
        assert "分析データ一覧の取得に失敗しました" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_analyses_by_voice_session_success(self, analysis_repository, mock_db, sample_analysis):
        """音声セッション関連分析取得成功テスト"""
        # モックの設定
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_analysis]
        mock_db.execute.return_value = mock_result
        
        # 実行
        result = await analysis_repository.get_analyses_by_voice_session(mock_db, 1)
        
        # 検証
        assert result == [sample_analysis]
        mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_analyses_by_voice_session_database_error(self, analysis_repository, mock_db):
        """音声セッション関連分析取得失敗テスト（データベースエラー）"""
        # データベースエラーをシミュレート
        mock_db.execute.side_effect = Exception("Database connection failed")
        
        # 実行と検証
        with pytest.raises(ValidationException) as exc_info:
            await analysis_repository.get_analyses_by_voice_session(mock_db, 1)
        
        assert "音声セッション関連の分析データ取得に失敗しました" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_analyses_by_transcription_success(self, analysis_repository, mock_db, sample_analysis):
        """転写関連分析取得成功テスト"""
        # モックの設定
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_analysis]
        mock_db.execute.return_value = mock_result
        
        # 実行
        result = await analysis_repository.get_analyses_by_transcription(mock_db, 1)
        
        # 検証
        assert result == [sample_analysis]
        mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_analyses_by_transcription_database_error(self, analysis_repository, mock_db):
        """転写関連分析取得失敗テスト（データベースエラー）"""
        # データベースエラーをシミュレート
        mock_db.execute.side_effect = Exception("Database connection failed")
        
        # 実行と検証
        with pytest.raises(ValidationException) as exc_info:
            await analysis_repository.get_analyses_by_transcription(mock_db, 1)
        
        assert "文字起こし関連の分析データ取得に失敗しました" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_update_analysis_success(self, analysis_repository, mock_db, sample_analysis):
        """分析更新成功テスト"""
        # モックの設定
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # 実行
        result = await analysis_repository.update_analysis(mock_db, 1, {
            "title": "更新されたタイトル",
            "status": "processing"
        })
        
        # 検証
        assert result is not None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_analysis_database_error(self, analysis_repository, mock_db):
        """分析更新失敗テスト（データベースエラー）"""
        # データベースエラーをシミュレート
        mock_db.add.side_effect = Exception("Database error")
        mock_db.rollback.return_value = None
        
        # 実行と検証
        with pytest.raises(ValidationException) as exc_info:
            await analysis_repository.update_analysis(mock_db, 1, {
                "title": "更新されたタイトル"
            })
        
        assert "分析データの更新に失敗しました" in str(exc_info.value)
        mock_db.rollback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_analysis_success(self, analysis_repository, mock_db):
        """分析削除成功テスト"""
        # モックの設定
        mock_db.delete.return_value = None
        mock_db.commit.return_value = None
        
        # 実行
        result = await analysis_repository.delete_analysis(mock_db, 1)
        
        # 検証
        assert result is True
        mock_db.delete.assert_called_once()
        mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_analysis_database_error(self, analysis_repository, mock_db):
        """分析削除失敗テスト（データベースエラー）"""
        # データベースエラーをシミュレート
        mock_db.delete.side_effect = Exception("Database error")
        mock_db.rollback.return_value = None
        
        # 実行と検証
        with pytest.raises(ValidationException) as exc_info:
            await analysis_repository.delete_analysis(mock_db, 1)
        
        assert "分析データの削除に失敗しました" in str(exc_info.value)
        mock_db.rollback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_analysis_statistics_success(self, analysis_repository, mock_db):
        """分析統計取得成功テスト"""
        # モックの設定
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            {"analysis_type": "personality", "count": 5},
            {"analysis_type": "communication", "count": 3}
        ]
        mock_db.execute.return_value = mock_result
        
        # 実行
        result = await analysis_repository.get_analysis_statistics(mock_db, 1)
        
        # 検証
        assert len(result) == 2
        mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_analysis_statistics_database_error(self, analysis_repository, mock_db):
        """分析統計取得失敗テスト（データベースエラー）"""
        # データベースエラーをシミュレート
        mock_db.execute.side_effect = Exception("Database connection failed")
        
        # 実行と検証
        with pytest.raises(ValidationException) as exc_info:
            await analysis_repository.get_analysis_statistics(mock_db, 1)
        
        assert "分析統計の取得に失敗しました" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_recent_analyses_success(self, analysis_repository, mock_db, sample_analysis):
        """最近の分析取得成功テスト"""
        # モックの設定
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_analysis]
        mock_db.execute.return_value = mock_result
        
        # 実行
        result = await analysis_repository.get_recent_analyses(mock_db, 1, limit=5)
        
        # 検証
        assert result == [sample_analysis]
        mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_recent_analyses_database_error(self, analysis_repository, mock_db):
        """最近の分析取得失敗テスト（データベースエラー）"""
        # データベースエラーをシミュレート
        mock_db.execute.side_effect = Exception("Database connection failed")
        
        # 実行と検証
        with pytest.raises(ValidationException) as exc_info:
            await analysis_repository.get_recent_analyses(mock_db, 1)
        
        assert "最近の分析データ取得に失敗しました" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_analyses_by_keywords_success(self, analysis_repository, mock_db, sample_analysis):
        """キーワード検索成功テスト"""
        # モックの設定
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_analysis]
        mock_db.execute.return_value = mock_result
        
        # 実行
        result = await analysis_repository.get_analyses_by_keywords(mock_db, 1, ["テスト", "分析"])
        
        # 検証
        assert result == [sample_analysis]
        mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_analyses_by_keywords_database_error(self, analysis_repository, mock_db):
        """キーワード検索失敗テスト（データベースエラー）"""
        # データベースエラーをシミュレート
        mock_db.execute.side_effect = Exception("Database connection failed")
        
        # 実行と検証
        with pytest.raises(ValidationException) as exc_info:
            await analysis_repository.get_analyses_by_keywords(mock_db, 1, ["テスト"])
        
        assert "キーワード検索に失敗しました" in str(exc_info.value)
