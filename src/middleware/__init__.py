"""Middleware package."""

from .auth_middleware import (
    require_auth,
    require_role,
    optional_auth,
    get_current_user_id,
    get_current_user_identity,
    get_current_user_role,
)
from .error_handler import register_error_handlers

__all__ = [
    'require_auth',
    'require_role',
    'optional_auth',
    'get_current_user_id',
    'get_current_user_identity',
    'get_current_user_role',
    'register_error_handlers',
]
