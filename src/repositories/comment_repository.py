"""Comment repository with specific queries."""

from typing import List, Optional, Dict, Any
from src.models import Comment
from .base import BaseRepository


class CommentRepository(BaseRepository):
    """Repository for Comment model."""
    
    def __init__(self):
        super().__init__(Comment)
    
    def get_by_issue(self, issue_id: int, limit: Optional[int] = None, offset: int = 0) -> List[Comment]:
        """Get comments by issue, ordered by creation date."""
        query = self.session.query(Comment).filter(
            Comment.issue_id == issue_id
        ).order_by(Comment.created_at.asc())
        
        if limit:
            query = query.limit(limit).offset(offset)
        
        return query.all()
    
    def paginate_by_issue(
        self,
        issue_id: int,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """Paginate comments for an issue."""
        query = self.session.query(Comment).filter(
            Comment.issue_id == issue_id
        ).order_by(Comment.created_at.asc())
        
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
