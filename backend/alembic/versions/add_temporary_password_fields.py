"""add temporary password fields

Revision ID: add_temporary_password_fields
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_temporary_password_fields'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 仮パスワード管理フィールドを追加
    op.add_column('users', sa.Column('has_temporary_password', sa.Boolean(), nullable=True, server_default='true'))
    op.add_column('users', sa.Column('temporary_password_expires_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('is_first_login', sa.Boolean(), nullable=True, server_default='true'))
    op.add_column('users', sa.Column('last_password_change_at', sa.DateTime(timezone=True), nullable=True))
    
    # 既存のユーザーに対してデフォルト値を設定
    op.execute("UPDATE users SET has_temporary_password = false, is_first_login = false WHERE firebase_uid IS NOT NULL")


def downgrade():
    # 追加したフィールドを削除
    op.drop_column('users', 'last_password_change_at')
    op.drop_column('users', 'is_first_login')
    op.drop_column('users', 'temporary_password_expires_at')
    op.drop_column('users', 'has_temporary_password')
