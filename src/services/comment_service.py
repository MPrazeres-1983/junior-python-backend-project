"""Comment service with business logic."""

from typing import Optional, Tuple
from src.models import Comment
from src.repositories import CommentRepository, IssueRepository, ProjectRepository
from src.utils.logger import logger


class CommentService:
    """Service for comment operations."""
    
    def __init__(self):
        self.comment_repo = CommentRepository()
        self.issue_repo = IssueRepository()
        self.project_repo = ProjectRepository()
    
    def create_comment(
        self,
        issue_id: int,
        author_id: int,
        content: str
    ) -> Tuple[Optional[Comment], Optional[str]]:
        """
        Create a new comment.
        
        Args:
            issue_id: Issue ID
            author_id: Author user ID
            content: Comment content
        
        Returns:
            Tuple of (Comment, error_message)
        """
        # Verify issue exists
        issue = self.issue_repo.get_by_id(issue_id)
        if not issue:
            return None, "Issue not found"
        
        # Check if user is member of the project
        if not self.project_repo.is_member(issue.project_id, author_id):
            return None, "User is not a member of the project"
        
        try:
            comment = self.comment_repo.create(
                issue_id=issue_id,
                author_id=author_id,
                content=content
            )
            logger.info(f"Comment created on issue {issue_id} by user {author_id}")
            return comment, None
        except Exception as e:
            logger.error(f"Error creating comment: {str(e)}")
            return None, "Failed to create comment"
    
    def get_comment(self, comment_id: int) -> Optional[Comment]:
        """Get comment by ID."""
        return self.comment_repo.get_by_id(comment_id)
    
    def update_comment(
        self,
        comment_id: int,
        user_id: int,
        content: str
    ) -> Tuple[Optional[Comment], Optional[str]]:
        """
        Update comment.
        
        Args:
            comment_id: Comment ID
            user_id: User making the update
            content: New content
        
        Returns:
            Tuple of (Comment, error_message)
        """
        comment = self.comment_repo.get_by_id(comment_id)
        if not comment:
            return None, "Comment not found"
        
        # Only author or admin can update
        if not self.can_modify_comment(comment_id, user_id):
            return None, "Not authorized to update this comment"
        
        try:
            updated_comment = self.comment_repo.update(comment_id, content=content)
            logger.info(f"Comment {comment_id} updated")
            return updated_comment, None
        except Exception as e:
            logger.error(f"Error updating comment: {str(e)}")
            return None, "Failed to update comment"
    
    def delete_comment(
        self,
        comment_id: int,
        user_id: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Delete comment.
        
        Args:
            comment_id: Comment ID
            user_id: User making the deletion
        
        Returns:
            Tuple of (success, error_message)
        """
        comment = self.comment_repo.get_by_id(comment_id)
        if not comment:
            return False, "Comment not found"
        
        # Only author or admin can delete
        if not self.can_modify_comment(comment_id, user_id):
            return False, "Not authorized to delete this comment"
        
        try:
            self.comment_repo.delete(comment_id)
            logger.info(f"Comment {comment_id} deleted")
            return True, None
        except Exception as e:
            logger.error(f"Error deleting comment: {str(e)}")
            return False, "Failed to delete comment"
    
    def can_modify_comment(self, comment_id: int, user_id: int) -> bool:
        """
        Check if user can modify comment.
        
        Args:
            comment_id: Comment ID
            user_id: User ID
        
        Returns:
            True if user can modify, False otherwise
        """
        comment = self.comment_repo.get_by_id(comment_id)
        if not comment:
            return False
        
        # Author can modify
        if comment.author_id == user_id:
            return True
        
        # Get issue to check project admin
        issue = self.issue_repo.get_by_id(comment.issue_id)
        if not issue:
            return False
        
        # Project admin can modify
        member = self.project_repo.get_member(issue.project_id, user_id)
        if member and member.role in ['owner', 'admin']:
            return True
        
        return False
    
    def can_access_comment(self, comment_id: int, user_id: int) -> bool:
        """
        Check if user can access comment.
        
        Args:
            comment_id: Comment ID
            user_id: User ID
        
        Returns:
            True if user can access, False otherwise
        """
        comment = self.comment_repo.get_by_id(comment_id)
        if not comment:
            return False
        
        # Get issue to check project membership
        issue = self.issue_repo.get_by_id(comment.issue_id)
        if not issue:
            return False
        
        # Check if user is member of the project
        return self.project_repo.is_member(issue.project_id, user_id)
