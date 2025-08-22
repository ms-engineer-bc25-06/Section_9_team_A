from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
import stripe

from app.api.deps import get_current_admin_user, get_db
from app.models.user import User
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.models.payment import Payment
from app.models.subscription import Subscription
from app.schemas.admin_billing import (
    BillingSummary,
    OrganizationBillingInfo,
    UserCountInfo,
    CreateCheckoutSessionRequest,
    CheckoutSessionResponse
)

router = APIRouter()


@router.get("/billing/summary", response_model=BillingSummary)
async def get_billing_summary(
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    管理者用：システム全体の決済・課金サマリーを取得
    """
    try:
        # 組織ごとの利用者数と課金状況を取得
        org_billing_info = []
        
        result = await db.execute(select(Organization))
        organizations = result.scalars().all()
        
        for org in organizations:
            # 組織のメンバー数を取得
            member_count = db.query(OrganizationMember).filter(
                OrganizationMember.organization_id == org.id,
                OrganizationMember.status == 'active'
            ).count()
            
            # 無料枠を超過しているかチェック
            is_over_limit = member_count > org.free_user_limit
            additional_users = max(0, member_count - org.free_user_limit)
            additional_cost = additional_users * org.cost_per_user
            
            # 最新の決済状況を取得
            latest_payment = db.query(Payment).filter(
                Payment.organization_id == org.id,
                Payment.status == 'succeeded'
            ).order_by(Payment.created_at.desc()).first()
            
            # サブスクリプション状況を取得
            subscription = db.query(Subscription).filter(
                Subscription.organization_id == org.id,
                Subscription.status == 'active'
            ).first()
            
            org_info = OrganizationBillingInfo(
                organization_id=org.id,
                organization_name=org.name,
                organization_slug=org.slug,
                member_count=member_count,
                free_user_limit=org.free_user_limit,
                cost_per_user=org.cost_per_user,
                is_over_limit=is_over_limit,
                additional_users=additional_users,
                additional_cost=additional_cost,
                subscription_status=org.subscription_status,
                stripe_customer_id=org.stripe_customer_id,
                last_payment_date=latest_payment.created_at if latest_payment else None,
                last_payment_amount=latest_payment.amount if latest_payment else None
            )
            
            org_billing_info.append(org_info)
        
        # システム全体の統計
        total_organizations = len(organizations)
        total_users = sum(org.member_count for org in org_billing_info)
        total_additional_cost = sum(org.additional_cost for org in org_billing_info)
        organizations_over_limit = len([org for org in org_billing_info if org.is_over_limit])
        
        summary = BillingSummary(
            total_organizations=total_organizations,
            total_users=total_users,
            total_additional_cost=total_additional_cost,
            organizations_over_limit=organizations_over_limit,
            organizations=org_billing_info
        )
        
        return summary
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"決済サマリーの取得に失敗しました: {str(e)}"
        )


@router.get("/billing/organization/{organization_id}", response_model=OrganizationBillingInfo)
async def get_organization_billing_info(
    organization_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    管理者用：特定組織の決済・課金情報を取得
    """
    try:
        organization = db.query(Organization).filter(Organization.id == organization_id).first()
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="組織が見つかりません"
            )
        
        # 組織のメンバー数を取得
        member_count = db.query(OrganizationMember).filter(
            OrganizationMember.organization_id == organization.id,
            OrganizationMember.status == 'active'
        ).count()
        
        # 無料枠を超過しているかチェック
        is_over_limit = member_count > organization.free_user_limit
        additional_users = max(0, member_count - organization.free_user_limit)
        additional_cost = additional_users * organization.cost_per_user
        
        # 最新の決済状況を取得
        latest_payment = db.query(Payment).filter(
            Payment.organization_id == organization.id,
            Payment.status == 'succeeded'
        ).order_by(Payment.created_at.desc()).first()
        
        org_info = OrganizationBillingInfo(
            organization_id=organization.id,
            organization_name=organization.name,
            organization_slug=organization.slug,
            member_count=member_count,
            free_user_limit=organization.free_user_limit,
            cost_per_user=organization.cost_per_user,
            is_over_limit=is_over_limit,
            additional_users=additional_users,
            additional_cost=additional_cost,
            subscription_status=organization.subscription_status,
            stripe_customer_id=organization.stripe_customer_id,
            last_payment_date=latest_payment.created_at if latest_payment else None,
            last_payment_amount=latest_payment.amount if latest_payment else None
        )
        
        return org_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"組織の決済情報取得に失敗しました: {str(e)}"
        )


