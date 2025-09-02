import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.billing import Billing
from app.services.billing_service import BillingService
from tests.test_utils.test_helpers import (
    create_mock_billing,
    create_mock_invoice_data,
    assert_billing_data
)
from unittest.mock import patch


class TestBillingModel:
    """請求モデルのテスト"""
    
    def test_billing_creation(self):
        """請求の作成テスト"""
        billing = Billing(
            id=1,
            billing_id="bill_123456",
            invoice_number="INV-2024-001",
            amount=1000.0,
            currency="JPY",
            tax_amount=100.0,
            total_amount=1100.0,
            status="pending",
            payment_method="credit_card",
            user_id=1
        )
        
        assert billing.id == 1
        assert billing.billing_id == "bill_123456"
        assert billing.invoice_number == "INV-2024-001"
        assert billing.amount == 1000.0
        assert billing.currency == "JPY"
        assert billing.tax_amount == 100.0
        assert billing.total_amount == 1100.0
        assert billing.status == "pending"
        assert billing.payment_method == "credit_card"
        assert billing.user_id == 1
    
    def test_billing_default_values(self):
        """請求のデフォルト値テスト"""
        billing = Billing(
            billing_id="bill_123456",
            amount=1000.0,
            total_amount=1000.0,
            user_id=1
        )
        
        assert billing.currency == "JPY"
        assert billing.tax_amount == 0.0
        assert billing.status == "pending"
        assert billing.payment_method is None
    
    def test_billing_status_properties(self):
        """請求ステータスのプロパティテスト"""
        # 支払い済み
        paid_billing = Billing(
            billing_id="bill_123456",
            amount=1000.0,
            total_amount=1000.0,
            user_id=1,
            status="paid",
            paid_at=datetime.utcnow()
        )
        assert paid_billing.is_paid is True
        assert paid_billing.is_overdue is False
        assert paid_billing.is_failed is False
        assert paid_billing.is_refunded is False
        
        # 期限切れ
        overdue_billing = Billing(
            billing_id="bill_123456",
            amount=1000.0,
            total_amount=1000.0,
            user_id=1,
            status="pending",
            due_date=datetime.utcnow() - timedelta(days=1)
        )
        assert overdue_billing.is_overdue is True
        
        # 失敗
        failed_billing = Billing(
            billing_id="bill_123456",
            amount=1000.0,
            total_amount=1000.0,
            user_id=1,
            status="failed"
        )
        assert failed_billing.is_failed is True
        
        # 返金済み
        refunded_billing = Billing(
            billing_id="bill_123456",
            amount=1000.0,
            total_amount=1000.0,
            user_id=1,
            status="refunded"
        )
        assert refunded_billing.is_refunded is True


class TestBillingBusinessLogic:
    """請求ビジネスロジックのテスト"""
    
    def test_billing_calculation(self):
        """請求計算のテスト"""
        # 税込計算
        billing = Billing(
            billing_id="bill_123456",
            amount=1000.0,
            tax_amount=100.0,
            total_amount=1100.0,
            user_id=1
        )
        
        assert billing.calculate_total() == 1100.0
        assert billing.calculate_tax_rate() == 0.1  # 10%
        
        # 税抜計算
        billing_no_tax = Billing(
            billing_id="bill_123456",
            amount=1000.0,
            tax_amount=0.0,
            total_amount=1000.0,
            user_id=1
        )
        
        assert billing_no_tax.calculate_total() == 1000.0
        assert billing_no_tax.calculate_tax_rate() == 0.0
    
    def test_billing_payment_processing(self):
        """請求支払い処理のテスト"""
        billing = Billing(
            billing_id="bill_123456",
            amount=1000.0,
            total_amount=1000.0,
            user_id=1,
            status="pending"
        )
        
        # 支払い処理
        billing.process_payment("credit_card", datetime.utcnow())
        
        assert billing.status == "paid"
        assert billing.payment_method == "credit_card"
        assert billing.paid_at is not None
    
    def test_billing_overdue_detection(self):
        """請求期限切れ検出のテスト"""
        # 期限切れ
        overdue_billing = Billing(
            billing_id="bill_123456",
            amount=1000.0,
            total_amount=1000.0,
            user_id=1,
            status="pending",
            due_date=datetime.utcnow() - timedelta(days=1)
        )
        
        assert overdue_billing.is_overdue is True
        assert overdue_billing.days_overdue() == 1
        
        # 期限内
        current_billing = Billing(
            billing_id="bill_123456",
            amount=1000.0,
            total_amount=1000.0,
            user_id=1,
            status="pending",
            due_date=datetime.utcnow() + timedelta(days=1)
        )
        
        assert current_billing.is_overdue is False
        assert current_billing.days_until_due() == 1


