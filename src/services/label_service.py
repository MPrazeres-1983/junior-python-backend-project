"""Label service with business logic."""

from typing import Optional, Tuple
from src.models import Label
from src.repositories import LabelRepository, UserRepository
from src.utils.logger import logger


class LabelService:
    """Service for label operations."""
    
    def __init__(self):
        self.label_repo = LabelRepository()
        self.user_repo = UserRepository()
    
    def create_label(
        self,
        name: str,
        user_id: int,
        color: str = '#808080'
    ) -> Tuple[Optional[Label], Optional[str]]:
        """
        Create a new label.
        
        Args:
            name: Label name
            user_id: User creating the label
            color: Label color (hex)
        
        Returns:
            Tuple of (Label, error_message)
        """
        # Only admins can create labels
        user = self.user_repo.get_by_id(user_id)
        if not user or user.role != 'admin':
            return None, "Only admins can create labels"
        
        # Check if label name exists
        if self.label_repo.name_exists(name):
            return None, "Label with this name already exists"
        
        try:
            label = self.label_repo.create(name=name, color=color)
            logger.info(f"Label created: {name}")
            return label, None
        except Exception as e:
            logger.error(f"Error creating label: {str(e)}")
            return None, "Failed to create label"
    
    def get_label(self, label_id: int) -> Optional[Label]:
        """Get label by ID."""
        return self.label_repo.get_by_id(label_id)
    
    def get_all_labels(self) -> list:
        """Get all labels."""
        return self.label_repo.get_all()
    
    def update_label(
        self,
        label_id: int,
        user_id: int,
        **kwargs
    ) -> Tuple[Optional[Label], Optional[str]]:
        """
        Update label.
        
        Args:
            label_id: Label ID
            user_id: User making the update
            **kwargs: Fields to update
        
        Returns:
            Tuple of (Label, error_message)
        """
        # Only admins can update labels
        user = self.user_repo.get_by_id(user_id)
        if not user or user.role != 'admin':
            return None, "Only admins can update labels"
        
        label = self.label_repo.get_by_id(label_id)
        if not label:
            return None, "Label not found"
        
        # If name is being updated, check for duplicates
        if 'name' in kwargs:
            existing = self.label_repo.get_by_name(kwargs['name'])
            if existing and existing.id != label_id:
                return None, "Label with this name already exists"
        
        try:
            updated_label = self.label_repo.update(label_id, **kwargs)
            logger.info(f"Label {label_id} updated")
            return updated_label, None
        except Exception as e:
            logger.error(f"Error updating label: {str(e)}")
            return None, "Failed to update label"
    
    def delete_label(
        self,
        label_id: int,
        user_id: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Delete label.
        
        Args:
            label_id: Label ID
            user_id: User making the deletion
        
        Returns:
            Tuple of (success, error_message)
        """
        # Only admins can delete labels
        user = self.user_repo.get_by_id(user_id)
        if not user or user.role != 'admin':
            return False, "Only admins can delete labels"
        
        label = self.label_repo.get_by_id(label_id)
        if not label:
            return False, "Label not found"
        
        try:
            self.label_repo.delete(label_id)
            logger.info(f"Label {label_id} deleted")
            return True, None
        except Exception as e:
            logger.error(f"Error deleting label: {str(e)}")
            return False, "Failed to delete label"
