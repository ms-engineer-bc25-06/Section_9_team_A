"""
決済システム統合テスト

テスト対象:
- 決済フロー全体の統合テスト
- Stripe Webhook統合テスト
- エラーハンドリング統合テスト
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.payment import Payment
from app.services.payment_service import PaymentService
from tests.test_utils.test_helpers import (
    create_mock_payment,
    create_mock_checkout_event,
    create_mock_payment_succeeded_event,
    create_mock_payment_failed_event
)


class TestPaymentModel:
    """決済モデルのテスト"""
    
    def test_payment_creation(self):
        """決済の作成テスト"""
        payment = Payment(
            id=1,
            organization_id=1,
            amount=2980,
            currency="jpy",
            status="pending",
            stripe_payment_intent_id="pi_test_123",
            payment_method="card",
            description="Premium Plan - Monthly Subscription"
        )
        
        assert payment.id == 1
        assert payment.organization_id == 1
        assert payment.amount == 2980
        assert payment.currency == "jpy"
        assert payment.status == "pending"
        assert payment.stripe_payment_intent_id == "pi_test_123"
        assert payment.payment_method == "card"
        assert payment.description == "Premium Plan - Monthly Subscription"
    
    def test_payment_default_values(self):
        """決済のデフォルト値テスト"""
        payment = Payment(
            organization_id=1,
            amount=2980
        )
        
        assert payment.currency == "jpy"
        assert payment.status == "pending"
        assert payment.payment_method is None
        assert payment.created_at is not None
    
    def test_payment_status_properties(self):
        """決済ステータスのプロパティテスト"""
        # 支払い待ち
        pending_payment = Payment(
            organization_id=1,
            amount=2980,
            status="pending"
        )
        assert pending_payment.is_pending is True
        assert pending_payment.is_succeeded is False
        assert pending_payment.is_failed is False
        assert pending_payment.is_cancelled is False
        
        # 成功
        succeeded_payment = Payment(
            organization_id=1,
            amount=2980,
            status="succeeded",
            succeeded_at=datetime.utcnow()
        )
        assert succeeded_payment.is_succeeded is True
        
        # 失敗
        failed_payment = Payment(
            organization_id=1,
            amount=2980,
            status="failed",
            failed_at=datetime.utcnow()
        )
        assert failed_payment.is_failed is True
        
        # キャンセル
        cancelled_payment = Payment(
            organization_id=1,
            amount=2980,
            status="cancelled",
            cancelled_at=datetime.utcnow()
        )
        assert cancelled_payment.is_cancelled is True


class TestPaymentBusinessLogic:
    """決済ビジネスロジックのテスト"""
    
    def test_payment_amount_validation(self):
        """決済金額のバリデーションテスト"""
        # 有効な金額
        valid_payment = Payment(
            organization_id=1,
            amount=2980
        )
        assert valid_payment.is_valid_amount() is True
        
        # 無効な金額（負の値）
        invalid_payment = Payment(
            organization_id=1,
            amount=-1000
        )
        assert invalid_payment.is_valid_amount() is False
        
        # 無効な金額（0）
        zero_payment = Payment(
            organization_id=1,
            amount=0
        )
        assert zero_payment.is_valid_amount() is False
    
    def test_payment_currency_validation(self):
        """決済通貨のバリデーションテスト"""
        valid_currencies = ["jpy", "usd", "eur"]
        
        for currency in valid_currencies:
            payment = Payment(
                organization_id=1,
                amount=1000,
                currency=currency
            )
            assert payment.is_valid_currency() is True
        
        # 無効な通貨
        invalid_payment = Payment(
            organization_id=1,
            amount=1000,
            currency="invalid"
        )
        assert invalid_payment.is_valid_currency() is False
    
    def test_payment_status_transitions(self):
        """決済ステータスの遷移テスト"""
        payment = Payment(
            organization_id=1,
            amount=2980,
            status="pending"
        )
        
        # 成功への遷移
        payment.mark_as_succeeded()
        assert payment.status == "succeeded"
        assert payment.succeeded_at is not None
        
        # 失敗への遷移
        payment = Payment(
            organization_id=1,
            amount=2980,
            status="pending"
        )
        payment.mark_as_failed("Insufficient funds")
        assert payment.status == "failed"
        assert payment.failed_at is not None
        assert payment.failure_reason == "Insufficient funds"
        
        # キャンセルへの遷移
        payment = Payment(
            organization_id=1,
            amount=2980,
            status="pending"
        )
        payment.mark_as_cancelled("User cancelled")
        assert payment.status == "cancelled"
        assert payment.cancelled_at is not None
        assert payment.cancellation_reason == "User cancelled"


class TestPaymentAPI:
    """決済APIのテスト"""
    
    async def test_get_payment_info(self, client, mock_db_session):
        """決済情報取得のテスト"""
        # モック決済オブジェクトの作成
        mock_payment = create_mock_payment()
        
        # データベースセッションのモック
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_payment
        
        # APIリクエストのテスト
        response = client.get("/api/v1/payments/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["stripe_payment_intent_id"] == "pi_test_1"
        assert data["amount"] == 2980
    
    async def test_create_payment(self, client, mock_db_session):
        """決済作成のテスト"""
        # 決済作成リクエストのテスト
        payment_data = {
            "organization_id": 1,
            "amount": 2980,
            "currency": "jpy",
            "description": "Premium Plan - Monthly Subscription"
        }
        
        response = client.post("/api/v1/payments", json=payment_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "stripe_payment_intent_id" in data
        assert data["amount"] == payment_data["amount"]


class TestPaymentService:
    """決済サービスのテスト"""

    @pytest.fixture
    def payment_service(self):
        """決済サービスインスタンス"""
        return PaymentService()

    @pytest.fixture
    def mock_db(self):
        """モックデータベースセッション"""
        return AsyncMock()

    async def test_create_payment_intent_success(self, payment_service, mock_db):
        """決済インテント作成の成功テスト"""
        payment_data = {
            "organization_id": 1,
            "amount": 2980,
            "currency": "jpy",
            "description": "Premium Plan - Monthly Subscription"
        }
        
        mock_payment_intent = {
            "id": "pi_test_123",
            "client_secret": "pi_test_secret_123",
            "status": "requires_payment_method"
        }
        
        with patch('app.services.payment_service.stripe.PaymentIntent.create') as mock_stripe_create:
            mock_stripe_create.return_value = mock_payment_intent
            
            with patch('app.services.payment_service.payment_repository.create_payment') as mock_create:
                mock_payment = create_mock_payment()
                mock_create.return_value = mock_payment
                
                result = await payment_service.create_payment_intent(
                    db=mock_db,
                    organization_id=1,
                    amount=2980,
                    currency="jpy",
                    description="Premium Plan - Monthly Subscription"
                )
                
                # 検証
                assert result["payment_intent_id"] == "pi_test_123"
                assert result["client_secret"] == "pi_test_secret_123"
                assert result["status"] == "requires_payment_method"
                mock_stripe_create.assert_called_once()
                mock_create.assert_called_once()
    
    async def test_create_payment_intent_stripe_error(self, payment_service, mock_db):
        """決済インテント作成のStripeエラーテスト"""
        with patch('app.services.payment_service.stripe.PaymentIntent.create') as mock_stripe_create:
            mock_stripe_create.side_effect = Exception("Stripe error")
            
            with pytest.raises(Exception, match="Stripe error"):
                await payment_service.create_payment_intent(
                    db=mock_db,
                    organization_id=1,
                    amount=2980
                )
    
    async def test_confirm_payment_success(self, payment_service, mock_db):
        """決済確認の成功テスト"""
        mock_payment_intent = {
            "id": "pi_test_123",
            "status": "succeeded",
            "amount": 2980
        }
        
        with patch('app.services.payment_service.stripe.PaymentIntent.confirm') as mock_stripe_confirm:
            mock_stripe_confirm.return_value = mock_payment_intent
            
            with patch('app.services.payment_service.payment_repository.update_payment_status') as mock_update:
                mock_update.return_value = True
                
                result = await payment_service.confirm_payment(
                    db=mock_db,
                    payment_intent_id="pi_test_123"
                )
                
                # 検証
                assert result["success"] is True
                assert result["status"] == "succeeded"
                mock_stripe_confirm.assert_called_once_with("pi_test_123")
                mock_update.assert_called_once()
    
    async def test_confirm_payment_failure(self, payment_service, mock_db):
        """決済確認の失敗テスト"""
        mock_payment_intent = {
            "id": "pi_test_123",
            "status": "requires_payment_method",
            "last_payment_error": {
                "message": "Your card was declined."
            }
        }
        
        with patch('app.services.payment_service.stripe.PaymentIntent.confirm') as mock_stripe_confirm:
            mock_stripe_confirm.return_value = mock_payment_intent
            
            result = await payment_service.confirm_payment(
                db=mock_db,
                payment_intent_id="pi_test_123"
            )
                
            # 検証
            assert result["success"] is False
            assert result["status"] == "requires_payment_method"
            assert "Your card was declined" in result["error"]
    
    async def test_cancel_payment_success(self, payment_service, mock_db):
        """決済キャンセルの成功テスト"""
        mock_payment_intent = {
            "id": "pi_test_123",
            "status": "cancelled"
        }
        
        with patch('app.services.payment_service.stripe.PaymentIntent.cancel') as mock_stripe_cancel:
            mock_stripe_cancel.return_value = mock_payment_intent
            
            with patch('app.services.payment_service.payment_repository.update_payment_status') as mock_update:
                mock_update.return_value = True
                
                result = await payment_service.cancel_payment(
                    db=mock_db,
                    payment_intent_id="pi_test_123"
                )
                
                # 検証
                assert result["success"] is True
                assert result["status"] == "cancelled"
                mock_stripe_cancel.assert_called_once_with("pi_test_123")
                mock_update.assert_called_once()
    
    async def test_refund_payment_success(self, payment_service, mock_db):
        """決済返金の成功テスト"""
        mock_refund = {
            "id": "re_test_123",
            "status": "succeeded",
            "amount": 2980
        }
        
        with patch('app.services.payment_service.stripe.Refund.create') as mock_stripe_refund:
            mock_stripe_refund.return_value = mock_refund
            
            with patch('app.services.payment_service.payment_repository.create_refund') as mock_create_refund:
                mock_create_refund.return_value = True
                
                result = await payment_service.refund_payment(
                    db=mock_db,
                    payment_intent_id="pi_test_123",
                    amount=2980,
                    reason="Customer request"
                )
                
                # 検証
                assert result["success"] is True
                assert result["refund_id"] == "re_test_123"
                assert result["status"] == "succeeded"
                mock_stripe_refund.assert_called_once()
                mock_create_refund.assert_called_once()


class TestStripeWebhookHandling:
    """Stripe Webhook処理のテスト"""
    
    @pytest.fixture
    def payment_service(self):
        """決済サービスインスタンス"""
        return PaymentService()
    
    @pytest.fixture
    def mock_db(self):
        """モックデータベースセッション"""
        return AsyncMock()
    
    async def test_handle_checkout_session_completed(self, payment_service, mock_db):
        """チェックアウトセッション完了Webhookの処理テスト"""
        webhook_data = create_mock_checkout_event()
        
        with patch('app.services.payment_service.payment_repository.create_payment') as mock_create:
            mock_payment = create_mock_payment()
            mock_create.return_value = mock_payment
            
            result = await payment_service.handle_webhook(mock_db, webhook_data)
            
            # 検証
            assert result["success"] is True
            assert result["action"] == "checkout_session_completed"
            mock_create.assert_called_once()
    
    async def test_handle_payment_intent_succeeded(self, payment_service, mock_db):
        """決済インテント成功Webhookの処理テスト"""
        webhook_data = create_mock_payment_succeeded_event()
        
        with patch('app.services.payment_service.payment_repository.update_payment_status') as mock_update:
            mock_update.return_value = True
            
            result = await payment_service.handle_webhook(mock_db, webhook_data)
            
            # 検証
            assert result["success"] is True
            assert result["action"] == "payment_intent_succeeded"
            mock_update.assert_called_once()
    
    async def test_handle_payment_intent_failed(self, payment_service, mock_db):
        """決済インテント失敗Webhookの処理テスト"""
        webhook_data = create_mock_payment_failed_event()
        
        with patch('app.services.payment_service.payment_repository.update_payment_status') as mock_update:
            mock_update.return_value = True
            
            result = await payment_service.handle_webhook(mock_db, webhook_data)
            
            # 検証
            assert result["success"] is True
            assert result["action"] == "payment_intent_failed"
            mock_update.assert_called_once()
    
    async def test_handle_unknown_webhook(self, payment_service, mock_db):
        """不明なWebhookの処理テスト"""
        webhook_data = {
            "type": "unknown.event",
            "data": {}
        }
        
        result = await payment_service.handle_webhook(mock_db, webhook_data)
        
        # 検証
        assert result["success"] is False
        assert result["error"] == "Unknown webhook type: unknown.event"


class TestPaymentValidation:
    """決済バリデーションのテスト"""
    
    def test_payment_model_creation(self):
        """決済モデル作成のテスト"""
        payment = Payment(
            organization_id=1,
            amount=2980
        )
        
        assert payment.organization_id == 1
        assert payment.amount == 2980
        assert payment.currency == "jpy"
        assert payment.status == "pending"
    
    def test_payment_model_default_values(self):
        """決済モデルデフォルト値のテスト"""
        payment = Payment(
            organization_id=1,
            amount=2980
        )
        
        assert payment.currency == "jpy"
        assert payment.status == "pending"
        assert payment.payment_method is None
        assert payment.created_at is not None
    
    def test_payment_model_validation(self):
        """決済モデルバリデーションのテスト"""
        # 有効な決済
        valid_payment = Payment(
            organization_id=1,
            amount=2980
        )
        
        assert valid_payment.is_valid() is True
        
        # 無効な決済（金額が負）
        invalid_payment = Payment(
            organization_id=1,
            amount=-1000
        )
        
        assert invalid_payment.is_valid() is False
        
        # 無効な決済（組織IDが負）
        invalid_org_payment = Payment(
            organization_id=-1,
            amount=2980
        )
        
        assert invalid_org_payment.is_valid() is False
    
    def test_payment_method_validation(self):
        """決済方法バリデーションのテスト"""
        valid_methods = ["card", "bank_transfer", "paypal", "apple_pay", "google_pay"]
        
        for method in valid_methods:
            payment = Payment(
                organization_id=1,
                amount=2980,
                payment_method=method
            )
            
            assert payment.is_valid_payment_method() is True
        
        # 無効な決済方法
        invalid_payment = Payment(
            organization_id=1,
            amount=2980,
            payment_method="invalid_method"
        )
        
        assert invalid_payment.is_valid_payment_method() is False


class TestPaymentAnalytics:
    """決済分析のテスト"""
    
    @pytest.fixture
    def payment_service(self):
        """決済サービスインスタンス"""
        return PaymentService()
    
    @pytest.fixture
    def mock_db(self):
        """モックデータベースセッション"""
        return AsyncMock()
    
    async def test_get_payment_metrics(self, payment_service, mock_db):
        """決済指標取得のテスト"""
        mock_metrics = {
            "total_payments": 1000,
            "successful_payments": 950,
            "failed_payments": 50,
            "total_revenue": 2500000,
            "average_payment_amount": 2500,
            "success_rate": 0.95
        }
        
        with patch('app.services.payment_service.payment_repository.get_payment_metrics') as mock_get:
            mock_get.return_value = mock_metrics
            
            result = await payment_service.get_payment_metrics(mock_db)
            
            # 検証
            assert result["total_payments"] == 1000
            assert result["successful_payments"] == 950
            assert result["success_rate"] == 0.95
            mock_get.assert_called_once_with(mock_db)
    
    async def test_get_payment_trends(self, payment_service, mock_db):
        """決済トレンド取得のテスト"""
        mock_trends = [
            {"month": "2024-01", "payments": 80, "revenue": 200000},
            {"month": "2024-02", "payments": 90, "revenue": 225000},
            {"month": "2024-03", "payments": 100, "revenue": 250000}
        ]
        
        with patch('app.services.payment_service.payment_repository.get_payment_trends') as mock_get:
            mock_get.return_value = mock_trends
            
            result = await payment_service.get_payment_trends(mock_db, months=3)
            
            # 検証
            assert len(result) == 3
            assert result[0]["month"] == "2024-01"
            assert result[0]["payments"] == 80
            mock_get.assert_called_once_with(mock_db, 3)
    
    async def test_get_organization_payment_history(self, payment_service, mock_db):
        """組織決済履歴取得のテスト"""
        mock_payments = [
            create_mock_payment(1, 1, 2980, "succeeded"),
            create_mock_payment(2, 1, 2980, "succeeded"),
            create_mock_payment(3, 1, 2980, "pending")
        ]
        
        with patch('app.services.payment_service.payment_repository.get_organization_payments') as mock_get:
            mock_get.return_value = mock_payments
            
            result = await payment_service.get_organization_payment_history(mock_db, 1, limit=100)
            
            # 検証
            assert len(result["payments"]) == 3
            assert result["total_count"] == 3
            mock_get.assert_called_once_with(mock_db, 1, limit=100)