"""Add privacy tables

Revision ID: 004_add_privacy_tables
Revises: 003_add_team_dynamics
Create Date: 2025-08-15 05:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004_add_privacy_tables'
down_revision = '003_add_team_dynamics'
branch_labels = None
depends_on = None


def upgrade():
    # Create encrypted_data table
    op.create_table('encrypted_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('data_id', sa.String(length=255), nullable=False),
        sa.Column('data_type', sa.String(length=100), nullable=False),
        sa.Column('data_category', sa.String(length=50), nullable=False),
        sa.Column('encrypted_content', sa.Text(), nullable=False),
        sa.Column('encryption_algorithm', sa.String(length=50), nullable=False),
        sa.Column('encryption_key_id', sa.String(length=255), nullable=False),
        sa.Column('iv', sa.String(length=255), nullable=False),
        sa.Column('original_size', sa.Integer(), nullable=True),
        sa.Column('compression_ratio', sa.Integer(), nullable=True),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('privacy_level', sa.String(length=50), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create data_access_permissions table
    op.create_table('data_access_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('encrypted_data_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('access_level', sa.String(length=50), nullable=False),
        sa.Column('can_read', sa.Boolean(), nullable=True),
        sa.Column('can_write', sa.Boolean(), nullable=True),
        sa.Column('can_delete', sa.Boolean(), nullable=True),
        sa.Column('can_share', sa.Boolean(), nullable=True),
        sa.Column('granted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('granted_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create privacy_settings table
    op.create_table('privacy_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('default_profile_privacy', sa.String(length=50), nullable=True),
        sa.Column('default_analysis_privacy', sa.String(length=50), nullable=True),
        sa.Column('default_goals_privacy', sa.String(length=50), nullable=True),
        sa.Column('default_improvement_privacy', sa.String(length=50), nullable=True),
        sa.Column('auto_delete_after_days', sa.Integer(), nullable=True),
        sa.Column('auto_delete_enabled', sa.Boolean(), nullable=True),
        sa.Column('allow_team_sharing', sa.Boolean(), nullable=True),
        sa.Column('allow_manager_access', sa.Boolean(), nullable=True),
        sa.Column('allow_anonymous_analytics', sa.Boolean(), nullable=True),
        sa.Column('notify_on_access', sa.Boolean(), nullable=True),
        sa.Column('notify_on_breach', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create data_retention_policies table
    op.create_table('data_retention_policies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('data_category', sa.String(length=50), nullable=False),
        sa.Column('user_role', sa.String(length=50), nullable=True),
        sa.Column('retention_days', sa.Integer(), nullable=False),
        sa.Column('deletion_action', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create privacy_audit_logs table
    op.create_table('privacy_audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('data_id', sa.String(length=255), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('action_details', sa.JSON(), nullable=True),
        sa.Column('accessed_by', sa.Integer(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_encrypted_data_id'), 'encrypted_data', ['id'], unique=False)
    op.create_index(op.f('ix_encrypted_data_data_id'), 'encrypted_data', ['data_id'], unique=True)
    op.create_index(op.f('ix_encrypted_data_owner_id'), 'encrypted_data', ['owner_id'], unique=False)
    op.create_index(op.f('ix_encrypted_data_data_category'), 'encrypted_data', ['data_category'], unique=False)
    
    op.create_index(op.f('ix_data_access_permissions_id'), 'data_access_permissions', ['id'], unique=False)
    op.create_index(op.f('ix_data_access_permissions_encrypted_data_id'), 'data_access_permissions', ['encrypted_data_id'], unique=False)
    op.create_index(op.f('ix_data_access_permissions_user_id'), 'data_access_permissions', ['user_id'], unique=False)
    
    op.create_index(op.f('ix_privacy_settings_id'), 'privacy_settings', ['id'], unique=False)
    op.create_index(op.f('ix_privacy_settings_user_id'), 'privacy_settings', ['user_id'], unique=True)
    
    op.create_index(op.f('ix_data_retention_policies_id'), 'data_retention_policies', ['id'], unique=False)
    op.create_index(op.f('ix_data_retention_policies_data_category'), 'data_retention_policies', ['data_category'], unique=False)
    
    op.create_index(op.f('ix_privacy_audit_logs_id'), 'privacy_audit_logs', ['id'], unique=False)
    op.create_index(op.f('ix_privacy_audit_logs_user_id'), 'privacy_audit_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_privacy_audit_logs_timestamp'), 'privacy_audit_logs', ['timestamp'], unique=False)
    
    # Create foreign key constraints
    op.create_foreign_key(None, 'encrypted_data', 'users', ['owner_id'], ['id'])
    op.create_foreign_key(None, 'data_access_permissions', 'encrypted_data', ['encrypted_data_id'], ['id'])
    op.create_foreign_key(None, 'data_access_permissions', 'users', ['user_id'], ['id'])
    op.create_foreign_key(None, 'data_access_permissions', 'users', ['granted_by'], ['id'])
    op.create_foreign_key(None, 'privacy_settings', 'users', ['user_id'], ['id'])
    op.create_foreign_key(None, 'privacy_audit_logs', 'users', ['user_id'], ['id'])
    op.create_foreign_key(None, 'privacy_audit_logs', 'users', ['accessed_by'], ['id'])


def downgrade():
    # Drop foreign key constraints
    op.drop_constraint(None, 'privacy_audit_logs', type_='foreignkey')
    op.drop_constraint(None, 'privacy_audit_logs', type_='foreignkey')
    op.drop_constraint(None, 'privacy_settings', type_='foreignkey')
    op.drop_constraint(None, 'data_access_permissions', type_='foreignkey')
    op.drop_constraint(None, 'data_access_permissions', type_='foreignkey')
    op.drop_constraint(None, 'data_access_permissions', type_='foreignkey')
    op.drop_constraint(None, 'encrypted_data', type_='foreignkey')
    
    # Drop indexes
    op.drop_index(op.f('ix_privacy_audit_logs_timestamp'), table_name='privacy_audit_logs')
    op.drop_index(op.f('ix_privacy_audit_logs_user_id'), table_name='privacy_audit_logs')
    op.drop_index(op.f('ix_privacy_audit_logs_id'), table_name='privacy_audit_logs')
    op.drop_index(op.f('ix_data_retention_policies_data_category'), table_name='data_retention_policies')
    op.drop_index(op.f('ix_data_retention_policies_id'), table_name='data_retention_policies')
    op.drop_index(op.f('ix_privacy_settings_user_id'), table_name='privacy_settings')
    op.drop_index(op.f('ix_privacy_settings_id'), table_name='privacy_settings')
    op.drop_index(op.f('ix_data_access_permissions_user_id'), table_name='data_access_permissions')
    op.drop_index(op.f('ix_data_access_permissions_encrypted_data_id'), table_name='data_access_permissions')
    op.drop_index(op.f('ix_data_access_permissions_id'), table_name='data_access_permissions')
    op.drop_index(op.f('ix_encrypted_data_data_category'), table_name='encrypted_data')
    op.drop_index(op.f('ix_encrypted_data_owner_id'), table_name='encrypted_data')
    op.drop_index(op.f('ix_encrypted_data_data_id'), table_name='encrypted_data')
    op.drop_index(op.f('ix_encrypted_data_id'), table_name='encrypted_data')
    
    # Drop tables
    op.drop_table('privacy_audit_logs')
    op.drop_table('data_retention_policies')
    op.drop_table('privacy_settings')
    op.drop_table('data_access_permissions')
    op.drop_table('encrypted_data')
    
    # No enum types to drop
    pass
