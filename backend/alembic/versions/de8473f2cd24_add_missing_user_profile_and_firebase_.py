"""add_missing_user_profile_and_firebase_fields

Revision ID: de8473f2cd24
Revises: 006_add_feedback_approval_system
Create Date: 2025-08-20 05:09:08.074642

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'de8473f2cd24'
down_revision = '006_add_feedback_approval_system'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # usersテーブルに不足しているプロフィール項目を追加
    op.add_column('users', sa.Column('nickname', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('department', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('join_date', sa.Date(), nullable=True))
    op.add_column('users', sa.Column('birth_date', sa.Date(), nullable=True))
    op.add_column('users', sa.Column('hometown', sa.String(length=200), nullable=True))
    op.add_column('users', sa.Column('residence', sa.String(length=200), nullable=True))
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
    
    # Firebase認証関連のカラムを追加
    op.add_column('users', sa.Column('firebase_uid', sa.String(length=128), nullable=True))
    op.add_column('users', sa.Column('hashed_password', sa.String(length=255), nullable=True))
    
    # アカウント状態関連のカラムを追加
    op.add_column('users', sa.Column('is_premium', sa.Boolean(), default=False, nullable=True))
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), default=False, nullable=True))
    
    # サブスクリプション関連のカラムを追加
    op.add_column('users', sa.Column('subscription_status', sa.String(length=50), default='free', nullable=True))
    op.add_column('users', sa.Column('subscription_end_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('monthly_voice_minutes', sa.Integer(), default=0, nullable=True))
    op.add_column('users', sa.Column('monthly_analysis_count', sa.Integer(), default=0, nullable=True))
    op.add_column('users', sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True))
    
    # インデックスを追加
    op.create_index('ix_users_firebase_uid', 'users', ['firebase_uid'])
    op.create_index('ix_users_subscription_status', 'users', ['subscription_status'])


def downgrade() -> None:
    # インデックスを削除
    op.drop_index('ix_users_subscription_status', 'users')
    op.drop_index('ix_users_firebase_uid', 'users')
    
    # サブスクリプション関連のカラムを削除
    op.drop_column('users', 'last_login_at')
    op.drop_column('users', 'monthly_analysis_count')
    op.drop_column('users', 'monthly_voice_minutes')
    op.drop_column('users', 'subscription_end_date')
    op.drop_column('users', 'subscription_status')
    
    # アカウント状態関連のカラムを削除
    op.drop_column('users', 'is_admin')
    op.drop_column('users', 'is_premium')
    
    # Firebase認証関連のカラムを削除
    op.drop_column('users', 'hashed_password')
    op.drop_column('users', 'firebase_uid')
    
    # プロフィール項目のカラムを削除
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
