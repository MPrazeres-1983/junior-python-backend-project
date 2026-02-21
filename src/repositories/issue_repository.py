"""Issue repository with specific queries."""

from typing import List, Optional, Dict, Any
from src.models import Issue, Assignment
from .base import BaseRepository


class IssueRepository(BaseRepository):
    """Repository for Issue model."""
    
    def __init__(self):
        super().__init__(Issue)
    
    def get_by_project(self, project_id: int, limit: Optional[int] = None, offset: int = 0) -> List[Issue]:
        """Get issues by project."""
        query = self.session.query(Issue).filter(Issue.project_id == project_id)
        if limit:
            query = query.limit(limit).offset(offset)
        return query.all()
    
    def get_by_reporter(self, reporter_id: int, limit: Optional[int] = None, offset: int = 0) -> List[Issue]:
        """Get issues by reporter."""
        query = self.session.query(Issue).filter(Issue.reporter_id == reporter_id)
        if limit:
            query = query.limit(limit).offset(offset)
        return query.all()
    
    def get_by_assignee(self, user_id: int, limit: Optional[int] = None, offset: int = 0) -> List[Issue]:
        """Get issues assigned to a user."""
        query = self.session.query(Issue).join(Assignment).filter(
            Assignment.user_id == user_id
        )
        if limit:
            query = query.limit(limit).offset(offset)
        return query.all()
    
    def paginate_with_filters(
        self,
        project_id: int,
        page: int = 1,
        per_page: int = 20,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        reporter_id: Optional[int] = None,
        assignee_id: Optional[int] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Paginate issues with filters."""
        query = self.session.query(Issue).filter(Issue.project_id == project_id)
        
        if status:
            query = query.filter(Issue.status == status)
        
        if priority:
            query = query.filter(Issue.priority == priority)
        
        if reporter_id:
            query = query.filter(Issue.reporter_id == reporter_id)
        
        if assignee_id:
            query = query.join(Assignment).filter(Assignment.user_id == assignee_id)
        
        if search:
            search_pattern = f'%{search}%'
            query = query.filter(
                Issue.title.ilike(search_pattern) | Issue.description.ilike(search_pattern)
            )
        
        query = query.order_by(Issue.created_at.desc())
        
        total = query.count()
        offset = (page - 1) * per_page
        items = query.limit(per_page).offset(offset).all()
        
        return {
            'items': items,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page if total > 0 else 0
        }
    
    def assign_user(self, issue_id: int, user_id: int) -> Assignment:
        """Assign a user to an issue."""
        assignment = Assignment(issue_id=issue_id, user_id=user_id)
        self.session.add(assignment)
        self.session.commit()
        self.session.refresh(assignment)
        return assignment
    
    def unassign_user(self, issue_id: int, user_id: int) -> bool:
        """Unassign a user from an issue."""
        assignment = self.session.query(Assignment).filter_by(
            issue_id=issue_id,
            user_id=user_id
        ).first()
        
        if assignment:
            self.session.delete(assignment)
            self.session.commit()
            return True
        return False
    
    def is_assigned(self, issue_id: int, user_id: int) -> bool:
        """Check if user is assigned to issue."""
        return self.session.query(Assignment).filter_by(
            issue_id=issue_id,
            user_id=user_id
        ).first() is not None
