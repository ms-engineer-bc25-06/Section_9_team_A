"""add

Revision ID: 14002dbad3b6
Revises: ee081fb7b2a9
Create Date: 2025-08-14 11:54:12.257768

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '14002dbad3b6'
down_revision = 'ee081fb7b2a9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 既に列があれば何もしない（Postgres）
    op.execute('ALTER TABLE teams ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(500)')

def downgrade() -> None:
    op.execute('ALTER TABLE teams DROP COLUMN IF EXISTS avatar_url')