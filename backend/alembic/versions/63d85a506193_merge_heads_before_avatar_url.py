"""merge heads before avatar_url

Revision ID: 63d85a506193
Revises: 7b8f6314a525, add_team_dynamics_tables
Create Date: 2025-08-14 20:24:56.233566

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '63d85a506193'
down_revision = ('7b8f6314a525', 'add_team_dynamics_tables')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
