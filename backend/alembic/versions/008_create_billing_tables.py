"""Create billing tables

Revision ID: 008_create_billing_tables
Revises: 007_consolidate_team_to_organization
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '008_create_billing_tables'
down_revision = '007_consolidate_team_to_organization'
branch_labels = None
depends_on = None


def upgrade():
    """安全なテーブル作成"""
    # 既存テーブルの確認
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    existing_tables = inspector.get_table_names()
    
    try:
        # organizationsテーブルの作成
        if 'organizations' not in existing_tables:
            op.create_table('organizations',
                sa.Column('id', sa.Integer(), nullable=False),
                sa.Column('name', sa.String(length=255), nullable=False),
                sa.Column('slug', sa.String(length=100), nullable=False),
                sa.Column('description', sa.Text(), nullable=True),
                sa.Column('free_user_limit', sa.Integer(), nullable=False, default=10),
                sa.Column('cost_per_user', sa.Integer(), nullable=False, default=500),
                sa.Column('subscription_status', sa.String(length=50), nullable=False, default='free'),
                sa.Column('stripe_customer_id', sa.String(length=255), nullable=True, unique=True),
                sa.Column('stripe_subscription_id', sa.String(length=255), nullable=True, unique=True),
                sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
                sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()')),
                sa.PrimaryKeyConstraint('id'),
                sa.UniqueConstraint('slug'),
                sa.UniqueConstraint('stripe_customer_id'),
                sa.UniqueConstraint('stripe_subscription_id')
            )
            print("✅ organizationsテーブル作成完了")
        else:
            print("⚠️  organizationsテーブルは既に存在します")
    except Exception as e:
        print(f"⚠️  organizationsテーブル作成スキップ: {e}")

    try:
        # organization_membersテーブルの作成
        if 'organization_members' not in existing_tables:
            op.create_table('organization_members',
                sa.Column('id', sa.Integer(), nullable=False),
                sa.Column('organization_id', sa.Integer(), nullable=False),
                sa.Column('user_id', sa.Integer(), nullable=False),
                sa.Column('role', sa.String(length=50), nullable=False, default='member'),
                sa.Column('status', sa.String(length=50), nullable=False, default='active'),
                sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
                sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
                sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()')),
                sa.PrimaryKeyConstraint('id'),
                sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
                sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
                sa.UniqueConstraint('organization_id', 'user_id')
            )
            print("✅ organization_membersテーブル作成完了")
        else:
            print("⚠️  organization_membersテーブルは既に存在します")
    except Exception as e:
        print(f"⚠️  organization_membersテーブル作成スキップ: {e}")

    try:
        # paymentsテーブルの作成
        if 'payments' not in existing_tables:
            op.create_table('payments',
                sa.Column('id', sa.Integer(), nullable=False),
                sa.Column('organization_id', sa.Integer(), nullable=False),
                sa.Column('stripe_payment_intent_id', sa.String(length=255), nullable=False, unique=True),
                sa.Column('stripe_checkout_session_id', sa.String(length=255), nullable=True, unique=True),
                sa.Column('amount', sa.Integer(), nullable=False),  # Amount in cents
                sa.Column('currency', sa.String(length=3), nullable=False, default='jpy'),
                sa.Column('status', sa.String(length=50), nullable=False),
                sa.Column('payment_method', sa.String(length=50), nullable=True),
                sa.Column('description', sa.Text(), nullable=True),
                sa.Column('payment_metadata', sa.JSON(), nullable=True),
                sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
                sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()')),
                sa.PrimaryKeyConstraint('id'),
                sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
                sa.UniqueConstraint('stripe_payment_intent_id'),
                sa.UniqueConstraint('stripe_checkout_session_id')
            )
            print("✅ paymentsテーブル作成完了")
        else:
            print("⚠️  paymentsテーブルは既に存在します")
    except Exception as e:
        print(f"⚠️  paymentsテーブル作成スキップ: {e}")

    try:
        # subscriptionsテーブルの作成
        if 'subscriptions' not in existing_tables:
            op.create_table('subscriptions',
                sa.Column('id', sa.Integer(), nullable=False),
                sa.Column('user_id', sa.Integer(), nullable=False),
                sa.Column('organization_id', sa.Integer(), nullable=False),
                sa.Column('stripe_subscription_id', sa.String(length=255), nullable=False),
                sa.Column('stripe_price_id', sa.String(length=255), nullable=True),
                sa.Column('status', sa.String(length=50), nullable=False),
                sa.Column('current_period_start', sa.DateTime(timezone=True), nullable=True),
                sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=True),
                sa.Column('canceled_at', sa.DateTime(timezone=True), nullable=True),
                sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
                sa.Column('quantity', sa.Integer(), nullable=False, default=0),
                sa.Column('subscription_metadata', sa.JSON(), nullable=True),
                sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
                sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()')),
                sa.PrimaryKeyConstraint('id'),
                sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
                sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
                sa.UniqueConstraint('stripe_subscription_id')
            )
            print("✅ subscriptionsテーブル作成完了")
        else:
            print("⚠️  subscriptionsテーブルは既に存在します")
    except Exception as e:
        print(f"⚠️  subscriptionsテーブル作成スキップ: {e}")

    # インデックスの作成（エラーが発生しても続行）
    try:
        if 'organizations' in existing_tables:
            op.create_index('idx_organizations_stripe_customer', 'organizations', ['stripe_customer_id'])
            print("✅ organizationsインデックス作成完了")
    except Exception as e:
        print(f"⚠️  organizationsインデックス作成スキップ: {e}")
    
    try:
        if 'organization_members' in existing_tables:
            op.create_index('idx_organization_members_org_user', 'organization_members', ['organization_id', 'user_id'])
            print("✅ organization_membersインデックス作成完了")
    except Exception as e:
        print(f"⚠️  organization_membersインデックス作成スキップ: {e}")
    
    try:
        if 'payments' in existing_tables:
            op.create_index('idx_payments_organization', 'payments', ['organization_id'])
            op.create_index('idx_payments_stripe_payment_intent', 'payments', ['stripe_payment_intent_id'])
            print("✅ paymentsインデックス作成完了")
    except Exception as e:
        print(f"⚠️  paymentsインデックス作成スキップ: {e}")
    
    try:
        if 'subscriptions' in existing_tables:
            op.create_index('idx_subscriptions_organization', 'subscriptions', ['organization_id'])
            op.create_index('idx_subscriptions_stripe_subscription', 'subscriptions', ['stripe_subscription_id'])
            print("✅ subscriptionsインデックス作成完了")
    except Exception as e:
        print(f"⚠️  subscriptionsインデックス作成スキップ: {e}")


def downgrade():
    """安全なテーブル削除"""
    # インデックスの削除（エラーが発生しても続行）
    try:
        op.drop_index('idx_subscriptions_stripe_subscription', 'subscriptions')
        print("✅ subscriptionsインデックス削除完了")
    except Exception as e:
        print(f"⚠️  subscriptionsインデックス削除スキップ: {e}")
    
    try:
        op.drop_index('idx_subscriptions_organization', 'subscriptions')
        print("✅ subscriptions organizationインデックス削除完了")
    except Exception as e:
        print(f"⚠️  subscriptions organizationインデックス削除スキップ: {e}")
    
    try:
        op.drop_index('idx_payments_stripe_payment_intent', 'payments')
        print("✅ payments payment_intentインデックス削除完了")
    except Exception as e:
        print(f"⚠️  payments payment_intentインデックス削除スキップ: {e}")
    
    try:
        op.drop_index('idx_payments_organization', 'payments')
        print("✅ payments organizationインデックス削除完了")
    except Exception as e:
        print(f"⚠️  payments organizationインデックス削除スキップ: {e}")
    
    try:
        op.drop_index('idx_organization_members_org_user', 'organization_members')
        print("✅ organization_membersインデックス削除完了")
    except Exception as e:
        print(f"⚠️  organization_members organizationインデックス削除スキップ: {e}")
    
    try:
        op.drop_index('idx_organizations_stripe_customer', 'organizations')
        print("✅ organizationsインデックス削除完了")
    except Exception as e:
        print(f"⚠️  organizationsインデックス削除スキップ: {e}")

    # テーブルの削除（依存関係を考慮して逆順で）
    try:
        op.drop_table('subscriptions')
        print("✅ subscriptionsテーブル削除完了")
    except Exception as e:
        print(f"⚠️  subscriptionsテーブル削除スキップ: {e}")
    
    try:
        op.drop_table('payments')
        print("✅ paymentsテーブル削除完了")
    except Exception as e:
        print(f"⚠️  paymentsテーブル削除スキップ: {e}")
    
    try:
        op.drop_table('organization_members')
        print("✅ organization_membersテーブル削除完了")
    except Exception as e:
        print(f"⚠️  organization_membersテーブル削除スキップ: {e}")
    
    try:
        op.drop_table('organizations')
        print("✅ organizationsテーブル削除完了")
    except Exception as e:
        print(f"⚠️  organizationsテーブル削除スキップ: {e}")
