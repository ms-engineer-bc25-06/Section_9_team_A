"""merge multiple heads

Revision ID: f05fa44445c4
Revises: 7b8f6314a525, add_privacy_models, add_team_dynamics_tables
Create Date: 2025-08-14 11:32:26.837448

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f05fa44445c4'
down_revision = ('7b8f6314a525', 'add_privacy_models', 'add_team_dynamics_tables')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
