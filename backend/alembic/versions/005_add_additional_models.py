"""Add additional models

Revision ID: 005_add_additional_models
Revises: 004_add_privacy_tables
Create Date: 2025-08-15 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005_add_additional_models'
down_revision = '004_add_privacy_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create subscriptions table
    op.create_table('subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('subscription_id', sa.String(length=255), nullable=False),
        sa.Column('plan_type', sa.String(length=50), nullable=False),
        sa.Column('plan_name', sa.String(length=255), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('billing_cycle', sa.String(length=50), nullable=True),
        sa.Column('max_voice_minutes', sa.Integer(), nullable=True),
        sa.Column('max_analysis_count', sa.Integer(), nullable=True),
        sa.Column('max_team_members', sa.Integer(), nullable=True),
        sa.Column('max_storage_gb', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('trial_end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('canceled_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create invitations table
    op.create_table('invitations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('invitation_id', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('invitation_type', sa.String(length=50), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('team_id', sa.Integer(), nullable=True),
        sa.Column('invited_by', sa.Integer(), nullable=False),
        sa.Column('invited_user', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('accepted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create billings table
    op.create_table('billings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('billing_id', sa.String(length=255), nullable=False),
        sa.Column('invoice_number', sa.String(length=255), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('tax_amount', sa.Float(), nullable=True),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('stripe_payment_intent_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_invoice_id', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('billing_metadata', sa.JSON(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('subscription_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create audit_logs table
    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('log_id', sa.String(length=255), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', sa.String(length=255), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('user_email', sa.String(length=255), nullable=True),
        sa.Column('user_ip', sa.String(length=45), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('session_id', sa.String(length=255), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_subscriptions_id'), 'subscriptions', ['id'], unique=False)
    op.create_index(op.f('ix_subscriptions_subscription_id'), 'subscriptions', ['subscription_id'], unique=True)
    op.create_index(op.f('ix_subscriptions_user_id'), 'subscriptions', ['user_id'], unique=False)
    op.create_index(op.f('ix_subscriptions_plan_type'), 'subscriptions', ['plan_type'], unique=False)
    op.create_index(op.f('ix_subscriptions_status'), 'subscriptions', ['status'], unique=False)
    
    op.create_index(op.f('ix_invitations_id'), 'invitations', ['id'], unique=False)
    op.create_index(op.f('ix_invitations_invitation_id'), 'invitations', ['invitation_id'], unique=True)
    op.create_index(op.f('ix_invitations_email'), 'invitations', ['email'], unique=False)
    op.create_index(op.f('ix_invitations_team_id'), 'invitations', ['team_id'], unique=False)
    op.create_index(op.f('ix_invitations_invited_by'), 'invitations', ['invited_by'], unique=False)
    op.create_index(op.f('ix_invitations_status'), 'invitations', ['status'], unique=False)
    
    op.create_index(op.f('ix_billings_id'), 'billings', ['id'], unique=False)
    op.create_index(op.f('ix_billings_billing_id'), 'billings', ['billing_id'], unique=True)
    op.create_index(op.f('ix_billings_invoice_number'), 'billings', ['invoice_number'], unique=True)
    op.create_index(op.f('ix_billings_user_id'), 'billings', ['user_id'], unique=False)
    op.create_index(op.f('ix_billings_subscription_id'), 'billings', ['subscription_id'], unique=False)
    op.create_index(op.f('ix_billings_status'), 'billings', ['status'], unique=False)
    
    op.create_index(op.f('ix_audit_logs_id'), 'audit_logs', ['id'], unique=False)
    op.create_index(op.f('ix_audit_logs_log_id'), 'audit_logs', ['log_id'], unique=True)
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_audit_logs_resource_type'), 'audit_logs', ['resource_type'], unique=False)
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_created_at'), 'audit_logs', ['created_at'], unique=False)
    
    # Create foreign key constraints
    op.create_foreign_key(None, 'subscriptions', 'users', ['user_id'], ['id'])
    op.create_foreign_key(None, 'invitations', 'teams', ['team_id'], ['id'])
    op.create_foreign_key(None, 'invitations', 'users', ['invited_by'], ['id'])
    op.create_foreign_key(None, 'invitations', 'users', ['invited_user'], ['id'])
    op.create_foreign_key(None, 'billings', 'users', ['user_id'], ['id'])
    op.create_foreign_key(None, 'billings', 'subscriptions', ['subscription_id'], ['id'])
    op.create_foreign_key(None, 'audit_logs', 'users', ['user_id'], ['id'])


def downgrade():
    # Drop foreign key constraints
    op.drop_constraint(None, 'audit_logs', type_='foreignkey')
    op.drop_constraint(None, 'billings', type_='foreignkey')
    op.drop_constraint(None, 'billings', type_='foreignkey')
    op.drop_constraint(None, 'invitations', type_='foreignkey')
    op.drop_constraint(None, 'invitations', type_='foreignkey')
    op.drop_constraint(None, 'invitations', type_='foreignkey')
    op.drop_constraint(None, 'subscriptions', type_='foreignkey')
    
    # Drop indexes
    op.drop_index(op.f('ix_audit_logs_created_at'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_user_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_resource_type'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_action'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_log_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_id'), table_name='audit_logs')
    
    op.drop_index(op.f('ix_billings_status'), table_name='billings')
    op.drop_index(op.f('ix_billings_subscription_id'), table_name='billings')
    op.drop_index(op.f('ix_billings_user_id'), table_name='billings')
    op.drop_index(op.f('ix_billings_invoice_number'), table_name='billings')
    op.drop_index(op.f('ix_billings_billing_id'), table_name='billings')
    op.drop_index(op.f('ix_billings_id'), table_name='billings')
    
    op.drop_index(op.f('ix_invitations_status'), table_name='invitations')
    op.drop_index(op.f('ix_invitations_invited_by'), table_name='invitations')
    op.drop_index(op.f('ix_invitations_team_id'), table_name='invitations')
    op.drop_index(op.f('ix_invitations_email'), table_name='invitations')
    op.drop_index(op.f('ix_invitations_invitation_id'), table_name='invitations')
    op.drop_index(op.f('ix_invitations_id'), table_name='invitations')
    
    op.drop_index(op.f('ix_subscriptions_status'), table_name='subscriptions')
    op.drop_index(op.f('ix_subscriptions_plan_type'), table_name='subscriptions')
    op.drop_index(op.f('ix_subscriptions_user_id'), table_name='subscriptions')
    op.drop_index(op.f('ix_subscriptions_subscription_id'), table_name='subscriptions')
    op.drop_index(op.f('ix_subscriptions_id'), table_name='subscriptions')
    
    # Drop tables
    op.drop_table('audit_logs')
    op.drop_table('billings')
    op.drop_table('invitations')
    op.drop_table('subscriptions')
