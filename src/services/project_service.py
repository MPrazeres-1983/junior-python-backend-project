"""Project service with business logic."""

from typing import Dict, List, Optional, Tuple
from src.models import Project, User
from src.repositories import ProjectRepository, UserRepository
from src.utils.logger import logger


class ProjectService:
    """Service for project operations."""
    
    def __init__(self):
        self.project_repo = ProjectRepository()
        self.user_repo = UserRepository()
    
    def create_project(
        self,
        name: str,
        owner_id: int,
        description: Optional[str] = None
    ) -> Tuple[Optional[Project], Optional[str]]:
        """
        Create a new project.
        
        Args:
            name: Project name
            owner_id: Owner user ID
            description: Project description
        
        Returns:
            Tuple of (Project, error_message)
        """
        # Verify owner exists
        owner = self.user_repo.get_by_id(owner_id)
        if not owner:
            return None, "Owner not found"
        
        # Create project
        try:
            project = self.project_repo.create(
                name=name,
                owner_id=owner_id,
                description=description,
                is_active=True
            )
            
            # Automatically add owner as a member with 'owner' role
            self.project_repo.add_member(project.id, owner_id, role='owner')
            
            logger.info(f"Project created: {name} by user {owner_id}")
            return project, None
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            return None, "Failed to create project"
    
    def get_project(self, project_id: int) -> Optional[Project]:
        """Get project by ID."""
        return self.project_repo.get_by_id(project_id)
    
    def update_project(
        self,
        project_id: int,
        user_id: int,
        **kwargs
    ) -> Tuple[Optional[Project], Optional[str]]:
        """
        Update project.
        
        Args:
            project_id: Project ID
            user_id: User making the update
            **kwargs: Fields to update
        
        Returns:
            Tuple of (Project, error_message)
        """
        project = self.project_repo.get_by_id(project_id)
        if not project:
            return None, "Project not found"
        
        # Check authorization (only owner or admin)
        if not self.can_modify_project(project_id, user_id):
            return None, "Not authorized to update this project"
        
        try:
            updated_project = self.project_repo.update(project_id, **kwargs)
            logger.info(f"Project {project_id} updated by user {user_id}")
            return updated_project, None
        except Exception as e:
            logger.error(f"Error updating project: {str(e)}")
            return None, "Failed to update project"
    
    def delete_project(
        self,
        project_id: int,
        user_id: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Delete project.
        
        Args:
            project_id: Project ID
            user_id: User making the deletion
        
        Returns:
            Tuple of (success, error_message)
        """
        project = self.project_repo.get_by_id(project_id)
        if not project:
            return False, "Project not found"
        
        # Only owner can delete
        if project.owner_id != user_id:
            # Check if user is admin role
            user = self.user_repo.get_by_id(user_id)
            if not user or user.role != 'admin':
                return False, "Only project owner or admin can delete"
        
        try:
            self.project_repo.delete(project_id)
            logger.info(f"Project {project_id} deleted by user {user_id}")
            return True, None
        except Exception as e:
            logger.error(f"Error deleting project: {str(e)}")
            return False, "Failed to delete project"
    
    def add_member(
        self,
        project_id: int,
        user_id: int,
        member_user_id: int,
        role: str = 'member'
    ) -> Tuple[bool, Optional[str]]:
        """
        Add member to project.
        
        Args:
            project_id: Project ID
            user_id: User adding the member (must be owner/admin)
            member_user_id: User to add as member
            role: Role for the member
        
        Returns:
            Tuple of (success, error_message)
        """
        # Check authorization
        if not self.can_modify_project(project_id, user_id):
            return False, "Not authorized to add members"
        
        # Verify member user exists
        member = self.user_repo.get_by_id(member_user_id)
        if not member:
            return False, "User not found"
        
        # Check if already a member
        if self.project_repo.is_member(project_id, member_user_id):
            return False, "User is already a member"
        
        try:
            self.project_repo.add_member(project_id, member_user_id, role)
            logger.info(f"User {member_user_id} added to project {project_id}")
            return True, None
        except Exception as e:
            logger.error(f"Error adding member: {str(e)}")
            return False, "Failed to add member"
    
    def remove_member(
        self,
        project_id: int,
        user_id: int,
        member_user_id: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Remove member from project.
        
        Args:
            project_id: Project ID
            user_id: User removing the member
            member_user_id: User to remove
        
        Returns:
            Tuple of (success, error_message)
        """
        project = self.project_repo.get_by_id(project_id)
        if not project:
            return False, "Project not found"
        
        # Cannot remove owner
        if project.owner_id == member_user_id:
            return False, "Cannot remove project owner"
        
        # Check authorization
        if not self.can_modify_project(project_id, user_id):
            return False, "Not authorized to remove members"
        
        try:
            success = self.project_repo.remove_member(project_id, member_user_id)
            if success:
                logger.info(f"User {member_user_id} removed from project {project_id}")
                return True, None
            return False, "Member not found"
        except Exception as e:
            logger.error(f"Error removing member: {str(e)}")
            return False, "Failed to remove member"
    
    def can_modify_project(self, project_id: int, user_id: int) -> bool:
        """
        Check if user can modify project.
        
        Args:
            project_id: Project ID
            user_id: User ID
        
        Returns:
            True if user can modify, False otherwise
        """
        project = self.project_repo.get_by_id(project_id)
        if not project:
            return False
        
        # Owner can always modify
        if project.owner_id == user_id:
            return True
        
        # Check if user is admin member
        member = self.project_repo.get_member(project_id, user_id)
        if member and member.role in ['owner', 'admin']:
            return True
        
        # Check if user has global admin role
        user = self.user_repo.get_by_id(user_id)
        if user and user.role == 'admin':
            return True
        
        return False
    
    def can_access_project(self, project_id: int, user_id: int) -> bool:
        """
        Check if user can access project.
        
        Args:
            project_id: Project ID
            user_id: User ID
        
        Returns:
            True if user can access, False otherwise
        """
        # Check if user is member (includes owner)
        return self.project_repo.is_member(project_id, user_id)
    
    def get_user_projects(self, user_id: int) -> List[Project]:
        """
        Get all projects user has access to.
        
        Args:
            user_id: User ID
        
        Returns:
            List of projects
        """
        return self.project_repo.get_user_projects(user_id)
