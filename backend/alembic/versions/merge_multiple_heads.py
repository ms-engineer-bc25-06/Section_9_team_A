"""Merge multiple heads

Revision ID: merge_multiple_heads
Revises: add_privacy_models, add_role_tables, simple_migration
Create Date: 2025-08-15 01:35:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'merge_multiple_heads'
down_revision = ('add_privacy_models', 'add_role_tables', 'simple_migration')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
