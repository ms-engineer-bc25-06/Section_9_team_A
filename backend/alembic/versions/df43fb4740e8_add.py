"""add

Revision ID: df43fb4740e8
Revises: 14002dbad3b6
Create Date: 2025-08-14 12:41:35.383329

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'df43fb4740e8'
down_revision = '14002dbad3b6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Postgres想定：既にあればスキップ
    op.execute("ALTER TABLE teams ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT FALSE")
    op.execute("ALTER TABLE teams ADD COLUMN IF NOT EXISTS max_members INTEGER DEFAULT 10")

def downgrade() -> None:
    op.execute("ALTER TABLE teams DROP COLUMN IF EXISTS is_public")
    op.execute("ALTER TABLE teams DROP COLUMN IF EXISTS max_members")
