"""Project model."""

from .base import db, TimestampMixin


class Project(db.Model, TimestampMixin):
    """Project model for organizing issues."""
    
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    # Relationships
    owner = db.relationship('User', back_populates='owned_projects', foreign_keys=[owner_id])
    members = db.relationship('ProjectMember', back_populates='project', lazy='dynamic', cascade='all, delete-orphan')
    issues = db.relationship('Issue', back_populates='project', lazy='dynamic', cascade='all, delete-orphan')
    
    # Indexes
    __table_args__ = (
        db.Index('idx_projects_owner', 'owner_id'),
        db.Index('idx_projects_name', 'name'),
    )
    
    def __repr__(self):
        return f'<Project {self.name}>'
    
    def to_dict(self, include_owner: bool = True):
        """Convert project to dictionary."""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'owner_id': self.owner_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_owner and self.owner:
            data['owner'] = self.owner.to_dict()
        return data
