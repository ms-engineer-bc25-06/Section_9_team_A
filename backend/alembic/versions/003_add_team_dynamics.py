"""Add team dynamics tables

Revision ID: 003_add_team_dynamics
Revises: 002_add_chat_rooms
Create Date: 2025-08-15 04:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003_add_team_dynamics'
down_revision = '002_add_chat_rooms'
branch_labels = None
depends_on = None


def upgrade():
    # Create team_interactions table
    op.create_table('team_interactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('speaker_id', sa.Integer(), nullable=False),
        sa.Column('listener_id', sa.Integer(), nullable=False),
        sa.Column('interaction_type', sa.String(length=50), nullable=False),
        sa.Column('interaction_strength', sa.Float(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('duration', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create team_compatibilities table
    op.create_table('team_compatibilities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('member1_id', sa.Integer(), nullable=False),
        sa.Column('member2_id', sa.Integer(), nullable=False),
        sa.Column('communication_style_score', sa.Float(), nullable=True),
        sa.Column('personality_compatibility', sa.Float(), nullable=True),
        sa.Column('work_style_score', sa.Float(), nullable=True),
        sa.Column('overall_compatibility', sa.Float(), nullable=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create team_cohesions table
    op.create_table('team_cohesions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('cohesion_score', sa.Float(), nullable=True),
        sa.Column('common_topics', sa.JSON(), nullable=True),
        sa.Column('opinion_alignment', sa.Float(), nullable=True),
        sa.Column('cultural_formation', sa.Float(), nullable=True),
        sa.Column('improvement_suggestions', sa.Text(), nullable=True),
        sa.Column('analysis_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create team_member_profiles table
    op.create_table('team_member_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('communication_style', sa.String(length=50), nullable=True),
        sa.Column('personality_traits', sa.JSON(), nullable=True),
        sa.Column('work_preferences', sa.JSON(), nullable=True),
        sa.Column('interaction_patterns', sa.JSON(), nullable=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_team_interactions_id'), 'team_interactions', ['id'], unique=False)
    op.create_index(op.f('ix_team_interactions_team_id'), 'team_interactions', ['team_id'], unique=False)
    op.create_index(op.f('ix_team_interactions_session_id'), 'team_interactions', ['session_id'], unique=False)
    op.create_index(op.f('ix_team_interactions_speaker_id'), 'team_interactions', ['speaker_id'], unique=False)
    op.create_index(op.f('ix_team_interactions_listener_id'), 'team_interactions', ['listener_id'], unique=False)
    op.create_index(op.f('ix_team_interactions_interaction_type'), 'team_interactions', ['interaction_type'], unique=False)
    
    op.create_index(op.f('ix_team_compatibilities_id'), 'team_compatibilities', ['id'], unique=False)
    op.create_index(op.f('ix_team_compatibilities_team_id'), 'team_compatibilities', ['team_id'], unique=False)
    op.create_index(op.f('ix_team_compatibilities_member1_id'), 'team_compatibilities', ['member1_id'], unique=False)
    op.create_index(op.f('ix_team_compatibilities_member2_id'), 'team_compatibilities', ['member2_id'], unique=False)
    
    op.create_index(op.f('ix_team_cohesions_id'), 'team_cohesions', ['id'], unique=False)
    op.create_index(op.f('ix_team_cohesions_team_id'), 'team_cohesions', ['team_id'], unique=False)
    op.create_index(op.f('ix_team_cohesions_session_id'), 'team_cohesions', ['session_id'], unique=False)
    
    op.create_index(op.f('ix_team_member_profiles_id'), 'team_member_profiles', ['id'], unique=False)
    op.create_index(op.f('ix_team_member_profiles_user_id'), 'team_member_profiles', ['user_id'], unique=False)
    op.create_index(op.f('ix_team_member_profiles_team_id'), 'team_member_profiles', ['team_id'], unique=False)
    
    # Create foreign key constraints
    op.create_foreign_key(None, 'team_interactions', 'teams', ['team_id'], ['id'])
    op.create_foreign_key(None, 'team_interactions', 'voice_sessions', ['session_id'], ['id'])
    op.create_foreign_key(None, 'team_interactions', 'users', ['speaker_id'], ['id'])
    op.create_foreign_key(None, 'team_interactions', 'users', ['listener_id'], ['id'])
    
    op.create_foreign_key(None, 'team_compatibilities', 'teams', ['team_id'], ['id'])
    op.create_foreign_key(None, 'team_compatibilities', 'users', ['member1_id'], ['id'])
    op.create_foreign_key(None, 'team_compatibilities', 'users', ['member2_id'], ['id'])
    
    op.create_foreign_key(None, 'team_cohesions', 'teams', ['team_id'], ['id'])
    op.create_foreign_key(None, 'team_cohesions', 'voice_sessions', ['session_id'], ['id'])
    
    op.create_foreign_key(None, 'team_member_profiles', 'users', ['user_id'], ['id'])
    op.create_foreign_key(None, 'team_member_profiles', 'teams', ['team_id'], ['id'])


def downgrade():
    # Drop foreign key constraints
    op.drop_constraint(None, 'team_member_profiles', type_='foreignkey')
    op.drop_constraint(None, 'team_member_profiles', type_='foreignkey')
    op.drop_constraint(None, 'team_cohesions', type_='foreignkey')
    op.drop_constraint(None, 'team_cohesions', type_='foreignkey')
    op.drop_constraint(None, 'team_compatibilities', type_='foreignkey')
    op.drop_constraint(None, 'team_compatibilities', type_='foreignkey')
    op.drop_constraint(None, 'team_compatibilities', type_='foreignkey')
    op.drop_constraint(None, 'team_interactions', type_='foreignkey')
    op.drop_constraint(None, 'team_interactions', type_='foreignkey')
    op.drop_constraint(None, 'team_interactions', type_='foreignkey')
    op.drop_constraint(None, 'team_interactions', type_='foreignkey')
    
    # Drop indexes
    op.drop_index(op.f('ix_team_member_profiles_team_id'), table_name='team_member_profiles')
    op.drop_index(op.f('ix_team_member_profiles_user_id'), table_name='team_member_profiles')
    op.drop_index(op.f('ix_team_member_profiles_id'), table_name='team_member_profiles')
    op.drop_index(op.f('ix_team_cohesions_session_id'), table_name='team_cohesions')
    op.drop_index(op.f('ix_team_cohesions_team_id'), table_name='team_cohesions')
    op.drop_index(op.f('ix_team_cohesions_id'), table_name='team_cohesions')
    op.drop_index(op.f('ix_team_compatibilities_member2_id'), table_name='team_compatibilities')
    op.drop_index(op.f('ix_team_compatibilities_member1_id'), table_name='team_compatibilities')
    op.drop_index(op.f('ix_team_compatibilities_team_id'), table_name='team_compatibilities')
    op.drop_index(op.f('ix_team_compatibilities_id'), table_name='team_compatibilities')
    op.drop_index(op.f('ix_team_interactions_interaction_type'), table_name='team_interactions')
    op.drop_index(op.f('ix_team_interactions_listener_id'), table_name='team_interactions')
    op.drop_index(op.f('ix_team_interactions_speaker_id'), table_name='team_interactions')
    op.drop_index(op.f('ix_team_interactions_session_id'), table_name='team_interactions')
    op.drop_index(op.f('ix_team_interactions_team_id'), table_name='team_interactions')
    op.drop_index(op.f('ix_team_interactions_id'), table_name='team_interactions')
    
    # Drop tables
    op.drop_table('team_member_profiles')
    op.drop_table('team_cohesions')
    op.drop_table('team_compatibilities')
    op.drop_table('team_interactions')
