"""merge heads

Revision ID: b9dbef7eca8d
Revises: 006_add_feedback_approval_system, create_billing_tables
Create Date: 2025-08-20 19:09:21.244374

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b9dbef7eca8d'
down_revision = ('006_add_feedback_approval_system', 'create_billing_tables')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
