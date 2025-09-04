import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class TestUserModel:
    """ユーザーモデルのテスト"""
    
    def test_user_creation(self):
        """ユーザーの作成テスト"""
        user = User(
            id=1,
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            firebase_uid="test_firebase_uid_123"
        )
        
        assert user.id == 1
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        assert user.firebase_uid == "test_firebase_uid_123"
        assert user.is_active is True
        assert user.is_premium is False
    
    def test_user_default_values(self):
        """ユーザーのデフォルト値テスト"""
        user = User(
            email="test@example.com",
            username="testuser"
        )
        
        assert user.is_active is True
        assert user.is_verified is False
        assert user.is_premium is False
        assert user.is_admin is False
        assert user.subscription_status == "free"
        assert user.monthly_voice_minutes == 0
        assert user.monthly_analysis_count == 0


class TestUserSchemas:
    """ユーザースキーマのテスト"""
    
    def test_user_create_schema(self):
        """ユーザー作成スキーマのテスト"""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "full_name": "New User"
        }
        
        user_create = UserCreate(**user_data)
        assert user_create.email == "newuser@example.com"
        assert user_create.username == "newuser"
        assert user_create.full_name == "New User"
    
    def test_user_update_schema(self):
        """ユーザー更新スキーマのテスト"""
        update_data = {
            "full_name": "Updated Name",
            "bio": "Updated bio"
        }
        
        user_update = UserUpdate(**update_data)
        assert user_update.full_name == "Updated Name"
        assert user_update.bio == "Updated bio"


class TestUserAPI:
    """ユーザーAPIのテスト"""
    
    @pytest.mark.asyncio
    async def test_get_user_profile(self, client, mock_db_session, sample_user_data):
        """ユーザープロフィール取得のテスト"""
        # モックの設定
        mock_user = MagicMock()
        mock_user.id = sample_user_data["id"]
        mock_user.email = sample_user_data["email"]
        mock_user.username = sample_user_data["username"]
        mock_user.full_name = sample_user_data["full_name"]
        
        # テスト実行（実際のAPIエンドポイントがない場合はスキップ）
        # このテストは実際のAPIエンドポイントが実装された後に有効化
        pass
    
    @pytest.mark.asyncio
    async def test_update_user_profile(self, client, mock_db_session, sample_user_data):
        """ユーザープロフィール更新のテスト"""
        # モックの設定
        mock_user = MagicMock()
        mock_user.id = sample_user_data["id"]
        
        # テスト実行（実際のAPIエンドポイントがない場合はスキップ）
        # このテストは実際のAPIエンドポイントが実装された後に有効化
        pass
