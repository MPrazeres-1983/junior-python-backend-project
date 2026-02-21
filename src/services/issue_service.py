"""Issue service with business logic."""

from typing import Dict, List, Optional, Tuple
from src.models import Issue, Label
from src.repositories import IssueRepository, ProjectRepository, LabelRepository
from src.utils.logger import logger


class IssueService:
    """Service for issue operations."""
    
    def __init__(self):
        self.issue_repo = IssueRepository()
        self.project_repo = ProjectRepository()
        self.label_repo = LabelRepository()
    
    def create_issue(
        self,
        project_id: int,
        title: str,
        reporter_id: int,
        description: Optional[str] = None,
        priority: str = 'medium',
        status: str = 'open'
    ) -> Tuple[Optional[Issue], Optional[str]]:
        """
        Create a new issue.
        
        Args:
            project_id: Project ID
            title: Issue title
            reporter_id: Reporter user ID
            description: Issue description
            priority: Priority level
            status: Issue status
        
        Returns:
            Tuple of (Issue, error_message)
        """
        # Verify project exists
        project = self.project_repo.get_by_id(project_id)
        if not project:
            return None, "Project not found"
        
        # Verify user is member
        if not self.project_repo.is_member(project_id, reporter_id):
            return None, "User is not a member of this project"
        
        try:
            issue = self.issue_repo.create(
                project_id=project_id,
                title=title,
                description=description,
                reporter_id=reporter_id,
                priority=priority,
                status=status
            )
            logger.info(f"Issue created: {title} in project {project_id}")
            return issue, None
        except Exception as e:
            logger.error(f"Error creating issue: {str(e)}")
            return None, "Failed to create issue"
    
    def get_issue(self, issue_id: int) -> Optional[Issue]:
        """Get issue by ID."""
        return self.issue_repo.get_by_id(issue_id)
    
    def update_issue(
        self,
        issue_id: int,
        user_id: int,
        **kwargs
    ) -> Tuple[Optional[Issue], Optional[str]]:
        """
        Update issue.
        
        Args:
            issue_id: Issue ID
            user_id: User making the update
            **kwargs: Fields to update
        
        Returns:
            Tuple of (Issue, error_message)
        """
        issue = self.issue_repo.get_by_id(issue_id)
        if not issue:
            return None, "Issue not found"
        
        # Check authorization
        if not self.can_modify_issue(issue_id, user_id):
            return None, "Not authorized to update this issue"
        
        try:
            updated_issue = self.issue_repo.update(issue_id, **kwargs)
            logger.info(f"Issue {issue_id} updated by user {user_id}")
            return updated_issue, None
        except Exception as e:
            logger.error(f"Error updating issue: {str(e)}")
            return None, "Failed to update issue"
    
    def delete_issue(
        self,
        issue_id: int,
        user_id: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Delete issue.
        
        Args:
            issue_id: Issue ID
            user_id: User making the deletion
        
        Returns:
            Tuple of (success, error_message)
        """
        issue = self.issue_repo.get_by_id(issue_id)
        if not issue:
            return False, "Issue not found"
        
        # Check authorization (reporter or project admin)
        if not self.can_delete_issue(issue_id, user_id):
            return False, "Not authorized to delete this issue"
        
        try:
            self.issue_repo.delete(issue_id)
            logger.info(f"Issue {issue_id} deleted by user {user_id}")
            return True, None
        except Exception as e:
            logger.error(f"Error deleting issue: {str(e)}")
            return False, "Failed to delete issue"
    
    def assign_user(
        self,
        issue_id: int,
        user_id: int,
        assignee_id: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Assign user to issue.
        
        Args:
            issue_id: Issue ID
            user_id: User making the assignment
            assignee_id: User to assign
        
        Returns:
            Tuple of (success, error_message)
        """
        issue = self.issue_repo.get_by_id(issue_id)
        if not issue:
            return False, "Issue not found"
        
        # Check if user can modify issue
        if not self.can_modify_issue(issue_id, user_id):
            return False, "Not authorized to assign users"
        
        # Check if assignee is a member of the project
        if not self.project_repo.is_member(issue.project_id, assignee_id):
            return False, "Assignee is not a member of the project"
        
        # Check if already assigned
        if self.issue_repo.is_assigned(issue_id, assignee_id):
            return False, "User is already assigned to this issue"
        
        try:
            self.issue_repo.assign_user(issue_id, assignee_id)
            logger.info(f"User {assignee_id} assigned to issue {issue_id}")
            return True, None
        except Exception as e:
            logger.error(f"Error assigning user: {str(e)}")
            return False, "Failed to assign user"
    
    def unassign_user(
        self,
        issue_id: int,
        user_id: int,
        assignee_id: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Unassign user from issue.
        
        Args:
            issue_id: Issue ID
            user_id: User making the unassignment
            assignee_id: User to unassign
        
        Returns:
            Tuple of (success, error_message)
        """
        issue = self.issue_repo.get_by_id(issue_id)
        if not issue:
            return False, "Issue not found"
        
        # Check authorization
        if not self.can_modify_issue(issue_id, user_id):
            return False, "Not authorized to unassign users"
        
        try:
            success = self.issue_repo.unassign_user(issue_id, assignee_id)
            if success:
                logger.info(f"User {assignee_id} unassigned from issue {issue_id}")
                return True, None
            return False, "User is not assigned to this issue"
        except Exception as e:
            logger.error(f"Error unassigning user: {str(e)}")
            return False, "Failed to unassign user"
    
    def add_label(
        self,
        issue_id: int,
        user_id: int,
        label_id: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Add label to issue.
        
        Args:
            issue_id: Issue ID
            user_id: User adding the label
            label_id: Label ID
        
        Returns:
            Tuple of (success, error_message)
        """
        issue = self.issue_repo.get_by_id(issue_id)
        if not issue:
            return False, "Issue not found"
        
        # Check authorization
        if not self.can_modify_issue(issue_id, user_id):
            return False, "Not authorized to add labels"
        
        # Verify label exists
        label = self.label_repo.get_by_id(label_id)
        if not label:
            return False, "Label not found"
        
        # Check if label already added
        if label in issue.labels:
            return False, "Label already added to issue"
        
        try:
            issue.labels.append(label)
            from src.models.base import db
            db.session.commit()
            logger.info(f"Label {label_id} added to issue {issue_id}")
            return True, None
        except Exception as e:
            logger.error(f"Error adding label: {str(e)}")
            from src.models.base import db
            db.session.rollback()
            return False, "Failed to add label"
    
    def remove_label(
        self,
        issue_id: int,
        user_id: int,
        label_id: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Remove label from issue.
        
        Args:
            issue_id: Issue ID
            user_id: User removing the label
            label_id: Label ID
        
        Returns:
            Tuple of (success, error_message)
        """
        issue = self.issue_repo.get_by_id(issue_id)
        if not issue:
            return False, "Issue not found"
        
        # Check authorization
        if not self.can_modify_issue(issue_id, user_id):
            return False, "Not authorized to remove labels"
        
        # Verify label exists
        label = self.label_repo.get_by_id(label_id)
        if not label:
            return False, "Label not found"
        
        # Check if label is on issue
        if label not in issue.labels:
            return False, "Label is not on this issue"
        
        try:
            issue.labels.remove(label)
            from src.models.base import db
            db.session.commit()
            logger.info(f"Label {label_id} removed from issue {issue_id}")
            return True, None
        except Exception as e:
            logger.error(f"Error removing label: {str(e)}")
            from src.models.base import db
            db.session.rollback()
            return False, "Failed to remove label"
    
    def can_modify_issue(self, issue_id: int, user_id: int) -> bool:
        """
        Check if user can modify issue.
        
        Args:
            issue_id: Issue ID
            user_id: User ID
        
        Returns:
            True if user can modify, False otherwise
        """
        issue = self.issue_repo.get_by_id(issue_id)
        if not issue:
            return False
        
        # Reporter can modify
        if issue.reporter_id == user_id:
            return True
        
        # Assignees can modify
        if self.issue_repo.is_assigned(issue_id, user_id):
            return True
        
        # Project admin can modify
        member = self.project_repo.get_member(issue.project_id, user_id)
        if member and member.role in ['owner', 'admin']:
            return True
        
        return False
    
    def can_delete_issue(self, issue_id: int, user_id: int) -> bool:
        """
        Check if user can delete issue.
        
        Args:
            issue_id: Issue ID
            user_id: User ID
        
        Returns:
            True if user can delete, False otherwise
        """
        issue = self.issue_repo.get_by_id(issue_id)
        if not issue:
            return False
        
        # Reporter can delete
        if issue.reporter_id == user_id:
            return True
        
        # Project admin can delete
        member = self.project_repo.get_member(issue.project_id, user_id)
        if member and member.role in ['owner', 'admin']:
            return True
        
        return False
    
    def can_access_issue(self, issue_id: int, user_id: int) -> bool:
        """
        Check if user can access issue.
        
        Args:
            issue_id: Issue ID
            user_id: User ID
        
        Returns:
            True if user can access, False otherwise
        """
        issue = self.issue_repo.get_by_id(issue_id)
        if not issue:
            return False
        
        # Check if user is member of the project
        return self.project_repo.is_member(issue.project_id, user_id)
