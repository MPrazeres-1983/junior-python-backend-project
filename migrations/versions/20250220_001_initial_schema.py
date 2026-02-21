"""Initial schema with all models

Revision ID: 001_initial
Revises: 
Create Date: 2025-02-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint("role IN ('admin', 'developer', 'viewer')", name='check_user_role'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)

    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_projects_name', 'projects', ['name'], unique=False)
    op.create_index('idx_projects_owner', 'projects', ['owner_id'], unique=False)

    # Create labels table
    op.create_table(
        'labels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_labels_name', 'labels', ['name'], unique=True)

    # Create issues table
    op.create_table(
        'issues',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False),
        sa.Column('reporter_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint("status IN ('open', 'in_progress', 'resolved', 'closed')", name='check_issue_status'),
        sa.CheckConstraint("priority IN ('low', 'medium', 'high', 'critical')", name='check_issue_priority'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reporter_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_issues_priority', 'issues', ['priority'], unique=False)
    op.create_index('idx_issues_project', 'issues', ['project_id'], unique=False)
    op.create_index('idx_issues_reporter', 'issues', ['reporter_id'], unique=False)
    op.create_index('idx_issues_status', 'issues', ['status'], unique=False)

    # Create project_members table (association)
    op.create_table(
        'project_members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('joined_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id', 'user_id', name='unique_project_member')
    )
    op.create_index('idx_project_members_project', 'project_members', ['project_id'], unique=False)
    op.create_index('idx_project_members_user', 'project_members', ['user_id'], unique=False)

    # Create assignments table (association)
    op.create_table(
        'assignments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('issue_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('assigned_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['issue_id'], ['issues.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('issue_id', 'user_id', name='unique_assignment')
    )
    op.create_index('idx_assignments_issue', 'assignments', ['issue_id'], unique=False)
    op.create_index('idx_assignments_user', 'assignments', ['user_id'], unique=False)

    # Create comments table
    op.create_table(
        'comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('issue_id', sa.Integer(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['issue_id'], ['issues.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_comments_author', 'comments', ['author_id'], unique=False)
    op.create_index('idx_comments_created', 'comments', ['created_at'], unique=False)
    op.create_index('idx_comments_issue', 'comments', ['issue_id'], unique=False)

    # Create issue_labels table (association)
    op.create_table(
        'issue_labels',
        sa.Column('issue_id', sa.Integer(), nullable=False),
        sa.Column('label_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['issue_id'], ['issues.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['label_id'], ['labels.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('issue_id', 'label_id')
    )


def downgrade():
    op.drop_table('issue_labels')
    op.drop_index('idx_comments_issue', table_name='comments')
    op.drop_index('idx_comments_created', table_name='comments')
    op.drop_index('idx_comments_author', table_name='comments')
    op.drop_table('comments')
    op.drop_index('idx_assignments_user', table_name='assignments')
    op.drop_index('idx_assignments_issue', table_name='assignments')
    op.drop_table('assignments')
    op.drop_index('idx_project_members_user', table_name='project_members')
    op.drop_index('idx_project_members_project', table_name='project_members')
    op.drop_table('project_members')
    op.drop_index('idx_issues_status', table_name='issues')
    op.drop_index('idx_issues_reporter', table_name='issues')
    op.drop_index('idx_issues_project', table_name='issues')
    op.drop_index('idx_issues_priority', table_name='issues')
    op.drop_table('issues')
    op.drop_index('ix_labels_name', table_name='labels')
    op.drop_table('labels')
    op.drop_index('idx_projects_owner', table_name='projects')
    op.drop_index('idx_projects_name', table_name='projects')
    op.drop_table('projects')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
