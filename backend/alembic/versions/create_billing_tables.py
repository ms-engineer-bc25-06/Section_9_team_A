"""Create billing tables

Revision ID: create_billing_tables
Revises: df43fb4740e8
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'create_billing_tables'
down_revision = 'df43fb4740e8'
branch_labels = None
depends_on = None


def upgrade():
    # Create organizations table
    op.create_table('organizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('free_user_limit', sa.Integer(), nullable=False, default=10),
        sa.Column('cost_per_user', sa.Integer(), nullable=False, default=500),
        sa.Column('subscription_status', sa.String(length=50), nullable=False, default='free'),
        sa.Column('stripe_customer_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'),
        sa.UniqueConstraint('stripe_customer_id'),
        sa.UniqueConstraint('stripe_subscription_id')
    )

    # Create organization_members table
    op.create_table('organization_members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, default='member'),
        sa.Column('status', sa.String(length=50), nullable=False, default='active'),
        sa.Column('joined_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('organization_id', 'user_id')
    )

    # Create payments table
    op.create_table('payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('stripe_payment_intent_id', sa.String(length=255), nullable=False),
        sa.Column('stripe_checkout_session_id', sa.String(length=255), nullable=True),
        sa.Column('amount', sa.Integer(), nullable=False),  # Amount in cents
        sa.Column('currency', sa.String(length=3), nullable=False, default='jpy'),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('payment_metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('stripe_payment_intent_id'),
        sa.UniqueConstraint('stripe_checkout_session_id')
    )

    # Create subscriptions table
    op.create_table('subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('stripe_subscription_id', sa.String(length=255), nullable=False),
        sa.Column('stripe_price_id', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('current_period_start', sa.DateTime(), nullable=True),
        sa.Column('current_period_end', sa.DateTime(), nullable=True),
        sa.Column('canceled_at', sa.DateTime(), nullable=True),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False, default=0),
        sa.Column('subscription_metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('stripe_subscription_id')
    )

    # Create indexes for better performance
    op.create_index('idx_organizations_stripe_customer', 'organizations', ['stripe_customer_id'])
    op.create_index('idx_organization_members_org_user', 'organization_members', ['organization_id', 'user_id'])
    op.create_index('idx_payments_organization', 'payments', ['organization_id'])
    op.create_index('idx_payments_stripe_payment_intent', 'payments', ['stripe_payment_intent_id'])
    op.create_index('idx_subscriptions_organization', 'subscriptions', ['organization_id'])
    op.create_index('idx_subscriptions_stripe_subscription', 'subscriptions', ['stripe_subscription_id'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_subscriptions_stripe_subscription', 'subscriptions')
    op.drop_index('idx_subscriptions_organization', 'subscriptions')
    op.drop_index('idx_payments_stripe_payment_intent', 'payments')
    op.drop_index('idx_payments_organization', 'payments')
    op.drop_index('idx_organization_members_org_user', 'organization_members')
    op.drop_index('idx_organizations_stripe_customer', 'organizations')

    # Drop tables
    op.drop_table('subscriptions')
    op.drop_table('payments')
    op.drop_table('organization_members')
    op.drop_table('organizations')
