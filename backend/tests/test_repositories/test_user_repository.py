import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.exceptions import ValidationException, NotFoundException

class TestUserRepository:
    """ユーザーリポジトリのテストクラス"""
    
    @pytest.fixture
    def mock_db(self):
        """モックデータベースセッション"""
        return AsyncMock(spec=AsyncSession)
    
    @pytest.fixture
    def user_repository(self):
        """ユーザーリポジトリインスタンス"""
        return UserRepository()
    
    @pytest.fixture
    def sample_user(self):
        """サンプルユーザーオブジェクト"""
        user = User(
            id=1,
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            is_active=True,
            is_premium=False,
            firebase_uid="test_firebase_uid_123"
        )
        return user
    
    @pytest.fixture
    def sample_user_create(self):
        """サンプルユーザー作成データ"""
        return UserCreate(
            email="newuser@example.com",
            username="newuser",
            full_name="New User",
            firebase_uid="new_firebase_uid_456"
        )
    
    @pytest.fixture
    def sample_user_update(self):
        """サンプルユーザー更新データ"""
        return UserUpdate(
            full_name="Updated User Name",
            is_premium=True
        )

    @pytest.mark.asyncio
    async def test_get_by_email_success(self, user_repository, mock_db, sample_user):
        """メールアドレスでのユーザー取得成功テスト"""
        # モックの設定
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db.execute.return_value = mock_result
        
        # 実行
        result = await user_repository.get_by_email(mock_db, "test@example.com")
        
        # 検証
        assert result == sample_user
        mock_db.execute.assert_called_once()
        # select文の検証
        call_args = mock_db.execute.call_args[0][0]
        assert isinstance(call_args, select)
    
    @pytest.mark.asyncio
    async def test_get_by_email_not_found(self, user_repository, mock_db):
        """メールアドレスでのユーザー取得失敗テスト（ユーザー不存在）"""
        # モックの設定
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        # 実行
        result = await user_repository.get_by_email(mock_db, "nonexistent@example.com")
        
        # 検証
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_by_email_database_error(self, user_repository, mock_db):
        """メールアドレスでのユーザー取得失敗テスト（データベースエラー）"""
        # データベースエラーをシミュレート
        mock_db.execute.side_effect = Exception("Database connection failed")
        
        # 実行と検証
        with pytest.raises(ValidationException) as exc_info:
            await user_repository.get_by_email(mock_db, "test@example.com")
        
        assert "メールアドレスでのユーザー取得に失敗しました" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_by_username_success(self, user_repository, mock_db, sample_user):
        """ユーザー名でのユーザー取得成功テスト"""
        # モックの設定
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db.execute.return_value = mock_result
        
        # 実行
        result = await user_repository.get_by_username(mock_db, "testuser")
        
        # 検証
        assert result == sample_user
        mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_username_database_error(self, user_repository, mock_db):
        """ユーザー名でのユーザー取得失敗テスト（データベースエラー）"""
        # データベースエラーをシミュレート
        mock_db.execute.side_effect = Exception("Database connection failed")
        
        # 実行と検証
        with pytest.raises(ValidationException) as exc_info:
            await user_repository.get_by_username(mock_db, "testuser")
        
        assert "ユーザー名でのユーザー取得に失敗しました" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_by_firebase_uid_success(self, user_repository, mock_db, sample_user):
        """Firebase UIDでのユーザー取得成功テスト"""
        # モックの設定
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db.execute.return_value = mock_result
        
        # 実行
        result = await user_repository.get_by_firebase_uid(mock_db, "test_firebase_uid_123")
        
        # 検証
        assert result == sample_user
        mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_firebase_uid_database_error(self, user_repository, mock_db):
        """Firebase UIDでのユーザー取得失敗テスト（データベースエラー）"""
        # データベースエラーをシミュレート
        mock_db.execute.side_effect = Exception("Database connection failed")
        
        # 実行と検証
        with pytest.raises(ValidationException) as exc_info:
            await user_repository.get_by_firebase_uid(mock_db, "test_firebase_uid_123")
        
        assert "Firebase UIDでのユーザー取得に失敗しました" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_active_users_success(self, user_repository, mock_db, sample_user):
        """アクティブユーザー一覧取得成功テスト"""
        # モックの設定
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_user]
        mock_db.execute.return_value = mock_result
        
        # 実行
        result = await user_repository.get_active_users(mock_db, skip=0, limit=10)
        
        # 検証
        assert result == [sample_user]
        mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_active_users_database_error(self, user_repository, mock_db):
        """アクティブユーザー一覧取得失敗テスト（データベースエラー）"""
        # データベースエラーをシミュレート
        mock_db.execute.side_effect = Exception("Database connection failed")
        
        # 実行と検証
        with pytest.raises(ValidationException) as exc_info:
            await user_repository.get_active_users(mock_db, skip=0, limit=10)
        
        assert "アクティブユーザーの取得に失敗しました" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_premium_users_success(self, user_repository, mock_db, sample_user):
        """プレミアムユーザー一覧取得成功テスト"""
        # モックの設定
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_user]
        mock_db.execute.return_value = mock_result
        
        # 実行
        result = await user_repository.get_premium_users(mock_db, skip=0, limit=10)
        
        # 検証
        assert result == [sample_user]
        mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_premium_users_database_error(self, user_repository, mock_db):
        """プレミアムユーザー一覧取得失敗テスト（データベースエラー）"""
        # データベースエラーをシミュレート
        mock_db.execute.side_effect = Exception("Database connection failed")
        
        # 実行と検証
        with pytest.raises(ValidationException) as exc_info:
            await user_repository.get_premium_users(mock_db, skip=0, limit=10)
        
        assert "プレミアムユーザーの取得に失敗しました" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_search_users_success(self, user_repository, mock_db, sample_user):
        """ユーザー検索成功テスト"""
        # モックの設定
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_user]
        mock_db.execute.return_value = mock_result
        
        # 実行
        result = await user_repository.search_users(mock_db, "test", skip=0, limit=10)
        
        # 検証
        assert result == [sample_user]
        mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_users_database_error(self, user_repository, mock_db):
        """ユーザー検索失敗テスト（データベースエラー）"""
        # データベースエラーをシミュレート
        mock_db.execute.side_effect = Exception("Database connection failed")
        
        # 実行と検証
        with pytest.raises(ValidationException) as exc_info:
            await user_repository.search_users(mock_db, "test", skip=0, limit=10)
        
        assert "ユーザー検索に失敗しました" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_update_last_login_success(self, user_repository, mock_db, sample_user):
        """最終ログイン時刻更新成功テスト"""
        # モックの設定
        user_repository.get.return_value = sample_user
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # 実行
        result = await user_repository.update_last_login(mock_db, 1)
        
        # 検証
        assert result == sample_user
        mock_db.add.assert_called_once_with(sample_user)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(sample_user)
    
    @pytest.mark.asyncio
    async def test_update_last_login_user_not_found(self, user_repository, mock_db):
        """最終ログイン時刻更新失敗テスト（ユーザー不存在）"""
        # モックの設定
        user_repository.get.return_value = None
        
        # 実行
        result = await user_repository.update_last_login(mock_db, 999)
        
        # 検証
        assert result is None
    
    @pytest.mark.asyncio
    async def test_update_last_login_database_error(self, user_repository, mock_db, sample_user):
        """最終ログイン時刻更新失敗テスト（データベースエラー）"""
        # モックの設定
        user_repository.get.return_value = sample_user
        mock_db.add.side_effect = Exception("Database error")
        mock_db.rollback.return_value = None
        
        # 実行と検証
        with pytest.raises(ValidationException) as exc_info:
            await user_repository.update_last_login(mock_db, 1)
        
        assert "最終ログイン時刻の更新に失敗しました" in str(exc_info.value)
        mock_db.rollback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, user_repository, mock_db, sample_user_create):
        """ユーザー作成成功テスト"""
        # モックの設定
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # 実行
        result = await user_repository.create(mock_db, sample_user_create)
        
        # 検証
        assert result is not None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_user_success(self, user_repository, mock_db, sample_user):
        """ユーザー取得成功テスト"""
        # モックの設定
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db.execute.return_value = mock_result
        
        # 実行
        result = await user_repository.get(mock_db, 1)
        
        # 検証
        assert result == sample_user
        mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_user_not_found(self, user_repository, mock_db):
        """ユーザー取得失敗テスト（ユーザー不存在）"""
        # モックの設定
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        # 実行
        result = await user_repository.get(mock_db, 999)
        
        # 検証
        assert result is None
