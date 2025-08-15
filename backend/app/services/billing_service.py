from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, asc
import structlog
from datetime import datetime, timedelta

from app.repositories.billing_repository import billing_repository

logger = structlog.get_logger()


class BillingService:
    """請求サービス"""

    async def create_invoice(
        self,
        db: AsyncSession,
        user_id: int,
        amount: float,
        currency: str = "JPY",
        description: str = "",
        due_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """請求書を作成"""
        try:
            if not due_date:
                due_date = datetime.utcnow() + timedelta(days=30)

            invoice_data = {
                "user_id": user_id,
                "amount": amount,
                "currency": currency,
                "description": description,
                "due_date": due_date,
                "status": "pending",
                "created_at": datetime.utcnow()
            }

            invoice = await billing_repository.create_invoice(db, invoice_data)

            return {
                "invoice_id": invoice.id,
                "amount": invoice.amount,
                "currency": invoice.currency,
                "due_date": invoice.due_date.isoformat(),
                "status": invoice.status
            }

        except Exception as e:
            logger.error(f"Failed to create invoice: {str(e)}")
            raise

    async def get_user_invoices(
        self,
        db: AsyncSession,
        user_id: int,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Any]:
        """ユーザーの請求書一覧を取得"""
        return await billing_repository.get_user_invoices(db, user_id, status, limit)

    async def get_invoice(
        self, db: AsyncSession, invoice_id: int
    ) -> Optional[Any]:
        """請求書を取得"""
        return await billing_repository.get_invoice(db, invoice_id)

    async def update_invoice_status(
        self,
        db: AsyncSession,
        invoice_id: int,
        status: str
    ) -> bool:
        """請求書のステータスを更新"""
        try:
            await billing_repository.update_invoice_status(db, invoice_id, status)
            logger.info(f"Invoice {invoice_id} status updated to {status}")
            return True
        except Exception as e:
            logger.error(f"Failed to update invoice status: {str(e)}")
            return False

    async def mark_invoice_as_paid(
        self,
        db: AsyncSession,
        invoice_id: int,
        payment_method: str = "credit_card",
        transaction_id: Optional[str] = None
    ) -> bool:
        """請求書を支払い済みにマーク"""
        try:
            payment_data = {
                "status": "paid",
                "paid_at": datetime.utcnow(),
                "payment_method": payment_method,
                "transaction_id": transaction_id
            }

            await billing_repository.update_invoice_payment(db, invoice_id, payment_data)
            logger.info(f"Invoice {invoice_id} marked as paid")
            return True

        except Exception as e:
            logger.error(f"Failed to mark invoice as paid: {str(e)}")
            return False

    async def get_payment_history(
        self,
        db: AsyncSession,
        user_id: int,
        limit: int = 100
    ) -> List[Any]:
        """支払い履歴を取得"""
        return await billing_repository.get_payment_history(db, user_id, limit)

    async def calculate_subscription_cost(
        self,
        db: AsyncSession,
        user_id: int,
        plan_type: str,
        billing_cycle: str = "monthly"
    ) -> Dict[str, Any]:
        """サブスクリプション料金を計算"""
        try:
            # 基本料金
            base_prices = {
                "basic": {"monthly": 1000, "yearly": 10000},
                "pro": {"monthly": 3000, "yearly": 30000},
                "enterprise": {"monthly": 10000, "yearly": 100000}
            }

            base_price = base_prices.get(plan_type, {}).get(billing_cycle, 0)
            
            # 割引計算（年額の場合）
            discount = 0.0
            if billing_cycle == "yearly":
                discount = 0.2  # 20%割引

            final_price = base_price * (1 - discount)

            return {
                "plan_type": plan_type,
                "billing_cycle": billing_cycle,
                "base_price": base_price,
                "discount": discount,
                "final_price": final_price,
                "currency": "JPY"
            }

        except Exception as e:
            logger.error(f"Failed to calculate subscription cost: {str(e)}")
            return {}

    async def create_subscription_billing(
        self,
        db: AsyncSession,
        user_id: int,
        plan_type: str,
        billing_cycle: str = "monthly"
    ) -> Dict[str, Any]:
        """サブスクリプション請求を作成"""
        try:
            cost_info = await self.calculate_subscription_cost(
                db, user_id, plan_type, billing_cycle
            )

            if not cost_info:
                raise ValueError("Failed to calculate subscription cost")

            # 請求書を作成
            invoice = await self.create_invoice(
                db=db,
                user_id=user_id,
                amount=cost_info["final_price"],
                currency=cost_info["currency"],
                description=f"{plan_type}プラン - {billing_cycle}請求",
                due_date=datetime.utcnow() + timedelta(days=30)
            )

            return {
                "invoice": invoice,
                "cost_info": cost_info,
                "next_billing_date": datetime.utcnow() + timedelta(days=30)
            }

        except Exception as e:
            logger.error(f"Failed to create subscription billing: {str(e)}")
            raise

    async def get_billing_summary(
        self,
        db: AsyncSession,
        user_id: int,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """請求サマリーを取得"""
        try:
            invoices = await self.get_user_invoices(db, user_id)
            
            total_amount = sum(invoice.amount for invoice in invoices)
            paid_amount = sum(
                invoice.amount for invoice in invoices 
                if invoice.status == "paid"
            )
            pending_amount = sum(
                invoice.amount for invoice in invoices 
                if invoice.status == "pending"
            )

            return {
                "total_invoices": len(invoices),
                "total_amount": total_amount,
                "paid_amount": paid_amount,
                "pending_amount": pending_amount,
                "currency": "JPY"
            }

        except Exception as e:
            logger.error(f"Failed to get billing summary: {str(e)}")
            return {}


# シングルトンインスタンス
billing_service = BillingService()
