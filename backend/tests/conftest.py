import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db
from app.core.config import settings

# テスト用のモックデータベースセッション
@pytest.fixture
def mock_db_session():
    """モックデータベースセッション"""
    return AsyncMock(spec=AsyncSession)

# テスト用のHTTPクライアント
@pytest.fixture
def client():
    """テスト用HTTPクライアント"""
    return TestClient(app)

# テスト用のユーザーデータ
@pytest.fixture
def sample_user_data():
    """サンプルユーザーデータ"""
    return {
        "id": 1,
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "is_active": True,
        "is_premium": False,
        "firebase_uid": "test_firebase_uid_123"
    }

# テスト用のチームデータ
@pytest.fixture
def sample_team_data():
    """サンプルチームデータ"""
    return {
        "id": 1,
        "name": "Test Team",
        "description": "A test team",
        "owner_id": 1,
        "is_active": True
    }

# テスト用の音声セッションデータ
@pytest.fixture
def sample_voice_session_data():
    """サンプル音声セッションデータ"""
    return {
        "id": 1,
        "title": "Test Session",
        "description": "A test voice session",
        "team_id": 1,
        "host_id": 1,
        "status": "active",
        "is_recording": False
    }

# テスト用の転写データ
@pytest.fixture
def sample_transcription_data():
    """サンプル転写データ"""
    return {
        "id": 1,
        "voice_session_id": 1,
        "speaker_id": 1,
        "text_content": "これはテスト用の転写テキストです。",
        "start_time_seconds": 0.0,
        "end_time_seconds": 5.0,
        "confidence_score": 0.95,
        "language": "ja",
        "is_final": True,
        "is_processed": False
    }

# テスト用の分析データ
@pytest.fixture
def sample_analysis_data():
    """サンプル分析データ"""
    return {
        "id": 1,
        "analysis_id": "analysis_123",
        "analysis_type": "personality",
        "content": "テスト用の分析コンテンツ",
        "user_id": 1,
        "status": "completed"
    }

# モックリポジトリのフィクスチャ
@pytest.fixture
def mock_user_repository():
    """モックユーザーリポジトリ"""
    return MagicMock()

@pytest.fixture
def mock_team_repository():
    """モックチームリポジトリ"""
    return MagicMock()

@pytest.fixture
def mock_voice_session_repository():
    """モック音声セッションリポジトリ"""
    return MagicMock()

@pytest.fixture
def mock_transcription_repository():
    """モック転写リポジトリ"""
    return MagicMock()

@pytest.fixture
def mock_analysis_repository():
    """モック分析リポジトリ"""
    return MagicMock()

# モックサービスのフィクスチャ
@pytest.fixture
def mock_auth_service():
    """モック認証サービス"""
    return MagicMock()

@pytest.fixture
def mock_user_service():
    """モックユーザーサービス"""
    return MagicMock()

@pytest.fixture
def mock_team_service():
    """モックチームサービス"""
    return MagicMock()

@pytest.fixture
def mock_voice_session_service():
    """モック音声セッションサービス"""
    return MagicMock()

@pytest.fixture
def mock_transcription_service():
    """モック転写サービス"""
    return MagicMock()

@pytest.fixture
def mock_ai_analysis_service():
    """モックAI分析サービス"""
    return MagicMock()

# テスト用の設定
@pytest.fixture(autouse=True)
def setup_test_environment():
    """テスト環境のセットアップ"""
    # テスト用の設定を適用
    settings.ENVIRONMENT = "test"
    settings.DEBUG = True
    
    yield
    
    # テスト後のクリーンアップ
    pass
