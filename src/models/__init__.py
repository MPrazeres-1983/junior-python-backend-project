"""Models package - SQLAlchemy models for the application."""

from .base import db
from .user import User
from .project import Project
from .issue import Issue
from .label import Label
from .comment import Comment
from .associations import ProjectMember, Assignment, issue_labels

# Setup relationships that need to be imported after all models are defined
# This ensures circular imports don't cause issues

# Add relationship to ProjectMember
ProjectMember.project = db.relationship('Project', back_populates='members')
ProjectMember.user = db.relationship('User', back_populates='project_memberships')

# Add relationship to Assignment
Assignment.issue = db.relationship('Issue', back_populates='assignments')
Assignment.user = db.relationship('User', back_populates='assignments')

__all__ = [
    'db',
    'User',
    'Project',
    'Issue',
    'Label',
    'Comment',
    'ProjectMember',
    'Assignment',
    'issue_labels',
]
