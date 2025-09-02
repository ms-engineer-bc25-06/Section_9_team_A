import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient
from app.models.user import User
from app.core.auth import create_access_token
from app.core.websocket import WebSocketAuth
from app.config import settings


class TestUserAuthentication:
    """ユーザー認証のテスト"""
    
    def test_user_authentication_status(self):
        """ユーザー認証状態のテスト"""
        # アクティブユーザー
        active_user = User(
            id=1,
            email="active@example.com",
            username="activeuser",
            is_active=True,
            is_verified=True
        )
        assert active_user.is_active is True
        assert active_user.is_verified is True
        
        # 非アクティブユーザー
        inactive_user = User(
            id=2,
            email="inactive@example.com",
            username="inactiveuser",
            is_active=False,
            is_verified=False
        )
        assert inactive_user.is_active is False
        assert inactive_user.is_verified is False
    
    def test_user_premium_status(self):
        """ユーザープレミアム状態のテスト"""
        # プレミアムユーザー
        premium_user = User(
            id=1,
            email="premium@example.com",
            username="premiumuser",
            is_premium=True,
            subscription_status="premium"
        )
        assert premium_user.is_premium is True
        assert premium_user.subscription_status == "premium"
        
        # 無料ユーザー
        free_user = User(
            id=2,
            email="free@example.com",
            username="freeuser",
            is_premium=False,
            subscription_status="free"
        )
        assert free_user.is_premium is False
        assert free_user.subscription_status == "free"
    
    def test_user_admin_status(self):
        """ユーザー管理者状態のテスト"""
        # 管理者ユーザー
        admin_user = User(
            id=1,
            email="admin@example.com",
            username="adminuser",
            is_admin=True
        )
        assert admin_user.is_admin is True
        
        # 一般ユーザー
        regular_user = User(
            id=2,
            email="regular@example.com",
            username="regularuser",
            is_admin=False
        )
        assert regular_user.is_admin is False


class TestUserFirebaseAuth:
    """Firebase認証のテスト"""
    
    def test_firebase_uid_assignment(self):
        """Firebase UIDの割り当てテスト"""
        firebase_uid = "firebase_uid_123456"
        user = User(
            id=1,
            email="firebase@example.com",
            username="firebaseuser",
            firebase_uid=firebase_uid
        )
        
        assert user.firebase_uid == firebase_uid
        assert user.hashed_password is None  # Firebase認証の場合はパスワード不要
    
    def test_user_without_firebase(self):
        """Firebase認証なしユーザーのテスト"""
        user = User(
            id=1,
            email="local@example.com",
            username="localuser",
            hashed_password="hashed_password_123"
        )
        
        assert user.firebase_uid is None
        assert user.hashed_password is not None


class TestUserPasswordManagement:
    """ユーザーパスワード管理のテスト"""
    
    def test_temporary_password_management(self):
        """仮パスワード管理のテスト"""
        from datetime import datetime, timedelta
        
        user = User(
            id=1,
            email="temp@example.com",
            username="tempuser",
            has_temporary_password=True,
            temporary_password_expires_at=datetime.utcnow() + timedelta(days=7)
        )
        
        assert user.has_temporary_password is True
        assert user.temporary_password_expires_at > datetime.utcnow()
    
    def test_first_login_flag(self):
        """初回ログインフラグのテスト"""
        user = User(
            id=1,
            email="first@example.com",
            username="firstuser",
            is_first_login=True
        )
        
        assert user.is_first_login is True


class TestUserUsageLimits:
    """ユーザー使用制限のテスト"""
    
    def test_monthly_voice_minutes(self):
        """月間音声利用時間のテスト"""
        user = User(
            id=1,
            email="voice@example.com",
            username="voiceuser",
            monthly_voice_minutes=120
        )
        
        assert user.monthly_voice_minutes == 120
        assert user.remaining_voice_minutes() == 120
    
    def test_monthly_analysis_count(self):
        """月間分析回数のテスト"""
        user = User(
            id=1,
            email="analysis@example.com",
            username="analysisuser",
            monthly_analysis_count=5
        )
        
        assert user.monthly_analysis_count == 5
        assert user.remaining_analysis_count() == 5


