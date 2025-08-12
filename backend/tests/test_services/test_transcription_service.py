import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.transcription_service import TranscriptionService
from app.repositories.transcription_repository import transcription_repository
from app.schemas.transcription import TranscriptionCreate, TranscriptionResponse
from app.core.exceptions import ValidationException

class TestTranscriptionService:
    """転写サービスのテストクラス"""
    
    @pytest.fixture
    def mock_db(self):
        """モックデータベースセッション"""
        return AsyncMock(spec=AsyncSession)
    
    @pytest.fixture
    def transcription_service(self):
        """転写サービスインスタンス"""
        return TranscriptionService()
    
    @pytest.fixture
    def sample_transcription_create(self):
        """サンプル転写作成データ"""
        return TranscriptionCreate(
            voice_session_id=1,
            speaker_id=1,
            text_content="これはテスト用の転写テキストです。",
            start_time_seconds=0.0,
            end_time_seconds=5.0,
            confidence_score=0.95,
            language="ja",
            is_final=True,
            is_processed=False
        )
    
    @pytest.fixture
    def sample_transcription_response(self):
        """サンプル転写レスポンスデータ"""
        return TranscriptionResponse(
            id=1,
            voice_session_id=1,
            speaker_id=1,
            text_content="これはテスト用の転写テキストです。",
            start_time_seconds=0.0,
            end_time_seconds=5.0,
            confidence_score=0.95,
            language="ja",
            is_final=True,
            is_processed=False,
            created_at="2024-01-01T00:00:00",
            updated_at=None,
            processed_at=None,
            speaker_name="Test Speaker",
            speaker_avatar=None
        )

    @pytest.mark.asyncio
    async def test_create_transcription_success(self, transcription_service, mock_db, sample_transcription_create):
        """転写作成成功テスト"""
        # モックの設定
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # 実行
        result = await transcription_service.create(sample_transcription_create)
        
        # 検証
        assert result is not None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_transcription_database_error(self, transcription_service, mock_db, sample_transcription_create):
        """転写作成失敗テスト（データベースエラー）"""
        # データベースエラーをシミュレート
        mock_db.add.side_effect = Exception("Database error")
        mock_db.rollback.return_value = None
        
        # 実行と検証
        with pytest.raises(ValidationException) as exc_info:
            await transcription_service.create(sample_transcription_create)
        
        assert "Failed to create transcription" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_by_session_success(self, transcription_service, mock_db, sample_transcription_response):
        """セッション別転写取得成功テスト"""
        # モックの設定
        mock_transcription = MagicMock()
        mock_transcription.model_validate.return_value = sample_transcription_response
        
        # transcription_repositoryのモック
        with pytest.MonkeyPatch().context() as m:
            m.setattr(transcription_repository, 'get_by_session', AsyncMock(return_value=[mock_transcription]))
            
            # 実行
            result = await transcription_service.get_by_session(1, limit=10, offset=0)
        
        # 検証
        assert result is not None
        assert len(result) == 1
    
    @pytest.mark.asyncio
    async def test_get_by_session_database_error(self, transcription_service, mock_db):
        """セッション別転写取得失敗テスト（データベースエラー）"""
        # データベースエラーをシミュレート
        with pytest.MonkeyPatch().context() as m:
            m.setattr(transcription_repository, 'get_by_session', AsyncMock(side_effect=Exception("Database error")))
            
            # 実行と検証
            with pytest.raises(ValidationException) as exc_info:
                await transcription_service.get_by_session(1, limit=10, offset=0)
            
            assert "Failed to get transcriptions by session" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_session_stats_success(self, transcription_service, mock_db):
        """セッション統計取得成功テスト"""
        # モックの設定
        mock_stats = MagicMock()
        mock_stats.model_validate.return_value = MagicMock(
            total_transcriptions=10,
            total_duration=50.0,
            average_confidence=0.92,
            unique_speakers=3
        )
        
        # transcription_repositoryのモック
        with pytest.MonkeyPatch().context() as m:
            m.setattr(transcription_repository, 'get_session_stats', AsyncMock(return_value=mock_stats))
            
            # 実行
            result = await transcription_service.get_session_stats(1)
        
        # 検証
        assert result is not None
        assert result.total_transcriptions == 10
        assert result.total_duration == 50.0
        assert result.average_confidence == 0.92
        assert result.unique_speakers == 3
    
    @pytest.mark.asyncio
    async def test_get_session_stats_database_error(self, transcription_service, mock_db):
        """セッション統計取得失敗テスト（データベースエラー）"""
        # データベースエラーをシミュレート
        with pytest.MonkeyPatch().context() as m:
            m.setattr(transcription_repository, 'get_session_stats', AsyncMock(side_effect=Exception("Database error")))
            
            # 実行と検証
            with pytest.raises(ValidationException) as exc_info:
                await transcription_service.get_session_stats(1)
            
            assert "Failed to get session stats" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_process_realtime_transcription_success(self, transcription_service):
        """リアルタイム転写処理成功テスト"""
        # テストデータ
        audio_data = b"test_audio_data"
        session_id = 1
        user_id = 1
        
        # 実行
        result = await transcription_service.process_realtime_transcription(
            audio_data, session_id, user_id
        )
        
        # 検証
        assert result is not None
        assert "transcription_id" in result
        assert "confidence" in result
    
    @pytest.mark.asyncio
    async def test_process_realtime_transcription_invalid_audio(self, transcription_service):
        """リアルタイム転写処理失敗テスト（無効な音声データ）"""
        # 無効な音声データ
        invalid_audio_data = b""
        session_id = 1
        user_id = 1
        
        # 実行と検証
        with pytest.raises(ValidationException) as exc_info:
            await transcription_service.process_realtime_transcription(
                invalid_audio_data, session_id, user_id
            )
        
        assert "Invalid audio data" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_enhance_transcription_success(self, transcription_service, sample_transcription_response):
        """転写強化成功テスト"""
        # テストデータ
        transcription_id = 1
        enhancement_options = {
            "grammar_correction": True,
            "punctuation_restoration": True,
            "context_clarification": False
        }
        
        # 実行
        result = await transcription_service.enhance_transcription(
            transcription_id, enhancement_options
        )
        
        # 検証
        assert result is not None
        assert "enhanced_text" in result
        assert "enhancement_metadata" in result
    
    @pytest.mark.asyncio
    async def test_enhance_transcription_not_found(self, transcription_service):
        """転写強化失敗テスト（転写不存在）"""
        # 存在しない転写ID
        transcription_id = 999
        enhancement_options = {"grammar_correction": True}
        
        # 実行と検証
        with pytest.raises(ValidationException) as exc_info:
            await transcription_service.enhance_transcription(
                transcription_id, enhancement_options
            )
        
        assert "Transcription not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_search_transcriptions_success(self, transcription_service):
        """転写検索成功テスト"""
        # テストデータ
        session_id = 1
        search_query = "テスト"
        limit = 10
        
        # 実行
        result = await transcription_service.search_transcriptions(
            session_id, search_query, limit
        )
        
        # 検証
        assert result is not None
        assert "transcriptions" in result
        assert "total_count" in result
    
    @pytest.mark.asyncio
    async def test_search_transcriptions_empty_query(self, transcription_service):
        """転写検索失敗テスト（空のクエリ）"""
        # 空の検索クエリ
        session_id = 1
        search_query = ""
        limit = 10
        
        # 実行と検証
        with pytest.raises(ValidationException) as exc_info:
            await transcription_service.search_transcriptions(
                session_id, search_query, limit
            )
        
        assert "Search query cannot be empty" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_export_transcriptions_success(self, transcription_service):
        """転写エクスポート成功テスト"""
        # テストデータ
        session_id = 1
        export_format = "json"
        
        # 実行
        result = await transcription_service.export_transcriptions(
            session_id, export_format
        )
        
        # 検証
        assert result is not None
        assert "export_data" in result
        assert "format" in result
        assert result["format"] == export_format
    
    @pytest.mark.asyncio
    async def test_export_transcriptions_unsupported_format(self, transcription_service):
        """転写エクスポート失敗テスト（サポートされていない形式）"""
        # サポートされていない形式
        session_id = 1
        export_format = "unsupported_format"
        
        # 実行と検証
        with pytest.raises(ValidationException) as exc_info:
            await transcription_service.export_transcriptions(
                session_id, export_format
            )
        
        assert "Unsupported export format" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_speaker_statistics_success(self, transcription_service):
        """話者統計取得成功テスト"""
        # テストデータ
        session_id = 1
        
        # 実行
        result = await transcription_service.get_speaker_statistics(session_id)
        
        # 検証
        assert result is not None
        assert "speakers" in result
        assert "total_speaking_time" in result
        assert "speaking_distribution" in result
    
    @pytest.mark.asyncio
    async def test_get_speaker_statistics_no_session(self, transcription_service):
        """話者統計取得失敗テスト（セッション不存在）"""
        # 存在しないセッションID
        session_id = 999
        
        # 実行と検証
        with pytest.raises(ValidationException) as exc_info:
            await transcription_service.get_speaker_statistics(session_id)
        
        assert "Session not found" in str(exc_info.value)
