"""Recreate analysis tables

Revision ID: 010_recreate_analysis_tables
Revises: 009_add_temporary_password_fields
Create Date: 2025-08-26 14:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "010_recreate_analysis_tables"
down_revision = "009_add_temporary_password_fields"
branch_labels = None
depends_on = None


def upgrade():
    # 1. analysesテーブルを作成
    op.create_table(
        "analyses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column(
            "analysis_type",
            sa.String(100),
            nullable=False,
            server_default="voice_analysis",
        ),
        sa.Column("status", sa.String(50), nullable=False, server_default="completed"),
        sa.Column("is_public", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column(
            "visibility_level", sa.String(50), nullable=True, server_default="private"
        ),
        sa.Column(
            "requires_approval", sa.Boolean(), nullable=True, server_default="true"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            onupdate=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # 2. analysesテーブルのインデックスを作成
    op.create_index(op.f("ix_analyses_user_id"), "analyses", ["user_id"], unique=False)
    op.create_index(
        op.f("ix_analyses_analysis_type"), "analyses", ["analysis_type"], unique=False
    )
    op.create_index(op.f("ix_analyses_status"), "analyses", ["status"], unique=False)
    op.create_index(
        op.f("ix_analyses_is_public"), "analyses", ["is_public"], unique=False
    )
    op.create_index(
        op.f("ix_analyses_visibility_level"),
        "analyses",
        ["visibility_level"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analyses_requires_approval"),
        "analyses",
        ["requires_approval"],
        unique=False,
    )

    # 3. feedback_approvalsテーブルを作成
    op.create_table(
        "feedback_approvals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("analysis_id", sa.Integer(), nullable=False),
        sa.Column("requester_id", sa.Integer(), nullable=False),
        sa.Column("reviewer_id", sa.Integer(), nullable=True),
        sa.Column(
            "approval_status",
            sa.Enum(
                "pending",
                "under_review",
                "approved",
                "rejected",
                "requires_changes",
                name="approvalstatus",
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "visibility_level",
            sa.Enum(
                "private", "team", "organization", "public", name="visibilitylevel"
            ),
            nullable=False,
            server_default="private",
        ),
        sa.Column("request_reason", sa.Text(), nullable=True),
        sa.Column("review_notes", sa.Text(), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column(
            "is_staged_publication", sa.Boolean(), nullable=True, server_default="false"
        ),
        sa.Column("publication_stages", sa.Text(), nullable=True),
        sa.Column("current_stage", sa.Integer(), nullable=True, server_default="0"),
        sa.Column(
            "requires_confirmation", sa.Boolean(), nullable=True, server_default="true"
        ),
        sa.Column("is_confirmed", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("confirmation_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "requested_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # 4. feedback_approvalsテーブルのインデックスを作成
    op.create_index(
        op.f("ix_feedback_approvals_analysis_id"),
        "feedback_approvals",
        ["analysis_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_feedback_approvals_requester_id"),
        "feedback_approvals",
        ["requester_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_feedback_approvals_reviewer_id"),
        "feedback_approvals",
        ["reviewer_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_feedback_approvals_approval_status"),
        "feedback_approvals",
        ["approval_status"],
        unique=False,
    )

    # 5. 外部キー制約を追加
    op.create_foreign_key(
        None, "analyses", "users", ["user_id"], ["id"], ondelete="CASCADE"
    )
    op.create_foreign_key(
        None,
        "feedback_approvals",
        "analyses",
        ["analysis_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        None,
        "feedback_approvals",
        "users",
        ["requester_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        None,
        "feedback_approvals",
        "users",
        ["reviewer_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade():
    # 1. 外部キー制約を削除
    op.drop_constraint(None, "feedback_approvals", type_="foreignkey")
    op.drop_constraint(None, "feedback_approvals", type_="foreignkey")
    op.drop_constraint(None, "feedback_approvals", type_="foreignkey")
    op.drop_constraint(None, "analyses", type_="foreignkey")

    # 2. feedback_approvalsテーブルを削除
    op.drop_table("feedback_approvals")

    # 3. analysesテーブルを削除
    op.drop_table("analyses")

    # 4. 列挙型を削除
    op.execute("DROP TYPE IF EXISTS approvalstatus")
    op.execute("DROP TYPE IF EXISTS visibilitylevel")
