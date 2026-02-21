"""Comment model."""

from .base import db, TimestampMixin


class Comment(db.Model, TimestampMixin):
    """Comment model for issue discussions."""
    
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issues.id', ondelete='CASCADE'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    content = db.Column(db.Text, nullable=False)
    
    # Relationships
    issue = db.relationship('Issue', back_populates='comments')
    author = db.relationship('User', back_populates='comments')
    
    # Indexes
    __table_args__ = (
        db.Index('idx_comments_issue', 'issue_id'),
        db.Index('idx_comments_author', 'author_id'),
        db.Index('idx_comments_created', 'created_at'),
    )
    
    def __repr__(self):
        return f'<Comment {self.id} on Issue {self.issue_id}>'
    
    def to_dict(self, include_author: bool = True):
        """Convert comment to dictionary."""
        data = {
            'id': self.id,
            'issue_id': self.issue_id,
            'author_id': self.author_id,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_author and self.author:
            data['author'] = self.author.to_dict()
        
        return data
