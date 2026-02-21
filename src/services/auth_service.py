"""Authentication service with JWT and password hashing."""

import bcrypt
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt,
)
from src.models import User
from src.repositories import UserRepository
from src.utils.logger import logger


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self):
        self.user_repo = UserRepository()
    
    def hash_password(self, password: str) -> str:
        """
        Hash password using bcrypt.
        
        Args:
            password: Plain text password
        
        Returns:
            Hashed password
        """
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify password against hash.
        
        Args:
            password: Plain text password
            password_hash: Hashed password
        
        Returns:
            True if password matches, False otherwise
        """
        password_bytes = password.encode('utf-8')
        hash_bytes = password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    
    def register(
        self,
        username: str,
        email: str,
        password: str,
        role: str = 'developer'
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        Register a new user.
        
        Args:
            username: Username
            email: Email address
            password: Plain text password
            role: User role (default: developer)
        
        Returns:
            Tuple of (User, error_message)
        """
        # Check if username exists
        if self.user_repo.username_exists(username):
            return None, "Username already exists"
        
        # Check if email exists
        if self.user_repo.email_exists(email):
            return None, "Email already exists"
        
        # Hash password
        password_hash = self.hash_password(password)
        
        # Create user
        try:
            user = self.user_repo.create(
                username=username,
                email=email,
                password_hash=password_hash,
                role=role,
                is_active=True
            )
            logger.info(f"User registered: {username}")
            return user, None
        except Exception as e:
            logger.error(f"Error registering user: {str(e)}")
            return None, "Failed to register user"
    
    def login(
        self,
        username: str,
        password: str
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Authenticate user and generate tokens.
        
        Args:
            username: Username
            password: Plain text password
        
        Returns:
            Tuple of (tokens_dict, error_message)
        """
        # Get user by username
        user = self.user_repo.get_by_username(username)
        
        if not user:
            return None, "Invalid credentials"
        
        # Check if user is active
        if not user.is_active:
            return None, "Account is disabled"
        
        # Verify password
        if not self.verify_password(password, user.password_hash):
            return None, "Invalid credentials"
        
        # Generate tokens
        identity = {
            'user_id': user.id,
            'username': user.username,
            'role': user.role
        }
        
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)
        
        logger.info(f"User logged in: {username}")
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'user': user.to_dict(include_email=True)
        }, None
    
    def refresh(self, current_user_identity: Dict) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Generate new access token from refresh token.
        
        Args:
            current_user_identity: User identity from JWT
        
        Returns:
            Tuple of (tokens_dict, error_message)
        """
        # Verify user still exists and is active
        user = self.user_repo.get_by_id(current_user_identity['user_id'])
        
        if not user:
            return None, "User not found"
        
        if not user.is_active:
            return None, "Account is disabled"
        
        # Generate new access token
        identity = {
            'user_id': user.id,
            'username': user.username,
            'role': user.role
        }
        
        access_token = create_access_token(identity=identity)
        
        return {
            'access_token': access_token,
            'token_type': 'Bearer'
        }, None
    
    def get_current_user(self, user_id: int) -> Optional[User]:
        """
        Get current authenticated user.
        
        Args:
            user_id: User ID from JWT
        
        Returns:
            User or None
        """
        return self.user_repo.get_by_id(user_id)
    
    def update_password(
        self,
        user_id: int,
        current_password: str,
        new_password: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Update user password.
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
        
        Returns:
            Tuple of (success, error_message)
        """
        user = self.user_repo.get_by_id(user_id)
        
        if not user:
            return False, "User not found"
        
        # Verify current password
        if not self.verify_password(current_password, user.password_hash):
            return False, "Current password is incorrect"
        
        # Hash new password
        new_password_hash = self.hash_password(new_password)
        
        # Update password
        try:
            self.user_repo.update(user_id, password_hash=new_password_hash)
            logger.info(f"Password updated for user: {user.username}")
            return True, None
        except Exception as e:
            logger.error(f"Error updating password: {str(e)}")
            return False, "Failed to update password"