@router.get("/billing/user-count", response_model=UserCountInfo)
async def get_user_count(
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    管理者用：システム全体の利用者数を取得
    """
    try:
        # システム全体の利用者数を取得
        total_users = db.query(OrganizationMember).filter(
            OrganizationMember.status == 'active'
        ).count()
        
        # 組織ごとの利用者数
        org_user_counts = db.query(
            OrganizationMember.organization_id,
            func.count(OrganizationMember.id).label('user_count')
        ).filter(
            OrganizationMember.status == 'active'
        ).group_by(OrganizationMember.organization_id).all()
        
        # 無料枠を超過している組織の数
        organizations_over_limit = 0
        total_additional_cost = 0
        
        for org_id, user_count in org_user_counts:
            org = db.query(Organization).filter(Organization.id == org_id).first()
            if org and user_count > org.free_user_limit:
                organizations_over_limit += 1
                additional_users = user_count - org.free_user_limit
                total_additional_cost += additional_users * org.cost_per_user
        
        return UserCountInfo(
            total_users=total_users,
            organizations_over_limit=organizations_over_limit,
            total_additional_cost=total_additional_cost
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"利用者数の取得に失敗しました: {str(e)}"
        )


@router.post("/billing/checkout", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: CreateCheckoutSessionRequest,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    管理者用：Stripe Checkout Sessionを作成
    """
    try:
        # 組織の存在確認
        organization = db.query(Organization).filter(Organization.id == request.organization_id).first()
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="組織が見つかりません"
            )
        
        # 金額の検証
        expected_amount = request.additional_users * organization.cost_per_user * 100  # セント単位
        if request.amount != expected_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="金額が正しくありません"
            )
        
        # Stripe Checkout Session作成
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        try:
            # Checkout Session作成
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': request.currency.lower(),
                        'product_data': {
                            'name': f'{request.additional_users}人分の追加ユーザー料金',
                            'description': f'{organization.name}の追加ユーザー{request.additional_users}人分',
                        },
                        'unit_amount': request.amount,  # セント単位
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f"{settings.FRONTEND_URL}/admin/billing/success?session_id={{CHECKOUT_SESSION_ID}}&amount={request.amount}&additional_users={request.additional_users}&organization_id={request.organization_id}",
                cancel_url=f"{settings.FRONTEND_URL}/admin/users/add?canceled=true",
                metadata={
                    'additional_users': request.additional_users,
                    'organization_id': request.organization_id
                }
            )
            
            # 決済レコードを作成
            payment = Payment(
                organization_id=request.organization_id,
                stripe_payment_intent_id=checkout_session.payment_intent,
                stripe_checkout_session_id=checkout_session.id,
                amount=request.amount,
                currency=request.currency,
                status="pending",
                description=f"{request.additional_users}人分の追加料金",
                payment_metadata={
                    "additional_users": request.additional_users,
                    "organization_id": request.organization_id
                }
            )
            
            db.add(payment)
            await db.commit()
            
            return CheckoutSessionResponse(
                session_id=checkout_session.id,
                checkout_url=checkout_session.url,
                amount=request.amount,
                currency=request.currency,
                organization_id=request.organization_id,
                additional_users=request.additional_users
            )
            
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripeエラー: {str(e)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"チェックアウトセッションの作成に失敗しました: {str(e)}"
        )