class TestAuthAPI:
    """認証APIのテスト"""
    
    async def test_user_login(self, client, mock_db_session):
        """ユーザーログインのテスト"""
        # モックユーザーの作成
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.username = "testuser"
        mock_user.is_active = True
        mock_user.is_verified = True
        
        # データベースセッションのモック
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_user
        
        # ログインリクエストのテスト
        response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        
        assert response.status_code == 200
    
    async def test_user_logout(self, client, mock_db_session):
        """ユーザーログアウトのテスト"""
        # ログアウトリクエストのテスト
        response = client.post("/api/v1/auth/logout")
        
        assert response.status_code == 200


class TestFirebaseAuth:
    """Firebase認証のテスト"""
    
    def test_firebase_login_success(self, auth_client, test_user):
        """Firebase認証ログイン成功テスト"""
        with patch('app.api.v1.auth.verify_firebase_token') as mock_verify, \
             patch('app.api.v1.auth.AuthService') as mock_auth_service:
            
            # モック設定
            mock_verify.return_value = {
                "uid": "test_firebase_uid",
                "email": "test@example.com"
            }
            
            mock_service_instance = MagicMock()
            mock_service_instance.get_firebase_user_only.return_value = test_user
            mock_auth_service.return_value = mock_service_instance

            # リクエスト実行
            response = auth_client.post("/api/v1/auth/firebase-login", json={
                "id_token": "valid_firebase_token",
                "display_name": "Test User"
            })

            # アサーション
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
            assert data["user"]["email"] == "test@example.com"

    def test_firebase_login_invalid_token(self, auth_client):
        """Firebase認証ログイン失敗テスト（無効なトークン）"""
        with patch('app.api.v1.auth.verify_firebase_token') as mock_verify:
            mock_verify.return_value = None

            response = auth_client.post("/api/v1/auth/firebase-login", json={
                "id_token": "invalid_token",
                "display_name": "Test User"
            })

            assert response.status_code == 401

    def test_temporary_login_success(self, auth_client, test_user):
        """仮パスワードログイン成功テスト"""
        with patch('app.api.v1.auth.AuthService') as mock_auth_service:
            mock_service_instance = MagicMock()
            mock_service_instance.authenticate_user.return_value = test_user
            mock_auth_service.return_value = mock_service_instance

            response = auth_client.post("/api/v1/auth/temporary-login", json={
                "email": "test@example.com",
                "temporary_password": "temporary_password"
            })

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["user"]["email"] == "test@example.com"

    def test_temporary_login_expired(self, auth_client):
        """仮パスワードログイン失敗テスト（期限切れ）"""
        with patch('app.api.v1.auth.AuthService') as mock_auth_service:
            mock_service_instance = MagicMock()
            mock_service_instance.authenticate_user.return_value = None
            mock_auth_service.return_value = mock_service_instance

            response = auth_client.post("/api/v1/auth/temporary-login", json={
                "email": "test@example.com",
                "temporary_password": "expired_password"
            })

            assert response.status_code == 401


