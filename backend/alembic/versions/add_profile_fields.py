"""Add profile fields to users table

Revision ID: add_profile_fields
Revises: a1b2c3d4e5f6
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_profile_fields'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # プロフィール項目を追加
    op.add_column('users', sa.Column('nickname', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('department', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('join_date', sa.Date(), nullable=True))
    op.add_column('users', sa.Column('birth_date', sa.Date(), nullable=True))
    op.add_column('users', sa.Column('hometown', sa.String(200), nullable=True))
    op.add_column('users', sa.Column('residence', sa.String(200), nullable=True))
    op.add_column('users', sa.Column('hobbies', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('student_activities', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('holiday_activities', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('favorite_food', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('favorite_media', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('favorite_music', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('pets_oshi', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('respected_person', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('motto', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('future_goals', sa.Text(), nullable=True))


def downgrade() -> None:
    # プロフィール項目を削除
    op.drop_column('users', 'future_goals')
    op.drop_column('users', 'motto')
    op.drop_column('users', 'respected_person')
    op.drop_column('users', 'pets_oshi')
    op.drop_column('users', 'favorite_music')
    op.drop_column('users', 'favorite_media')
    op.drop_column('users', 'favorite_food')
    op.drop_column('users', 'holiday_activities')
    op.drop_column('users', 'student_activities')
    op.drop_column('users', 'hobbies')
    op.drop_column('users', 'residence')
    op.drop_column('users', 'hometown')
    op.drop_column('users', 'birth_date')
    op.drop_column('users', 'join_date')
    op.drop_column('users', 'department')
    op.drop_column('users', 'nickname')

