import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.subscription import Subscription
from app.services.subscription_service import SubscriptionService
from tests.test_utils.test_helpers import (
    create_mock_subscription,
    create_mock_subscription_data,
    assert_subscription_data
)


class TestSubscriptionModel:
    """サブスクリプションモデルのテスト"""
    
    def test_subscription_creation(self):
        """サブスクリプションの作成テスト"""
        subscription = Subscription(
            id=1,
            user_id=1,
            organization_id=1,
            stripe_subscription_id="sub_123456",
            stripe_price_id="price_123456",
            status="active",
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=30),
            quantity=5
        )
        
        assert subscription.id == 1
        assert subscription.user_id == 1
        assert subscription.organization_id == 1
        assert subscription.stripe_subscription_id == "sub_123456"
        assert subscription.stripe_price_id == "price_123456"
        assert subscription.status == "active"
        assert subscription.quantity == 5
    
    def test_subscription_default_values(self):
        """サブスクリプションのデフォルト値テスト"""
        subscription = Subscription(
            user_id=1,
            organization_id=1,
            stripe_subscription_id="sub_123456"
        )
        
        assert subscription.status == "trialing"
        assert subscription.quantity == 1
        assert subscription.created_at is not None
        assert subscription.updated_at is not None
    
    def test_subscription_status_properties(self):
        """サブスクリプションステータスのプロパティテスト"""
        # アクティブ
        active_subscription = Subscription(
            user_id=1,
            organization_id=1,
            stripe_subscription_id="sub_123456",
            status="active"
        )
        assert active_subscription.is_active is True
        assert active_subscription.is_trialing is False
        assert active_subscription.is_cancelled is False
        assert active_subscription.is_past_due is False
        
        # トライアル中
        trialing_subscription = Subscription(
            user_id=1,
            organization_id=1,
            stripe_subscription_id="sub_123456",
            status="trialing"
        )
        assert trialing_subscription.is_trialing is True
        
        # キャンセル済み
        cancelled_subscription = Subscription(
            user_id=1,
            organization_id=1,
            stripe_subscription_id="sub_123456",
            status="cancelled"
        )
        assert cancelled_subscription.is_cancelled is True
        
        # 支払い遅延
        past_due_subscription = Subscription(
            user_id=1,
            organization_id=1,
            stripe_subscription_id="sub_123456",
            status="past_due"
        )
        assert past_due_subscription.is_past_due is True
    
    def test_subscription_period_management(self):
        """サブスクリプション期間管理のテスト"""
        now = datetime.utcnow()
        subscription = Subscription(
            user_id=1,
            organization_id=1,
            stripe_subscription_id="sub_123456",
            current_period_start=now,
            current_period_end=now + timedelta(days=30)
        )
        
        assert subscription.is_current_period_active() is True
        assert subscription.days_remaining_in_period() > 0
        assert subscription.days_until_renewal() > 0
        
        # 期限切れ
        expired_subscription = Subscription(
            user_id=1,
            organization_id=1,
            stripe_subscription_id="sub_123456",
            current_period_start=now - timedelta(days=60),
            current_period_end=now - timedelta(days=30)
        )
        
        assert expired_subscription.is_current_period_active() is False
        assert expired_subscription.days_remaining_in_period() <= 0


class TestSubscriptionBusinessLogic:
    """サブスクリプションビジネスロジックのテスト"""
    
    def test_subscription_quantity_limits(self):
        """サブスクリプション数量制限のテスト"""
        subscription = Subscription(
            user_id=1,
            organization_id=1,
            stripe_subscription_id="sub_123456",
            quantity=5
        )
        
        assert subscription.can_add_member() is True
        assert subscription.can_remove_member() is True
        
        # 最小数量
        min_subscription = Subscription(
            user_id=1,
            organization_id=1,
            stripe_subscription_id="sub_123456",
            quantity=1
        )
        
        assert min_subscription.can_remove_member() is False
        
        # 最大数量
        max_subscription = Subscription(
            user_id=1,
            organization_id=1,
            stripe_subscription_id="sub_123456",
            quantity=100
        )
        
        assert max_subscription.can_add_member() is False
    
    def test_subscription_upgrade_downgrade(self):
        """サブスクリプションアップグレード・ダウングレードのテスト"""
        subscription = Subscription(
            user_id=1,
            organization_id=1,
            stripe_subscription_id="sub_123456",
            quantity=5
        )
        
        # アップグレード
        subscription.upgrade_quantity(10)
        assert subscription.quantity == 10
        assert subscription.status == "active"
        
        # ダウングレード
        subscription.downgrade_quantity(3)
        assert subscription.quantity == 3
        assert subscription.status == "active"
    
    def test_subscription_cancellation(self):
        """サブスクリプションキャンセルのテスト"""
        subscription = Subscription(
            user_id=1,
            organization_id=1,
            stripe_subscription_id="sub_123456",
            status="active"
        )
        
        # 即座キャンセル
        subscription.cancel_immediately()
        assert subscription.status == "cancelled"
        assert subscription.cancelled_at is not None
        
        # 期間終了時キャンセル
        subscription = Subscription(
            user_id=1,
            organization_id=1,
            stripe_subscription_id="sub_123456",
            status="active"
        )
        
        subscription.cancel_at_period_end()
        assert subscription.status == "active"
        assert subscription.cancel_at_period_end is True


