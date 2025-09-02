import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.core.database import get_db
from app.config import settings
from app.models.base import Base
from app.models.user import User
from app.core.auth import create_access_token

# テスト用のHTTPクライアント（同期・非同期両対応）
class CombinedTestClient:
    """同期・非同期両方のテストクライアント"""
    
    def __init__(self):
        self.sync_client = TestClient(app)
        self.async_client = None
    
    def __getattr__(self, name):
        """同期クライアントのメソッドを委譲"""
        return getattr(self.sync_client, name)
    
    async def get_async_client(self):
        """非同期クライアントを取得"""
        if self.async_client is None:
            self.async_client = AsyncClient(app=app, base_url="http://test")
        return self.async_client
    
    async def aclose(self):
        """非同期クライアントを閉じる"""
        if self.async_client:
            await self.async_client.aclose()
            self.async_client = None

# テスト用のデータベースエンジン
@pytest.fixture
def test_db_engine():
    """テスト用データベースエンジン"""
    # テスト用のインメモリSQLiteデータベース
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False
    )
    return engine

# テスト用のデータベースセッション
@pytest.fixture
async def test_db_session(test_db_engine):
    """テスト用データベースセッション"""
    # テーブル作成
    async with test_db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # セッション作成
    async_session = sessionmaker(
        test_db_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session

# テスト用のモックデータベースセッション
@pytest.fixture
def mock_db_session():
    """モックデータベースセッション"""
    return AsyncMock(spec=AsyncSession)

# テスト用のHTTPクライアント
@pytest.fixture
def client():
    """テスト用HTTPクライアント"""
    return CombinedTestClient()

# テスト用のクライアント（認証テスト用）
@pytest.fixture
def auth_client(test_db_session):
    """認証テスト用クライアント"""
    def override_get_db():
        return test_db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

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

# テスト用のユーザー（データベース内）
@pytest.fixture
async def test_user(test_db_session):
    """テスト用ユーザー"""
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        firebase_uid="test_firebase_uid",
        is_active=True,
        is_admin=False,
        has_temporary_password=False,
        is_first_login=False
    )
    
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    
    return user

# テスト用の管理者ユーザー
@pytest.fixture
async def test_admin_user(test_db_session):
    """テスト用管理者ユーザー"""
    admin_user = User(
        email="admin@example.com",
        username="admin",
        full_name="Admin User",
        firebase_uid="admin_firebase_uid",
        is_active=True,
        is_admin=True,
        has_temporary_password=False,
        is_first_login=False
    )
    
    test_db_session.add(admin_user)
    await test_db_session.commit()
    await test_db_session.refresh(admin_user)
    
    return admin_user

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

# JWTトークンフィクスチャ
@pytest.fixture
async def user_jwt_token(test_user):
    """ユーザー用JWTトークン"""
    user = await test_user  # 非同期フィクスチャを待機
    return create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )

@pytest.fixture
async def admin_jwt_token(test_admin_user):
    """管理者用JWTトークン"""
    admin_user = await test_admin_user  # 非同期フィクスチャを待機
    return create_access_token(
        data={"sub": str(admin_user.id), "email": admin_user.email}
    )

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
    mock_service = MagicMock()
    mock_service.authenticate_user = AsyncMock()
    mock_service.get_firebase_user_only = AsyncMock()
    mock_service.get_user_by_email = AsyncMock()
    return mock_service

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

# Firebase関連のモック
@pytest.fixture
def mock_firebase_auth():
    """Firebase認証のモック"""
    with pytest.MonkeyPatch().context() as m:
        # Firebase認証関連のモック
        m.setattr('app.core.auth.verify_firebase_token', AsyncMock())
        m.setattr('app.integrations.firebase_client.verify_firebase_token', AsyncMock())
        yield m

@pytest.fixture
def mock_firebase_user():
    """Firebaseユーザーのモック"""
    mock_user = MagicMock()
    mock_user.uid = "test_firebase_uid"
    mock_user.email = "test@example.com"
    mock_user.display_name = "Test User"
    mock_user.getIdToken = AsyncMock(return_value="firebase_id_token")
    return mock_user

@pytest.fixture
def mock_firebase_payload():
    """Firebase認証ペイロードのモック"""
    return {
        "uid": "test_firebase_uid",
        "email": "test@example.com",
        "name": "Test User"
    }

# WebSocket関連のモック
@pytest.fixture
def mock_websocket():
    """WebSocketのモック"""
    mock_ws = MagicMock()
    mock_ws.query_params = {}
    mock_ws.client_state.value = "CONNECTED"
    mock_ws.close = AsyncMock()
    return mock_ws

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

# テスト用のヘルパー関数
def create_test_user_data(email="test@example.com", is_admin=False):
    """テスト用ユーザーデータを作成"""
    return {
        "email": email,
        "username": email.split("@")[0],
        "full_name": "Test User",
        "firebase_uid": f"test_uid_{email.split('@')[0]}",
        "is_active": True,
        "is_admin": is_admin,
        "has_temporary_password": False,
        "is_first_login": False
    }

def create_auth_headers(token):
    """認証ヘッダーを作成"""
    return {"Authorization": f"Bearer {token}"}

async def create_test_user_in_db(session: AsyncSession, **kwargs):
    """データベースにテストユーザーを作成"""
    user_data = create_test_user_data(**kwargs)
    user = User(**user_data)
    
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    return user
