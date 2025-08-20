"""merge billing and feedback approval heads

Revision ID: 2540054e60a6
Revises: 007_consolidate_team_to_organization, create_billing_tables
Create Date: 2025-08-20 04:40:47.780694

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2540054e60a6'
down_revision = ('007_consolidate_team_to_organization', 'create_billing_tables')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
