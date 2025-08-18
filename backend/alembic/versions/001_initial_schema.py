"""Initial schema with all tables

Revision ID: 001_initial_schema
Revises: 
Create Date: 2025-08-15 03:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # Create teams table
    op.create_table('teams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False),
        sa.Column('max_members', sa.Integer(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_teams_id'), 'teams', ['id'], unique=False)
    op.create_index(op.f('ix_teams_name'), 'teams', ['name'], unique=False)
    
    # Create team_members table
    op.create_table('team_members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_team_members_id'), 'team_members', ['id'], unique=False)
    
    # Create voice_sessions table
    op.create_table('voice_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('audio_file_path', sa.String(length=500), nullable=True),
        sa.Column('audio_duration', sa.Float(), nullable=True),
        sa.Column('audio_format', sa.String(length=50), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('is_analyzed', sa.Boolean(), nullable=True),
        sa.Column('participant_count', sa.Integer(), nullable=True),
        sa.Column('participants', sa.Text(), nullable=True),
        sa.Column('analysis_summary', sa.Text(), nullable=True),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('key_topics', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_voice_sessions_id'), 'voice_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_voice_sessions_session_id'), 'voice_sessions', ['session_id'], unique=True)
    
    # Create roles table
    op.create_table('roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_roles_id'), 'roles', ['id'], unique=False)
    op.create_index(op.f('ix_roles_name'), 'roles', ['name'], unique=True)
    
    # Create user_roles table
    op.create_table('user_roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('assigned_by', sa.Integer(), nullable=True),
        sa.Column('assigned_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_roles_id'), 'user_roles', ['id'], unique=False)
    
    # Create transcriptions table
    op.create_table('transcriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('transcription_id', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=True),
        sa.Column('audio_file_path', sa.String(length=500), nullable=True),
        sa.Column('audio_duration', sa.Float(), nullable=True),
        sa.Column('audio_format', sa.String(length=50), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('speaker_count', sa.Integer(), nullable=True),
        sa.Column('speakers', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('is_edited', sa.Boolean(), nullable=True),
        sa.Column('voice_session_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transcriptions_id'), 'transcriptions', ['id'], unique=False)
    op.create_index(op.f('ix_transcriptions_transcription_id'), 'transcriptions', ['transcription_id'], unique=True)
    
    # Create analyses table
    op.create_table('analyses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('analysis_id', sa.String(length=255), nullable=False),
        sa.Column('analysis_type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('keywords', sa.Text(), nullable=True),
        sa.Column('topics', sa.Text(), nullable=True),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('sentiment_label', sa.String(length=50), nullable=True),
        sa.Column('word_count', sa.Integer(), nullable=True),
        sa.Column('sentence_count', sa.Integer(), nullable=True),
        sa.Column('speaking_time', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('voice_session_id', sa.Integer(), nullable=True),
        sa.Column('transcription_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_analyses_id'), 'analyses', ['id'], unique=False)
    op.create_index(op.f('ix_analyses_analysis_id'), 'analyses', ['analysis_id'], unique=True)
    op.create_index(op.f('ix_analyses_analysis_type'), 'analyses', ['analysis_type'], unique=False)
    op.create_index(op.f('ix_analyses_user_id'), 'analyses', ['user_id'], unique=False)
    op.create_index(op.f('ix_analyses_voice_session_id'), 'analyses', ['voice_session_id'], unique=False)
    op.create_index(op.f('ix_analyses_transcription_id'), 'analyses', ['transcription_id'], unique=False)
    
    # Create foreign key constraints
    op.create_foreign_key(None, 'teams', 'users', ['owner_id'], ['id'])
    op.create_foreign_key(None, 'team_members', 'teams', ['team_id'], ['id'])
    op.create_foreign_key(None, 'team_members', 'users', ['user_id'], ['id'])
    op.create_foreign_key(None, 'voice_sessions', 'users', ['user_id'], ['id'])
    op.create_foreign_key(None, 'voice_sessions', 'teams', ['team_id'], ['id'])
    op.create_foreign_key(None, 'user_roles', 'users', ['user_id'], ['id'])
    op.create_foreign_key(None, 'user_roles', 'roles', ['role_id'], ['id'])
    op.create_foreign_key(None, 'user_roles', 'users', ['assigned_by'], ['id'])
    op.create_foreign_key(None, 'transcriptions', 'voice_sessions', ['voice_session_id'], ['id'])
    op.create_foreign_key(None, 'transcriptions', 'users', ['user_id'], ['id'])
    op.create_foreign_key(None, 'analyses', 'voice_sessions', ['voice_session_id'], ['id'])
    op.create_foreign_key(None, 'analyses', 'transcriptions', ['transcription_id'], ['id'])
    op.create_foreign_key(None, 'analyses', 'users', ['user_id'], ['id'])
    
    # Insert default roles
    op.execute("""
        INSERT INTO roles (name, display_name, description, is_active) VALUES
        ('admin', '管理者', 'システム管理者', true),
        ('user', '一般ユーザー', '一般ユーザー', true)
    """)


def downgrade():
    # Drop foreign key constraints
    op.drop_constraint(None, 'analyses', type_='foreignkey')
    op.drop_constraint(None, 'analyses', type_='foreignkey')
    op.drop_constraint(None, 'analyses', type_='foreignkey')
    op.drop_constraint(None, 'transcriptions', type_='foreignkey')
    op.drop_constraint(None, 'transcriptions', type_='foreignkey')
    op.drop_constraint(None, 'user_roles', type_='foreignkey')
    op.drop_constraint(None, 'user_roles', type_='foreignkey')
    op.drop_constraint(None, 'user_roles', type_='foreignkey')
    op.drop_constraint(None, 'voice_sessions', type_='foreignkey')
    op.drop_constraint(None, 'voice_sessions', type_='foreignkey')
    op.drop_constraint(None, 'team_members', type_='foreignkey')
    op.drop_constraint(None, 'team_members', type_='foreignkey')
    op.drop_constraint(None, 'teams', type_='foreignkey')
    
    # Drop tables
    op.drop_table('analyses')
    op.drop_table('transcriptions')
    op.drop_table('user_roles')
    op.drop_table('roles')
    op.drop_table('voice_sessions')
    op.drop_table('team_members')
    op.drop_table('teams')
    op.drop_table('users')
