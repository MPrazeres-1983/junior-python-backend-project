"""User model."""

from .base import db, TimestampMixin


class User(db.Model, TimestampMixin):
    """User model for authentication and authorization."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='developer')  # admin, developer, viewer
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    # Relationships
    owned_projects = db.relationship('Project', back_populates='owner', lazy='dynamic', foreign_keys='Project.owner_id')
    project_memberships = db.relationship('ProjectMember', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    reported_issues = db.relationship('Issue', back_populates='reporter', lazy='dynamic', foreign_keys='Issue.reporter_id')
    assignments = db.relationship('Assignment', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', back_populates='author', lazy='dynamic', cascade='all, delete-orphan')
    
    # Constraints
    __table_args__ = (
        db.CheckConstraint("role IN ('admin', 'developer', 'viewer')", name='check_user_role'),
    )
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self, include_email: bool = False):
        """Convert user to dictionary."""
        data = {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_email:
            data['email'] = self.email
        return data
