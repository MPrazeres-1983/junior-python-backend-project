"""User repository with specific queries."""

from typing import Optional
from src.models import User
from .base import BaseRepository


class UserRepository(BaseRepository):
    """Repository for User model."""
    
    def __init__(self):
        super().__init__(User)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.filter_one(username=username)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.filter_one(email=email)
    
    def get_active_users(self, limit: Optional[int] = None, offset: int = 0):
        """Get all active users."""
        query = self.session.query(User).filter(User.is_active == True)
        if limit:
            query = query.limit(limit).offset(offset)
        return query.all()
    
    def username_exists(self, username: str) -> bool:
        """Check if username exists."""
        return self.exists(username=username)
    
    def email_exists(self, email: str) -> bool:
        """Check if email exists."""
        return self.exists(email=email)