class TestSubscriptionAPI:
    """サブスクリプションAPIのテスト"""
    
    async def test_get_subscription_info(self, client, mock_db_session):
        """サブスクリプション情報取得のテスト"""
        # モックサブスクリプションオブジェクトの作成
        mock_subscription = create_mock_subscription()
        
        # データベースセッションのモック
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_subscription
        
        # APIリクエストのテスト
        response = client.get("/api/v1/subscriptions/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["stripe_subscription_id"] == "sub_1"
        assert data["status"] == "active"
    
    async def test_create_subscription(self, client, mock_db_session):
        """サブスクリプション作成のテスト"""
        # サブスクリプション作成リクエストのテスト
        subscription_data = create_mock_subscription_data()
        
        response = client.post("/api/v1/subscriptions", json=subscription_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "stripe_subscription_id" in data
        assert data["status"] == subscription_data["status"]


class TestSubscriptionService:
    """サブスクリプションサービスのテスト"""
    
    @pytest.fixture
    def subscription_service(self):
        """サブスクリプションサービスインスタンス"""
        return SubscriptionService()
    
    @pytest.fixture
    def mock_db(self):
        """モックデータベースセッション"""
        return AsyncMock()
    
    async def test_create_subscription_success(self, subscription_service, mock_db):
        """サブスクリプション作成の成功テスト"""
        subscription_data = create_mock_subscription_data()
        mock_subscription = create_mock_subscription()
        
        with patch('app.services.subscription_service.subscription_repository.create_subscription') as mock_create:
            mock_create.return_value = mock_subscription
            
            result = await subscription_service.create_subscription(
                db=mock_db,
                user_id=1,
                organization_id=1,
                stripe_subscription_id="sub_test_123",
                stripe_price_id="price_test_123",
                quantity=5
            )
            
            # 検証
            assert result["subscription_id"] == 1
            assert result["stripe_subscription_id"] == "sub_test_123"
            assert result["status"] == "active"
            assert result["quantity"] == 5
            mock_create.assert_called_once()
    
    async def test_create_subscription_database_error(self, subscription_service, mock_db):
        """サブスクリプション作成のデータベースエラーテスト"""
        with patch('app.services.subscription_service.subscription_repository.create_subscription') as mock_create:
            mock_create.side_effect = Exception("Database error")
            
            with pytest.raises(Exception, match="Database error"):
                await subscription_service.create_subscription(
                    db=mock_db,
                    user_id=1,
                    organization_id=1,
                    stripe_subscription_id="sub_test_123"
                )
    
    async def test_get_user_subscriptions(self, subscription_service, mock_db):
        """ユーザーサブスクリプション一覧取得のテスト"""
        mock_subscriptions = [
            create_mock_subscription(1, 1, 1, "active"),
            create_mock_subscription(2, 1, 1, "trialing")
        ]
        
        with patch('app.services.subscription_service.subscription_repository.get_user_subscriptions') as mock_get:
            mock_get.return_value = mock_subscriptions
            
            result = await subscription_service.get_user_subscriptions(mock_db, 1)
            
            # 検証
            assert len(result["subscriptions"]) == 2
            assert result["total_count"] == 2
            mock_get.assert_called_once_with(mock_db, 1)
    
    async def test_get_subscription(self, subscription_service, mock_db):
        """サブスクリプション取得のテスト"""
        mock_subscription = create_mock_subscription()
        
        with patch('app.services.subscription_service.subscription_repository.get_subscription') as mock_get:
            mock_get.return_value = mock_subscription
            
            result = await subscription_service.get_subscription(mock_db, 1)
            
            # 検証
            assert result.id == 1
            assert result.status == "active"
            mock_get.assert_called_once_with(mock_db, 1)
    
    async def test_update_subscription_status_success(self, subscription_service, mock_db):
        """サブスクリプションステータス更新の成功テスト"""
        with patch('app.services.subscription_service.subscription_repository.update_subscription_status') as mock_update:
            mock_update.return_value = True
            
            result = await subscription_service.update_subscription_status(mock_db, 1, "cancelled")
            
            # 検証
            assert result is True
            mock_update.assert_called_once_with(mock_db, 1, "cancelled")
    
    async def test_update_subscription_status_failure(self, subscription_service, mock_db):
        """サブスクリプションステータス更新の失敗テスト"""
        with patch('app.services.subscription_service.subscription_repository.update_subscription_status') as mock_update:
            mock_update.return_value = False
            
            result = await subscription_service.update_subscription_status(mock_db, 1, "invalid_status")
            
            # 検証
            assert result is False
    
    async def test_cancel_subscription_success(self, subscription_service, mock_db):
        """サブスクリプションキャンセルの成功テスト"""
        with patch('app.services.subscription_service.subscription_repository.cancel_subscription') as mock_cancel:
            mock_cancel.return_value = True
            
            result = await subscription_service.cancel_subscription(mock_db, 1, cancel_at_period_end=True)
            
            # 検証
            assert result is True
            mock_cancel.assert_called_once()
            call_args = mock_cancel.call_args[0]
            assert call_args[0] == mock_db  # db
            assert call_args[1] == 1  # subscription_id
            assert call_args[2] is True  # cancel_at_period_end
    
    async def test_cancel_subscription_failure(self, subscription_service, mock_db):
        """サブスクリプションキャンセルの失敗テスト"""
        with patch('app.services.subscription_service.subscription_repository.cancel_subscription') as mock_cancel:
            mock_cancel.return_value = False
            
            result = await subscription_service.cancel_subscription(mock_db, 1)
            
            # 検証
            assert result is False
    
    async def test_update_subscription_quantity_success(self, subscription_service, mock_db):
        """サブスクリプション数量更新の成功テスト"""
        with patch('app.services.subscription_service.subscription_repository.update_subscription_quantity') as mock_update:
            mock_update.return_value = True
            
            result = await subscription_service.update_subscription_quantity(mock_db, 1, 10)
            
            # 検証
            assert result is True
            mock_update.assert_called_once_with(mock_db, 1, 10)
    
    async def test_get_subscription_usage(self, subscription_service, mock_db):
        """サブスクリプション使用量取得のテスト"""
        mock_usage = {
            "voice_minutes_used": 120,
            "voice_minutes_limit": 300,
            "analysis_count_used": 5,
            "analysis_count_limit": 10,
            "storage_used_mb": 50,
            "storage_limit_mb": 100
        }
        
        with patch('app.services.subscription_service.subscription_repository.get_subscription_usage') as mock_get:
            mock_get.return_value = mock_usage
            
            result = await subscription_service.get_subscription_usage(mock_db, 1)
            
            # 検証
            assert result["voice_minutes_used"] == 120
            assert result["voice_minutes_limit"] == 300
            assert result["analysis_count_used"] == 5
            assert result["analysis_count_limit"] == 10
            mock_get.assert_called_once_with(mock_db, 1)


class TestSubscriptionValidation:
    """サブスクリプションバリデーションのテスト"""
    
    def test_subscription_model_creation(self):
        """サブスクリプションモデル作成のテスト"""
        subscription = Subscription(
            user_id=1,
            organization_id=1,
            stripe_subscription_id="sub_123"
        )
        
        assert subscription.user_id == 1
        assert subscription.organization_id == 1
        assert subscription.stripe_subscription_id == "sub_123"
    
    def test_subscription_model_default_values(self):
        """サブスクリプションモデルデフォルト値のテスト"""
        subscription = Subscription(
            user_id=1,
            organization_id=1,
            stripe_subscription_id="sub_123"
        )
        
        assert subscription.status == "trialing"
        assert subscription.quantity == 1
        assert subscription.created_at is not None
        assert subscription.updated_at is not None
    
    def test_subscription_model_validation(self):
        """サブスクリプションモデルバリデーションのテスト"""
        # 有効なサブスクリプション
        valid_subscription = Subscription(
            user_id=1,
            organization_id=1,
            stripe_subscription_id="sub_123"
        )
        
        assert valid_subscription.is_valid() is True
        
        # 無効なサブスクリプション（数量が負）
        invalid_subscription = Subscription(
            user_id=1,
            organization_id=1,
            stripe_subscription_id="sub_123",
            quantity=-1
        )
        
        assert invalid_subscription.is_valid() is False
    
    def test_subscription_status_validation(self):
        """サブスクリプションステータスバリデーションのテスト"""
        valid_statuses = ["trialing", "active", "past_due", "cancelled", "unpaid"]
        
        for status in valid_statuses:
            subscription = Subscription(
                user_id=1,
                organization_id=1,
                stripe_subscription_id="sub_123",
                status=status
            )
            
            assert subscription.is_valid_status() is True
        
        # 無効なステータス
        invalid_subscription = Subscription(
            user_id=1,
            organization_id=1,
            stripe_subscription_id="sub_123",
            status="invalid_status"
        )
        
        assert invalid_subscription.is_valid_status() is False


class TestSubscriptionWebhooks:
    """サブスクリプションWebhookのテスト"""
    
    @pytest.fixture
    def subscription_service(self):
        """サブスクリプションサービスインスタンス"""
        return SubscriptionService()
    
    @pytest.fixture
    def mock_db(self):
        """モックデータベースセッション"""
        return AsyncMock()
    
    async def test_handle_subscription_created_webhook(self, subscription_service, mock_db):
        """サブスクリプション作成Webhookの処理テスト"""
        webhook_data = {
            "type": "customer.subscription.created",
            "data": {
                "object": {
                    "id": "sub_test_123",
                    "customer": "cus_test_123",
                    "status": "trialing",
                    "quantity": 5
                }
            }
        }
        
        with patch('app.services.subscription_service.subscription_repository.create_subscription') as mock_create:
            mock_subscription = create_mock_subscription()
            mock_create.return_value = mock_subscription
            
            result = await subscription_service.handle_webhook(mock_db, webhook_data)
            
            # 検証
            assert result["success"] is True
            assert result["action"] == "subscription_created"
            mock_create.assert_called_once()
    
    async def test_handle_subscription_updated_webhook(self, subscription_service, mock_db):
        """サブスクリプション更新Webhookの処理テスト"""
        webhook_data = {
            "type": "customer.subscription.updated",
            "data": {
                "object": {
                    "id": "sub_test_123",
                    "status": "active",
                    "quantity": 10
                }
            }
        }
        
        with patch('app.services.subscription_service.subscription_repository.update_subscription') as mock_update:
            mock_update.return_value = True
            
            result = await subscription_service.handle_webhook(mock_db, webhook_data)
            
            # 検証
            assert result["success"] is True
            assert result["action"] == "subscription_updated"
            mock_update.assert_called_once()
    
    async def test_handle_subscription_deleted_webhook(self, subscription_service, mock_db):
        """サブスクリプション削除Webhookの処理テスト"""
        webhook_data = {
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "id": "sub_test_123"
                }
            }
        }
        
        with patch('app.services.subscription_service.subscription_repository.delete_subscription') as mock_delete:
            mock_delete.return_value = True
            
            result = await subscription_service.handle_webhook(mock_db, webhook_data)
            
            # 検証
            assert result["success"] is True
            assert result["action"] == "subscription_deleted"
            mock_delete.assert_called_once()
    
    async def test_handle_unknown_webhook(self, subscription_service, mock_db):
        """不明なWebhookの処理テスト"""
        webhook_data = {
            "type": "unknown.event",
            "data": {}
        }
        
        result = await subscription_service.handle_webhook(mock_db, webhook_data)
        
        # 検証
        assert result["success"] is False
        assert result["error"] == "Unknown webhook type: unknown.event"


