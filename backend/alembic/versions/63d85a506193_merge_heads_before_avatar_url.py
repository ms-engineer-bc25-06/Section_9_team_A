"""merge heads before avatar_url

Revision ID: 63d85a506193
Revises: 003_add_team_dynamics, 005_add_additional_models
Create Date: 2025-08-14 20:24:56.233566

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '63d85a506193'
down_revision = ('003_add_team_dynamics', '005_add_additional_models')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
