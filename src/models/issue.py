"""Issue model."""

from .base import db, TimestampMixin
from .associations import issue_labels


class Issue(db.Model, TimestampMixin):
    """Issue model for tracking work items."""
    
    __tablename__ = 'issues'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='open')  # open, in_progress, resolved, closed
    priority = db.Column(db.String(20), nullable=False, default='medium')  # low, medium, high, critical
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    
    # Relationships
    project = db.relationship('Project', back_populates='issues')
    reporter = db.relationship('User', back_populates='reported_issues', foreign_keys=[reporter_id])
    assignments = db.relationship('Assignment', back_populates='issue', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', back_populates='issue', lazy='dynamic', cascade='all, delete-orphan', order_by='Comment.created_at')
    labels = db.relationship('Label', secondary=issue_labels, back_populates='issues', lazy='dynamic')
    
    # Constraints and indexes
    __table_args__ = (
        db.CheckConstraint("status IN ('open', 'in_progress', 'resolved', 'closed')", name='check_issue_status'),
        db.CheckConstraint("priority IN ('low', 'medium', 'high', 'critical')", name='check_issue_priority'),
        db.Index('idx_issues_project', 'project_id'),
        db.Index('idx_issues_status', 'status'),
        db.Index('idx_issues_priority', 'priority'),
        db.Index('idx_issues_reporter', 'reporter_id'),
    )
    
    def __repr__(self):
        return f'<Issue {self.id}: {self.title}>'
    
    def to_dict(self, include_relations: bool = False):
        """Convert issue to dictionary."""
        data = {
            'id': self.id,
            'project_id': self.project_id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'reporter_id': self.reporter_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_relations:
            if self.reporter:
                data['reporter'] = self.reporter.to_dict()
            data['assignees'] = [assignment.user.to_dict() for assignment in self.assignments]
            data['labels'] = [label.to_dict() for label in self.labels]
            data['comment_count'] = self.comments.count()
        
        return data
