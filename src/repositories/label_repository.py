"""Label repository with specific queries."""

from typing import Optional
from src.models import Label
from .base import BaseRepository


class LabelRepository(BaseRepository):
    """Repository for Label model."""
    
    def __init__(self):
        super().__init__(Label)
    
    def get_by_name(self, name: str) -> Optional[Label]:
        """Get label by name."""
        return self.filter_one(name=name)
    
    def name_exists(self, name: str) -> bool:
        """Check if label name exists."""
        return self.exists(name=name)