class TestJWTTokenAuth:
    """JWTトークン認証のテスト"""
    
    def test_get_current_user_success(self, auth_client, test_user, user_jwt_token):
        """現在のユーザー取得成功テスト"""
        response = auth_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {user_jwt_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"

    def test_get_current_user_unauthorized(self, auth_client):
        """現在のユーザー取得失敗テスト（未認証）"""
        response = auth_client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_refresh_token_success(self, auth_client, test_user, user_jwt_token):
        """トークン更新成功テスト"""
        response = auth_client.post(
            "/api/v1/auth/refresh",
            headers={"Authorization": f"Bearer {user_jwt_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_login_status_success(self, auth_client, test_user, user_jwt_token):
        """ログイン状態確認成功テスト"""
        response = auth_client.get(
            "/api/v1/auth/status",
            headers={"Authorization": f"Bearer {user_jwt_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_authenticated"] is True
        assert data["user"]["email"] == "test@example.com"


class TestPasswordManagement:
    """パスワード管理のテスト"""
    
    def test_change_password_success(self, auth_client, test_user, user_jwt_token):
        """パスワード変更成功テスト"""
        response = auth_client.post(
            "/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {user_jwt_token}"},
            json={
                "current_password": "old_password",
                "new_password": "new_password123"
            }
        )
        
        assert response.status_code == 200

    def test_logout_success(self, auth_client):
        """ログアウト成功テスト"""
        response = auth_client.post("/api/v1/auth/logout")
        assert response.status_code == 200


class TestAdminAuth:
    """管理者認証のテスト"""
    
    def test_check_admin_success(self, auth_client, test_admin_user, admin_jwt_token):
        """管理者権限確認成功テスト"""
        response = auth_client.get(
            "/api/v1/auth/admin/check",
            headers={"Authorization": f"Bearer {admin_jwt_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_admin"] is True

    def test_check_admin_forbidden(self, auth_client, user_jwt_token):
        """管理者権限確認失敗テスト（権限不足）"""
        response = auth_client.get(
            "/api/v1/auth/admin/check",
            headers={"Authorization": f"Bearer {user_jwt_token}"}
        )
        
        assert response.status_code == 403

    def test_create_admin_dev_environment(self, auth_client):
        """開発環境での管理者作成テスト"""
        response = auth_client.post("/api/v1/auth/admin/create-dev")
        
        # 開発環境でのみ成功する
        if settings.ENVIRONMENT == "development":
            assert response.status_code == 200
        else:
            assert response.status_code == 404


class TestWebSocketAuth:
    """WebSocket認証のテスト"""
    
    async def test_websocket_auth_success(self, test_user):
        """WebSocket認証成功テスト"""
        with patch('app.core.websocket.AsyncSessionLocal') as mock_session:
            mock_db = AsyncMock()
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = test_user
            
            mock_db.execute.return_value = mock_result
            mock_session.return_value.__aenter__.return_value = mock_db
            
            mock_websocket = MagicMock()
            mock_websocket.query_params = {"token": "valid_firebase_token"}
            mock_websocket.client_state.value = "CONNECTED"
            
            user = await WebSocketAuth.authenticate_websocket(mock_websocket)
            
            assert user is not None
            assert user.email == "test@example.com"

    async def test_websocket_auth_no_token(self):
        """WebSocket認証失敗テスト（トークンなし）"""
        mock_websocket = MagicMock()
        mock_websocket.query_params = {}
        mock_websocket.client_state.value = "CONNECTED"
        
        with pytest.raises(Exception):
            await WebSocketAuth.authenticate_websocket(mock_websocket)

    async def test_websocket_auth_invalid_token(self):
        """WebSocket認証失敗テスト（無効なトークン）"""
        mock_websocket = MagicMock()
        mock_websocket.query_params = {"token": "invalid_token"}
        mock_websocket.client_state.value = "CONNECTED"
        
        with pytest.raises(Exception):
            await WebSocketAuth.authenticate_websocket(mock_websocket)


class TestAuthService:
    """認証サービスのテスト"""
    
    @pytest.fixture
    def mock_db(self):
        """モックデータベースセッション"""
        return AsyncMock()
    
    @pytest.fixture
    def auth_service(self, mock_db):
        """認証サービスインスタンス"""
        from app.services.auth_service import AuthService
        return AuthService(mock_db)
    
    async def test_authenticate_user_success(self, auth_service, mock_db):
        """ユーザー認証成功テスト"""
        from app.models.user import User
        
        # モックユーザーの作成
        mock_user = User(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            firebase_uid="test_firebase_uid",
            is_active=True,
            is_admin=False,
            has_temporary_password=False,
            is_first_login=False
        )
        
        # データベースのモック
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result
        
        result = await auth_service.authenticate_user("test@example.com", "password")
        
        assert result is not None
        assert result.email == "test@example.com"
        mock_db.commit.assert_called_once()

    async def test_authenticate_user_invalid_password(self, auth_service, mock_db):
        """ユーザー認証失敗テスト（無効なパスワード）"""
        # データベースのモック
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        result = await auth_service.authenticate_user("test@example.com", "wrong_password")
        
        assert result is None

    async def test_authenticate_user_not_found(self, auth_service, mock_db):
        """ユーザー認証失敗テスト（ユーザーが見つからない）"""
        # データベースのモック
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        result = await auth_service.authenticate_user("nonexistent@example.com", "password")
        
        assert result is None
