"""merge all heads

Revision ID: bdc44edb92b0
Revises: add_temporary_password_fields, b9dbef7eca8d
Create Date: 2025-08-20 19:09:45.045835

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bdc44edb92b0'
down_revision = ('add_temporary_password_fields', 'b9dbef7eca8d')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
