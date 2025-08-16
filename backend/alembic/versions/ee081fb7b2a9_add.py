"""add

Revision ID: ee081fb7b2a9
Revises: 63d85a506193
Create Date: 2025-08-14 11:40:04.418932

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ee081fb7b2a9'
down_revision = '63d85a506193'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'teams',
        sa.Column('avatar_url', sa.String(length=500), nullable=True)
    )

def downgrade() -> None:
    op.drop_column('teams', 'avatar_url')