class TestBillingAPI:
    """請求APIのテスト"""
    
    async def test_get_billing_info(self, client, mock_db_session):
        """請求情報取得のテスト"""
        # モック請求オブジェクトの作成
        mock_billing = create_mock_billing()
        
        # データベースセッションのモック
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_billing
        
        # APIリクエストのテスト
        response = client.get("/api/v1/billing/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["billing_id"] == "bill_1"
        assert data["amount"] == 1000.0
    
    async def test_create_billing(self, client, mock_db_session):
        """請求作成のテスト"""
        # 請求作成リクエストのテスト
        billing_data = create_mock_invoice_data()
        
        response = client.post("/api/v1/billing", json=billing_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "billing_id" in data
        assert data["amount"] == billing_data["amount"]


class TestBillingService:
    """請求サービスのテスト"""
    
    @pytest.fixture
    def billing_service(self):
        """請求サービスインスタンス"""
        return BillingService()
    
    @pytest.fixture
    def mock_db(self):
        """モックデータベースセッション"""
        return AsyncMock()
    
    async def test_create_invoice_success(self, billing_service, mock_db):
        """請求書作成の成功テスト"""
        invoice_data = create_mock_invoice_data()
        mock_invoice = create_mock_billing()
        
        with patch('app.services.billing_service.billing_repository.create_invoice') as mock_create:
            mock_create.return_value = mock_invoice
            
            result = await billing_service.create_invoice(
                db=mock_db,
                user_id=1,
                amount=2980.0,
                currency="JPY",
                description="Premium Plan - Monthly Subscription"
            )
            
            # 検証
            assert result["invoice_id"] == 1
            assert result["amount"] == 2980.0
            assert result["currency"] == "JPY"
            assert result["status"] == "pending"
            assert "due_date" in result
            mock_create.assert_called_once()
    
    async def test_create_invoice_with_custom_due_date(self, billing_service, mock_db):
        """カスタム支払期日での請求書作成テスト"""
        custom_due_date = datetime.utcnow() + timedelta(days=15)
        mock_invoice = create_mock_billing()
        
        with patch('app.services.billing_service.billing_repository.create_invoice') as mock_create:
            mock_create.return_value = mock_invoice
            
            result = await billing_service.create_invoice(
                db=mock_db,
                user_id=1,
                amount=2980.0,
                due_date=custom_due_date
            )
            
            # 検証
            assert result["due_date"] == custom_due_date.isoformat()
            mock_create.assert_called_once()
    
    async def test_create_invoice_database_error(self, billing_service, mock_db):
        """請求書作成のデータベースエラーテスト"""
        with patch('app.services.billing_service.billing_repository.create_invoice') as mock_create:
            mock_create.side_effect = Exception("Database error")
            
            with pytest.raises(Exception, match="Database error"):
                await billing_service.create_invoice(
                    db=mock_db,
                    user_id=1,
                    amount=2980.0
                )
    
    async def test_get_user_invoices(self, billing_service, mock_db):
        """ユーザー請求書一覧取得のテスト"""
        mock_invoices = [
            create_mock_billing(1, 1, 1000.0),
            create_mock_billing(2, 1, 2000.0)
        ]
        
        with patch('app.services.billing_service.billing_repository.get_user_invoices') as mock_get:
            mock_get.return_value = mock_invoices
            
            result = await billing_service.get_user_invoices(mock_db, 1, "pending", 50)
            
            # 検証
            assert len(result["invoices"]) == 2
            assert result["total_count"] == 2
            mock_get.assert_called_once_with(mock_db, 1, "pending", 50)
    
    async def test_get_invoice(self, billing_service, mock_db):
        """請求書取得のテスト"""
        mock_invoice = create_mock_billing()
        
        with patch('app.services.billing_service.billing_repository.get_invoice') as mock_get:
            mock_get.return_value = mock_invoice
            
            result = await billing_service.get_invoice(mock_db, 1)
            
            # 検証
            assert result.id == 1
            assert result.amount == 1000.0
            mock_get.assert_called_once_with(mock_db, 1)
    
    async def test_update_invoice_status_success(self, billing_service, mock_db):
        """請求書ステータス更新の成功テスト"""
        with patch('app.services.billing_service.billing_repository.update_invoice_status') as mock_update:
            mock_update.return_value = True
            
            result = await billing_service.update_invoice_status(mock_db, 1, "paid")
            
            # 検証
            assert result is True
            mock_update.assert_called_once_with(mock_db, 1, "paid")
    
    async def test_update_invoice_status_failure(self, billing_service, mock_db):
        """請求書ステータス更新の失敗テスト"""
        with patch('app.services.billing_service.billing_repository.update_invoice_status') as mock_update:
            mock_update.return_value = False
            
            result = await billing_service.update_invoice_status(mock_db, 1, "invalid_status")
            
            # 検証
            assert result is False
    
    async def test_mark_invoice_as_paid_success(self, billing_service, mock_db):
        """請求書支払い済みマークの成功テスト"""
        with patch('app.services.billing_service.billing_repository.mark_invoice_as_paid') as mock_mark:
            mock_mark.return_value = True
            
            result = await billing_service.mark_invoice_as_paid(mock_db, 1)
            
            # 検証
            assert result is True
            mock_mark.assert_called_once()
            call_args = mock_mark.call_args[0]
            assert call_args[0] == mock_db  # db
            assert call_args[1] == 1  # invoice_id
    
    async def test_mark_invoice_as_paid_failure(self, billing_service, mock_db):
        """請求書支払い済みマークの失敗テスト"""
        with patch('app.services.billing_service.billing_repository.mark_invoice_as_paid') as mock_mark:
            mock_mark.return_value = False
            
            result = await billing_service.mark_invoice_as_paid(mock_db, 1)
            
            # 検証
            assert result is False
    
    async def test_get_payment_history(self, billing_service, mock_db):
        """支払い履歴取得のテスト"""
        mock_payments = [
            create_mock_billing(1, 1, 1000.0, status="paid"),
            create_mock_billing(2, 1, 2000.0, status="paid")
        ]
        
        with patch('app.services.billing_service.billing_repository.get_payment_history') as mock_get:
            mock_get.return_value = mock_payments
            
            result = await billing_service.get_payment_history(mock_db, 1, 100)
            
            # 検証
            assert len(result["payments"]) == 2
            assert result["total_count"] == 2
            mock_get.assert_called_once_with(mock_db, 1, 100)


class TestSubscriptionCostCalculation:
    """サブスクリプション料金計算のテスト"""
    
    @pytest.fixture
    def billing_service(self):
        """請求サービスインスタンス"""
        return BillingService()
    
    @pytest.fixture
    def mock_db(self):
        """モックデータベースセッション"""
        return AsyncMock()
    
    async def test_calculate_basic_monthly_cost(self, billing_service, mock_db):
        """ベーシックプラン月額料金計算のテスト"""
        result = await billing_service.calculate_subscription_cost(mock_db, "basic", "monthly")
        
        assert result["amount"] == 980.0
        assert result["currency"] == "JPY"
        assert result["billing_cycle"] == "monthly"
    
    async def test_calculate_basic_yearly_cost(self, billing_service, mock_db):
        """ベーシックプラン年額料金計算のテスト"""
        result = await billing_service.calculate_subscription_cost(mock_db, "basic", "yearly")
        
        assert result["amount"] == 9800.0
        assert result["currency"] == "JPY"
        assert result["billing_cycle"] == "yearly"
    
    async def test_calculate_premium_monthly_cost(self, billing_service, mock_db):
        """プレミアムプラン月額料金計算のテスト"""
        result = await billing_service.calculate_subscription_cost(mock_db, "premium", "monthly")
        
        assert result["amount"] == 2980.0
        assert result["currency"] == "JPY"
        assert result["billing_cycle"] == "monthly"
    
    async def test_calculate_enterprise_yearly_cost(self, billing_service, mock_db):
        """エンタープライズプラン年額料金計算のテスト"""
        result = await billing_service.calculate_subscription_cost(mock_db, "enterprise", "yearly")
        
        assert result["amount"] == 98000.0
        assert result["currency"] == "JPY"
        assert result["billing_cycle"] == "yearly"
    
    async def test_calculate_unknown_plan_cost(self, billing_service, mock_db):
        """不明なプランの料金計算のテスト"""
        result = await billing_service.calculate_subscription_cost(mock_db, "unknown", "monthly")
        
        assert result["amount"] == 0.0
        assert result["error"] == "Unknown plan: unknown"
    
    async def test_calculate_subscription_cost_error(self, billing_service, mock_db):
        """サブスクリプション料金計算エラーのテスト"""
        mock_db.execute.side_effect = Exception("Database error")
        
        with pytest.raises(Exception, match="Database error"):
            await billing_service.calculate_subscription_cost(mock_db, "basic", "monthly")


class TestSubscriptionBilling:
    """サブスクリプション請求のテスト"""
    
    @pytest.fixture
    def billing_service(self):
        """請求サービスインスタンス"""
        return BillingService()
    
    @pytest.fixture
    def mock_db(self):
        """モックデータベースセッション"""
        return AsyncMock()
    
    async def test_create_subscription_billing_success(self, billing_service, mock_db):
        """サブスクリプション請求作成の成功テスト"""
        # 料金計算のモック
        with patch.object(billing_service, 'calculate_subscription_cost') as mock_calc:
            mock_calc.return_value = {
                "amount": 2980.0,
                "currency": "JPY",
                "billing_cycle": "monthly"
            }
            
            # 請求書作成のモック
            with patch('app.services.billing_service.billing_repository.create_invoice') as mock_create:
                mock_invoice = create_mock_billing()
                mock_create.return_value = mock_invoice
                
                result = await billing_service.create_subscription_billing(
                    mock_db, 1, "premium", "monthly"
                )
                
                # 検証
                assert result["invoice_id"] == 1
                assert result["amount"] == 2980.0
                assert result["status"] == "pending"
                mock_calc.assert_called_once_with(mock_db, "premium", "monthly")
                mock_create.assert_called_once()
    
    async def test_create_subscription_billing_calculation_failed(self, billing_service, mock_db):
        """サブスクリプション請求作成の料金計算失敗テスト"""
        with patch.object(billing_service, 'calculate_subscription_cost') as mock_calc:
            mock_calc.return_value = {"error": "Invalid plan"}
            
            result = await billing_service.create_subscription_billing(
                mock_db, 1, "invalid", "monthly"
            )
            
            # 検証
            assert "error" in result
            assert result["error"] == "Invalid plan"
    
    async def test_create_subscription_billing_invoice_creation_failed(self, billing_service, mock_db):
        """サブスクリプション請求作成の請求書作成失敗テスト"""
        with patch.object(billing_service, 'calculate_subscription_cost') as mock_calc:
            mock_calc.return_value = {
                "amount": 2980.0,
                "currency": "JPY",
                "billing_cycle": "monthly"
            }
            
            with patch('app.services.billing_service.billing_repository.create_invoice') as mock_create:
                mock_create.side_effect = Exception("Invoice creation failed")
                
                with pytest.raises(Exception, match="Invoice creation failed"):
                    await billing_service.create_subscription_billing(
                        mock_db, 1, "premium", "monthly"
                    )


class TestBillingSummary:
    """請求サマリーのテスト"""
    
    @pytest.fixture
    def billing_service(self):
        """請求サービスインスタンス"""
        return BillingService()
    
    @pytest.fixture
    def mock_db(self):
        """モックデータベースセッション"""
        return AsyncMock()
    
    async def test_get_billing_summary_success(self, billing_service, mock_db):
        """請求サマリー取得の成功テスト"""
        mock_invoices = [
            create_mock_billing(1, 1, 1000.0, status="paid"),
            create_mock_billing(2, 1, 2000.0, status="pending"),
            create_mock_billing(3, 1, 3000.0, status="overdue")
        ]
        
        with patch('app.services.billing_service.billing_repository.get_user_invoices') as mock_get_invoices:
            mock_get_invoices.return_value = mock_invoices
            
            result = await billing_service.get_billing_summary(mock_db, 1)
            
            # 検証
            assert result["total_invoices"] == 3
            assert result["paid_amount"] == 1000.0
            assert result["pending_amount"] == 2000.0
            assert result["overdue_amount"] == 3000.0
            assert result["total_amount"] == 6000.0
            mock_get_invoices.assert_called_once()
    
    async def test_get_billing_summary_no_invoices(self, billing_service, mock_db):
        """請求サマリー取得の請求書なしテスト"""
        with patch('app.services.billing_service.billing_repository.get_user_invoices') as mock_get_invoices:
            mock_get_invoices.return_value = []
            
            result = await billing_service.get_billing_summary(mock_db, 1)
            
            # 検証
            assert result["total_invoices"] == 0
            assert result["paid_amount"] == 0.0
            assert result["pending_amount"] == 0.0
            assert result["overdue_amount"] == 0.0
            assert result["total_amount"] == 0.0
    
    async def test_get_billing_summary_error(self, billing_service, mock_db):
        """請求サマリー取得のエラーテスト"""
        with patch('app.services.billing_service.billing_repository.get_user_invoices') as mock_get_invoices:
            mock_get_invoices.side_effect = Exception("Database error")
            
            with pytest.raises(Exception, match="Database error"):
                await billing_service.get_billing_summary(mock_db, 1)


class TestBillingValidation:
    """請求バリデーションのテスト"""
    
    def test_billing_model_creation(self):
        """請求モデル作成のテスト"""
        billing = Billing(
            billing_id="bill_123",
            amount=1000.0,
            total_amount=1000.0,
            user_id=1
        )
        
        assert billing.billing_id == "bill_123"
        assert billing.amount == 1000.0
        assert billing.total_amount == 1000.0
        assert billing.user_id == 1
    
    def test_billing_model_default_values(self):
        """請求モデルデフォルト値のテスト"""
        billing = Billing(
            billing_id="bill_123",
            amount=1000.0,
            total_amount=1000.0,
            user_id=1
        )
        
        assert billing.currency == "JPY"
        assert billing.tax_amount == 0.0
        assert billing.status == "pending"
        assert billing.payment_method is None
    
    def test_billing_model_validation(self):
        """請求モデルバリデーションのテスト"""
        # 有効な請求
        valid_billing = Billing(
            billing_id="bill_123",
            amount=1000.0,
            total_amount=1000.0,
            user_id=1
        )
        
        assert valid_billing.is_valid() is True
        
        # 無効な請求（金額が負）
        invalid_billing = Billing(
            billing_id="bill_123",
            amount=-1000.0,
            total_amount=-1000.0,
            user_id=1
        )
        
        assert invalid_billing.is_valid() is False
    
    def test_payment_method_validation(self):
        """支払い方法バリデーションのテスト"""
        valid_methods = ["credit_card", "bank_transfer", "paypal"]
        
        for method in valid_methods:
            billing = Billing(
                billing_id="bill_123",
                amount=1000.0,
                total_amount=1000.0,
                user_id=1,
                payment_method=method
            )
            
            assert billing.is_valid_payment_method() is True
        
        # 無効な支払い方法
        invalid_billing = Billing(
            billing_id="bill_123",
            amount=1000.0,
            total_amount=1000.0,
            user_id=1,
            payment_method="invalid_method"
        )
        
        assert invalid_billing.is_valid_payment_method() is False
