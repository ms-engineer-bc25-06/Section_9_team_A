"""Add chat rooms tables

Revision ID: 002_add_chat_rooms
Revises: 001_initial_schema
Create Date: 2025-08-15 03:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_chat_rooms'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    # Create chat_rooms table
    op.create_table('chat_rooms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('max_participants', sa.Integer(), nullable=True),
        sa.Column('current_participants', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('room_type', sa.String(length=50), nullable=True),
        sa.Column('participants', sa.JSON(), nullable=True),
        sa.Column('moderators', sa.JSON(), nullable=True),
        sa.Column('total_messages', sa.Integer(), nullable=True),
        sa.Column('total_duration', sa.Integer(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create chat_messages table
    op.create_table('chat_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('message_id', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('message_type', sa.String(length=50), nullable=True),
        sa.Column('audio_file_path', sa.String(length=500), nullable=True),
        sa.Column('audio_duration', sa.Integer(), nullable=True),
        sa.Column('transcription', sa.Text(), nullable=True),
        sa.Column('is_edited', sa.Boolean(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('chat_room_id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create chat_room_participants table
    op.create_table('chat_room_participants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('chat_room_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('is_online', sa.Boolean(), nullable=True),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_active_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('total_messages', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_chat_rooms_id'), 'chat_rooms', ['id'], unique=False)
    op.create_index(op.f('ix_chat_rooms_room_id'), 'chat_rooms', ['room_id'], unique=True)
    op.create_index(op.f('ix_chat_messages_id'), 'chat_messages', ['id'], unique=False)
    op.create_index(op.f('ix_chat_messages_message_id'), 'chat_messages', ['message_id'], unique=True)
    op.create_index(op.f('ix_chat_room_participants_id'), 'chat_room_participants', ['id'], unique=False)
    
    # Create foreign key constraints
    op.create_foreign_key(None, 'chat_rooms', 'users', ['created_by'], ['id'])
    op.create_foreign_key(None, 'chat_rooms', 'teams', ['team_id'], ['id'])
    op.create_foreign_key(None, 'chat_messages', 'chat_rooms', ['chat_room_id'], ['id'])
    op.create_foreign_key(None, 'chat_messages', 'users', ['sender_id'], ['id'])
    op.create_foreign_key(None, 'chat_room_participants', 'chat_rooms', ['chat_room_id'], ['id'])
    op.create_foreign_key(None, 'chat_room_participants', 'users', ['user_id'], ['id'])


def downgrade():
    # Drop foreign key constraints
    op.drop_constraint(None, 'chat_room_participants', type_='foreignkey')
    op.drop_constraint(None, 'chat_room_participants', type_='foreignkey')
    op.drop_constraint(None, 'chat_messages', type_='foreignkey')
    op.drop_constraint(None, 'chat_messages', type_='foreignkey')
    op.drop_constraint(None, 'chat_rooms', type_='foreignkey')
    op.drop_constraint(None, 'chat_rooms', type_='foreignkey')
    
    # Drop indexes
    op.drop_index(op.f('ix_chat_room_participants_id'), table_name='chat_room_participants')
    op.drop_index(op.f('ix_chat_messages_message_id'), table_name='chat_messages')
    op.drop_index(op.f('ix_chat_messages_id'), table_name='chat_messages')
    op.drop_index(op.f('ix_chat_rooms_room_id'), table_name='chat_rooms')
    op.drop_index(op.f('ix_chat_rooms_id'), table_name='chat_rooms')
    
    # Drop tables
    op.drop_table('chat_room_participants')
    op.drop_table('chat_messages')
    op.drop_table('chat_rooms')