class TestSubscriptionAnalytics:
    """サブスクリプション分析のテスト"""
    
    @pytest.fixture
    def subscription_service(self):
        """サブスクリプションサービスインスタンス"""
        return SubscriptionService()
    
    @pytest.fixture
    def mock_db(self):
        """モックデータベースセッション"""
        return AsyncMock()
    
    async def test_get_subscription_metrics(self, subscription_service, mock_db):
        """サブスクリプション指標取得のテスト"""
        mock_metrics = {
            "total_subscriptions": 100,
            "active_subscriptions": 80,
            "trialing_subscriptions": 15,
            "cancelled_subscriptions": 5,
            "monthly_recurring_revenue": 250000,
            "churn_rate": 0.05
        }
        
        with patch('app.services.subscription_service.subscription_repository.get_subscription_metrics') as mock_get:
            mock_get.return_value = mock_metrics
            
            result = await subscription_service.get_subscription_metrics(mock_db)
            
            # 検証
            assert result["total_subscriptions"] == 100
            assert result["active_subscriptions"] == 80
            assert result["churn_rate"] == 0.05
            mock_get.assert_called_once_with(mock_db)
    
    async def test_get_subscription_trends(self, subscription_service, mock_db):
        """サブスクリプショントレンド取得のテスト"""
        mock_trends = [
            {"month": "2024-01", "new_subscriptions": 20, "cancellations": 5},
            {"month": "2024-02", "new_subscriptions": 25, "cancellations": 3},
            {"month": "2024-03", "new_subscriptions": 30, "cancellations": 7}
        ]
        
        with patch('app.services.subscription_service.subscription_repository.get_subscription_trends') as mock_get:
            mock_get.return_value = mock_trends
            
            result = await subscription_service.get_subscription_trends(mock_db, months=3)
            
            # 検証
            assert len(result) == 3
            assert result[0]["month"] == "2024-01"
            assert result[0]["new_subscriptions"] == 20
            mock_get.assert_called_once_with(mock_db, 3)
