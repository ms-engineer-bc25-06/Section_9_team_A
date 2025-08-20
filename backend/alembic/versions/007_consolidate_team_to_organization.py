"""Consolidate team models to organization models

Revision ID: 007_consolidate_team_to_organization
Revises: 006_add_feedback_approval_system
Create Date: 2025-08-20 14:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007_consolidate_team_to_organization'
down_revision = '006_add_feedback_approval_system'
branch_labels = None
depends_on = None


def upgrade():
    """Team系からOrganization系への統合"""
    
    # 1. organizationsテーブルの拡張（既存の場合はスキップ）
    try:
        # is_publicカラムの追加
        op.add_column('organizations', sa.Column('is_public', sa.Boolean(), nullable=True, default=False))
        print("✅ organizations.is_publicカラム追加完了")
    except Exception as e:
        print(f"⚠️  organizations.is_publicカラム追加スキップ: {e}")
    
    try:
        # max_membersカラムの追加
        op.add_column('organizations', sa.Column('max_members', sa.Integer(), nullable=True, default=10))
        print("✅ organizations.max_membersカラム追加完了")
    except Exception as e:
        print(f"⚠️  organizations.max_membersカラム追加スキップ: {e}")
    
    try:
        # avatar_urlカラムの追加
        op.add_column('organizations', sa.Column('avatar_url', sa.String(length=500), nullable=True))
        print("✅ organizations.avatar_urlカラム追加完了")
    except Exception as e:
        print(f"⚠️  organizations.avatar_urlカラム追加スキップ: {e}")
    
    try:
        # owner_idカラムの追加
        op.add_column('organizations', sa.Column('owner_id', sa.Integer(), nullable=True))
        print("✅ organizations.owner_idカラム追加完了")
    except Exception as e:
        print(f"⚠️  organizations.owner_idカラム追加スキップ: {e}")
    
    # 2. organization_membersテーブルの拡張
    try:
        # is_activeカラムの追加
        op.add_column('organization_members', sa.Column('is_active', sa.Boolean(), nullable=True, default=True))
        print("✅ organization_members.is_activeカラム追加完了")
    except Exception as e:
        print(f"⚠️  organization_members.is_activeカラム追加スキップ: {e}")
    
    # 3. voice_sessionsテーブルの更新
    try:
        # team_idをorganization_idに変更
        op.alter_column('voice_sessions', 'team_id', new_column_name='organization_id')
        print("✅ voice_sessions.team_id → organization_id変更完了")
    except Exception as e:
        print(f"⚠️  voice_sessions.team_id変更スキップ: {e}")
    
    # 4. chat_roomsテーブルの更新
    try:
        # team_idをorganization_idに変更
        op.alter_column('chat_rooms', 'team_id', new_column_name='organization_id')
        print("✅ chat_rooms.team_id → organization_id変更完了")
    except Exception as e:
        print(f"⚠️  chat_rooms.team_id変更スキップ: {e}")
    
    # 5. 外部キー制約の更新
    try:
        # voice_sessions.organization_idの外部キー制約
        op.create_foreign_key(
            'fk_voice_sessions_organization_id', 'voice_sessions', 'organizations', ['organization_id'], ['id']
        )
        print("✅ voice_sessions.organization_id外部キー制約作成完了")
    except Exception as e:
        print(f"⚠️  voice_sessions.organization_id外部キー制約作成スキップ: {e}")
    
    try:
        # chat_rooms.organization_idの外部キー制約
        op.create_foreign_key(
            'fk_chat_rooms_organization_id', 'chat_rooms', 'organizations', ['organization_id'], ['id']
        )
        print("✅ chat_rooms.organization_id外部キー制約作成完了")
    except Exception as e:
        print(f"⚠️  chat_rooms.organization_id外部キー制約作成スキップ: {e}")
    
    try:
        # organizations.owner_idの外部キー制約
        op.create_foreign_key(
            'fk_organizations_owner_id', 'organizations', 'users', ['owner_id'], ['id']
        )
        print("✅ organizations.owner_id外部キー制約作成完了")
    except Exception as e:
        print(f"⚠️  organizations.owner_id外部キー制約作成スキップ: {e}")


def downgrade():
    """統合の取り消し（Team系に戻す）"""
    
    # 1. 外部キー制約の削除
    try:
        op.drop_constraint('fk_voice_sessions_organization_id', 'voice_sessions', type_='foreignkey')
        print("✅ voice_sessions.organization_id外部キー制約削除完了")
    except Exception as e:
        print(f"⚠️  voice_sessions.organization_id外部キー制約削除スキップ: {e}")
    
    try:
        op.drop_constraint('fk_chat_rooms_organization_id', 'chat_rooms', type_='foreignkey')
        print("✅ chat_rooms.organization_id外部キー制約削除完了")
    except Exception as e:
        print(f"⚠️  chat_rooms.organization_id外部キー制約削除スキップ: {e}")
    
    try:
        op.drop_constraint('fk_organizations_owner_id', 'organizations', type_='foreignkey')
        print("✅ organizations.owner_id外部キー制約削除完了")
    except Exception as e:
        print(f"⚠️  organizations.owner_id外部キー制約削除スキップ: {e}")
    
    # 2. カラム名の戻し
    try:
        op.alter_column('voice_sessions', 'organization_id', new_column_name='team_id')
        print("✅ voice_sessions.organization_id → team_id変更完了")
    except Exception as e:
        print(f"⚠️  voice_sessions.organization_id変更スキップ: {e}")
    
    try:
        op.alter_column('chat_rooms', 'organization_id', new_column_name='team_id')
        print("✅ chat_rooms.organization_id → team_id変更完了")
    except Exception as e:
        print(f"⚠️  chat_rooms.organization_id変更スキップ: {e}")
    
    # 3. 追加したカラムの削除
    try:
        op.drop_column('organizations', 'is_public')
        op.drop_column('organizations', 'max_members')
        op.drop_column('organizations', 'avatar_url')
        op.drop_column('organizations', 'owner_id')
        print("✅ organizations追加カラム削除完了")
    except Exception as e:
        print(f"⚠️  organizations追加カラム削除スキップ: {e}")
    
    try:
        op.drop_column('organization_members', 'is_active')
        print("✅ organization_members追加カラム削除完了")
    except Exception as e:
        print(f"⚠️  organization_members追加カラム削除スキップ: {e}")
