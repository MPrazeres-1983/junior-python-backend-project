"""Pagination helpers."""

from typing import Any, Dict, List, Optional
from flask import request, url_for


def get_pagination_params(
    default_page_size: int = 20,
    max_page_size: int = 100
) -> Dict[str, int]:
    """
    Extract and validate pagination parameters from request.
    
    Args:
        default_page_size: Default number of items per page
        max_page_size: Maximum allowed items per page
    
    Returns:
        Dictionary with page and per_page values
    """
    try:
        page = int(request.args.get('page', 1))
        page = max(1, page)  # Ensure page >= 1
    except (TypeError, ValueError):
        page = 1
    
    try:
        per_page = int(request.args.get('per_page', default_page_size))
        per_page = max(1, min(per_page, max_page_size))  # Clamp between 1 and max
    except (TypeError, ValueError):
        per_page = default_page_size
    
    return {'page': page, 'per_page': per_page}


def build_pagination_response(
    items: List[Any],
    total: int,
    page: int,
    per_page: int,
    endpoint: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Build paginated response with metadata.
    
    Args:
        items: List of items for current page
        total: Total number of items
        page: Current page number
        per_page: Items per page
        endpoint: Flask endpoint for generating links (optional)
        **kwargs: Additional query parameters for links
    
    Returns:
        Dictionary with data and pagination metadata
    """
    total_pages = (total + per_page - 1) // per_page if total > 0 else 0
    
    response = {
        'data': items,
        'meta': {
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages,
        }
    }
    
    # Add navigation links if endpoint provided
    if endpoint:
        links = {}
        
        if page > 1:
            links['prev'] = url_for(endpoint, page=page - 1, per_page=per_page, **kwargs, _external=True)
            links['first'] = url_for(endpoint, page=1, per_page=per_page, **kwargs, _external=True)
        
        if page < total_pages:
            links['next'] = url_for(endpoint, page=page + 1, per_page=per_page, **kwargs, _external=True)
            links['last'] = url_for(endpoint, page=total_pages, per_page=per_page, **kwargs, _external=True)
        
        if links:
            response['links'] = links
    
    return response


class Pagination:
    """Pagination helper class."""
    
    def __init__(
        self,
        items: List[Any],
        total: int,
        page: int,
        per_page: int
    ):
        self.items = items
        self.total = total
        self.page = page
        self.per_page = per_page
        self.total_pages = (total + per_page - 1) // per_page if total > 0 else 0
    
    @property
    def has_prev(self) -> bool:
        """Check if there's a previous page."""
        return self.page > 1
    
    @property
    def has_next(self) -> bool:
        """Check if there's a next page."""
        return self.page < self.total_pages
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert pagination to dictionary."""
        return {
            'total': self.total,
            'page': self.page,
            'per_page': self.per_page,
            'total_pages': self.total_pages,
            'has_prev': self.has_prev,
            'has_next': self.has_next,
        }
