import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from app.main import app
from app.models.user import User
from app.core.auth import create_access_token, create_refresh_token

client = TestClient(app)


class TestFirebaseAuthentication:
    """Firebase認証のテスト"""

    @patch('app.core.firebase_client.verify_firebase_token')
    @patch('app.services.auth_service.AuthService.get_user_by_firebase_uid')
    @patch('app.services.auth_service.AuthService.create_user_by_firebase')
    def test_firebase_login_success_new_user(self, mock_create_user, mock_get_user, mock_verify_token):
        """新規ユーザーのFirebaseログイン成功テスト"""
        # モック設定
        mock_verify_token.return_value = {
            "uid": "test_firebase_uid",
            "email": "test@example.com"
        }
        mock_get_user.return_value = None
        
        mock_user = MagicMock()
        mock_user.email = "test@example.com"
        mock_user.id = 1
        mock_create_user.return_value = mock_user

        # テスト実行
        response = client.post("/api/v1/auth/login", json={
            "id_token": "valid_firebase_token",
            "display_name": "Test User",
            "avatar_url": "https://example.com/avatar.jpg"
        })

        # 検証
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data

    @patch('app.core.firebase_client.verify_firebase_token')
    @patch('app.services.auth_service.AuthService.get_user_by_firebase_uid')
    def test_firebase_login_success_existing_user(self, mock_get_user, mock_verify_token):
        """既存ユーザーのFirebaseログイン成功テスト"""
        # モック設定
        mock_verify_token.return_value = {
            "uid": "test_firebase_uid",
            "email": "test@example.com"
        }
        
        mock_user = MagicMock()
        mock_user.email = "test@example.com"
        mock_user.id = 1
        mock_get_user.return_value = mock_user

        # テスト実行
        response = client.post("/api/v1/auth/login", json={
            "id_token": "valid_firebase_token",
            "display_name": "Test User"
        })

        # 検証
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @patch('app.core.firebase_client.verify_firebase_token')
    def test_firebase_login_invalid_token(self, mock_verify_token):
        """無効なFirebaseトークンでのログイン失敗テスト"""
        # モック設定
        mock_verify_token.return_value = None

        # テスト実行
        response = client.post("/api/v1/auth/login", json={
            "id_token": "invalid_firebase_token",
            "display_name": "Test User"
        })

        # 検証
        assert response.status_code == 401
        assert "Invalid Firebase token" in response.json()["detail"]


class TestTokenRefresh:
    """トークンリフレッシュのテスト"""

    @patch('app.core.auth.verify_refresh_token')
    @patch('app.services.auth_service.AuthService.get_user_by_email')
    def test_refresh_token_success(self, mock_get_user, mock_verify_refresh):
        """リフレッシュトークン成功テスト"""
        # モック設定
        mock_verify_refresh.return_value = {
            "sub": "test@example.com",
            "type": "refresh"
        }
        
        mock_user = MagicMock()
        mock_user.email = "test@example.com"
        mock_get_user.return_value = mock_user

        # テスト実行
        response = client.post("/api/v1/auth/refresh", json={
            "refresh_token": "valid_refresh_token"
        })

        # 検証
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @patch('app.core.auth.verify_refresh_token')
    def test_refresh_token_invalid(self, mock_verify_refresh):
        """無効なリフレッシュトークンテスト"""
        # モック設定
        mock_verify_refresh.return_value = None

        # テスト実行
        response = client.post("/api/v1/auth/refresh", json={
            "refresh_token": "invalid_refresh_token"
        })

        # 検証
        assert response.status_code == 401
        assert "Invalid refresh token" in response.json()["detail"]


class TestUserAuthentication:
    """ユーザー認証のテスト"""

    @patch('app.api.deps.get_current_user')
    def test_get_current_user_info_success(self, mock_get_current_user):
        """現在のユーザー情報取得成功テスト"""
        # モック設定
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.firebase_uid = "test_firebase_uid"
        mock_user.full_name = "Test User"
        mock_user.username = "testuser"
        mock_user.avatar_url = "https://example.com/avatar.jpg"
        mock_user.is_active = True
        mock_user.last_login_at = datetime.utcnow()
        mock_user.created_at = datetime.utcnow()
        mock_user.profile = None
        mock_user.teams = []
        
        mock_get_current_user.return_value = mock_user

        # テスト実行
        response = client.get("/api/v1/users/me", headers={
            "Authorization": "Bearer valid_access_token"
        })

        # 検証
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["firebase_uid"] == "test_firebase_uid"
        assert data["display_name"] == "Test User"


class TestAdminAuthorization:
    """管理者認可のテスト"""

    @patch('app.api.deps.get_current_admin_user')
    def test_admin_only_endpoint_success(self, mock_get_current_admin):
        """管理者専用エンドポイント成功テスト"""
        # モック設定
        mock_admin = MagicMock()
        mock_admin.is_admin = True
        mock_get_current_admin.return_value = mock_admin

        # テスト実行
        response = client.get("/api/v1/admin-only", headers={
            "Authorization": "Bearer valid_admin_token"
        })

        # 検証
        assert response.status_code == 200

    @patch('app.api.deps.get_current_user')
    def test_admin_only_endpoint_forbidden(self, mock_get_current_user):
        """一般ユーザーの管理者エンドポイントアクセス拒否テスト"""
        # モック設定
        mock_user = MagicMock()
        mock_user.is_admin = False
        mock_get_current_user.return_value = mock_user

        # テスト実行
        response = client.get("/api/v1/admin-only", headers={
            "Authorization": "Bearer valid_user_token"
        })

        # 検証
        assert response.status_code == 403
        assert "管理者権限が必要です" in response.json()["detail"]


class TestLogout:
    """ログアウトのテスト"""

    @patch('app.api.deps.get_current_user')
    @patch('app.services.auth_service.AuthService.update_user_logout_time')
    def test_logout_success(self, mock_update_logout, mock_get_current_user):
        """ログアウト成功テスト"""
        # モック設定
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_get_current_user.return_value = mock_user
        mock_update_logout.return_value = True

        # テスト実行
        response = client.post("/api/v1/auth/logout", headers={
            "Authorization": "Bearer valid_access_token"
        })

        # 検証
        assert response.status_code == 200
        assert "Successfully logged out" in response.json()["message"]


if __name__ == "__main__":
    pytest.main([__file__])
