"""Label model."""

from .base import db, TimestampMixin
from .associations import issue_labels


class Label(db.Model, TimestampMixin):
    """Label model for categorizing issues."""
    
    __tablename__ = 'labels'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    color = db.Column(db.String(7), nullable=False, default='#808080')  # Hex color code
    
    # Relationships
    issues = db.relationship('Issue', secondary=issue_labels, back_populates='labels', lazy='dynamic')
    
    def __repr__(self):
        return f'<Label {self.name}>'
    
    def to_dict(self):
        """Convert label to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
