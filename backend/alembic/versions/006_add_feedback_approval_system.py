"""Add feedback approval system

Revision ID: 006_add_feedback_approval_system
Revises: 005_add_additional_models
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006_add_feedback_approval_system'
down_revision = '005_add_additional_models'
branch_labels = None
depends_on = None


def upgrade():
    # 1. 既存のanalysesテーブルに公開制御カラムを追加
    op.add_column('analyses', sa.Column('is_public', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('analyses', sa.Column('visibility_level', sa.String(50), nullable=True, server_default='private'))
    op.add_column('analyses', sa.Column('requires_approval', sa.Boolean(), nullable=True, server_default='true'))
    
    # 2. feedback_approvalsテーブルを作成
    op.create_table('feedback_approvals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('analysis_id', sa.Integer(), nullable=False),
        sa.Column('requester_id', sa.Integer(), nullable=False),
        sa.Column('reviewer_id', sa.Integer(), nullable=True),
        sa.Column('approval_status', sa.Enum('pending', 'under_review', 'approved', 'rejected', 'requires_changes', name='approvalstatus'), nullable=False, server_default='pending'),
        sa.Column('visibility_level', sa.Enum('private', 'team', 'organization', 'public', name='visibilitylevel'), nullable=False, server_default='private'),
        sa.Column('request_reason', sa.Text(), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('is_staged_publication', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('publication_stages', sa.Text(), nullable=True),
        sa.Column('current_stage', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('requires_confirmation', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_confirmed', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('confirmation_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('requested_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 3. インデックスを作成
    op.create_index(op.f('ix_feedback_approvals_analysis_id'), 'feedback_approvals', ['analysis_id'], unique=False)
    op.create_index(op.f('ix_feedback_approvals_requester_id'), 'feedback_approvals', ['requester_id'], unique=False)
    op.create_index(op.f('ix_feedback_approvals_reviewer_id'), 'feedback_approvals', ['reviewer_id'], unique=False)
    op.create_index(op.f('ix_feedback_approvals_approval_status'), 'feedback_approvals', ['approval_status'], unique=False)
    
    # 4. 外部キー制約を追加
    op.create_foreign_key(None, 'feedback_approvals', 'analyses', ['analysis_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'feedback_approvals', 'users', ['requester_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'feedback_approvals', 'users', ['reviewer_id'], ['id'], ondelete='SET NULL')
    
    # 5. 既存のanalysesテーブルのインデックスを更新
    op.create_index(op.f('ix_analyses_is_public'), 'analyses', ['is_public'], unique=False)
    op.create_index(op.f('ix_analyses_visibility_level'), 'analyses', ['visibility_level'], unique=False)
    op.create_index(op.f('ix_analyses_requires_approval'), 'analyses', ['requires_approval'], unique=False)


def downgrade():
    # 1. インデックスを削除
    op.drop_index(op.f('ix_analyses_requires_approval'), table_name='analyses')
    op.drop_index(op.f('ix_analyses_visibility_level'), table_name='analyses')
    op.drop_index(op.f('ix_analyses_is_public'), table_name='analyses')
    
    # 2. feedback_approvalsテーブルを削除
    op.drop_table('feedback_approvals')
    
    # 3. analysesテーブルからカラムを削除
    op.drop_column('analyses', 'requires_approval')
    op.drop_column('analyses', 'visibility_level')
    op.drop_column('analyses', 'is_public')
    
    # 4. 列挙型を削除
    op.execute("DROP TYPE IF EXISTS approvalstatus")
    op.execute("DROP TYPE IF EXISTS visibilitylevel")
